use super::{_SymbolStr, TypeSymbolIndex, Vocabulary};
use crate::ast::Span;
use crate::fodot::error::{
    ParseBaseTypeError, ParseBoolError, ParseIntError, ParseSymbolError, VocabMismatchError,
};
use crate::fodot::fmt::{
    self, BOOL_ASCII, BOOL_UNI, FALSE, Fmt, FodotDisplay, FodotOptions, FormatOptions, INT_ASCII,
    INT_UNI, REAL_ASCII, REAL_UNI, TRUE, simple_fodot_display,
};
use crate::fodot::{Metadata, MetadataIm, TryFromCtx, display_as_debug};
use comp_core::ParseRealError;
use comp_core::vocabulary::BaseType as CCBaseType;
use itertools::Either;
use sli_collections::rc::{PtrRepr, Rc, RcA};
use std::error::Error;
use std::hash::Hash;
use std::ops::Deref;
use std::{borrow::Borrow, fmt::Display, str::FromStr};

pub use comp_core::Int;

pub use comp_core::Real;

/// Parses a boolean value from a [str].
///
/// A boolean value is true if it corresponds to [TRUE] or false if it corresponds to [FALSE].
pub fn parse_bool_value(value: &str) -> Result<bool, ParseBoolError> {
    match value {
        TRUE => Ok(true),
        FALSE => Ok(false),
        _ => Err(ParseBoolError),
    }
}

pub fn parse_bool_value_or_string<T: AsRef<str>>(value: T) -> Either<bool, T> {
    parse_bool_value(value.as_ref())
        .map(|f| Either::Left(f))
        .unwrap_or_else(|_| Either::Right(value))
}

/// Parses an [Int] value from a [str].
pub fn parse_int_value(value: &str) -> Result<Int, ParseIntError> {
    Int::from_str(value).map_err(ParseIntError)
}

/// Parses a [Real] value from a [str].
///
/// Only parses decimal numbers, not decimal fractions.
pub fn parse_real_value(value: &str) -> Result<Real, ParseRealError> {
    Real::from_str(value)
}

#[non_exhaustive]
#[derive(Debug, Clone)]
pub struct ParsePrimitiveTypeError {}

impl Display for ParsePrimitiveTypeError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "Provided value is not a primitive type.")
    }
}

impl Error for ParsePrimitiveTypeError {}

/// Parses a [PrimitiveType] (builtin) type.
///
/// - [BOOL_ASCII] and [BOOL_UNI] for [PrimitiveType::Bool].
/// - [INT_ASCII] and [INT_UNI] for [PrimitiveType::Int].
/// - [REAL_ASCII] and [REAL_UNI] for [PrimitiveType::Real].
pub fn parse_primitive_type(value: &str) -> Result<PrimitiveType, ParsePrimitiveTypeError> {
    match value {
        BOOL_ASCII | BOOL_UNI => Ok(PrimitiveType::Bool),
        INT_ASCII | INT_UNI => Ok(PrimitiveType::Int),
        REAL_ASCII | REAL_UNI => Ok(PrimitiveType::Real),
        _ => Err(ParsePrimitiveTypeError {}),
    }
}

/// Represents a primitive (builtin) type.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum PrimitiveType {
    Bool,
    Int,
    Real,
}

impl FodotOptions for PrimitiveType {
    type Options<'a> = FormatOptions;
}

impl FodotDisplay for PrimitiveType {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        match fmt.value {
            Self::Bool => fmt.options.write_bool_type(f),
            Self::Int => fmt.options.write_int_type(f),
            Self::Real => fmt.options.write_real_type(f),
        }
    }
}

impl FromStr for PrimitiveType {
    type Err = ParsePrimitiveTypeError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        parse_primitive_type(s)
    }
}

/// Represents all subtype-able types.
#[non_exhaustive]
#[derive(Debug, Copy, Clone, Eq, PartialEq)]
pub enum BaseType {
    Int,
    Real,
    Str,
}

impl FromStr for BaseType {
    type Err = ParseBaseTypeError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s {
            INT_ASCII | INT_UNI => Ok(Self::Int),
            REAL_ASCII | REAL_UNI => Ok(Self::Real),
            _ => Err(ParseBaseTypeError),
        }
    }
}

impl From<CCBaseType> for BaseType {
    fn from(value: CCBaseType) -> Self {
        match value {
            CCBaseType::Int => BaseType::Int,
            CCBaseType::Real => BaseType::Real,
            CCBaseType::Str => BaseType::Str,
        }
    }
}

impl From<BaseType> for CCBaseType {
    fn from(value: BaseType) -> Self {
        match value {
            BaseType::Int => CCBaseType::Int,
            BaseType::Real => CCBaseType::Real,
            BaseType::Str => CCBaseType::Str,
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub(crate) enum _Type {
    Bool,
    Int,
    Real,
    IntType(TypeSymbolIndex),
    RealType(TypeSymbolIndex),
    StrType(TypeSymbolIndex),
}

impl _Type {
    pub(crate) fn wrap<T: PtrRepr<Vocabulary>>(self, vocab: T) -> Type<T> {
        match self {
            Self::Bool => Type::Bool,
            Self::Int => Type::Int,
            Self::Real => Type::Real,
            Self::IntType(id) => Type::IntType(IntType(id, vocab)),
            Self::RealType(id) => Type::RealType(RealType(id, vocab)),
            Self::StrType(id) => Type::StrType(StrType(id, vocab)),
        }
    }
}

impl From<PrimitiveType> for _Type {
    fn from(value: PrimitiveType) -> Self {
        match value {
            PrimitiveType::Bool => Self::Bool,
            PrimitiveType::Int => Self::Int,
            PrimitiveType::Real => Self::Real,
        }
    }
}

impl<'a, T: PtrRepr<Vocabulary>> From<&'a Type<T>> for _Type {
    fn from(value: &'a Type<T>) -> Self {
        match value {
            Type::Bool => Self::Bool,
            Type::Int => Self::Int,
            Type::Real => Self::Real,
            Type::IntType(value) => Self::IntType(value.0),
            Type::RealType(value) => Self::RealType(value.0),
            Type::StrType(value) => Self::StrType(value.0),
        }
    }
}

impl<T: PtrRepr<Vocabulary>> From<Type<T>> for _Type {
    fn from(value: Type<T>) -> Self {
        Self::from(&value)
    }
}

#[derive(Clone, Copy, PartialEq, Eq)]
pub(crate) enum _CustomType {
    IntType(TypeSymbolIndex),
    RealType(TypeSymbolIndex),
    String(TypeSymbolIndex),
}

impl _CustomType {
    pub(crate) fn wrap<T: PtrRepr<Vocabulary>>(self, vocab: T) -> CustomType<T> {
        match self {
            Self::IntType(id) => CustomType::Int(IntType(id, vocab)),
            Self::RealType(id) => CustomType::Real(RealType(id, vocab)),
            Self::String(id) => CustomType::Str(StrType(id, vocab)),
        }
    }
}

impl From<_CustomType> for _Type {
    fn from(value: _CustomType) -> Self {
        match value {
            _CustomType::IntType(id) => Self::IntType(id),
            _CustomType::RealType(id) => Self::RealType(id),
            _CustomType::String(id) => Self::StrType(id),
        }
    }
}

/// Represents an FO(·) type.
///
/// The most useful versions of this struct are [TypeRef] and [TypeRc].
#[derive(Clone, Copy)]
pub enum Type<T: PtrRepr<Vocabulary>> {
    Bool,
    Int,
    Real,
    IntType(IntType<T>),
    RealType(RealType<T>),
    StrType(StrType<T>),
}

impl<T: PtrRepr<Vocabulary>> PartialEq for Type<T> {
    fn eq(&self, other: &Self) -> bool {
        match (self, other) {
            (Self::Bool, Self::Bool) => true,
            (Self::Int, Self::Int) => true,
            (Self::Real, Self::Real) => true,
            (Self::IntType(value1), Self::IntType(value2)) if value1 == value2 => true,
            (Self::RealType(value1), Self::RealType(value2)) if value1 == value2 => true,
            (Self::StrType(value1), Self::StrType(value2)) if value1 == value2 => true,
            _ => false,
        }
    }
}

impl<T: PtrRepr<Vocabulary>, R: PtrRepr<Vocabulary>> PartialEq<CustomType<R>> for Type<T> {
    fn eq(&self, other: &CustomType<R>) -> bool {
        match (self, other) {
            (Self::IntType(value1), CustomType::Int(value2)) if value1 == value2 => true,
            (Self::RealType(value1), CustomType::Real(value2)) if value1 == value2 => true,
            (Self::StrType(value1), CustomType::Str(value2)) if value1 == value2 => true,
            _ => false,
        }
    }
}

impl<T: PtrRepr<Vocabulary>> Hash for Type<T> {
    fn hash<H: std::hash::Hasher>(&self, state: &mut H) {
        match self {
            Self::Bool => (1 as u32).hash(state),
            Self::Int => (2 as u32).hash(state),
            Self::Real => (3 as u32).hash(state),
            Self::IntType(value) => {
                (4 as u32).hash(state);
                value.hash(state)
            }
            Self::RealType(value) => {
                (4 as u32).hash(state);
                value.hash(state)
            }
            Self::StrType(value) => {
                (4 as u32).hash(state);
                value.hash(state)
            }
        }
    }
}

impl<T: PtrRepr<Vocabulary>> Eq for Type<T> {}

impl<T: PtrRepr<Vocabulary>> TryFromCtx<&str> for Type<T> {
    type Ctx = T::Ctx;
    type Error = ParseSymbolError;

    fn try_from_ctx(value: &str, ctx: Self::Ctx) -> Result<Self, Self::Error> {
        ctx.deref()._parse_type(value).map(|f| f.wrap(ctx.into()))
    }
}

impl<T: PtrRepr<Vocabulary>> TryFromCtx<&&str> for Type<T> {
    type Ctx = T::Ctx;
    type Error = ParseSymbolError;

    fn try_from_ctx(value: &&str, ctx: Self::Ctx) -> Result<Self, Self::Error> {
        Self::try_from_ctx(*value, ctx)
    }
}

impl<T: PtrRepr<Vocabulary>> TryFromCtx<Type<T>> for Type<T> {
    type Ctx = T::Ctx;
    type Error = VocabMismatchError;

    fn try_from_ctx(value: Type<T>, ctx: Self::Ctx) -> Result<Self, Self::Error> {
        if value
            .vocab()
            .map(|f| f.exact_eq(ctx.deref()))
            .unwrap_or(true)
        {
            Ok(value)
        } else {
            Err(VocabMismatchError)
        }
    }
}

impl<'a, T: PtrRepr<Vocabulary> + Clone> TryFromCtx<&'a Type<T>> for Type<T> {
    type Ctx = T::Ctx;
    type Error = VocabMismatchError;

    fn try_from_ctx(value: &'a Type<T>, ctx: Self::Ctx) -> Result<Self, Self::Error> {
        if value
            .vocab()
            .map(|f| f.exact_eq(ctx.deref()))
            .unwrap_or(true)
        {
            Ok(value.clone())
        } else {
            Err(VocabMismatchError)
        }
    }
}

/// A referencing type alias for [Type].
pub type TypeRef<'a> = Type<&'a Vocabulary>;
/// An owning (via [Rc]) type alias for [Type].
pub type TypeRc = Type<RcA<Vocabulary>>;

impl<T: PtrRepr<Vocabulary>> From<CustomType<T>> for Type<T> {
    fn from(value: CustomType<T>) -> Self {
        match value {
            CustomType::Int(value) => Type::IntType(value),
            CustomType::Real(value) => Type::RealType(value),
            CustomType::Str(value) => Type::StrType(value),
        }
    }
}

impl<'a> From<&'a TypeRc> for TypeRef<'a> {
    fn from(value: &'a TypeRc) -> Self {
        match value {
            Type::Bool => Type::Bool,
            Type::Int => Type::Int,
            Type::Real => Type::Real,
            Type::IntType(value) => Type::IntType(value.into()),
            Type::RealType(value) => Type::RealType(value.into()),
            Type::StrType(value) => Type::StrType(value.into()),
        }
    }
}

impl<T: PtrRepr<Vocabulary>> From<IntType<T>> for Type<T> {
    fn from(value: IntType<T>) -> Self {
        Self::IntType(value)
    }
}

impl<T: PtrRepr<Vocabulary>> From<RealType<T>> for Type<T> {
    fn from(value: RealType<T>) -> Self {
        Self::RealType(value)
    }
}

impl<T: PtrRepr<Vocabulary>> From<StrType<T>> for Type<T> {
    fn from(value: StrType<T>) -> Self {
        Self::StrType(value)
    }
}

impl<T: PtrRepr<Vocabulary>> FodotOptions for Type<T> {
    type Options<'a> = FormatOptions;
}

impl<T: PtrRepr<Vocabulary>> FodotDisplay for Type<T> {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        match fmt.value {
            Type::Bool => fmt.options.write_bool_type(f),
            Type::Int => fmt.options.write_int_type(f),
            Type::Real => fmt.options.write_real_type(f),
            Type::IntType(int) => write!(f, "{}", fmt.with_format_opts(int)),
            Type::RealType(real) => write!(f, "{}", fmt.with_format_opts(real)),
            Type::StrType(string) => write!(f, "{}", fmt.with_format_opts(string)),
        }
    }
}

impl<T: PtrRepr<Vocabulary>> Display for Type<T> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

display_as_debug!(Type<T>, gen: (T), where: (T: PtrRepr<Vocabulary>));

impl<T: PtrRepr<Vocabulary>> Type<T> {
    pub fn is_subtype<F: PtrRepr<Vocabulary>>(&self, other: &Type<F>) -> bool {
        match (self, other) {
            (Type::Bool, Type::Bool) => true,
            (Type::Int | Type::IntType(_), Type::Int) => true,
            (Type::Real | Type::RealType(_) | Type::Int | Type::IntType(_), Type::Real) => true,
            (Type::IntType(type1), Type::IntType(type2)) if type1 == type2 => true,
            (Type::RealType(type1), Type::RealType(type2)) if type1 == type2 => true,
            (Type::StrType(type1), Type::StrType(type2)) if type1 == type2 => true,
            _ => false,
        }
    }

    pub fn into_root_type(self) -> RootType<T> {
        match self {
            Self::Bool => RootType::Bool,
            Self::Int | Self::IntType(_) | Self::RealType(_) | Self::Real => RootType::Real,
            Self::StrType(str_type) => RootType::StrType(str_type),
        }
    }

    /// Returns the super type of the type if it has one.
    pub fn super_type(&self) -> Option<BaseType> {
        match self {
            Self::Bool => None,
            Self::Int => Some(BaseType::Int),
            Self::Real => Some(BaseType::Real),
            Self::IntType(_) => Some(BaseType::Int),
            Self::RealType(_) => Some(BaseType::Real),
            Self::StrType(_) => Some(BaseType::Str),
        }
    }

    /// Returns the corresponding [Vocabulary] if there is one.
    pub fn vocab(&self) -> Option<&Vocabulary> {
        self.vocab_repr().map(|f| f.deref())
    }

    pub(crate) fn wrap<F: PtrRepr<Vocabulary>>(self, new_vocab: F) -> Type<F> {
        match self {
            Type::Bool => Type::Bool,
            Type::Int => Type::Int,
            Type::Real => Type::Real,
            Type::IntType(value) => Type::IntType(value.wrap(new_vocab)),
            Type::RealType(value) => Type::RealType(value.wrap(new_vocab)),
            Type::StrType(value) => Type::StrType(value.wrap(new_vocab)),
        }
    }

    /// Returns the user given or ascii name of the type.
    pub fn name(&self) -> &str {
        match self {
            Type::Bool => BOOL_ASCII,
            Type::Int => INT_ASCII,
            Type::Real => REAL_ASCII,
            Type::IntType(value) => value.name(),
            Type::RealType(value) => value.name(),
            Type::StrType(value) => value.name(),
        }
    }

    pub(crate) fn vocab_repr(&self) -> Option<&T> {
        match self {
            Self::Bool | Self::Int | Self::Real => None,
            Self::IntType(value) => Some(&value.1),
            Self::RealType(value) => Some(&value.1),
            Self::StrType(value) => Some(&value.1),
        }
    }

    pub fn is_bool(&self) -> bool {
        match self {
            Self::Bool => true,
            _ => false,
        }
    }
}

impl TypeRc {
    pub fn vocab_rc(&self) -> Option<&RcA<Vocabulary>> {
        self.vocab_repr()
    }

    pub fn as_ref(&self) -> TypeRef {
        match self {
            Self::Bool => Type::Bool,
            Self::Int => Type::Int,
            Self::Real => Type::Real,
            Self::IntType(int_type) => Type::IntType(int_type.as_ref()),
            Self::RealType(real_type) => Type::RealType(real_type.as_ref()),
            Self::StrType(str_type) => Type::StrType(str_type.as_ref()),
        }
    }
}

impl FodotOptions for BaseType {
    type Options<'a> = FormatOptions;
}

impl FodotDisplay for BaseType {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        match fmt.value {
            BaseType::Real => fmt.options.write_real_type(f),
            BaseType::Int => fmt.options.write_int_type(f),
            BaseType::Str => f.write_str("str"),
        }
    }
}

/// Represents an FO(·) root type.
///
/// The most useful versions of this struct are [TypeRef] and [TypeRc].
#[non_exhaustive]
#[derive(Clone, Copy)]
pub enum RootType<T: PtrRepr<Vocabulary>> {
    Bool,
    Real,
    StrType(StrType<T>),
}

impl<T: PtrRepr<Vocabulary>> PartialEq for RootType<T> {
    fn eq(&self, other: &Self) -> bool {
        match (self, other) {
            (Self::Bool, Self::Bool) => true,
            (Self::Real, Self::Real) => true,
            (Self::StrType(left), Self::StrType(right)) if left == right => true,
            _ => false,
        }
    }
}

impl<T: PtrRepr<Vocabulary>> Eq for RootType<T> {}

impl<T: PtrRepr<Vocabulary>> From<RootType<T>> for TypeStr {
    fn from(value: RootType<T>) -> Self {
        match value {
            RootType::Bool => TypeStr::Bool,
            RootType::Real => TypeStr::Real,
            RootType::StrType(str_type) => TypeStr::custom(str_type.name().to_owned()),
        }
    }
}

impl<T: PtrRepr<Vocabulary>> From<RootType<T>> for Type<T> {
    fn from(value: RootType<T>) -> Self {
        match value {
            RootType::Bool => Self::Bool,
            RootType::Real => Self::Real,
            RootType::StrType(value) => Self::StrType(value),
        }
    }
}

pub type RootTypeRef<'a> = RootType<&'a Vocabulary>;
pub type RootTypeRc = RootType<RcA<Vocabulary>>;

#[non_exhaustive]
#[derive(Clone, Debug)]
pub struct NotACustomType {}

impl Display for NotACustomType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "The provided value was not a custom type")
    }
}

simple_fodot_display!(NotACustomType);

impl Error for NotACustomType {}

impl<'a> TryFrom<TypeRef<'a>> for CustomTypeRef<'a> {
    type Error = NotACustomType;

    fn try_from(value: TypeRef<'a>) -> Result<Self, Self::Error> {
        match value {
            TypeRef::Bool | TypeRef::Int | TypeRef::Real => Err(NotACustomType {}),
            TypeRef::IntType(decl) => Ok(decl.into()),
            TypeRef::RealType(decl) => Ok(decl.into()),
            TypeRef::StrType(decl) => Ok(decl.into()),
        }
    }
}

/// Represent only custom types defined in a vocabulary.
///
/// The most useful versions of this struct is [CustomTypeRef].
///
/// See also [Type].
#[derive(Clone, Copy)]
pub enum CustomType<T: PtrRepr<Vocabulary>> {
    Int(IntType<T>),
    Real(RealType<T>),
    Str(StrType<T>),
}

/// A referencing type alias for [CustomType].
pub type CustomTypeRef<'a> = CustomType<&'a Vocabulary>;
pub type CustomTypeRc = CustomType<RcA<Vocabulary>>;

impl<T: PtrRepr<Vocabulary>> From<IntType<T>> for CustomType<T> {
    fn from(value: IntType<T>) -> Self {
        Self::Int(value)
    }
}

impl<T: PtrRepr<Vocabulary>> From<RealType<T>> for CustomType<T> {
    fn from(value: RealType<T>) -> Self {
        Self::Real(value)
    }
}

impl<T: PtrRepr<Vocabulary>> From<StrType<T>> for CustomType<T> {
    fn from(value: StrType<T>) -> Self {
        Self::Str(value)
    }
}

impl<T: PtrRepr<Vocabulary>> CustomType<T> {
    pub(crate) fn type_id(&self) -> TypeSymbolIndex {
        match self {
            Self::Int(value) => value.0,
            Self::Real(value) => value.0,
            Self::Str(value) => value.0,
        }
    }

    pub(crate) fn vocab(&self) -> &Vocabulary {
        match self {
            Self::Int(value) => value.1.borrow(),
            Self::Real(value) => value.1.borrow(),
            Self::Str(value) => value.1.borrow(),
        }
    }

    pub fn name(&self) -> &str {
        match self {
            Self::Int(value) => value.name(),
            Self::Real(value) => value.name(),
            Self::Str(value) => value.name(),
        }
    }

    pub fn name_rc(&self) -> Rc<str> {
        match self {
            Self::Int(value) => value.name_rc(),
            Self::Real(value) => value.name_rc(),
            Self::Str(value) => value.name_rc(),
        }
    }

    pub fn super_type(&self) -> BaseType {
        match self {
            Self::Int(_) => BaseType::Int,
            Self::Real(_) => BaseType::Real,
            Self::Str(_) => BaseType::Str,
        }
    }
}

impl<T: PtrRepr<Vocabulary>> FodotOptions for CustomType<T> {
    type Options<'a> = FormatOptions;
}

impl<T: PtrRepr<Vocabulary>> FodotDisplay for CustomType<T> {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        f.write_str(fmt.value.name())
    }
}

impl<T: PtrRepr<Vocabulary>> Display for CustomType<T> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

display_as_debug!(CustomType<T>, gen: (T), where: (T: PtrRepr<Vocabulary>));

impl CustomTypeRc {
    pub fn as_ref(&self) -> CustomTypeRef {
        match self {
            Self::Int(value) => CustomType::Int(value.as_ref()),
            Self::Real(value) => CustomType::Real(value.as_ref()),
            Self::Str(value) => CustomType::Str(value.as_ref()),
        }
    }
}

impl<T: PtrRepr<Vocabulary>> MetadataIm for CustomType<T> {
    type Metadata = TypeMetadata;
    fn metadata(&self) -> Option<&Self::Metadata> {
        match self {
            Self::Int(value) => value.metadata(),
            Self::Real(value) => value.metadata(),
            Self::Str(value) => value.metadata(),
        }
    }
}

/// Represent a custom type that is a subtype of [BaseType::Int].
///
/// The most useful versions of this struct are [IntTypeRef] and [IntTypeRc].
///
/// See also [Type].
#[derive(Clone, Copy)]
pub struct IntType<T: PtrRepr<Vocabulary>>(pub(crate) TypeSymbolIndex, pub(crate) T);

// TODO
impl<T: PtrRepr<Vocabulary>> Hash for IntType<T> {
    fn hash<H: std::hash::Hasher>(&self, state: &mut H) {
        self.0.hash(state);
        core::ptr::hash(self.1.borrow(), state);
    }
}

impl<F, T> PartialEq<IntType<F>> for IntType<T>
where
    F: PtrRepr<Vocabulary>,
    T: PtrRepr<Vocabulary>,
{
    fn eq(&self, other: &IntType<F>) -> bool {
        self.1.deref().exact_eq(other.1.deref()) && self.0 == other.0
    }
}

impl<T: PtrRepr<Vocabulary>> Eq for IntType<T> {}

impl<T: PtrRepr<Vocabulary>> FodotOptions for IntType<T> {
    type Options<'a> = FormatOptions;
}

impl<T: PtrRepr<Vocabulary>> FodotDisplay for IntType<T> {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        f.write_str(fmt.value.name())
    }
}

impl<T: PtrRepr<Vocabulary>> Display for IntType<T> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

display_as_debug!(IntType<T>, gen: (T), where: (T: PtrRepr<Vocabulary>));

impl<T: PtrRepr<Vocabulary>> MetadataIm for IntType<T> {
    type Metadata = TypeMetadata;
    fn metadata(&self) -> Option<&Self::Metadata> {
        self.vocab()._type_metadata(self.0)
    }
}

impl<T: PtrRepr<Vocabulary>> IntType<T> {
    pub fn name(&self) -> &str {
        self.1.borrow().get_name(self.0)
    }

    pub fn name_rc(&self) -> Rc<str> {
        self.1.borrow().get_name_rc(self.0)
    }

    pub(crate) fn wrap<F: PtrRepr<Vocabulary>>(self, new_vocab: F) -> IntType<F> {
        IntType(self.0, new_vocab)
    }

    pub fn vocab(&self) -> &Vocabulary {
        self.1.borrow()
    }
}

/// A referencing type alias for [IntType].
pub type IntTypeRef<'a> = IntType<&'a Vocabulary>;
/// An owning (via [Rc]) type alias for [IntType].
pub type IntTypeRc = IntType<RcA<Vocabulary>>;

impl<'a> IntTypeRef<'a> {
    pub fn vocab_ref(&self) -> &'a Vocabulary {
        self.1
    }
}

impl IntTypeRc {
    pub fn as_ref(&self) -> IntTypeRef {
        IntType(self.0, self.1.borrow())
    }
}

impl<'a> From<&'a IntTypeRc> for IntTypeRef<'a> {
    fn from(value: &'a IntTypeRc) -> Self {
        Self(value.0, &value.1)
    }
}

/// Represent a custom type that is a subtype of [BaseType::Real].
///
/// The most useful versions of this struct are [RealTypeRef] and [RealTypeRc].
///
/// See also [Type].
#[derive(Clone, Copy)]
pub struct RealType<T: PtrRepr<Vocabulary>>(pub(crate) TypeSymbolIndex, pub(crate) T);

// TODO
impl<T: PtrRepr<Vocabulary>> Hash for RealType<T> {
    fn hash<H: std::hash::Hasher>(&self, state: &mut H) {
        self.0.hash(state);
        core::ptr::hash(self.1.borrow(), state);
    }
}

impl<F, T> PartialEq<RealType<F>> for RealType<T>
where
    F: PtrRepr<Vocabulary>,
    T: PtrRepr<Vocabulary>,
{
    fn eq(&self, other: &RealType<F>) -> bool {
        core::ptr::eq(self.1.deref(), other.1.deref()) && self.0 == other.0
    }
}

impl<T: PtrRepr<Vocabulary>> Eq for RealType<T> {}

impl<T: PtrRepr<Vocabulary>> FodotOptions for RealType<T> {
    type Options<'a> = FormatOptions;
}

impl<T: PtrRepr<Vocabulary>> FodotDisplay for RealType<T> {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        f.write_str(fmt.value.name())
    }
}

impl<T: PtrRepr<Vocabulary>> Display for RealType<T> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

display_as_debug!(RealType<T>, gen: (T), where: (T: PtrRepr<Vocabulary>));

impl<T: PtrRepr<Vocabulary>> MetadataIm for RealType<T> {
    type Metadata = TypeMetadata;
    fn metadata(&self) -> Option<&Self::Metadata> {
        self.vocab()._type_metadata(self.0)
    }
}

impl<T: PtrRepr<Vocabulary>> RealType<T> {
    pub fn name(&self) -> &str {
        self.1.borrow().get_name(self.0)
    }

    pub fn name_rc(&self) -> Rc<str> {
        self.1.borrow().get_name_rc(self.0)
    }

    pub(crate) fn wrap<F: PtrRepr<Vocabulary>>(self, new_vocab: F) -> RealType<F> {
        RealType(self.0, new_vocab)
    }

    pub fn vocab(&self) -> &Vocabulary {
        self.1.borrow()
    }
}

/// A referencing type alias for [RealType].
pub type RealTypeRef<'a> = RealType<&'a Vocabulary>;
/// An owning (via [Rc]) type alias for [RealType].
pub type RealTypeRc = RealType<RcA<Vocabulary>>;

impl<'a> RealTypeRef<'a> {
    pub fn vocab_ref(&self) -> &'a Vocabulary {
        self.1
    }
}

impl RealTypeRc {
    pub fn as_ref(&self) -> RealTypeRef {
        RealType(self.0, self.1.borrow())
    }
}

impl<'a> From<&'a RealTypeRc> for RealTypeRef<'a> {
    fn from(value: &'a RealTypeRc) -> Self {
        Self(value.0, &value.1)
    }
}

/// Represent a custom type that is a subtype of [BaseType::Str].
///
/// The most useful versions of this struct are [RealTypeRef] and [RealTypeRc].
///
/// See also [Type].
#[derive(Clone, Copy)]
pub struct StrType<T: PtrRepr<Vocabulary>>(pub(crate) TypeSymbolIndex, pub(crate) T);

// TODO
impl<T: PtrRepr<Vocabulary>> Hash for StrType<T> {
    fn hash<H: std::hash::Hasher>(&self, state: &mut H) {
        self.0.hash(state);
        core::ptr::hash(self.1.borrow(), state);
    }
}

impl<F, T> PartialEq<StrType<F>> for StrType<T>
where
    F: PtrRepr<Vocabulary>,
    T: PtrRepr<Vocabulary>,
{
    fn eq(&self, other: &StrType<F>) -> bool {
        core::ptr::eq(self.1.deref(), other.1.deref()) && self.0 == other.0
    }
}

impl<T: PtrRepr<Vocabulary>> Eq for StrType<T> {}

impl<T: PtrRepr<Vocabulary>> FodotOptions for StrType<T> {
    type Options<'a> = FormatOptions;
}

impl<T: PtrRepr<Vocabulary>> FodotDisplay for StrType<T> {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        f.write_str(fmt.value.name())
    }
}

impl<T: PtrRepr<Vocabulary>> Display for StrType<T> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

display_as_debug!(StrType<T>, gen: (T), where: (T: PtrRepr<Vocabulary>));

impl<T: PtrRepr<Vocabulary>> MetadataIm for StrType<T> {
    type Metadata = TypeMetadata;
    fn metadata(&self) -> Option<&Self::Metadata> {
        self.vocab()._type_metadata(self.0)
    }
}

impl<T: PtrRepr<Vocabulary>> StrType<T> {
    pub fn name(&self) -> &str {
        self.1.borrow().get_name(self.0)
    }

    pub fn name_rc(&self) -> Rc<str> {
        self.1.borrow().get_name_rc(self.0)
    }

    pub(crate) fn wrap<F: PtrRepr<Vocabulary>>(self, new_vocab: F) -> StrType<F> {
        StrType(self.0, new_vocab)
    }

    pub fn vocab(&self) -> &Vocabulary {
        self.1.borrow()
    }
}

/// A referencing type alias for [StrType].
pub type StrTypeRef<'a> = StrType<&'a Vocabulary>;
/// An owning (via [Rc]) type alias for [StrType].
pub type StrTypeRc = StrType<RcA<Vocabulary>>;

impl<'a> StrTypeRef<'a> {
    pub fn vocab_ref(&self) -> &'a Vocabulary {
        self.1
    }
}

impl StrTypeRc {
    pub fn as_ref(&self) -> StrTypeRef {
        StrType(self.0, self.1.borrow())
    }
}

impl<'a> From<&'a StrTypeRc> for StrTypeRef<'a> {
    fn from(value: &'a StrTypeRc) -> Self {
        Self(value.0, &value.1)
    }
}

impl<T: PtrRepr<Vocabulary>> From<PrimitiveType> for Type<T> {
    fn from(value: PrimitiveType) -> Self {
        match value {
            PrimitiveType::Bool => Self::Bool,
            PrimitiveType::Int => Self::Int,
            PrimitiveType::Real => Self::Real,
        }
    }
}

#[derive(Debug, Clone, Default, Hash, PartialEq, Eq)]
pub struct TypeMetadata {
    metadata: Metadata,
    name_span: Option<Span>,
    superset_span: Option<Span>,
}

impl AsRef<Metadata> for TypeMetadata {
    fn as_ref(&self) -> &Metadata {
        &self.metadata
    }
}

impl AsMut<Metadata> for TypeMetadata {
    fn as_mut(&mut self) -> &mut Metadata {
        &mut self.metadata
    }
}

impl Deref for TypeMetadata {
    type Target = Metadata;
    fn deref(&self) -> &Self::Target {
        &self.metadata
    }
}

impl TypeMetadata {
    pub fn set_metadata(&mut self, metadata: Metadata) -> &mut Self {
        self.metadata = metadata;
        self
    }

    pub fn with_metadata(mut self, metadata: Metadata) -> Self {
        self.set_metadata(metadata);
        self
    }

    pub fn name_span(&self) -> Option<&Span> {
        self.name_span.as_ref()
    }

    pub fn set_name_span(&mut self, name_span: Span) -> &mut Self {
        self.name_span = Some(name_span);
        self
    }

    pub fn with_name_span(mut self, name_span: Span) -> Self {
        self.set_name_span(name_span);
        self
    }

    pub fn superset_span(&self) -> Option<&Span> {
        self.superset_span.as_ref()
    }

    pub fn set_superset_span(&mut self, superset_span: Span) -> &mut Self {
        self.superset_span = Some(superset_span);
        self
    }

    pub fn with_superset_span(mut self, superset_span: Span) -> Self {
        self.set_superset_span(superset_span);
        self
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct TypeStr(_SymbolStr);

impl FodotOptions for TypeStr {
    type Options<'a> = FormatOptions;
}

impl FodotDisplay for TypeStr {
    fn fmt(
        fmt: fmt::Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        write!(f, "{}", fmt.with_opts(&fmt.value.0))
    }
}

impl Display for TypeStr {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

impl From<&str> for TypeStr {
    fn from(value: &str) -> Self {
        if let Ok(prim) = parse_primitive_type(value) {
            return prim.into();
        }
        TypeStr(value.into())
    }
}

impl<T: PtrRepr<Vocabulary>> From<Type<T>> for TypeStr {
    fn from(value: Type<T>) -> Self {
        match value {
            Type::Bool => Self(_SymbolStr::Bool),
            Type::Int => Self(_SymbolStr::Int),
            Type::Real => Self(_SymbolStr::Real),
            other => Self(other.name().into()),
        }
    }
}

impl From<PrimitiveType> for TypeStr {
    fn from(value: PrimitiveType) -> Self {
        match value {
            PrimitiveType::Bool => Self(_SymbolStr::Bool),
            PrimitiveType::Int => Self(_SymbolStr::Int),
            PrimitiveType::Real => Self(_SymbolStr::Real),
        }
    }
}

#[allow(non_upper_case_globals)]
impl TypeStr {
    pub const Bool: Self = TypeStr(_SymbolStr::Bool);
    pub const Int: Self = TypeStr(_SymbolStr::Int);
    pub const Real: Self = TypeStr(_SymbolStr::Real);

    pub fn custom(name: String) -> Self {
        TypeStr(_SymbolStr::Custom(name))
    }
}

/// contains all methods and functions needed for boomerang interface with comp_core
pub(crate) mod translation_layer {
    use super::*;
    use comp_core::{
        IndexRepr,
        vocabulary::{Type as CCType, TypeIndex},
    };

    impl<T: PtrRepr<Vocabulary>> Type<T> {
        pub(crate) fn from_cc(cc_type: &CCType, decls: T) -> Self {
            match cc_type {
                CCType::Bool => Self::Bool,
                CCType::Int => Self::Int,
                CCType::Real => Self::Real,
                CCType::IntType(id) => {
                    Self::IntType(IntType(Type::custom_type_id_from_cc(*id, &decls), decls))
                }
                CCType::RealType(id) => {
                    Self::RealType(RealType(Type::custom_type_id_from_cc(*id, &decls), decls))
                }
                CCType::Str(id) => {
                    // Do a check what kind of custom type
                    Self::StrType(StrType(Type::custom_type_id_from_cc(*id, &decls), decls))
                }
            }
        }

        pub(crate) fn custom_type_id_from_cc(index: TypeIndex, _vocab: &T) -> TypeSymbolIndex {
            TypeSymbolIndex::from(IndexRepr::from(index))
        }
    }

    impl<T: PtrRepr<Vocabulary>> Type<T> {
        pub(crate) fn to_cc(self) -> CCType {
            match self {
                Self::Bool => CCType::Bool,
                Self::Int => CCType::Int,
                Self::Real => CCType::Real,
                Self::IntType(id) => CCType::IntType(id.to_cc()),
                Self::RealType(id) => CCType::RealType(id.to_cc()),
                Self::StrType(id) => CCType::Str(id.to_cc()),
            }
        }

        pub(crate) fn custom_type_id_to_cc(
            index: TypeSymbolIndex,
            _vocab: &Vocabulary,
        ) -> TypeIndex {
            TypeIndex::from(IndexRepr::from(index))
        }
    }

    impl<T: PtrRepr<Vocabulary>> IntType<T> {
        pub(crate) fn to_cc(&self) -> TypeIndex {
            self.1.borrow().type_decl_to_cc(self.0)
        }
    }

    impl<T: PtrRepr<Vocabulary>> RealType<T> {
        pub(crate) fn to_cc(&self) -> TypeIndex {
            self.1.borrow().type_decl_to_cc(self.0)
        }
    }

    impl<T: PtrRepr<Vocabulary>> StrType<T> {
        pub(crate) fn to_cc(&self) -> TypeIndex {
            self.1.borrow().type_decl_to_cc(self.0)
        }
    }

    impl<'a> CustomTypeRef<'a> {
        pub(crate) fn from_cc(type_index: TypeIndex, decls: &'a Vocabulary) -> Self {
            _CustomType::from_cc(type_index, decls).wrap(decls)
        }
    }

    impl _CustomType {
        pub(crate) fn from_cc(type_index: TypeIndex, vocab: &Vocabulary) -> Self {
            let type_decl_index = TypeRef::custom_type_id_from_cc(type_index, &vocab);
            vocab._get_type_id(type_decl_index)
        }

        // NOTE: consider removing this int future
        #[allow(unused)]
        pub(crate) fn to_cc(self, vocab: &Vocabulary) -> CCType {
            match self {
                Self::IntType(id) => CCType::IntType(TypeRef::custom_type_id_to_cc(id, vocab)),
                Self::RealType(id) => CCType::RealType(TypeRef::custom_type_id_to_cc(id, vocab)),
                Self::String(id) => CCType::Str(TypeRef::custom_type_id_to_cc(id, vocab)),
            }
        }
    }

    impl _Type {
        pub(crate) fn to_cc(self, vocab: &Vocabulary) -> CCType {
            match self {
                Self::Bool => CCType::Bool,
                Self::Int => CCType::Int,
                Self::Real => CCType::Real,
                Self::IntType(id) => CCType::IntType(TypeRef::custom_type_id_to_cc(id, vocab)),
                Self::RealType(id) => CCType::RealType(TypeRef::custom_type_id_to_cc(id, vocab)),
                Self::StrType(id) => CCType::Str(TypeRef::custom_type_id_to_cc(id, vocab)),
            }
        }
    }
}
