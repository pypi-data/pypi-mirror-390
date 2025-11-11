use super::{
    _SymbolStr, CustomType, Domain, DomainRc, DomainRef, ExtendedDomain, PfuncIndex, StrType, Type,
    TypeRc, TypeRef, TypeSymbolIndex, Vocabulary,
};
use crate::ast::Span;
use crate::fodot::error::MissingSymbolError;
use crate::fodot::fmt::{
    self, CharSet, Fmt, FodotDisplay, FodotOptions, FormatOptions, IMAGE_ASCII, IMAGE_UNI,
    SymbolOptions,
};
use crate::fodot::structure::TypeInterp;
use crate::fodot::{Metadata, MetadataIm, TryFromCtx, display_as_debug};
use comp_core::vocabulary::TypeElementIndex;
use comp_core::{
    IndexRepr,
    vocabulary::{PfuncIndex as CCPfuncIndex, TypeEnum},
};
use sli_collections::rc::{PtrRepr, Rc, RcA};
use std::hash::Hash;
use std::{borrow::Borrow, fmt::Display};

/// Represents an FO(·) symbol.
///
/// Possible symbols are:
/// - types ([Symbol::Type])
/// - pfuncs ([Symbol::Pfunc]), which are predicates and functions (nullary symbols included)
/// - constructors ([Symbol::Constructor])
///
/// The most useful versions of this struct are [SymbolRef] and [SymbolRc].
#[derive(Clone, Hash)]
pub enum Symbol<T: PtrRepr<Vocabulary>> {
    Type(Type<T>),
    Pfunc(Pfunc<T>),
    Constructor(Constructor<T>),
}

impl<T: PtrRepr<Vocabulary>> PartialEq for Symbol<T> {
    fn eq(&self, other: &Self) -> bool {
        match (self, other) {
            (Self::Type(value1), Self::Type(value2)) => value1 == value2,
            (Self::Pfunc(value1), Self::Pfunc(value2)) => value1 == value2,
            (Self::Constructor(value1), Self::Constructor(value2)) => value1 == value2,
            _ => false,
        }
    }
}

impl<T: PtrRepr<Vocabulary>> Eq for Symbol<T> {}

impl<T: PtrRepr<Vocabulary>> FodotOptions for Symbol<T> {
    type Options<'a> = SymbolOptions;
}

impl<T: PtrRepr<Vocabulary>> FodotDisplay for Symbol<T> {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        match fmt.value {
            Symbol::Type(value) => write!(f, "{}", fmt.with_format_opts(value)),
            Symbol::Pfunc(value) => write!(f, "{}", fmt.with_opts(value)),
            Symbol::Constructor(value) => write!(f, "{}", fmt.with_format_opts(value)),
        }
    }
}

impl<T: PtrRepr<Vocabulary>> Display for Symbol<T> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

display_as_debug!(Symbol<T>, gen: (T), where: (T: PtrRepr<Vocabulary>));

/// A referencing type alias for [Symbol].
pub type SymbolRef<'a> = Symbol<&'a Vocabulary>;
/// An owning (via [Rc]) type alias for [Symbol].
pub type SymbolRc = Symbol<RcA<Vocabulary>>;

impl<'a> TryFromCtx<&str> for SymbolRef<'a> {
    type Ctx = &'a Vocabulary;
    type Error = MissingSymbolError;

    fn try_from_ctx(value: &str, ctx: Self::Ctx) -> Result<Self, Self::Error> {
        ctx.parse_symbol(value)
    }
}

impl TryFromCtx<&str> for SymbolRc {
    type Ctx = Rc<Vocabulary>;
    type Error = MissingSymbolError;

    fn try_from_ctx(value: &str, ctx: Self::Ctx) -> Result<Self, Self::Error> {
        Vocabulary::parse_symbol_rc(&ctx, value)
    }
}

impl<T: PtrRepr<Vocabulary>> From<Type<T>> for Symbol<T> {
    fn from(value: Type<T>) -> Self {
        Self::Type(value)
    }
}

impl<T: PtrRepr<Vocabulary>> From<CustomType<T>> for Symbol<T> {
    fn from(value: CustomType<T>) -> Self {
        Self::Type(value.into())
    }
}

impl<T: PtrRepr<Vocabulary>> From<Pfunc<T>> for Symbol<T> {
    fn from(value: Pfunc<T>) -> Self {
        Self::Pfunc(value)
    }
}

impl<T: PtrRepr<Vocabulary>> From<Constructor<T>> for Symbol<T> {
    fn from(value: Constructor<T>) -> Self {
        Self::Constructor(value)
    }
}

impl<T: PtrRepr<Vocabulary>> Symbol<T> {
    pub fn vocab(&self) -> Option<&Vocabulary> {
        self.vocab_repr().map(|f| f.deref())
    }

    pub(crate) fn _name(&self) -> &str {
        match self {
            Self::Type(value) => value.name(),
            Self::Pfunc(value) => value.name(),
            Self::Constructor(value) => value.name(),
        }
    }

    pub fn is_constructor(&self) -> bool {
        matches!(self, Self::Constructor(_))
    }

    pub(crate) fn wrap<F: PtrRepr<Vocabulary>>(self, new_vocab: F) -> Symbol<F> {
        match self {
            Self::Type(value) => value.wrap(new_vocab).into(),
            Self::Pfunc(value) => value.wrap(new_vocab).into(),
            Self::Constructor(value) => value.wrap(new_vocab).into(),
        }
    }

    fn vocab_repr(&self) -> Option<&T> {
        match self {
            Self::Type(value) => value.vocab_repr(),
            Self::Pfunc(value) => Some(&value.1),
            Self::Constructor(value) => value.vocab_repr().into(),
        }
    }

    pub fn domain(&self) -> ExtendedDomain {
        match self {
            Self::Type(_) => ExtendedDomain::UnaryUniverse,
            Self::Pfunc(pfunc) => ExtendedDomain::Domain(pfunc._domain()),
            Self::Constructor(value) => ExtendedDomain::Domain(value._domain()),
        }
    }

    pub fn codomain(&self) -> TypeRef {
        match self {
            Self::Type(_) => Type::Bool,
            Self::Pfunc(value) => value._codomain(),
            Self::Constructor(value) => value._codomain(),
        }
    }
}

impl SymbolRc {
    pub fn vocab_rc(&self) -> Option<&RcA<Vocabulary>> {
        self.vocab_repr()
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub(crate) enum CustomSymbolIndex {
    Pfunc(PfuncIndex),
    Type(TypeSymbolIndex),
    Constructor((TypeSymbolIndex, TypeEnum)),
}

/// Represents an FO(·) pfunc, which are predicates and functions (nullary symbols included).
///
/// The most useful versions of this struct are [PfuncRef] and [PfuncRc].
#[derive(Clone, Hash)]
pub struct Pfunc<T: PtrRepr<Vocabulary>>(pub(crate) PfuncIndex, pub(crate) T);

/// A referencing type alias for [Pfunc].
pub type PfuncRef<'a> = Pfunc<&'a Vocabulary>;
/// An owning (via [Rc]) type alias for [Pfunc].
pub type PfuncRc = Pfunc<RcA<Vocabulary>>;

impl<T: PtrRepr<Vocabulary>> PartialEq for Pfunc<T> {
    fn eq(&self, other: &Self) -> bool {
        self.0 == other.0 && self.1.borrow().exact_eq(other.1.borrow())
    }
}

impl<T: PtrRepr<Vocabulary>> Eq for Pfunc<T> {}

impl<'a, T: PtrRepr<Vocabulary>> From<&'a Pfunc<T>> for PfuncRef<'a> {
    fn from(value: &'a Pfunc<T>) -> Self {
        Self(value.0, value.1.deref())
    }
}

impl<T: PtrRepr<Vocabulary>> FodotOptions for Pfunc<T> {
    type Options<'a> = SymbolOptions;
}

impl<T: PtrRepr<Vocabulary>> FodotDisplay for Pfunc<T> {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        if fmt.name_only {
            return write!(f, "{}", fmt.value.name());
        }
        let image = match fmt.options.char_set {
            CharSet::Ascii => IMAGE_ASCII,
            CharSet::Unicode => IMAGE_UNI,
        };
        write!(
            f,
            "{}: {} {} {}",
            fmt.value.name(),
            fmt.with_format_opts(&fmt.value._domain()),
            image,
            fmt.with_format_opts(&fmt.value._codomain()),
        )
    }
}

display_as_debug!(Pfunc<T>, gen: (T), where: (T: PtrRepr<Vocabulary>));

impl<T: PtrRepr<Vocabulary>> Display for Pfunc<T> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

impl<T: PtrRepr<Vocabulary>> MetadataIm for Pfunc<T> {
    type Metadata = PfuncMetadata;

    fn metadata(&self) -> Option<&Self::Metadata> {
        self.vocab()._pfunc_metadata(self.0)
    }
}

impl<T: PtrRepr<Vocabulary>> Pfunc<T> {
    /// Returns the corresponding [Vocabulary].
    pub fn vocab(&self) -> &Vocabulary {
        self.1.deref()
    }

    pub fn name(&self) -> &str {
        &self.1.deref().pfunc_names[self.0]
    }

    pub fn name_rc(&self) -> Rc<str> {
        self.1.deref().pfunc_names[self.0].clone()
    }

    pub(crate) fn _domain(&self) -> DomainRef {
        DomainRef::from_pfunc_ref_decl(&self.into())
    }

    pub(crate) fn wrap<F: PtrRepr<Vocabulary>>(self, new_vocab: F) -> Pfunc<F> {
        Pfunc(self.0, new_vocab)
    }

    pub(crate) fn _codomain(&self) -> TypeRef {
        TypeRef::from_cc(
            &self
                .1
                .deref()
                .comp_core_symbs
                .pfuncs(IndexRepr::from(self.0).into())
                .codomain,
            self.1.deref(),
        )
    }

    pub(crate) fn to_cc(&self) -> CCPfuncIndex {
        self.1.deref().pfunc_index_to_cc(self.0)
    }
}

impl<'a> Copy for PfuncRef<'a> {}

impl<'a> PfuncRef<'a> {
    /// Returns the corresponding domain as a [DomainRef].
    pub fn domain(&self) -> DomainRef<'a> {
        DomainRef::from_pfunc_ref_decl(self)
    }

    /// Returns the corresponding codomain as a [TypeRef].
    pub fn codomain(&self) -> TypeRef<'a> {
        TypeRef::from_cc(
            &self
                .1
                .comp_core_symbs
                .pfuncs(IndexRepr::from(self.0).into())
                .codomain,
            self.1,
        )
    }

    /// Returns the name of the pfunc.
    pub fn name_ref(&self) -> &'a str {
        &self.1.borrow().pfunc_names[self.0]
    }
}

impl PfuncRc {
    /// Returns the corresponding domain as a [DomainRef].
    pub fn domain(&self) -> DomainRef {
        self._domain()
    }

    /// Returns the corresponding domain as a [DomainRc].
    pub fn domain_rc(&self) -> DomainRc {
        Domain(self._domain().0, self.1.clone())
    }

    /// Returns the corresponding codomain as a [TypeRef].
    pub fn codomain(&self) -> TypeRef {
        self._codomain()
    }

    /// Returns the corresponding codomain as a [TypeRef].
    pub fn codomain_rc(&self) -> TypeRc {
        self._codomain().wrap(self.1.clone())
    }
}

#[derive(Debug, Clone, Default, Hash, PartialEq, Eq)]
pub struct PfuncMetadata {
    metadata: Metadata,
    pfunc_span: Option<Span>,
    domain_span: Option<Rc<[Span]>>,
    codomain_span: Option<Span>,
}

impl AsRef<Metadata> for PfuncMetadata {
    fn as_ref(&self) -> &Metadata {
        &self.metadata
    }
}

impl AsMut<Metadata> for PfuncMetadata {
    fn as_mut(&mut self) -> &mut Metadata {
        &mut self.metadata
    }
}

impl core::ops::Deref for PfuncMetadata {
    type Target = Metadata;

    fn deref(&self) -> &Self::Target {
        &self.metadata
    }
}

impl PfuncMetadata {
    pub fn set_metadata(&mut self, metadata: Metadata) -> &mut Self {
        self.metadata = metadata;
        self
    }

    pub fn with_metadata(mut self, metadata: Metadata) -> Self {
        self.set_metadata(metadata);
        self
    }

    pub fn pfunc_span(&self) -> Option<&Span> {
        self.pfunc_span.as_ref()
    }

    pub fn set_pfunc_span(&mut self, pfunc_span: Span) -> &mut Self {
        self.pfunc_span = Some(pfunc_span);
        self
    }

    pub fn with_pfunc_span(mut self, pfunc_span: Span) -> Self {
        self.set_pfunc_span(pfunc_span);
        self
    }

    pub fn domain_span(&self) -> Option<&[Span]> {
        self.domain_span.as_deref()
    }

    pub fn set_domain_span(&mut self, domain_span: Rc<[Span]>) -> &mut Self {
        self.domain_span = Some(domain_span);
        self
    }

    pub fn with_domain_span(mut self, domain_span: Rc<[Span]>) -> Self {
        self.set_domain_span(domain_span);
        self
    }

    pub fn codomain_span(&self) -> Option<&Span> {
        self.codomain_span.as_ref()
    }

    pub fn set_codomain_span(&mut self, codomain_span: Span) -> &mut Self {
        self.codomain_span = Some(codomain_span);
        self
    }

    pub fn with_codomain_span(mut self, codomain_span: Span) -> Self {
        self.set_codomain_span(codomain_span);
        self
    }
}

/// Represents a FO(·) constructor.
/// These are declared in type enumerations.
///
/// The most useful versions of this struct are [ConstructorRef] and [ConstructorRc].
#[derive(Clone, Hash)]
pub struct Constructor<T: PtrRepr<Vocabulary>> {
    pub(crate) type_id: StrType<T>,
    pub(crate) type_enum: TypeEnum,
}

impl<T: PtrRepr<Vocabulary>> PartialEq for Constructor<T> {
    fn eq(&self, other: &Self) -> bool {
        self.type_id == other.type_id && self.type_enum == other.type_enum
    }
}

impl<T: PtrRepr<Vocabulary>> Eq for Constructor<T> {}

impl<T: PtrRepr<Vocabulary>> FodotOptions for Constructor<T> {
    type Options<'a> = FormatOptions;
}

impl<T: PtrRepr<Vocabulary>> FodotDisplay for Constructor<T> {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        f.write_str(fmt.value.name())
    }
}

impl<'a, T: PtrRepr<Vocabulary>> Display for Constructor<T> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

display_as_debug!(Constructor<T>, gen: (T), where: (T: PtrRepr<Vocabulary>));

impl<T: PtrRepr<Vocabulary>> Constructor<T> {
    pub(crate) fn vocab_repr(&self) -> &T {
        &self.type_id.1
    }

    pub(crate) fn _vocab(&self) -> &Vocabulary {
        self.type_id.1.borrow()
    }

    pub fn name(&self) -> &str {
        &self._name_rc()
    }

    fn _name_rc(&self) -> &Rc<str> {
        let a = self.type_id.1.borrow();
        let TypeInterp::Str(str_interp) = &a.part_type_interps.get_interp(self.type_id.0).unwrap()
        else {
            unreachable!();
        };
        str_interp
            .0
            .get_index(usize::try_from(self.type_enum).unwrap())
            .unwrap()
    }

    pub fn name_rc(&self) -> Rc<str> {
        self._name_rc().clone()
    }

    pub(crate) fn wrap<F: PtrRepr<Vocabulary>>(self, new_vocab: F) -> Constructor<F> {
        Constructor {
            type_id: self.type_id.wrap(new_vocab),
            type_enum: self.type_enum,
        }
    }

    pub(crate) fn _domain(&self) -> DomainRef {
        Domain(None, self.type_id.1.borrow())
    }

    pub(crate) fn _codomain(&self) -> TypeRef {
        TypeRef::StrType(StrType(self.type_id.0, self.type_id.1.borrow()))
    }

    pub(crate) fn to_cc(&self) -> TypeElementIndex {
        TypeElementIndex(self.type_id.to_cc(), self.type_enum)
    }
}

/// A referencing type alias for [Constructor].
pub type ConstructorRef<'a> = Constructor<&'a Vocabulary>;

impl<'a> ConstructorRef<'a> {
    /// Returns the name of the pfunc.
    pub fn name_ref(&self) -> &'a str {
        let a = self.type_id.1;
        let TypeInterp::Str(str_interp) = &a.part_type_interps.get_interp(self.type_id.0).unwrap()
        else {
            unreachable!();
        };
        str_interp
            .0
            .get_index(usize::try_from(self.type_enum).unwrap())
            .unwrap()
    }

    /// Returns the corresponding [Vocabulary].
    pub fn vocab(&self) -> &'a Vocabulary {
        self.vocab_repr()
    }

    /// Returns the corresponding domain as a [DomainRef].
    pub fn domain(&self) -> DomainRef<'a> {
        Domain(None, self.type_id.1)
    }

    /// Returns the corresponding domain as a [DomainRc].
    pub fn codomain(&self) -> TypeRef<'a> {
        TypeRef::StrType(StrType(self.type_id.0, self.type_id.1))
    }
}

/// An owning (via [Rc]) type alias for [Constructor].
pub type ConstructorRc = Constructor<RcA<Vocabulary>>;

impl ConstructorRc {
    pub fn vocab(&self) -> &Vocabulary {
        self._vocab()
    }

    pub fn vocab_rc(&self) -> &RcA<Vocabulary> {
        self.vocab_repr()
    }

    pub fn domain(&self) -> DomainRef {
        self._domain()
    }

    pub fn codomain(&self) -> TypeRef {
        self._codomain()
    }
}

impl<'a> From<&'a ConstructorRc> for ConstructorRef<'a> {
    fn from(value: &'a ConstructorRc) -> Self {
        Self {
            type_id: StrType(value.type_id.0, &value.type_id.1),
            type_enum: value.type_enum,
        }
    }
}

/// The type of an FO(·) symbol.
#[non_exhaustive]
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum SymbolType {
    /// A type symbol is a predicate with its domain being the universe.
    ///
    /// For most inference tasks the interpretation of all types in a [Vocabulary] must be known.
    Type,
    /// A predicate or function.
    Pfunc,
    /// A constant created for the enumeration of a type.
    ///
    /// See also [Herbrand structure](https://en.wikipedia.org/wiki/Herbrand_structure).
    Constructor,
}

impl<'a, T: PtrRepr<Vocabulary>> From<&'a Symbol<T>> for SymbolType {
    fn from(value: &'a Symbol<T>) -> Self {
        match value {
            Symbol::Type(_) => SymbolType::Type,
            Symbol::Pfunc(_) => SymbolType::Pfunc,
            Symbol::Constructor(_) => SymbolType::Constructor,
        }
    }
}

impl<'a> From<&'a CustomSymbolIndex> for SymbolType {
    fn from(value: &'a CustomSymbolIndex) -> Self {
        match value {
            CustomSymbolIndex::Type(_) => SymbolType::Type,
            CustomSymbolIndex::Pfunc(_) => SymbolType::Pfunc,
            CustomSymbolIndex::Constructor(_) => SymbolType::Constructor,
        }
    }
}

impl SymbolType {
    pub(crate) fn sentence_name(&self) -> &'static str {
        match self {
            SymbolType::Type => "type",
            SymbolType::Pfunc => "predicate or function",
            SymbolType::Constructor => "constructor",
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct SymbolStr(_SymbolStr);

impl From<&str> for SymbolStr {
    fn from(value: &str) -> Self {
        Self(value.into())
    }
}

impl FodotOptions for SymbolStr {
    type Options<'a> = FormatOptions;
}

impl FodotDisplay for SymbolStr {
    fn fmt(
        fmt: fmt::Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        write!(f, "{}", fmt.with_opts(&fmt.value.0))
    }
}

impl Display for SymbolStr {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

impl<T: PtrRepr<Vocabulary>> From<Symbol<T>> for SymbolStr {
    fn from(value: Symbol<T>) -> Self {
        match value {
            Symbol::Type(Type::Bool) => Self(_SymbolStr::Bool),
            Symbol::Type(Type::Int) => Self(_SymbolStr::Int),
            Symbol::Type(Type::Real) => Self(_SymbolStr::Real),
            Symbol::Type(other) => Self(_SymbolStr::Custom(other.name().to_owned())),
            Symbol::Pfunc(pfunc) => Self(_SymbolStr::Custom(pfunc.name().to_owned())),
            Symbol::Constructor(constr) => Self(_SymbolStr::Custom(constr.name().to_owned())),
        }
    }
}

impl core::ops::Deref for SymbolStr {
    type Target = str;

    fn deref(&self) -> &Self::Target {
        self.0.deref()
    }
}
