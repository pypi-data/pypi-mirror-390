//! Vocabulary datastructures and methods.
//!
//! A [Vocabulary] contains a collection of [Symbol]s and some [TypeInterp]s.

use super::error::ParseCustomTypeError;
use super::error::parse::{Diagnostics, IDPError};
use super::fmt::{
    self, CharSet, Fmt, FodotDisplay, FodotOptions, FormatOptions, PRODUCT_ASCII, PRODUCT_UNI,
};
use super::structure::{
    _PartialTypeInterps, DomainFull, IntInterpRef, IntoPtr, PartialTypeInterps, RealInterpRef,
    StrInterpRef, TypeInterp, TypeInterpRef, TypeInterps,
};
use super::theory::vocabs_ptr_eq;
use super::{TryIntoCtx, display_as_debug};
use crate::ast::{self, VocabAst, tree_sitter::TsParser};
use crate::fodot::error::{
    BaseTypeMismatchError, MissingSymbol, MissingSymbolError, OverrideBuiltinTypeInterpError,
    ParseSymbolError, Redeclaration, RedeclarationError, StrSetTypeInterpError, VocabMismatchError,
    WrongSymbolType,
};
use crate::sli_entrance::parse_vocab_decls;
use comp_core::{
    IndexRange, IndexRepr,
    vocabulary::{
        BaseType as CCBaseType, Domain as CCDomain, DomainIndex, DomainSlice as CCDomainSlice,
        PfuncDecl as CCPfuncDecl, PfuncIndex as CCPfuncIndex, Type as CCType, TypeDecl, TypeIndex,
        Vocabulary as CCVocabulary,
    },
};
use const_format::formatcp;
use itertools::Itertools;
use sli_collections::hash_map::IdHashMap;
use sli_collections::{
    iterator::Iterator as SIterator,
    rc::{PtrRepr, Rc, RcA},
};
use std::ops::Deref;
use std::{
    borrow::Borrow,
    collections::HashMap,
    error::Error,
    fmt::{Display, Write},
};
use typed_index_collections::TiVec;

mod types;
pub use types::*;
mod symbols;
pub use symbols::*;

mod indexes {
    use comp_core::create_index;
    create_index!(TypeSymbolIndex);
    create_index!(PfuncIndex);
    create_index!(RealTypeIndex);
}
pub(super) use indexes::*;

/// An FO(·) vocabulary.
///
/// Each symbol name in a vocabulary must be unique.
/// e.g. adding a type named `T` and then adding a pfunc with a name `T` results in an error being
/// returned when trying to add the pfunc since a symbol with the name `T` already exists.
///
/// All methods are fallible because of the possibility of supplying an argument that is bound to
/// a vocabulary but this vocabulary is not the same as the one you're calling the method on.
///
/// Using a vocabulary for a structure first requires it to become immutable and ownable from
/// multiple sources using an [Rc].
/// This is done via the [Self::complete_vocab] method.
///
/// Note: each vocabulary is currently considered unique even if they contain the exact same
/// symbols.
#[derive(Clone)]
pub struct Vocabulary {
    pub name: Rc<str>,
    type_names: TiVec<TypeSymbolIndex, Rc<str>>,
    pfunc_names: TiVec<PfuncIndex, Rc<str>>,
    pub(crate) part_type_interps: _PartialTypeInterps,
    voc_symbols: HashMap<Rc<str>, CustomSymbolIndex>,
    vocabular_metadata: VocabularyMetadata,
    pub(super) comp_core_symbs: Rc<comp_core::vocabulary::Vocabulary>,
}

impl FodotOptions for Vocabulary {
    type Options<'a> = FormatOptions;
}

impl FodotDisplay for Vocabulary {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        writeln!(f, "vocabulary {} {{", fmt.value.name)?;
        for voc_type in fmt.value.iter_types() {
            fmt.options.write_indent_extra(f, 1)?;
            write!(f, "type {}", fmt.with_format_opts(&voc_type))?;
            let write_def_eq = |f: &mut std::fmt::Formatter<'_>| -> std::fmt::Result {
                f.write_char(' ')?;
                fmt.options.write_def_eq(f)
            };
            match voc_type {
                CustomTypeRef::Int(int_type) => {
                    if let Some(type_enum) =
                        int_type.interp_from_partial(&fmt.value.part_type_interps)
                    {
                        write_def_eq(f)?;
                        write!(f, " {}", fmt.with_format_opts(type_enum.interp()))?;
                    }
                }
                CustomTypeRef::Real(real_type) => {
                    if let Some(type_enum) =
                        real_type.interp_from_partial(&fmt.value.part_type_interps)
                    {
                        write_def_eq(f)?;
                        write!(f, " {}", fmt.with_format_opts(type_enum.interp()))?;
                    }
                }
                CustomTypeRef::Str(str_type) => {
                    if let Some(type_enum) =
                        str_type.interp_from_partial(&fmt.value.part_type_interps)
                    {
                        write_def_eq(f)?;
                        write!(f, " {}", fmt.with_format_opts(type_enum.interp()))?;
                    }
                }
            }
            f.write_char(' ')?;
            if !matches!(voc_type.super_type(), BaseType::Str) {
                fmt.options.write_superset(f)?;
                write!(f, " {}", fmt.with_format_opts(&voc_type.super_type()))?;
            }
            f.write_char('\n')?;
        }
        for func in fmt.value.iter_pfuncs() {
            fmt.options.write_indent_extra(f, 1)?;
            writeln!(f, "{}", fmt.with_format_opts(&func))?;
        }
        write!(f, "}}")
    }
}

impl Display for Vocabulary {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", Fmt::with_defaults(self))
    }
}

display_as_debug!(Vocabulary);

impl Vocabulary {
    /// Create an empty vocabulary with a name.
    pub fn new(name: &str) -> Self {
        Self {
            name: name.into(),
            type_names: Default::default(),
            pfunc_names: Default::default(),
            voc_symbols: Default::default(),
            part_type_interps: Default::default(),
            vocabular_metadata: Default::default(),
            comp_core_symbs: Rc::new(CCVocabulary::new()),
        }
    }

    pub fn name(&self) -> &str {
        &self.name
    }

    pub fn parse(&mut self, decls: &str) -> Result<&mut Self, Diagnostics> {
        let mut parser = TsParser::new();
        let vocab_ast = ast::Parser::parse_vocab(&mut parser, decls);
        let mut diagnostics = Diagnostics::new();
        for (err, span) in vocab_ast.parse_errors() {
            diagnostics.add_error(IDPError::new(err.into(), span));
        }
        // This is sad, but ok
        let old = self.clone();
        parse_vocab_decls(&decls, self, vocab_ast.decls(), &mut diagnostics);
        if diagnostics.errors().len() == 0 {
            Ok(self)
        } else {
            *self = old;
            Err(diagnostics)
        }
    }

    fn get_name(&self, type_id: TypeSymbolIndex) -> &str {
        &self.type_names[type_id]
    }

    fn get_name_rc(&self, type_id: TypeSymbolIndex) -> Rc<str> {
        self.type_names[type_id].clone()
    }

    /// Returns [SymbolRef] from the corresponding name.
    pub fn parse_symbol(&self, name: &str) -> Result<SymbolRef, MissingSymbolError> {
        if let Ok(value) = parse_primitive_type(name) {
            return Ok(Symbol::Type(value.into()));
        }

        // Don't consider builtin elements such as true, false, 0, 1, 2...
        // as actual symbols.
        match self.voc_symbols.get(name) {
            Some(CustomSymbolIndex::Type(custom_type)) => {
                Ok(self._get_type_id(*custom_type).wrap(self).into())
            }
            Some(CustomSymbolIndex::Pfunc(pfunc)) => Ok(Pfunc(*pfunc, self).into()),
            Some(CustomSymbolIndex::Constructor(constr)) => Ok(Constructor {
                type_id: StrType(constr.0, self),
                type_enum: constr.1,
            }
            .into()),
            None => {
                return Err(MissingSymbol(name.into()).into());
            }
        }
    }

    /// [Rc] version of [Self::parse_symbol].
    pub fn parse_symbol_rc(this: &Rc<Self>, name: &str) -> Result<SymbolRc, MissingSymbolError> {
        this.parse_symbol(name)
            .map(|f| f.wrap(Rc::clone(this).into()))
    }

    /// Adds a type with given name to the vocabulary with given [BaseType].
    ///
    /// This function returns [Err] if the given name is already a symbol.
    pub fn add_type_decl(
        &mut self,
        name: &str,
        super_set: BaseType,
    ) -> Result<&mut Self, RedeclarationError> {
        match self.voc_symbols.get(name) {
            Some(_) => return Err(Redeclaration(name.into()).into()),
            None => {}
        }
        let name = name.into();
        Rc::make_mut(&mut self.comp_core_symbs).add_type_decl(TypeDecl {
            super_type: super_set.into(),
        });
        // TODO this is not great
        let index = self.type_names.len().into();
        self.type_names.push(Rc::clone(&name));
        self.voc_symbols
            .insert(name, CustomSymbolIndex::Type(index));
        Ok(self)
    }

    /// A type declaration with an interpretation.
    ///
    /// This function is a combination of [Self::add_type_decl] and [Self::add_voc_type_interp].
    /// Without the need for the [BaseType] argument in [Self::add_type_decl] since we can find
    /// this from the `interp` argument.
    pub fn add_type_decl_with_interp(
        &mut self,
        name: &str,
        interp: TypeInterp,
    ) -> Result<&mut Self, RedeclarationError> {
        let base_type = interp.base_type();
        self.add_type_decl(name, base_type)?;
        self.add_voc_type_interp(name, interp).unwrap();
        Ok(self)
    }

    fn _parse_type(&self, value: &str) -> Result<_Type, ParseSymbolError> {
        if let Ok(prim) = parse_primitive_type(value) {
            return Ok(prim.into());
        }
        self._parse_custom_type(value).map(|f| f.into())
    }

    fn _parse_custom_type(&self, value: &str) -> Result<_CustomType, ParseSymbolError> {
        match self.voc_symbols.get(value) {
            Some(&CustomSymbolIndex::Type(type_index)) => Ok(self._get_type_id(type_index).into()),
            Some(value) => Err(WrongSymbolType {
                found: value.into(),
                expected: SymbolType::Type,
            }
            .into()),
            None => Err(MissingSymbol(value.into()).into()),
        }
    }

    fn _get_type_id(&self, type_index: TypeSymbolIndex) -> _CustomType {
        match self.comp_core_symbs.types[TypeIndex::from(IndexRepr::from(type_index))].super_type {
            CCBaseType::Int => _CustomType::IntType(type_index),
            CCBaseType::Real => _CustomType::RealType(type_index),
            CCBaseType::Str => _CustomType::String(type_index),
        }
    }

    pub(super) fn _get_type(&self, type_index: TypeSymbolIndex) -> CustomTypeRef {
        self._get_type_id(type_index).wrap(self)
    }

    /// Returns [TypeRef] from the corresponding name.
    pub fn parse_type(&self, name: &str) -> Result<TypeRef, ParseSymbolError> {
        self._parse_type(name).map(|f| f.wrap(self))
    }

    pub fn parse_custom_type(&self, name: &str) -> Result<CustomTypeRef, ParseSymbolError> {
        self._parse_custom_type(name).map(|f| f.wrap(self))
    }

    /// [Rc] version of [Self::parse_type].
    pub fn parse_type_rc(this: &Rc<Self>, name: &str) -> Result<TypeRc, ParseSymbolError> {
        this._parse_type(name).map(|f| f.wrap(this.clone().into()))
    }

    /// [Rc] version of [Self::parse_type].
    pub fn parse_custom_type_rc(
        this: &Rc<Self>,
        name: &str,
    ) -> Result<CustomTypeRc, ParseSymbolError> {
        this._parse_custom_type(name)
            .map(|f| f.wrap(this.clone().into()))
    }

    /// Returns [PfuncRef] from the corresponding name.
    pub fn parse_pfunc(&self, name: &str) -> Result<PfuncRef, ParseSymbolError> {
        if let Some(value) = self.voc_symbols.get(name) {
            match value {
                CustomSymbolIndex::Pfunc(index) => Ok(Pfunc(*index, self)),
                value => Err(WrongSymbolType {
                    found: value.into(),
                    expected: SymbolType::Pfunc,
                }
                .into()),
            }
        } else {
            Err(MissingSymbol(name.into()).into())
        }
    }

    /// [Rc] version of [Self::parse_pfunc].
    pub fn parse_pfunc_rc(this: &Rc<Self>, name: &str) -> Result<PfuncRc, ParseSymbolError> {
        this.parse_pfunc(name)
            .map(|f| Pfunc(f.0, Rc::clone(this).into()))
    }

    fn add_pfunc_decl(
        &mut self,
        name: Rc<str>,
        domain: &[_Type],
        codomain: &_Type,
    ) -> Result<PfuncIndex, RedeclarationError> {
        match self.voc_symbols.get(&name) {
            Some(_) => Err(Redeclaration(name.as_ref().into()).into()),
            None => {
                let pfunc_decl_index = PfuncIndex::from(self.pfunc_names.len());
                self.pfunc_names.push(Rc::clone(&name));
                let cc_codomain = codomain.to_cc(&self);
                let dom_id = self.add_domain(domain);
                let cc = Rc::make_mut(&mut self.comp_core_symbs);
                // TODO
                let _ = cc.add_pfunc_decl(CCPfuncDecl {
                    domain: dom_id,
                    codomain: cc_codomain,
                });
                Ok(pfunc_decl_index)
            }
        }
    }

    pub(crate) fn add_domain(&self, domain: &[_Type]) -> DomainIndex {
        let cc_domain = domain.iter().map(|&f| f.to_cc(&self)).collect::<Box<[_]>>();
        self.comp_core_symbs.add_domain(cc_domain)
    }

    pub(crate) fn id_iter_types(&self) -> IndexRange<TypeSymbolIndex> {
        IndexRange::new(0..self.type_names.len())
    }

    /// Returns an [Iterator] over all types declared in the vocabulary.
    ///
    /// This iterator iterates over [CustomTypeRef] instead of [Type] since builtin types are not
    /// declarable in a vocabulary.
    pub fn iter_types(&self) -> impl SIterator<Item = CustomTypeRef> {
        self.id_iter_types()
            .map(move |f| self._get_type_id(f).wrap(self))
    }

    pub(crate) fn id_iter_pfuncs(&self) -> IndexRange<PfuncIndex> {
        IndexRange::new(0..self.pfunc_names.len())
    }

    /// Returns an [Iterator] over all [Pfunc]s as [PfuncRef]s.
    pub fn iter_pfuncs(&self) -> impl SIterator<Item = PfuncRef> + Clone {
        self.id_iter_pfuncs().map(move |f| Pfunc(f, self))
    }

    /// Returns an [Iterator] over all [Pfunc]s as [PfuncRef]s.
    pub fn iter_pfuncs_rc(this: &Rc<Self>) -> impl SIterator<Item = PfuncRc> + Clone {
        let vocab = Rc::clone(this);
        this.id_iter_pfuncs()
            .map(move |f| Pfunc(f, vocab.clone().into()))
    }

    /// Completes the vocabulary.
    ///
    /// Returning an [Rc] wrapped version of it that is immutable and a
    /// [PartialTypeInterps] that contains all the types that have already been given an
    /// interpretation.
    ///
    /// Also see [PartialTypeInterps].
    pub fn complete_vocab(self) -> (Rc<Vocabulary>, PartialTypeInterps) {
        let vocab: Rc<_> = self.into();
        (
            Rc::clone(&vocab),
            PartialTypeInterps::for_vocab(vocab.clone()),
        )
    }

    pub fn get_type_interps(this: Rc<Self>) -> PartialTypeInterps {
        PartialTypeInterps::for_vocab(this.clone())
    }

    /// Adds a [TypeInterp] to the vocabulary.
    ///
    /// The enumerations of [TypeInterp]s with [BaseType::Str] get added as
    /// constructors.
    ///
    /// Others enable the use of directly specifying the arguments in an
    /// [AppliedSymbol](crate::fodot::theory::AppliedSymbol).
    pub fn add_voc_type_interp(
        &mut self,
        type_name: &str,
        interp: TypeInterp,
    ) -> Result<&mut Self, StrSetTypeInterpError> {
        let val = self._parse_type(type_name)?;
        match (val, interp) {
            (_Type::IntType(type_id), TypeInterp::Int(interp)) => {
                self.part_type_interps.add_interp(type_id, interp.into());
                Ok(self)
            }
            (_Type::RealType(type_id), TypeInterp::Real(interp)) => {
                self.part_type_interps.add_interp(type_id, interp.into());
                Ok(self)
            }
            (_Type::StrType(type_id), TypeInterp::Str(interp)) => {
                let (new_voc_symbols, fix_up) =
                    if let Some(prev) = self.part_type_interps.get_interp(type_id) {
                        let TypeInterp::Str(prev) = prev else {
                            unreachable!()
                        };
                        let mut voc_symbols = self.voc_symbols.clone();
                        for value in prev.iter() {
                            voc_symbols.remove(value.as_ref());
                        }
                        (voc_symbols, false)
                    } else {
                        (core::mem::take(&mut self.voc_symbols), true)
                    };
                if let Some(value) = interp
                    .iter()
                    .find(|f| new_voc_symbols.contains_key(f.as_ref()))
                {
                    if fix_up {
                        self.voc_symbols = new_voc_symbols;
                    }
                    return Err(Redeclaration(value.as_ref().into()).into());
                }
                self.voc_symbols = new_voc_symbols;
                self.voc_symbols
                    .extend(interp.into_iter().enumerate().map(|(id, val)| {
                        (
                            Rc::clone(val),
                            CustomSymbolIndex::Constructor((type_id, id.into())),
                        )
                    }));
                self.part_type_interps.add_interp(type_id, interp.into());
                Ok(self)
            }
            (builtin @ (_Type::Bool | _Type::Int | _Type::Real), _) => {
                let prim_type = match builtin {
                    _Type::Bool => PrimitiveType::Bool,
                    _Type::Int => PrimitiveType::Int,
                    _Type::Real => PrimitiveType::Real,
                    _ => unreachable!(),
                };
                Err(OverrideBuiltinTypeInterpError(prim_type).into())
            }
            (declared_type, gotten) => {
                let declared_base = match declared_type {
                    _Type::IntType(_) => BaseType::Int,
                    _Type::RealType(_) => BaseType::Real,
                    _Type::StrType(_) => BaseType::Str,
                    _ => unreachable!(),
                };
                Err(BaseTypeMismatchError {
                    found: gotten.base_type(),
                    expected: declared_base,
                }
                .into())
            }
        }
    }

    /// Method for creating a [Pfunc].
    /// Additional options for the [Pfunc] can be specified using the method on [PfuncBuilder].
    pub fn build_pfunc_decl<'a>(
        &'a mut self,
        codomain: &str,
    ) -> Result<PfuncBuilder<'a>, ParseSymbolError> {
        let codomain = self._parse_type(codomain)?;
        Ok(PfuncBuilder {
            vocab: self,
            domain: Default::default(),
            codomain,
        })
    }

    /// Returns a [TypeInterpRef] if the given [CustomType] has been given an interpretations in
    /// this vocabulary.
    pub fn get_interp<'a>(
        &'a self,
        type_: CustomTypeRef<'a>,
    ) -> Result<Option<TypeInterpRef<'a>>, VocabMismatchError> {
        if !self.exact_eq(type_.vocab()) {
            return Err(VocabMismatchError {}.into());
        }
        let value = if let Some(value) = self.part_type_interps.get_interp(type_.type_id()) {
            value
        } else {
            return Ok(None);
        };
        match (value, TypeRef::from(type_)) {
            (TypeInterp::Int(interp), TypeRef::IntType(decl)) => {
                Ok(Some(IntInterpRef { decl, interp }.into()))
            }
            (TypeInterp::Real(interp), TypeRef::RealType(decl)) => {
                Ok(Some(RealInterpRef { decl, interp }.into()))
            }
            (TypeInterp::Str(interp), TypeRef::StrType(decl)) => {
                Ok(Some(StrInterpRef { decl, interp }.into()))
            }
            (_, TypeRef::Bool | TypeRef::Int | TypeRef::Real) => unreachable!(),
            _ => panic!("Internal error"),
        }
    }

    pub fn exact_eq(&self, other: &Self) -> bool {
        core::ptr::eq(self, other)
    }

    fn _pfunc_metadata(&self, id: PfuncIndex) -> Option<&PfuncMetadata> {
        self.vocabular_metadata.pfunc_metadata.get(&id)
    }

    fn _pfunc_metadata_mut(&mut self, id: PfuncIndex) -> &mut PfuncMetadata {
        self.vocabular_metadata
            .pfunc_metadata
            .entry(id)
            .or_default()
    }

    fn _type_metadata(&self, id: TypeSymbolIndex) -> Option<&TypeMetadata> {
        self.vocabular_metadata.type_metadata.get(&id)
    }

    fn _type_metadata_mut(&mut self, id: TypeSymbolIndex) -> &mut TypeMetadata {
        self.vocabular_metadata.type_metadata.entry(id).or_default()
    }

    pub fn pfunc_metadata_mut(
        &mut self,
        pfunc: &str,
    ) -> Result<&mut PfuncMetadata, ParseSymbolError> {
        let pfunc = self.parse_pfunc(pfunc)?;
        let id = pfunc.0;
        Ok(self._pfunc_metadata_mut(id))
    }

    pub fn type_metadata_mut(
        &mut self,
        name: &str,
    ) -> Result<&mut TypeMetadata, ParseCustomTypeError> {
        let type_ = CustomType::try_from(self.parse_type(name)?)?;
        let id = type_.type_id();
        Ok(self._type_metadata_mut(id))
    }
}

#[derive(Clone, Default)]
struct VocabularyMetadata {
    pfunc_metadata: IdHashMap<PfuncIndex, PfuncMetadata>,
    type_metadata: IdHashMap<TypeSymbolIndex, TypeMetadata>,
}

#[derive(Debug, Clone)]
pub enum SymbolError {
    Redeclaration,
    IDK,
}

impl Error for SymbolError {}

impl Display for SymbolError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{:#?}", self)
    }
}

/// Used for building [Pfunc]s.
pub struct PfuncBuilder<'a> {
    vocab: &'a mut Vocabulary,
    domain: Vec<_Type>,
    codomain: _Type,
}

impl<'a> PfuncBuilder<'a> {
    /// Returns a reference to the [Vocabulary] for which we are building [Pfunc]s.
    pub fn vocab(&self) -> &Vocabulary {
        &self.vocab
    }

    pub fn take_vocab(self) -> &'a mut Vocabulary {
        self.vocab
    }

    pub fn vocab_mut(&mut self) -> &mut Vocabulary {
        self.vocab
    }

    /// Adds the given [Type] in [str] format to the domain of the symbol.
    pub fn add_to_domain(&mut self, type_name: &str) -> Result<&mut Self, ParseSymbolError> {
        let tye = self.vocab._parse_type(type_name)?;
        self.domain.push(tye);
        Ok(self)
    }

    /// Sets the domain to the given iterator of type names.
    pub fn set_domain<'b, I: IntoIterator<Item = &'b str>>(
        &mut self,
        type_names: I,
    ) -> Result<&mut Self, ParseSymbolError> {
        self.domain.clear();
        for value in type_names {
            let tye = self.vocab._parse_type(value)?;
            self.domain.push(tye);
        }
        Ok(self)
    }

    /// Adds the symbol to the [Vocabulary].
    /// A [PfuncBuilder] can be reused for adding symbols with the same signature but with a
    /// different name.
    pub fn complete_with_name(&mut self, decl_name: &str) -> Result<&mut Self, RedeclarationError> {
        let decl_name = decl_name.into();
        let index =
            self.vocab
                .add_pfunc_decl(Rc::clone(&decl_name), &self.domain, &self.codomain)?;
        self.vocab
            .voc_symbols
            .insert(decl_name, CustomSymbolIndex::Pfunc(index));
        Ok(self)
    }
}

/// A [Domain] which is extended to represent the domain of [Type]s, which are unary domains
/// over the universe.
#[non_exhaustive]
#[derive(Clone)]
pub enum ExtendedDomain<'a> {
    UnaryUniverse,
    Domain(DomainRef<'a>),
}

impl<'a> ExtendedDomain<'a> {
    /// Checks if the domain is an unary domain with the only type being the universe.
    pub fn is_unary_universe(&self) -> bool {
        match self {
            ExtendedDomain::UnaryUniverse => true,
            ExtendedDomain::Domain(_) => false,
        }
    }

    /// Returns the arity of the domain.
    pub fn arity(&self) -> usize {
        match self {
            ExtendedDomain::UnaryUniverse => 1,
            ExtendedDomain::Domain(dom) => dom.arity(),
        }
    }

    /// Tries to return the underlying [DomainRef].
    pub fn try_into_domain(self) -> Option<DomainRef<'a>> {
        match self {
            ExtendedDomain::Domain(value) => Some(value),
            _ => None,
        }
    }
}

pub(crate) mod domain_funcs {
    use super::*;

    pub(crate) fn cc_domain<'a>(
        id: Option<DomainIndex>,
        vocab: &'a Vocabulary,
    ) -> &'a CCDomainSlice {
        if let Some(index) = id {
            vocab.comp_core_symbs.get_domain(index)
        } else {
            &CCDomain([])
        }
    }

    pub(crate) fn get<'a>(
        id: Option<DomainIndex>,
        vocab: &'a Vocabulary,
        index: usize,
    ) -> TypeRef<'a> {
        Type::from_cc(&cc_domain(id, vocab)[index], vocab)
    }

    pub(crate) fn get_rc(id: Option<DomainIndex>, vocab: &RcA<Vocabulary>, index: usize) -> TypeRc {
        Type::from_cc(&cc_domain(id, &vocab)[index], vocab.clone().into())
    }

    pub(crate) fn iter<'a>(
        id: Option<DomainIndex>,
        vocab: &'a Vocabulary,
    ) -> impl SIterator<Item = TypeRef<'a>> {
        cc_domain(id, vocab)
            .iter()
            .map(move |type_e| Type::from_cc(type_e, vocab))
    }

    pub fn iter_rc(
        id: Option<DomainIndex>,
        vocab: &RcA<Vocabulary>,
    ) -> impl SIterator<Item = TypeRc> + '_ {
        let vocab_ref = vocab.clone();
        cc_domain(id, vocab.as_ref())
            .iter()
            .map(move |type_e| Type::from_cc(type_e, RcA::clone(&vocab_ref).into()))
    }

    pub fn arity(id: Option<DomainIndex>, vocab: &Vocabulary) -> usize {
        cc_domain(id, vocab).len()
    }
}

/// An FO(·) Domain.
///
/// The most useful versions of this struct are [DomainRef] and [DomainRc].
#[derive(Clone)]
pub struct Domain<T: PtrRepr<Vocabulary>>(pub(crate) Option<DomainIndex>, pub(crate) T);

impl<T: PtrRepr<Vocabulary>> FodotOptions for Domain<T> {
    type Options<'a> = FormatOptions;
}

impl<T: PtrRepr<Vocabulary>, D: PtrRepr<Vocabulary>> PartialEq<Domain<D>> for Domain<T> {
    fn eq(&self, other: &Domain<D>) -> bool {
        self.0 == other.0 && vocabs_ptr_eq(Some(self.vocab()), Some(other.vocab()))
    }
}

impl<T: PtrRepr<Vocabulary>> Eq for Domain<T> {}

impl<T: PtrRepr<Vocabulary>> FodotDisplay for Domain<T> {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        if fmt.value.arity() == 0 {
            write!(f, "()")
        } else {
            write!(
                f,
                "{}",
                fmt.value.iter().format(match fmt.options.char_set {
                    CharSet::Ascii => formatcp!(" {} ", PRODUCT_ASCII),
                    CharSet::Unicode => formatcp!(" {} ", PRODUCT_UNI),
                })
            )
        }
    }
}

impl<T: PtrRepr<Vocabulary>> Display for Domain<T> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

impl<T: PtrRepr<Vocabulary>> From<Domain<T>> for StrDomain {
    fn from(value: Domain<T>) -> Self {
        value.str_domain()
    }
}

impl<'a, T: PtrRepr<Vocabulary>> From<&'a Domain<T>> for StrDomain {
    fn from(value: &'a Domain<T>) -> Self {
        value.str_domain()
    }
}

display_as_debug!(Domain<T>, gen: (T), where: (T: PtrRepr<Vocabulary>));

impl<T: PtrRepr<Vocabulary>> Domain<T> {
    /// Get the [Domain] of the [Pfunc].
    pub fn from_pfunc_decl(pfunc_decl: Pfunc<T>) -> Self {
        let vocab = pfunc_decl.1.borrow();
        Domain(
            vocab
                .comp_core_symbs
                .get_pfunc_decl(vocab.pfunc_index_to_cc(pfunc_decl.0))
                .domain
                .into(),
            pfunc_decl.1,
        )
    }

    pub fn with_interps<I: IntoPtr<PartialTypeInterps> + Deref<Target = TypeInterps>>(
        self,
        type_interps: I,
    ) -> Result<DomainFull<<I as IntoPtr<PartialTypeInterps>>::Target>, VocabMismatchError> {
        if !vocabs_ptr_eq(Some(self.1.borrow()), Some(type_interps.deref().vocab())) {
            return Err(VocabMismatchError);
        }
        Ok(DomainFull(self.0, type_interps.into_ptr()))
    }

    pub fn with_partial_interps<I: PtrRepr<PartialTypeInterps>>(
        self,
        type_interps: I::Ctx,
    ) -> Result<DomainFull<I>, VocabMismatchError> {
        if !vocabs_ptr_eq(Some(self.1.borrow()), Some(type_interps.deref().vocab())) {
            return Err(VocabMismatchError);
        }
        Ok(DomainFull(self.0, type_interps.into()))
    }

    pub(crate) fn _cc_domain(&self) -> &CCDomainSlice {
        domain_funcs::cc_domain(self.0, self.1.borrow())
    }

    pub fn vocab(&self) -> &Vocabulary {
        self.1.deref()
    }

    pub fn get(&self, index: usize) -> TypeRef {
        domain_funcs::get(self.0, self.1.borrow(), index)
    }

    pub fn iter(&self) -> impl SIterator<Item = TypeRef> {
        domain_funcs::iter(self.0, self.1.deref())
    }

    /// Returns the arity of the domain.
    pub fn arity(&self) -> usize {
        domain_funcs::arity(self.0, self.1.deref())
    }

    pub fn is_infinite(&self) -> bool {
        self.iter().any(|f| match f {
            Type::Int | Type::Real => true,
            Type::Bool | Type::IntType(_) | Type::RealType(_) | Type::StrType(_) => false,
        })
    }

    pub fn str_domain(&self) -> StrDomain {
        StrDomain {
            values: self.iter().map(|f| f.into()).collect(),
        }
    }
}

/// A referencing type alias for [Domain].
pub type DomainRef<'a> = Domain<&'a Vocabulary>;

impl<'a> DomainRef<'a> {
    pub(crate) fn cc_domain(&self) -> &'a CCDomainSlice {
        domain_funcs::cc_domain(self.0, self.1)
    }

    /// Reference version of [Self::from_pfunc_decl].
    pub fn from_pfunc_ref_decl(pfunc_decl: &PfuncRef<'a>) -> Self {
        let vocab = pfunc_decl.1;
        Domain(
            vocab
                .comp_core_symbs
                .get_pfunc_decl(vocab.pfunc_index_to_cc(pfunc_decl.0))
                .domain
                .into(),
            pfunc_decl.1,
        )
    }

    /// Get the type at given index as a [TypeRef].
    ///
    /// # Panics
    ///
    /// If the index is larger or equal than the [arity](Self::arity).
    pub fn get_ref(&self, index: usize) -> TypeRef<'a> {
        domain_funcs::get(self.0, self.1, index)
    }

    /// Returns an [Iterator] over all types in the domain as a [TypeRef].
    pub fn iter_ref(&self) -> impl SIterator<Item = TypeRef<'a>> {
        domain_funcs::iter(self.0, self.1)
    }

    /// Returns the corresponding [Vocabulary].
    pub fn vocab_ref(&self) -> &'a Vocabulary {
        self.1
    }
}

/// An owning (via [Rc]) type alias for [Domain].
pub type DomainRc = Domain<RcA<Vocabulary>>;

impl DomainRc {
    pub fn new<T>(
        types: &[T],
        vocab: Rc<Vocabulary>,
    ) -> Result<Self, <&T as TryIntoCtx<TypeRc>>::Error>
    where
        for<'a> &'a T: TryIntoCtx<TypeRc, Ctx = Rc<Vocabulary>>,
    {
        let types: Box<[TypeRc]> = types
            .iter()
            .map(|f| f.try_into_ctx(vocab.clone()))
            .collect::<Result<Box<[TypeRc]>, _>>()?;
        Ok(Self::_new(types, vocab))
    }

    /// All [TypeRc] values must already be consistent with the given vocabulary.
    pub(crate) fn _new(types: Box<[TypeRc]>, vocab: Rc<Vocabulary>) -> Self {
        let vocab = vocab;
        let symb_domain: Box<[_]> = types.iter().map(|f| _Type::from(f)).collect();

        Self(Some(vocab.add_domain(&symb_domain)), vocab.into())
    }

    /// Get the type at given index as a [TypeRc].
    ///
    /// # Panics
    ///
    /// If the index is larger or equal than the [arity](Self::arity).
    pub fn get_rc(&self, index: usize) -> TypeRc {
        domain_funcs::get_rc(self.0, &self.1, index)
    }

    /// Return an [Iterator] over all the types in the domain as a [TypeRc].
    pub fn iter_rc(&self) -> impl SIterator<Item = TypeRc> + '_ {
        domain_funcs::iter_rc(self.0, &self.1)
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct StrDomain {
    values: Vec<TypeStr>,
}

impl FodotOptions for StrDomain {
    type Options<'a> = FormatOptions;
}

impl FodotDisplay for StrDomain {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        if fmt.value.values.len() == 0 {
            write!(f, "()")?;
            return Ok(());
        }
        let mut values = fmt.value.values.iter().peekable();
        while let Some(value) = values.next() {
            write!(f, "{}", fmt.with_opts(value))?;
            if values.peek().is_some() {
                write!(f, " ")?;
                fmt.write_product(f)?;
                write!(f, " ")?;
            }
        }
        Ok(())
    }
}

impl Display for StrDomain {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub(crate) enum _SymbolStr {
    Bool,
    Int,
    Real,
    Custom(String),
}

impl From<&str> for _SymbolStr {
    fn from(value: &str) -> Self {
        let Ok(value) = parse_primitive_type(value) else {
            return _SymbolStr::Custom(value.into());
        };
        value.into()
    }
}

impl From<PrimitiveType> for _SymbolStr {
    fn from(value: PrimitiveType) -> Self {
        match value {
            PrimitiveType::Bool => _SymbolStr::Bool,
            PrimitiveType::Int => _SymbolStr::Int,
            PrimitiveType::Real => _SymbolStr::Real,
        }
    }
}

impl FodotOptions for _SymbolStr {
    type Options<'a> = FormatOptions;
}

impl FodotDisplay for _SymbolStr {
    fn fmt(
        fmt: fmt::Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        match fmt.value {
            Self::Bool => fmt.options.write_bool_type(f),
            Self::Int => fmt.options.write_int_type(f),
            Self::Real => fmt.options.write_real_type(f),
            Self::Custom(value) => f.write_str(&value),
        }
    }
}

impl core::ops::Deref for _SymbolStr {
    type Target = str;

    fn deref(&self) -> &Self::Target {
        match self {
            Self::Bool => &fmt::BOOL_ASCII,
            Self::Int => &fmt::INT_ASCII,
            Self::Real => &fmt::REAL_ASCII,
            Self::Custom(value) => &value,
        }
    }
}

impl _SymbolStr {
    #[allow(unused)]
    pub(crate) fn to_owned(&self) -> String {
        match self {
            Self::Bool => fmt::BOOL_ASCII.to_owned(),
            Self::Int => fmt::INT_ASCII.to_owned(),
            Self::Real => fmt::REAL_ASCII.to_owned(),
            Self::Custom(cust) => cust.clone(),
        }
    }
}

/// contains all methods and functions needed for boomerang interface with comp_core
pub(in crate::fodot) mod translation_layer {
    use super::{CCPfuncIndex, CCType, PfuncIndex, TypeRef, TypeSymbolIndex, Vocabulary};
    use comp_core::{IndexRepr, vocabulary::TypeIndex};

    impl Vocabulary {
        #[allow(unused)]
        pub(in crate::fodot) fn type_to_cc(&self, type_: TypeRef) -> CCType {
            match type_ {
                TypeRef::Bool => CCType::Bool,
                TypeRef::Int => CCType::Int,
                TypeRef::Real => CCType::Real,
                TypeRef::IntType(id) => CCType::IntType(self.type_decl_to_cc(id.0)),
                TypeRef::RealType(id) => CCType::RealType(self.type_decl_to_cc(id.0)),
                TypeRef::StrType(id) => CCType::Str(self.type_decl_to_cc(id.0)),
            }
        }

        pub(in crate::fodot) fn type_decl_to_cc(&self, type_id: TypeSymbolIndex) -> TypeIndex {
            TypeIndex::from(IndexRepr::from(type_id))
        }

        pub(in crate::fodot) fn pfunc_index_to_cc(&self, pfunc_id: PfuncIndex) -> CCPfuncIndex {
            CCPfuncIndex::from(IndexRepr::from(pfunc_id))
        }
    }
}

#[cfg(test)]
mod tests {
    use super::{BaseType, Vocabulary};

    #[test]
    fn parse_vocab() {
        let mut vocab = Vocabulary::new("T");
        vocab.add_type_decl("D", BaseType::Int).unwrap();
        vocab.parse("type T p: T -> Bool r: T -> D").unwrap();
    }

    #[test]
    fn failed_parse_vocabulary() {
        let mut vocab = Vocabulary::new("T");
        vocab.add_type_decl("D", BaseType::Int).unwrap();
        let diag = vocab.parse("type T p: T -> Bool r: T -> D.").unwrap_err();
        assert!(diag.errors().len() == 1);
        assert!(vocab.voc_symbols.len() == 1);
    }

    #[test]
    fn escaped_vocab() {
        let mut vocab = Vocabulary::new("T");
        vocab.add_type_decl("D", BaseType::Int).unwrap();
        let decls = "type T p: T -> Bool r: T -> D } theory T:V {";
        let diag = vocab.parse(decls).unwrap_err();
        assert!(diag.errors().len() == 1);
        let a = diag.errors().first().unwrap();
        assert_eq!(a.span().end, decls.len());
    }
}
