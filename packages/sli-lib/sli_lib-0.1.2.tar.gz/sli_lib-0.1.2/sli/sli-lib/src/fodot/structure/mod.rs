//! Structure datastructures and methods.
//!
//! A Structure ([PartialStructure], [CompleteStructure]) contains the
//! interpretation of both types and predicates and functions (pfuncs).

use super::error::parse::{Diagnostics, IDPError};
use super::error::{
    ArgAddErrorKind, ArgMismatchError, DomainMismatch, MissingTypeInterps, MissingTypeInterpsError,
    SetTypeInterpIncompleteError, TypeInterpDependence, TypeInterpDependenceError,
};
use super::fmt::{Fmt, FodotDisplay, FodotOptions, FormatOptions, StructFmt, StructureOptions};
use super::vocabulary::{
    Domain, DomainRc, DomainRef, PfuncRef, SymbolError, Type, TypeRc, Vocabulary, domain_funcs,
};
use super::{TryFromCtx, TryIntoCtx, display_as_debug};
use crate::ast::tree_sitter::TsParser;
use crate::ast::{Parser, StructureAst};
use crate::fodot::error::{
    ArgAddError, ArgCreationErrorExtension, MismatchedArity, MismatchedArityError,
    TypeInterpsMismatchError, TypeMismatch,
};
use crate::fodot::vocabulary::CustomTypeRef;
use crate::sli_entrance::parse_struct_decls;
use crate::solver::Constraints;
use comp_core::IndexRange;
use comp_core::structure::{DomainEnumBuilder, DomainEnumErrors};
use comp_core::vocabulary::{DomainEnum, DomainIndex, DomainSlice as CCDomainSlice};
use itertools::{EitherOrBoth, Itertools};
use sli_collections::{
    iterator::Iterator as SIterator,
    rc::{PtrRepr, Rc, RcA},
};
use std::borrow::Borrow;
use std::fmt::Display;
use std::fmt::Write;
use std::ops::Deref;

mod pfunc;
pub use pfunc::*;
mod type_interps;
pub use type_interps::*;

macro_rules! extract_pfunc_interp {
    (
        $type_interps:expr, $pfunc_decl:expr, $cc_interp:expr,
        $cc_pfunc_type:path, $fodot_pfunc_type:path $(,)?
    ) => {{
        use $cc_pfunc_type as cc;
        use $fodot_pfunc_type as fo;
        let type_interps = $type_interps;
        let cc_interp = $cc_interp;
        let pfunc_decl = $pfunc_decl;
        let decl_interp = get_pfunc_interp(type_interps, pfunc_decl);
        match (decl_interp, cc_interp) {
            (pfunc::PfuncDeclInterps::Primitive(decl), cc::SymbolInterp::Prop(interp)) => {
                fo::PropInterp { interp, decl }.into()
            }
            (
                pfunc::PfuncDeclInterps::Primitive(decl),
                cc::SymbolInterp::IntConst(cc::IntCoConstInterp::Int(interp)),
            ) => fo::IntConstInterp { interp, decl }.into(),
            (
                pfunc::PfuncDeclInterps::IntType(decl),
                cc::SymbolInterp::IntConst(cc::IntCoConstInterp::IntType(interp)),
            ) => fo::IntTypeConstInterp { interp, decl }.into(),
            (
                pfunc::PfuncDeclInterps::Primitive(decl),
                cc::SymbolInterp::RealConst(cc::RealCoConstInterp::Real(interp)),
            ) => fo::RealConstInterp { interp, decl }.into(),
            (
                pfunc::PfuncDeclInterps::RealType(decl),
                cc::SymbolInterp::RealConst(cc::RealCoConstInterp::RealType(interp)),
            ) => fo::RealTypeConstInterp { interp, decl }.into(),
            (pfunc::PfuncDeclInterps::Str(decl), cc::SymbolInterp::StrConst(interp)) => {
                fo::StrConstInterp { interp, decl }.into()
            }
            (pfunc::PfuncDeclInterps::Primitive(decl), cc::SymbolInterp::Pred(interp)) => {
                fo::PredInterp { interp, decl }.into()
            }
            (
                pfunc::PfuncDeclInterps::Primitive(decl),
                cc::SymbolInterp::IntFunc(cc::IntCoFuncInterp::Int(interp)),
            ) => fo::IntFuncInterp { interp, decl }.into(),
            (
                pfunc::PfuncDeclInterps::IntType(decl),
                cc::SymbolInterp::IntFunc(cc::IntCoFuncInterp::IntType(interp)),
            ) => fo::IntTypeFuncInterp { interp, decl }.into(),
            (
                pfunc::PfuncDeclInterps::Primitive(decl),
                cc::SymbolInterp::RealFunc(cc::RealCoFuncInterp::Real(interp)),
            ) => fo::RealFuncInterp { interp, decl }.into(),
            (
                pfunc::PfuncDeclInterps::RealType(decl),
                cc::SymbolInterp::RealFunc(cc::RealCoFuncInterp::RealType(interp)),
            ) => fo::RealTypeFuncInterp { interp, decl }.into(),
            (pfunc::PfuncDeclInterps::Str(decl), cc::SymbolInterp::StrFunc(interp)) => {
                fo::StrFuncInterp { interp, decl }.into()
            }
            _ => unreachable!(),
        }
    }};
}

#[derive(Clone)]
pub struct IncompleteStructure {
    pub(crate) partial_type_interps: Rc<PartialTypeInterps>,
    pub(crate) cc_struct: CCMoveablePartialStructure,
}

#[derive(Clone)]
pub(crate) struct CCMoveablePartialStructure(Option<comp_core::structure::PartialStructure>);

impl From<comp_core::structure::PartialStructure> for CCMoveablePartialStructure {
    fn from(value: comp_core::structure::PartialStructure) -> Self {
        Self(Some(value))
    }
}

impl CCMoveablePartialStructure {
    fn get(&self) -> &comp_core::structure::PartialStructure {
        self.0
            .as_ref()
            .expect("IncompleteStructure in invalid state")
    }

    fn get_mut(&mut self) -> &mut comp_core::structure::PartialStructure {
        self.0
            .as_mut()
            .expect("IncompleteStructure in invalid state")
    }

    /// Takes struct leaves self in an transitional incorrect state.
    ///
    /// Use [Self::set] to put `self` back in a correct state.
    fn take(&mut self) -> comp_core::structure::PartialStructure {
        self.0.take().expect("IncompleteStructure in invalid state")
    }

    fn set(&mut self, cc_struct: comp_core::structure::PartialStructure) {
        self.0 = Some(cc_struct);
    }
}

impl Display for IncompleteStructure {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "{}",
            self.display().map_options(|mut f| {
                f.struct_opts = StructFmt::Full;
                f
            })
        )
    }
}

impl FodotOptions for IncompleteStructure {
    type Options<'a> = StructureOptions<'a>;
}

display_as_debug!(IncompleteStructure);

impl FodotDisplay for IncompleteStructure {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        match fmt.options.struct_opts {
            StructFmt::PFuncOnly => Self::write_pfuncs(fmt, f),
            StructFmt::Full => Self::write_all(fmt, f),
            StructFmt::Diff(_) => todo!(),
        }
    }
}

impl IncompleteStructure {
    fn write_all<'a, W: Write>(
        fmt: Fmt<&'a Self, <Self as FodotOptions>::Options<'a>>,
        f: &mut W,
    ) -> std::fmt::Result {
        write!(f, "{}", fmt.with_format_opts(fmt.value.type_interps()))?;
        Self::write_pfuncs(fmt, f)
    }

    fn write_pfuncs<'a, W: Write>(
        fmt: Fmt<&'a Self, <Self as FodotOptions>::Options<'a>>,
        f: &mut W,
    ) -> std::fmt::Result {
        for pfunc_interp in fmt.value.iter_known() {
            fmt.options.opts.write_indent(f)?;
            writeln!(f, "{}.", fmt.with_format_opts(&pfunc_interp))?;
        }
        Ok(())
    }
}

impl PartialEq for IncompleteStructure {
    fn eq(&self, other: &Self) -> bool {
        self.type_interps() == other.type_interps() && self.cc_struct.get() == other.cc_struct.get()
    }
}

impl PartialEq<PartialStructure> for IncompleteStructure {
    fn eq(&self, other: &PartialStructure) -> bool {
        self.type_interps() == other.type_interps() && self.cc_struct.get() == &other.cc_struct
    }
}

impl PartialEq<IncompleteStructure> for PartialStructure {
    fn eq(&self, other: &IncompleteStructure) -> bool {
        PartialEq::<PartialStructure>::eq(other, self)
    }
}

impl PartialEq<CompleteStructure> for IncompleteStructure {
    fn eq(&self, other: &CompleteStructure) -> bool {
        self.type_interps() == other.type_interps() && self.cc_struct.get() == &other.cc_struct
    }
}

impl PartialEq<IncompleteStructure> for CompleteStructure {
    fn eq(&self, other: &IncompleteStructure) -> bool {
        PartialEq::<CompleteStructure>::eq(other, self)
    }
}

impl Eq for IncompleteStructure {}

impl IncompleteStructure {
    /// Create an empty [IncompleteStructure].
    pub fn new(type_interps: PartialTypeInterps) -> Self {
        Self {
            cc_struct: comp_core::structure::PartialStructure::new(Rc::clone(&type_interps.cc))
                .into(),
            partial_type_interps: type_interps.into(),
        }
    }

    pub fn parse(&mut self, source: &str) -> Result<&mut Self, Diagnostics> {
        let structure_ast = TsParser::new().parse_structure(source);
        let mut diagnostics = Diagnostics::new();
        for (err, span) in structure_ast.parse_errors() {
            diagnostics.add_error(IDPError::new(err.into(), span));
        }
        let old = self.clone();
        parse_struct_decls(self, structure_ast.decls(), &source, &mut diagnostics);
        if diagnostics.errors().len() == 0 {
            Ok(self)
        } else {
            *self = old;
            Err(diagnostics)
        }
    }

    pub fn set_interp(
        &mut self,
        custom_type: CustomTypeRef,
        interp: TypeInterp,
    ) -> Result<&mut Self, SetTypeInterpIncompleteError> {
        if let Some(value) = self.type_interps().get_interp(custom_type)? {
            if value == interp {
                return Ok(self);
            }
        }
        self.init_pfunc_interps(custom_type)?;
        // avoid cloning the predicate and function interpretations, we do clone the original
        // `TypeInterps` (this is a vector of Rc<..>) and the inner type interps (if this is the
        // only instance that references these type interps.
        let (type_interps, backend) = self.cc_struct.take().into_raw();
        drop(type_interps);
        Rc::make_mut(&mut self.partial_type_interps).set_interp(custom_type, interp)?;
        self.cc_struct
            .set(comp_core::structure::partial::PartialStructure::from_raw(
                self.partial_type_interps.cc.clone(),
                backend,
            ));
        Ok(self)
    }

    fn init_pfunc_interps(
        &mut self,
        custom_type: CustomTypeRef,
    ) -> Result<(), TypeInterpDependenceError> {
        let vocab_rc = self.vocab_rc().clone();
        let pfuncs_with_type = vocab_rc.iter_pfuncs().filter(|pfunc| {
            pfunc.domain().iter().any(|f| f == custom_type) || pfunc.codomain() == custom_type
        });
        let check_if_interp_ok = |pfunc: PfuncRef, structure: &Self| {
            let Ok(value) = structure.get(pfunc.clone()) else {
                return true;
            };
            !value.any_known()
        };
        let pfuncs: Vec<_> = pfuncs_with_type
            .clone()
            .filter(|f| !check_if_interp_ok(f.clone(), &*self))
            .map(|f| f.name().to_string())
            .collect();
        if pfuncs.len() != 0 {
            return Err(TypeInterpDependence {
                custom_type_name: custom_type.name().to_string(),
                pfuncs,
            }
            .into());
        }
        for pfunc in pfuncs_with_type {
            let cc_id = self.vocab().pfunc_index_to_cc(pfunc.0);
            self.cc_struct.get_mut().reinit_pfunc(cc_id);
        }
        Ok(())
    }

    /// Returns the corresponding [PartialTypeInterps].
    pub fn type_interps(&self) -> &PartialTypeInterps {
        &self.partial_type_interps
    }

    /// Returns the corresponding [Vocabulary].
    pub fn vocab(&self) -> &Vocabulary {
        self.type_interps().vocab()
    }

    /// Returns the corresponding [Vocabulary] as a reference to an [Rc].
    pub fn vocab_rc(&self) -> &Rc<Vocabulary> {
        self.type_interps().vocab_rc()
    }

    /// Returns an immutable view into an interpretation of a pfunc.
    ///
    /// See [pfunc::partial::immutable::SymbolInterp] for more info.
    pub fn get(
        &self,
        pfunc_decl: PfuncRef,
    ) -> Result<pfunc::partial::immutable::SymbolInterp, MissingTypeInterpsError> {
        if let Some(value) = self.check_all_interps(&pfunc_decl) {
            return Err(value.into());
        }
        Ok(extract_pfunc_interp! {
            self.type_interps(), pfunc_decl, self.cc_struct.get().get(self.vocab().pfunc_index_to_cc(pfunc_decl.0)),
            comp_core::structure::partial::immutable, pfunc::partial::immutable
        })
    }

    fn check_all_interps(&self, pfunc_decl: &PfuncRef) -> Option<MissingTypeInterps> {
        let missing: Vec<_> = pfunc_decl
            .domain()
            .iter()
            .filter_map(|f| CustomTypeRef::try_from(f).ok())
            .filter(|f| !self.partial_type_interps.has_interp(*f).unwrap())
            .map(|f| f.name().to_string())
            .chain(
                CustomTypeRef::try_from(pfunc_decl.codomain())
                    .ok()
                    .map(|f| (f, self.partial_type_interps.has_interp(f).unwrap()))
                    .map(|f| {
                        if !f.1 {
                            Some(f.0.name().to_string())
                        } else {
                            None
                        }
                    })
                    .flatten()
                    .into_iter(),
            )
            .collect();
        if missing.len() == 0 {
            None
        } else {
            Some(MissingTypeInterps { missing })
        }
    }

    /// Returns an mutable view into an interpretation of a pfunc.
    ///
    /// See [pfunc::partial::mutable::SymbolInterp] for more info.
    pub fn get_mut(
        &mut self,
        pfunc_decl: PfuncRef,
    ) -> Result<pfunc::partial::mutable::SymbolInterp, MissingTypeInterpsError> {
        if let Some(value) = self.check_all_interps(&pfunc_decl) {
            return Err(value.into());
        }
        let id = self.vocab().pfunc_index_to_cc(pfunc_decl.0);
        Ok(extract_pfunc_interp! {
            &self.partial_type_interps, pfunc_decl,
            self.cc_struct.get_mut().get_mut(id),
            comp_core::structure::partial::mutable, pfunc::partial::mutable
        })
    }

    /// Returns an [Iterator] over all pfunc interpretations in this structure.
    ///
    /// This includes empty interpretations, see [Self::iter_known] if you want only
    /// interpretations that are not empty.
    pub fn iter(&self) -> impl SIterator<Item = pfunc::partial::immutable::SymbolInterp> {
        self.vocab().iter_pfuncs().filter_map(|f| self.get(f).ok())
    }

    /// Returns an [Iterator] over all pfunc interpretations in this structure that are not
    /// completely unknown.
    pub fn iter_known(&self) -> impl SIterator<Item = pfunc::partial::immutable::SymbolInterp> {
        self.vocab()
            .iter_pfuncs()
            .filter_map(|f| self.get(f).ok())
            .filter_map(|f| if f.any_known() { Some(f) } else { None })
    }

    pub fn try_into_partial(mut self) -> Result<PartialStructure, Self> {
        match PartialTypeInterps::try_rc_into_complete(self.partial_type_interps) {
            Ok(value) => Ok(PartialStructure {
                type_interps: value.into(),
                cc_struct: self.cc_struct.take(),
            }),
            Err(partial_type) => {
                self.partial_type_interps = partial_type;
                Err(self)
            }
        }
    }

    pub fn is_complete(&self) -> bool {
        self.type_interps().is_complete() && self.cc_struct.get().is_complete()
    }

    pub fn try_into_complete(self) -> Result<CompleteStructure, Self> {
        self.try_into_partial()
            .and_then(|f| f.try_into_complete().map_err(|f| f.into_incomplete()))
    }
}

/// A structure with partial interpretations.
///
/// More precisely all pfuncs of the corresponding vocabulary need to have an
/// interpretation and the interpretations of the pfuncs are allowed to be partial.
#[derive(Clone)]
pub struct PartialStructure {
    pub(crate) type_interps: Rc<TypeInterps>,
    pub(crate) cc_struct: comp_core::structure::PartialStructure,
}

impl Display for PartialStructure {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

impl FodotOptions for PartialStructure {
    type Options<'a> = StructureOptions<'a>;
}

display_as_debug!(PartialStructure);

impl FodotDisplay for PartialStructure {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        match fmt.options.struct_opts {
            StructFmt::PFuncOnly => Self::write_pfuncs(fmt, f),
            StructFmt::Full => Self::write_all(fmt, f),
            StructFmt::Diff(_) => todo!(),
        }
    }
}

impl PartialStructure {
    fn write_all<'a, W: Write>(
        fmt: Fmt<&'a Self, <Self as FodotOptions>::Options<'a>>,
        f: &mut W,
    ) -> std::fmt::Result {
        write!(f, "{}", fmt.with_format_opts(fmt.value.type_interps()))?;
        Self::write_pfuncs(fmt, f)
    }

    fn write_pfuncs<'a, W: Write>(
        fmt: Fmt<&'a Self, <Self as FodotOptions>::Options<'a>>,
        f: &mut W,
    ) -> std::fmt::Result {
        for pfunc_interp in fmt.value.iter_known() {
            fmt.options.opts.write_indent(f)?;
            writeln!(f, "{}.", fmt.with_format_opts(&pfunc_interp))?;
        }
        Ok(())
    }
}

impl PartialEq for PartialStructure {
    fn eq(&self, other: &Self) -> bool {
        self.cc_struct == other.cc_struct
    }
}

impl PartialEq<CompleteStructure> for PartialStructure {
    fn eq(&self, other: &CompleteStructure) -> bool {
        self.cc_struct == other.cc_struct
    }
}

impl Eq for PartialStructure {}

impl Precision for PartialStructure {
    fn is_more_precise(&self, rhs: &Self) -> bool {
        self.vocab().exact_eq(rhs.vocab()) && self.cc_struct.is_more_precise(&rhs.cc_struct)
    }
}

impl Precision<CompleteStructure> for PartialStructure {
    fn is_more_precise(&self, rhs: &CompleteStructure) -> bool {
        self.vocab().exact_eq(rhs.vocab()) && self.cc_struct.is_more_precise(&rhs.cc_struct)
    }
}

fn get_pfunc_interp<'a>(
    type_interps: &'a PartialTypeInterps,
    decl: PfuncRef,
) -> pfunc::PfuncDeclInterps<'a> {
    let decl_interp = PfuncDeclInterp {
        pfunc_decl_index: decl.0,
        type_interps,
    };
    match decl.codomain() {
        Type::Bool | Type::Int | Type::Real => pfunc::PfuncDeclInterps::Primitive(decl_interp),
        Type::IntType(_) => pfunc::PfuncDeclInterps::IntType(IntTypeDeclInterp(decl_interp)),
        Type::RealType(_) => pfunc::PfuncDeclInterps::RealType(RealTypeDeclInterp(decl_interp)),
        Type::StrType(_) => pfunc::PfuncDeclInterps::Str(StrDeclInterp(decl_interp)),
    }
}

impl PartialStructure {
    /// Create an empty [PartialStructure].
    pub fn new(type_interps: Rc<TypeInterps>) -> Self {
        Self {
            cc_struct: comp_core::structure::PartialStructure::new(Rc::clone(
                &type_interps.deref().0.cc,
            )),
            type_interps,
        }
    }

    pub fn parse(&mut self, source: &str) -> Result<&mut Self, Diagnostics> {
        let replacement_incomplete =
            comp_core::structure::PartialStructure::new(self.cc_struct.rc_type_interps().clone());
        let cur_cc_struct = core::mem::replace(&mut self.cc_struct, replacement_incomplete);
        let mut incomplete_structure = IncompleteStructure {
            partial_type_interps: PartialTypeInterps::from_rc_complete(self.type_interps.clone()),
            cc_struct: cur_cc_struct.into(),
        };
        let res = incomplete_structure.parse(source).map(|_| ());
        self.cc_struct = incomplete_structure.cc_struct.take();
        res.map(|_| self)
    }

    /// Returns the corresponding [TypeInterps].
    pub fn type_interps(&self) -> &TypeInterps {
        &self.type_interps
    }

    /// Returns the corresponding [TypeInterps] as a reference to an [Rc].
    pub fn type_interps_rc(&self) -> &Rc<TypeInterps> {
        &self.type_interps
    }

    /// Returns the corresponding [Vocabulary].
    pub fn vocab(&self) -> &Vocabulary {
        self.type_interps.vocab()
    }

    /// Returns the corresponding [Vocabulary] as a reference to an [Rc].
    pub fn vocab_rc(&self) -> &Rc<Vocabulary> {
        &self.type_interps.vocab_rc()
    }

    /// Tries to convert the [PartialStructure] to a [CompleteStructure].
    ///
    /// If this conversion fails because the [PartialStructure] is not complete the original
    /// structure is returned in the [Err] value.
    pub fn try_into_complete(self) -> Result<CompleteStructure, Self> {
        match self.cc_struct.try_into_complete() {
            Ok(cc_struct) => Ok(CompleteStructure {
                type_interps: self.type_interps,
                cc_struct,
            }),
            Err(cc_struct) => Err(PartialStructure {
                type_interps: self.type_interps,
                cc_struct,
            }),
        }
    }

    /// Tries to create an empty [PartialStructure] from a [PartialTypeInterps].
    ///
    /// All types in the corresponding vocabulary of the [PartialTypeInterps] need to be given a
    /// interpretation for this function to succeed.
    pub fn from_partial_interps(
        partial_interps: PartialTypeInterps,
    ) -> Result<Self, MissingTypeInterpsError> {
        let type_interps: Rc<TypeInterps> = Rc::new(TypeInterps::try_from(partial_interps)?);
        Ok(Self {
            cc_struct: comp_core::structure::PartialStructure::new(Rc::clone(&type_interps.0.cc)),
            type_interps,
        })
    }

    /// Returns an immutable view into an interpretation of a pfunc.
    ///
    /// See [pfunc::partial::immutable::SymbolInterp] for more info.
    pub fn get(&self, pfunc_decl: PfuncRef) -> pfunc::partial::immutable::SymbolInterp {
        extract_pfunc_interp! {
            &self.type_interps.0, pfunc_decl, self.cc_struct.get(self.vocab().pfunc_index_to_cc(pfunc_decl.0)),
            comp_core::structure::partial::immutable, pfunc::partial::immutable
        }
    }

    /// Returns an mutable view into an interpretation of a pfunc.
    ///
    /// See [pfunc::partial::mutable::SymbolInterp] for more info.
    pub fn get_mut(&mut self, pfunc_decl: PfuncRef) -> pfunc::partial::mutable::SymbolInterp {
        extract_pfunc_interp! {
            &self.type_interps.0, pfunc_decl, self.cc_struct.get_mut(self.vocab().pfunc_index_to_cc(pfunc_decl.0)),
            comp_core::structure::partial::mutable, pfunc::partial::mutable
        }
    }

    /// Returns an [Iterator] over all pfunc interpretations in this structure.
    ///
    /// This includes empty interpretations, see [Self::iter_known] if you want only
    /// interpretations that are not empty.
    pub fn iter(&self) -> impl SIterator<Item = pfunc::partial::immutable::SymbolInterp> {
        self.vocab().iter_pfuncs().map(|f| self.get(f))
    }

    /// Returns an [Iterator] over all pfunc interpretations in this structure that are not
    /// completely unknown.
    pub fn iter_known(&self) -> impl SIterator<Item = pfunc::partial::immutable::SymbolInterp> {
        self.vocab().iter_pfuncs().filter_map(|f| {
            let interp = self.get(f);
            if interp.any_known() {
                Some(interp)
            } else {
                None
            }
        })
    }

    pub fn into_incomplete(self) -> IncompleteStructure {
        IncompleteStructure {
            partial_type_interps: PartialTypeInterps::from_rc_complete(self.type_interps),
            cc_struct: self.cc_struct.into(),
        }
    }

    /// Skips infinite values by default.
    pub fn iter_complete(&self) -> IterCompleteStructure {
        IterCompleteStructure::new(self)
    }

    /// Skips infinite values by default.
    pub fn into_iter_complete(self) -> IntoIterCompleteStructure {
        IntoIterCompleteStructure::new(self)
    }
}

impl From<PartialStructure> for IncompleteStructure {
    fn from(value: PartialStructure) -> Self {
        value.into_incomplete()
    }
}

/// A structure where all pfuncs of the corresponding vocabulary have a complete
/// interpretation.
///
/// For creating this structure see [PartialStructure::try_into_complete].
#[derive(Clone)]
pub struct CompleteStructure {
    type_interps: Rc<TypeInterps>,
    cc_struct: comp_core::structure::CompleteStructure,
}

impl Display for CompleteStructure {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

display_as_debug!(CompleteStructure);

impl FodotOptions for CompleteStructure {
    type Options<'a> = StructureOptions<'a>;
}

impl FodotDisplay for CompleteStructure {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        match fmt.options.struct_opts {
            StructFmt::PFuncOnly => Self::write_pfuncs(fmt, f),
            StructFmt::Full => Self::write_all(fmt, f),
            StructFmt::Diff(_) => todo!(),
        }
    }
}

impl CompleteStructure {
    fn write_all<'a, W: Write>(
        fmt: Fmt<&'a Self, <Self as FodotOptions>::Options<'a>>,
        f: &mut W,
    ) -> std::fmt::Result {
        write!(f, "{}", fmt.with_format_opts(fmt.value.type_interps()))?;
        Self::write_pfuncs(fmt, f)
    }

    fn write_pfuncs<'a, W: Write>(
        fmt: Fmt<&'a Self, <Self as FodotOptions>::Options<'a>>,
        f: &mut W,
    ) -> std::fmt::Result {
        for pfunc_interp in fmt.value.iter() {
            fmt.options.opts.write_indent(f)?;
            writeln!(f, "{}.", fmt.with_format_opts(&pfunc_interp))?;
        }
        Ok(())
    }
}

impl PartialEq for CompleteStructure {
    fn eq(&self, other: &Self) -> bool {
        self.cc_struct == other.cc_struct
    }
}

impl PartialEq<PartialStructure> for CompleteStructure {
    fn eq(&self, other: &PartialStructure) -> bool {
        self.cc_struct == other.cc_struct
    }
}

impl Eq for CompleteStructure {}

impl Precision for CompleteStructure {
    fn is_more_precise(&self, rhs: &Self) -> bool {
        self.vocab().exact_eq(rhs.vocab()) && self.cc_struct.is_more_precise(&rhs.cc_struct)
    }
}

impl Precision<PartialStructure> for CompleteStructure {
    fn is_more_precise(&self, rhs: &PartialStructure) -> bool {
        self.vocab().exact_eq(rhs.vocab()) && self.cc_struct.is_more_precise(&rhs.cc_struct)
    }
}

impl CompleteStructure {
    /// Returns the corresponding [TypeInterps].
    pub fn type_interps(&self) -> &TypeInterps {
        &self.type_interps
    }

    /// Returns the corresponding [Vocabulary].
    pub fn vocab(&self) -> &Vocabulary {
        self.type_interps.vocab()
    }

    /// Returns the corresponding [Vocabulary] as a reference to an [Rc].
    pub fn vocab_rc(&self) -> Rc<Vocabulary> {
        Rc::clone(&self.type_interps.vocab_rc())
    }

    /// Returns an immutable view into an interpretation of a pfunc.
    ///
    /// See [pfunc::complete::immutable::SymbolInterp] for more info.
    pub fn get(&self, pfunc_decl: PfuncRef) -> pfunc::complete::immutable::SymbolInterp {
        extract_pfunc_interp! {
            &self.type_interps.0, pfunc_decl, self.cc_struct.get(self.vocab().pfunc_index_to_cc(pfunc_decl.0)),
            comp_core::structure::complete::immutable, pfunc::complete::immutable
        }
    }

    /// Returns an mutable view into an interpretation of a pfunc.
    ///
    /// See [pfunc::complete::mutable::SymbolInterp] for more info.
    pub fn get_mut(&mut self, pfunc_decl: PfuncRef) -> pfunc::complete::mutable::SymbolInterp {
        extract_pfunc_interp! {
            &self.type_interps.0, pfunc_decl, self.cc_struct.get_mut(self.vocab().pfunc_index_to_cc(pfunc_decl.0)),
            comp_core::structure::complete::mutable, pfunc::complete::mutable
        }
    }

    /// Returns an [Iterator] over all pfunc interpretations in this structure.
    pub fn iter(&self) -> impl SIterator<Item = pfunc::complete::immutable::SymbolInterp> {
        self.vocab().iter_pfuncs().map(|f| self.get(f))
    }

    /// Turn this structure into a [PartialStructure].
    pub fn into_partial(self) -> PartialStructure {
        self.into()
    }
}

impl From<CompleteStructure> for PartialStructure {
    fn from(value: CompleteStructure) -> Self {
        Self {
            type_interps: value.type_interps,
            cc_struct: value.cc_struct.into_partial(),
        }
    }
}

/// An iterator over all [CompleteStructure] that are an extension of a [PartialStructure].
///
/// See [PartialStructure::iter_complete].
pub struct IterCompleteStructure<'a> {
    type_interps: Rc<TypeInterps>,
    iter: comp_core::structure::partial::IterCompleteStructure<'a>,
}

impl<'a> IterCompleteStructure<'a> {
    fn new(partial_structure: &'a PartialStructure) -> Self {
        Self {
            type_interps: partial_structure.type_interps.clone(),
            iter: partial_structure.cc_struct.iter_complete(),
        }
    }

    /// Enable the skipping of infinite values in the iteration.
    ///
    /// e.g. a constant with codomain Int will cause this iterator to iterate 'forever'.
    /// Calling this function will skip over these values.
    pub fn enable_skip_infinite(mut self) -> Self {
        self.iter = self.iter.enable_skip_infinite();
        self
    }

    /// Disable the skipping of infinite values in the iteration.
    ///
    /// See [Self::enable_skip_infinite].
    pub fn disable_skip_infinite(mut self) -> Self {
        self.iter = self.iter.disable_skip_infinite();
        self
    }

    /// Skips infinite values if `skip` is true, otherwise iterates over infinite values.
    pub fn skip_infinite(self, skip: bool) -> Self {
        if skip {
            self.enable_skip_infinite()
        } else {
            self.disable_skip_infinite()
        }
    }
}

impl<'a> Iterator for IterCompleteStructure<'a> {
    type Item = CompleteStructure;

    fn next(&mut self) -> Option<Self::Item> {
        self.iter.next().map(|f| CompleteStructure {
            type_interps: self.type_interps.clone(),
            cc_struct: f,
        })
    }
}

/// An owned iterator over all [CompleteStructure] that are an extension of a [PartialStructure].
///
/// See [PartialStructure::into_iter_complete].
pub struct IntoIterCompleteStructure {
    type_interps: Rc<TypeInterps>,
    iter: comp_core::structure::partial::IntoIterCompleteStructure,
}

impl IntoIterCompleteStructure {
    fn new(partial_structure: PartialStructure) -> Self {
        Self {
            type_interps: partial_structure.type_interps,
            iter: partial_structure.cc_struct.into_iter_complete(),
        }
    }

    /// Enable the skipping of infinite values in the iteration.
    ///
    /// e.g. a constant with codomain Int will cause this iterator to iterate 'forever'.
    /// Calling this function will skip over these values.
    pub fn enable_skip_infinite(mut self) -> Self {
        self.iter = self.iter.enable_skip_infinite();
        self
    }

    /// Disable the skipping of infinite values in the iteration.
    ///
    /// See [Self::enable_skip_infinite].
    pub fn disable_skip_infinite(mut self) -> Self {
        self.iter = self.iter.disable_skip_infinite();
        self
    }

    /// Skips infinite values if `skip` is true, otherwise iterates over infinite values.
    pub fn skip_infinite(self, skip: bool) -> Self {
        if skip {
            self.enable_skip_infinite()
        } else {
            self.disable_skip_infinite()
        }
    }

    /// Skips infinite values if `skip` is true, otherwise iterates over infinite values.
    pub fn mut_skip_infinite(&mut self, skip: bool) {
        self.iter.skip_infinite = skip;
    }
}

impl Iterator for IntoIterCompleteStructure {
    type Item = CompleteStructure;

    fn next(&mut self) -> Option<Self::Item> {
        self.iter.next().map(|f| CompleteStructure {
            type_interps: self.type_interps.clone(),
            cc_struct: f,
        })
    }
}

/// A named [PartialStructure].
#[derive(Clone)]
pub struct StructureBlock {
    pub name: Rc<str>,
    pub structure: IncompleteStructure,
}

impl<'a> Display for Fmt<&'a StructureBlock> {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        writeln!(
            f,
            "structure {}:{} {{",
            self.value.name,
            self.value.structure.type_interps().vocab().name(),
        )?;
        write!(f, "{}", self.value.structure.display().with_indent())?;
        writeln!(f, "}}")
    }
}

impl Display for StructureBlock {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

display_as_debug!(StructureBlock);

impl Deref for StructureBlock {
    type Target = IncompleteStructure;

    fn deref(&self) -> &Self::Target {
        &self.structure
    }
}

/// A model of certain constraints.
#[derive(Clone)]
pub struct Model {
    #[allow(unused)]
    pub(crate) constraints: Constraints,
    pub(crate) structure: CompleteStructure,
}

impl FodotOptions for Model {
    type Options<'a> = StructureOptions<'a>;
}

impl FodotDisplay for Model {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        write!(f, "{}", fmt.with_opts(&fmt.value.structure))
    }
}

impl Display for Model {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

display_as_debug!(Model);

impl From<Model> for CompleteStructure {
    fn from(value: Model) -> Self {
        value.structure
    }
}

impl AsRef<CompleteStructure> for Model {
    fn as_ref(&self) -> &CompleteStructure {
        &self.structure
    }
}

impl Borrow<CompleteStructure> for Model {
    fn borrow(&self) -> &CompleteStructure {
        &self.structure
    }
}

impl Model {
    /// Converts the model into a [PartialStructure].
    pub fn into_partial(self) -> PartialStructure {
        CompleteStructure::from(self).into_partial()
    }
}

/// A set of model of certain constraints.
#[derive(Clone)]
pub struct GlobModel {
    pub(crate) constraints: Constraints,
    pub(crate) structure: PartialStructure,
}

impl FodotOptions for GlobModel {
    type Options<'a> = StructureOptions<'a>;
}

impl FodotDisplay for GlobModel {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        write!(f, "{}", fmt.with_opts(&fmt.value.structure))
    }
}

impl Display for GlobModel {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

display_as_debug!(GlobModel);

impl GlobModel {
    /// Skips infinite values by default.
    pub fn into_iter_models(self) -> IntoIterCompleteModel {
        IntoIterCompleteModel::new(self)
    }

    /// Skips infinite values by default.
    pub fn iter_models(&self) -> IterCompleteModel {
        IterCompleteModel::new(&self)
    }
}

impl From<GlobModel> for PartialStructure {
    fn from(value: GlobModel) -> Self {
        value.structure
    }
}

impl AsRef<PartialStructure> for GlobModel {
    fn as_ref(&self) -> &PartialStructure {
        &self.structure
    }
}

/// An iterator over all [Model]s in a [GlobModel].
///
/// See [IterCompleteStructure] for further documentation.
pub struct IterCompleteModel<'a> {
    constraints: Constraints,
    iter: IterCompleteStructure<'a>,
}

impl<'a> IterCompleteModel<'a> {
    fn new(glob_model: &'a GlobModel) -> Self {
        Self {
            constraints: glob_model.constraints.clone(),
            iter: glob_model.structure.iter_complete(),
        }
    }

    /// See [IterCompleteStructure::enable_skip_infinite].
    pub fn enable_skip_infinite(mut self) -> Self {
        self.iter = self.iter.enable_skip_infinite();
        self
    }

    /// See [IterCompleteStructure::disable_skip_infinite].
    pub fn disable_skip_infinite(mut self) -> Self {
        self.iter = self.iter.disable_skip_infinite();
        self
    }

    /// See [IterCompleteStructure::skip_infinite].
    pub fn skip_infinite(self, skip: bool) -> Self {
        if skip {
            self.enable_skip_infinite()
        } else {
            self.disable_skip_infinite()
        }
    }
}

impl<'a> Iterator for IterCompleteModel<'a> {
    type Item = Model;

    fn next(&mut self) -> Option<Self::Item> {
        self.iter.next().map(|f| Model {
            constraints: self.constraints.clone(),
            structure: f,
        })
    }
}

/// An owning iterator over all [Model]s in a [GlobModel].
///
/// See [IntoIterCompleteStructure] for further documentation.
pub struct IntoIterCompleteModel {
    constraints: Constraints,
    iter: IntoIterCompleteStructure,
}

impl IntoIterCompleteModel {
    fn new(glob_model: GlobModel) -> Self {
        Self {
            constraints: glob_model.constraints.clone(),
            iter: glob_model.structure.into_iter_complete(),
        }
    }

    /// See [IntoIterCompleteStructure::enable_skip_infinite].
    pub fn enable_skip_infinite(mut self) -> Self {
        self.iter = self.iter.enable_skip_infinite();
        self
    }

    /// See [IntoIterCompleteStructure::disable_skip_infinite].
    pub fn disable_skip_infinite(mut self) -> Self {
        self.iter = self.iter.disable_skip_infinite();
        self
    }

    /// See [IntoIterCompleteStructure::skip_infinite].
    pub fn skip_infinite(self, skip: bool) -> Self {
        if skip {
            self.enable_skip_infinite()
        } else {
            self.disable_skip_infinite()
        }
    }

    /// See [IntoIterCompleteStructure::skip_infinite].
    pub fn mut_skip_infinite(&mut self, skip: bool) {
        self.iter.mut_skip_infinite(skip);
    }
}

impl Iterator for IntoIterCompleteModel {
    type Item = Model;

    fn next(&mut self) -> Option<Self::Item> {
        self.iter.next().map(|f| Model {
            constraints: self.constraints.clone(),
            structure: f,
        })
    }
}

/// A builder for [Pfunc](super::vocabulary::Pfunc) arguments.
pub struct ArgsBuilder<'a> {
    domain_enum_builder: DomainEnumBuilder<'a>,
    domain: DomainFullRef<'a>,
}

impl<'a> ArgsBuilder<'a> {
    /// Creates a new [ArgsBuilder].
    pub fn new(domain: DomainFullRef<'a>) -> Self {
        Self {
            domain_enum_builder: DomainEnumBuilder::new(
                domain.cc_domain(),
                &domain.type_interps_ref().cc,
            ),
            domain,
        }
    }

    /// Returns the type of the current expected argument as a [TypeFull].
    pub fn cur_arg_type(&self) -> Option<TypeFull<'a>> {
        if self.domain_enum_builder.cur_arg_index() < self.domain.arity() {
            Some(
                self.domain
                    .get_ref(self.domain_enum_builder.cur_arg_index()),
            )
        } else {
            None
        }
    }

    pub fn cur_amount_of_args(&self) -> usize {
        self.domain_enum_builder.cur_arg_index()
    }

    fn _add_argument(&mut self, element: TypeElement) -> Result<&mut Self, ArgAddError> {
        self.domain_enum_builder
            .add_type_el_arg(element.clone().into())
            .map_err(|err| match err {
                DomainEnumErrors::WrongType => ArgAddError::from(TypeMismatch {
                    found: element.codomain().into(),
                    expected: self.cur_arg_type().unwrap().into(),
                }),
                DomainEnumErrors::TooManyArgs => ArgAddError::from(MismatchedArity {
                    expected: self.domain().arity(),
                    found: self.cur_amount_of_args(),
                }),
                _ => unreachable!(),
            })?;
        Ok(self)
    }

    /// Add the given element as an argument in the current position.
    ///
    /// This function is generic over any type that can be converted to a [TypeElement] via
    /// [TryIntoCtx].
    /// Some notable implementations: [TypeElement], &[str].
    pub fn add_argument<T>(
        &mut self,
        element: T,
    ) -> Result<&mut Self, <T::Error as ArgCreationErrorExtension>::Error>
    where
        T: TryIntoCtx<TypeElement<'a>, Ctx = TypeFull<'a>, Error: ArgCreationErrorExtension>,
    {
        if let Some(cur_type) = self.cur_arg_type() {
            let element = element.try_into_ctx(cur_type)?;
            self._add_argument(element).map_err(|f| f.into())
        } else {
            Err(
                ArgAddError::from(ArgAddErrorKind::MismatchedArity(MismatchedArity {
                    expected: self.domain().arity(),
                    found: self.cur_amount_of_args(),
                }))
                .into(),
            )
        }
    }

    /// Get the inputted [Args], leaving the [ArgsBuilder] untouched.
    pub fn get_args(&self) -> Result<ArgsRef<'a>, MismatchedArityError> {
        self.domain_enum_builder
            .get_index()
            .map(|f| ArgsRef {
                domain_enum: f,
                domain: self.domain.clone(),
            })
            .map_err(|err| match err {
                DomainEnumErrors::TooFewArgs => MismatchedArity {
                    expected: self.domain().arity(),
                    found: self.domain_enum_builder.cur_arg_index() + 1,
                }
                .into(),
                _ => unreachable!(),
            })
    }

    /// Get the inputted [Args], consuming the [ArgsBuilder].
    pub fn take_args(self) -> Result<ArgsRef<'a>, SymbolError> {
        self.domain_enum_builder
            .get_index()
            .map(|f| ArgsRef {
                domain_enum: f,
                domain: self.domain.clone(),
            })
            .map_err(|_| SymbolError::IDK)
    }

    /// Resets the inputted args.
    ///
    /// Allowing the [ArgsBuilder] to be reused for new arguments for the same domain.
    pub fn reset(&mut self) {
        self.domain_enum_builder.reset()
    }

    /// Get the inputted args and reset the [ArgsBuilder].
    ///
    /// This method always [resets](Self::reset) the [ArgsBuilder] even when it returns an [Err].
    ///
    /// See [Self::get_args] and [Self::reset].
    pub fn finish(&mut self) -> Result<ArgsRef<'a>, MismatchedArityError> {
        let ret = self.get_args();
        self.reset();
        ret
    }

    pub fn domain(&self) -> &DomainFullRef<'a> {
        &self.domain
    }
}

// Represents a tuple of a domain? Should this be called tuple??
#[derive(Clone)]
pub struct Args<T: PtrRepr<PartialTypeInterps>> {
    pub(crate) domain_enum: DomainEnum,
    pub(crate) domain: DomainFull<T>,
}

impl<T: PtrRepr<PartialTypeInterps>> FodotOptions for Args<T> {
    type Options<'a> = FormatOptions;
}

impl<T: PtrRepr<PartialTypeInterps>> FodotDisplay for Args<T> {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        let arg = fmt
            .value
            .iter()
            .map(|f| fmt.with_format_opts(f))
            .format(", ");
        if fmt.value.domain().arity() > 1 {
            write!(f, "({})", arg)
        } else {
            write!(f, "{}", arg)
        }
    }
}

impl<T: PtrRepr<PartialTypeInterps>> PartialEq for Args<T> {
    fn eq(&self, other: &Self) -> bool {
        self.domain_enum == other.domain_enum && self.domain == other.domain
    }
}

impl<T: PtrRepr<PartialTypeInterps>> Eq for Args<T> {}

impl<T: PtrRepr<PartialTypeInterps>> Args<T> {
    pub(crate) fn new(domain_enum: DomainEnum, domain: DomainFull<T>) -> Self {
        Args {
            domain_enum,
            domain,
        }
    }

    pub fn empty(domain: DomainFull<T>) -> Result<Self, MismatchedArity> {
        if domain.arity() == 0 {
            return Ok(Self::new(0.into(), domain));
        }
        return Err(MismatchedArity {
            expected: 0,
            found: domain.arity(),
        });
    }

    pub fn is_unit(&self) -> bool {
        self.domain().arity() == 0
    }

    /// Get the [TypeElement] at the given index.
    ///
    /// # Panics
    ///
    /// If the index is equal to or larger than the arity of the domain.
    pub fn get(&self, index: usize) -> TypeElement {
        self.domain
            .type_interps()
            .domain_enum_to_args(self.domain_enum, self.domain.as_domain())
            .nth(index)
            .expect("Out of index")
    }

    /// Returns an [Iterator] of the arguments as [TypeElement]s.
    pub fn iter(&self) -> impl SIterator<Item = TypeElement> {
        self.domain
            .type_interps()
            .domain_enum_to_args(self.domain_enum, self.domain.as_domain())
    }

    pub fn domain(&self) -> &DomainFull<T> {
        &self.domain
    }
}

pub type ArgsRef<'a> = Args<&'a PartialTypeInterps>;

impl<'a> ArgsRef<'a> {
    /// Get the [TypeElement] at the given index.
    ///
    /// # Panics
    ///
    /// If the index is equal to or larger than the arity of the domain.
    pub fn get_ref(&self, index: usize) -> TypeElement<'a> {
        self.domain
            .type_interps_ref()
            .domain_enum_to_args(self.domain_enum, self.domain.borrow().into())
            .nth(index)
            .expect("Out of index")
    }

    /// Returns an [Iterator] of the arguments as [TypeElement]s.
    pub fn iter_ref(&self) -> impl SIterator<Item = TypeElement<'a>> {
        self.domain
            .type_interps_ref()
            .domain_enum_to_args(self.domain_enum, self.domain.borrow().into())
    }

    pub fn into_iter_ref(self) -> impl SIterator<Item = TypeElement<'a>> {
        self.domain
            .type_interps_ref()
            .domain_enum_to_args(self.domain_enum, self.domain.borrow().into())
    }
}

pub type ArgsRc = Args<RcA<PartialTypeInterps>>;

/// Trait alias for `TryIntoCtx<Args<'a>, Ctx = DomainFull<'a>>`.
pub trait TryIntoArgs<'a>: TryIntoCtx<ArgsRef<'a>, Ctx = DomainFullRef<'a>> {}

impl<'a, T: TryIntoCtx<ArgsRef<'a>, Ctx = DomainFullRef<'a>>> TryIntoArgs<'a> for T {}

impl<
    'a,
    T: TryIntoCtx<TypeElement<'a>, Ctx = TypeFull<'a>, Error: ArgCreationErrorExtension>,
    I: IntoIterator<Item = T>,
> TryFromCtx<I> for ArgsRef<'a>
{
    type Ctx = DomainFullRef<'a>;
    type Error = <T::Error as ArgCreationErrorExtension>::Error;

    fn try_from_ctx(value: I, ctx: Self::Ctx) -> Result<Self, Self::Error> {
        let mut args_builder = ArgsBuilder::new(ctx.clone());
        for val in value.into_iter().zip_longest(ctx.iter_ref()) {
            let EitherOrBoth::Both(arg, arg_type) = val else {
                return Err(MismatchedArity {
                    expected: args_builder.domain().arity(),
                    found: args_builder.cur_amount_of_args(),
                }
                .into());
            };
            args_builder._add_argument(arg.try_into_ctx(arg_type)?)?;
        }
        args_builder.get_args().map_err(|f| f.into())
    }
}

impl<T: PtrRepr<PartialTypeInterps>> TryFromCtx<Args<T>> for Args<T> {
    type Ctx = DomainFull<T>;
    type Error = ArgMismatchError;

    fn try_from_ctx(value: Args<T>, ctx: Self::Ctx) -> Result<Self, Self::Error> {
        if value.domain().as_domain() != ctx.as_domain() {
            Err(DomainMismatch {
                expected: ctx.as_domain().into(),
                found: value.domain().as_domain().into(),
            }
            .into())
        } else if !core::ptr::eq(value.domain.type_interps(), ctx.type_interps()) {
            Err(TypeInterpsMismatchError.into())
        } else {
            Ok(value)
        }
    }
}

/// All usages of PartialTypeInterps must contain all types in the given domain.
pub(crate) mod domain_full_funcs {
    use super::*;
    use crate::fodot::vocabulary::domain_funcs;

    pub(crate) fn iter_args<'a>(
        id: Option<DomainIndex>,
        type_interps: &'a PartialTypeInterps,
    ) -> impl SIterator<Item = ArgsRef<'a>> {
        let len =
            domain_funcs::cc_domain(id, type_interps.vocab()).domain_len(type_interps.cc.as_ref());
        IndexRange::new(0..len).map(move |domain_enum| ArgsRef {
            domain_enum,
            domain: DomainFull(id, type_interps),
        })
    }

    pub(crate) fn get<'a>(
        id: Option<DomainIndex>,
        type_interps: &'a PartialTypeInterps,
        index: usize,
    ) -> TypeFull<'a> {
        domain_funcs::get(id, type_interps.vocab(), index)
            .with_partial_interps(type_interps)
            .unwrap()
    }

    pub(crate) fn iter<'a>(
        id: Option<DomainIndex>,
        type_interps: &'a PartialTypeInterps,
    ) -> impl SIterator<Item = TypeFull<'a>> {
        domain_funcs::iter(id, type_interps.vocab())
            .map(move |f| f.with_partial_interps(type_interps).unwrap())
    }
}

#[derive(Clone)]
pub struct DomainFull<T: PtrRepr<PartialTypeInterps>>(pub(super) Option<DomainIndex>, pub(super) T);

impl<T: PtrRepr<PartialTypeInterps>> FodotOptions for DomainFull<T> {
    type Options<'b> = <DomainRc as FodotOptions>::Options<'b>;
}

impl<T: PtrRepr<PartialTypeInterps>> FodotDisplay for DomainFull<T> {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        write!(f, "{}", fmt.with_opts(&(fmt.value._dom_ref())))
    }
}

impl<T: PtrRepr<PartialTypeInterps>> Display for DomainFull<T> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

display_as_debug!(DomainFull<T>, gen: (T), where: (T: PtrRepr<PartialTypeInterps>));

impl<T: PtrRepr<PartialTypeInterps>> PartialEq for DomainFull<T> {
    fn eq(&self, other: &Self) -> bool {
        self.0 == other.0 && core::ptr::eq(self.1.deref(), other.1.deref())
    }
}

impl<'a, T: PtrRepr<PartialTypeInterps>> From<&'a DomainFull<T>> for DomainFullRef<'a> {
    fn from(value: &'a DomainFull<T>) -> Self {
        Self(value.0, value.1.deref())
    }
}

impl<T: PtrRepr<PartialTypeInterps>> Eq for DomainFull<T> {}

impl<T: PtrRepr<PartialTypeInterps>> DomainFull<T> {
    pub(crate) fn _dom_ref(&self) -> DomainRef {
        Domain(self.0, self.type_interps().vocab())
    }

    pub fn iter_args(&self) -> impl SIterator<Item = ArgsRef> + '_ {
        domain_full_funcs::iter_args(self.0, self.1.deref())
    }

    pub fn get(&self, index: usize) -> TypeFull {
        domain_full_funcs::get(self.0, self.1.deref(), index)
    }

    pub fn iter(&self) -> impl SIterator<Item = TypeFull> {
        domain_full_funcs::iter(self.0, self.1.deref())
    }

    pub fn arity(&self) -> usize {
        domain_funcs::arity(self.0, self.1.deref().vocab())
    }

    pub fn len(&self) -> usize {
        self.as_domain()
            .cc_domain()
            .domain_len(self.1.deref().cc.as_ref())
    }

    pub fn type_interps(&self) -> &PartialTypeInterps {
        self.1.deref()
    }

    pub fn as_domain(&self) -> DomainRef {
        Domain(self.0, self.1.deref().vocab())
    }

    pub fn is_infinite(&self) -> bool {
        self.as_domain().is_infinite()
    }
}

pub type DomainFullRef<'a> = DomainFull<&'a PartialTypeInterps>;

impl<'a> From<&'_ DomainFullRef<'a>> for DomainRef<'a> {
    fn from(value: &'_ DomainFullRef<'a>) -> Self {
        Self(value.0, value.1.vocab())
    }
}

impl<'a> DomainFullRef<'a> {
    pub(crate) fn cc_domain(&self) -> &'a CCDomainSlice {
        domain_funcs::cc_domain(self.0, self.1.vocab())
    }

    pub fn iter_args_ref(&self) -> impl SIterator<Item = ArgsRef<'a>> + '_ {
        domain_full_funcs::iter_args(self.0, self.1)
    }

    pub fn into_iter_args(self) -> impl SIterator<Item = ArgsRef<'a>> {
        domain_full_funcs::iter_args(self.0, self.1)
    }

    pub fn get_ref(&self, index: usize) -> TypeFull<'a> {
        domain_full_funcs::get(self.0, self.1, index)
    }

    pub fn iter_ref(&self) -> impl SIterator<Item = TypeFull<'a>> {
        domain_full_funcs::iter(self.0, self.1)
    }

    pub fn type_interps_ref(&self) -> &'a PartialTypeInterps {
        self.1
    }

    pub fn build_args(&self) -> ArgsBuilder<'a> {
        ArgsBuilder::new(self.clone())
    }
}

pub type DomainFullRc = DomainFull<RcA<PartialTypeInterps>>;

impl<'a> From<&'a DomainFullRc> for DomainRef<'a> {
    fn from(value: &'a DomainFullRc) -> Self {
        Self(value.0, value.1.vocab())
    }
}

impl DomainFullRc {
    pub fn new<T>(
        types: &[T],
        type_interps: Rc<TypeInterps>,
    ) -> Result<Self, <&T as TryIntoCtx<TypeRc>>::Error>
    where
        for<'a> &'a T: TryIntoCtx<TypeRc, Ctx = Rc<Vocabulary>>,
    {
        Ok(DomainRc::new(types, type_interps.vocab_rc().clone())?
            .with_interps(type_interps)
            .unwrap())
    }
}

pub use comp_core::structure::Precision;

pub(in crate::fodot) mod translation_layer {
    use super::{CustomElement, PartialTypeInterps, SIterator, StrElement, TypeElement};
    use crate::fodot::vocabulary::{CustomTypeRef, DomainRef, StrTypeRef, TypeRef};
    use comp_core::structure::TypeElementIter;
    use comp_core::vocabulary::TypeEnum;
    use comp_core::{self as cc, IndexRepr, vocabulary::TypeElementIndex};

    impl<'a> From<TypeElement<'a>> for cc::structure::TypeElement {
        fn from(value: TypeElement<'a>) -> Self {
            match value {
                TypeElement::Bool(value) => Self::Bool(value),
                TypeElement::Int(value) => Self::Int(value),
                TypeElement::Real(value) => Self::Real(value),
                TypeElement::Str(value) => Self::Custom(value.into()),
            }
        }
    }

    impl<'a> From<StrElement<'a>> for TypeElementIndex {
        fn from(value: StrElement<'a>) -> Self {
            let index = IndexRepr::try_from(
                value
                    .type_interps
                    .ensured_get_interp(value.decl().into())
                    .unwrap_str()
                    .0
                    .get_index_of(value.value)
                    .unwrap(),
            )
            .unwrap();
            TypeElementIndex(
                TypeRef::custom_type_id_to_cc(value.type_decl_index, value.type_interps.vocab()),
                index.into(),
            )
        }
    }

    impl<'a> TypeElement<'a> {
        pub(in crate::fodot) fn from_cc(
            cc_type_element: cc::structure::TypeElement,
            type_interps: &'a PartialTypeInterps,
        ) -> Self {
            use cc::structure::TypeElement as TE;
            match cc_type_element {
                TE::Bool(value) => Self::Bool(value),
                TE::Int(value) => Self::Int(value),
                TE::Real(value) => Self::Real(value),
                TE::Custom(value) => CustomElement::from_cc(value, type_interps).into(),
            }
        }
    }

    impl<'a> CustomElement<'a> {
        pub(in crate::fodot) fn from_cc(
            type_element_index: TypeElementIndex,
            type_interps: &'a PartialTypeInterps,
        ) -> Self {
            let custom_type = CustomTypeRef::from_cc(type_element_index.0, type_interps.vocab());
            match custom_type {
                CustomTypeRef::Str(value) => {
                    StrElement::from_type_enum(value, type_interps, type_element_index.1).into()
                }
                _ => panic!("This should never happen but maybe I'll handle this in the future"),
            }
        }
    }

    impl<'a> StrElement<'a> {
        pub(in crate::fodot) fn get_type_enum(&self) -> TypeEnum {
            TypeEnum::from(
                self.type_interps
                    .ensured_get_interp(self.decl().into())
                    .unwrap_str()
                    .0
                    .get_index_of(self.value)
                    .unwrap(),
            )
        }

        pub(in crate::fodot) fn from_type_enum(
            str_type: StrTypeRef<'a>,
            type_interps: &'a PartialTypeInterps,
            type_enum: TypeEnum,
        ) -> Self {
            let str_interp = type_interps
                .ensured_get_interp(str_type.into())
                .unwrap_str();
            let element = str_interp
                .0
                .get_index(usize::try_from(IndexRepr::from(type_enum)).unwrap())
                .unwrap();
            Self {
                value: element.as_ref(),
                type_decl_index: str_type.0,
                type_interps: &type_interps,
            }
        }
    }

    impl PartialTypeInterps {
        pub(in crate::fodot) fn domain_enum_to_args<'a, 'b>(
            &'b self,
            domain_enum: cc::vocabulary::DomainEnum,
            domain: DomainRef<'b>,
        ) -> impl SIterator<Item = TypeElement<'a>> + 'b
        where
            'b: 'a,
        {
            TypeElementIter::new(&self.cc, domain.cc_domain().iter(), domain_enum)
                .map(move |f| TypeElement::from_cc(f, self))
        }
    }
}

#[cfg(test)]
mod tests {
    use super::{IncompleteStructure, IntInterp, PartialStructure, StrInterp, partial};
    use crate::Rc;
    use crate::fodot::TryIntoCtx;
    use crate::fodot::structure::TypeElement;
    use crate::fodot::vocabulary::{BaseType, Vocabulary};

    #[test]
    fn parse_structure() {
        let mut vocab = Vocabulary::new("T");
        vocab.add_type_decl("D", BaseType::Int).unwrap();
        vocab.parse("type T p: T -> Bool r: T -> D").unwrap();
        let (vocab, mut part_type_interps) = vocab.complete_vocab();
        part_type_interps
            .set_interp(
                vocab.parse_type("T").unwrap().try_into().unwrap(),
                StrInterp::from_iter(["a", "b"]).into(),
            )
            .unwrap();
        part_type_interps
            .set_interp(
                vocab.parse_type("D").unwrap().try_into().unwrap(),
                IntInterp::try_from_iterator([1, 2]).unwrap().into(),
            )
            .unwrap();
        let type_interps = Rc::new(part_type_interps.try_err_complete().unwrap());
        let mut structure = PartialStructure::new(type_interps.clone());
        structure.parse("p := {a}. r :> { a -> 2 }.").unwrap();
        let partial::immutable::SymbolInterp::Pred(p) =
            structure.get(vocab.parse_pfunc("p").unwrap())
        else {
            unreachable!()
        };
        assert_eq!(
            p.get(["a"].try_into_ctx(p.domain_full()).unwrap()).unwrap(),
            Some(true)
        );
        assert_eq!(
            p.get(["b"].try_into_ctx(p.domain_full()).unwrap()).unwrap(),
            Some(false)
        );
        let partial::immutable::SymbolInterp::IntFunc(r) =
            structure.get(vocab.parse_pfunc("r").unwrap())
        else {
            unreachable!()
        };
        assert_eq!(
            r.get(["a"].try_into_ctx(r.domain_full()).unwrap()).unwrap(),
            Some(2)
        );
        assert_eq!(
            r.get(["b"].try_into_ctx(r.domain_full()).unwrap()).unwrap(),
            None
        );
    }

    #[test]
    fn failed_parse_structure() {
        let mut vocab = Vocabulary::new("T");
        vocab.add_type_decl("D", BaseType::Int).unwrap();
        vocab.parse("type T p: T -> Bool r: T -> D").unwrap();
        let (vocab, mut part_type_interps) = vocab.complete_vocab();
        part_type_interps
            .set_interp(
                vocab.parse_type("T").unwrap().try_into().unwrap(),
                StrInterp::from_iter(["a", "b"]).into(),
            )
            .unwrap();
        part_type_interps
            .set_interp(
                vocab.parse_type("D").unwrap().try_into().unwrap(),
                IntInterp::try_from_iterator([1, 2]).unwrap().into(),
            )
            .unwrap();
        let type_interps = Rc::new(part_type_interps.try_err_complete().unwrap());
        let mut structure = PartialStructure::new(type_interps.clone());
        let partial::mutable::SymbolInterp::Pred(mut p) =
            structure.get_mut(vocab.parse_pfunc("p").unwrap())
        else {
            unreachable!()
        };
        p.set(["a"].try_into_ctx(p.domain_full()).unwrap(), Some(true))
            .unwrap();
        let old_structure = structure.clone();
        let diag = structure.parse("r :> { a -> 2 }").unwrap_err();
        assert_eq!(diag.errors().len(), 1);
        assert_eq!(old_structure, structure);
    }

    #[test]
    fn escaped_structure() {
        let mut vocab = Vocabulary::new("T");
        vocab.add_type_decl("D", BaseType::Int).unwrap();
        vocab.parse("type T p: T -> Bool r: T -> D").unwrap();
        let (vocab, mut part_type_interps) = vocab.complete_vocab();
        part_type_interps
            .set_interp(
                vocab.parse_type("T").unwrap().try_into().unwrap(),
                StrInterp::from_iter(["a", "b"]).into(),
            )
            .unwrap();
        part_type_interps
            .set_interp(
                vocab.parse_type("D").unwrap().try_into().unwrap(),
                IntInterp::try_from_iterator([1, 2]).unwrap().into(),
            )
            .unwrap();
        let type_interps = Rc::new(part_type_interps.try_err_complete().unwrap());
        let mut structure = PartialStructure::new(type_interps.clone());
        let decls = "} theory T:V {";
        let diag = structure.parse(decls).unwrap_err();
        assert_eq!(diag.errors().len(), 1);
        let a = diag.errors().first().unwrap();
        assert_eq!(a.span().end, decls.len());
    }

    #[test]
    fn incomplete_structure() {
        let mut vocab = Vocabulary::new("V");
        vocab
            .parse(
                "
            type T
            type B
            p: T -> Bool
            t: B -> Bool
        ",
            )
            .unwrap();
        let (vocab, type_interps) = vocab.complete_vocab();
        let mut structure = IncompleteStructure::new(type_interps);
        let t_type = vocab.parse_custom_type("T").unwrap();
        let b_type = vocab.parse_custom_type("B").unwrap();
        let p_pred = vocab.parse_pfunc("p").unwrap();
        assert!(structure.get(p_pred).is_err());
        structure
            .set_interp(t_type, StrInterp::from_iter(["a", "b", "c"]).into())
            .unwrap();
        let p_interp = structure.get(p_pred).unwrap();
        assert!(!p_interp.any_known());
        let partial::mutable::SymbolInterp::Pred(mut p_interp) = structure.get_mut(p_pred).unwrap()
        else {
            unreachable!()
        };
        p_interp
            .set(
                ["a"].try_into_ctx(p_interp.domain_full()).unwrap(),
                Some(true),
            )
            .unwrap();
        assert!(
            structure
                .set_interp(t_type, StrInterp::from_iter(["a", "b", "c", "d"]).into())
                .is_err()
        );
        let p_interp = structure.get(p_pred).unwrap();
        assert_eq!(
            p_interp
                .get(["a"].try_into_ctx(p_interp.domain_full()).unwrap())
                .unwrap(),
            Some(TypeElement::Bool(true))
        );
        assert_eq!(
            p_interp
                .get(["b"].try_into_ctx(p_interp.domain_full()).unwrap())
                .unwrap(),
            None
        );
        assert!(
            structure
                .set_interp(b_type, StrInterp::from_iter(["a", "b", "c", "d"]).into())
                .is_ok()
        );
        assert!(structure.try_into_partial().is_ok());
    }
}
