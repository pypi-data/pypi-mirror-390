//! fodot errors
//!
//! In sli, errors describe exactly everything that could possibly go wrong (expect for broken
//! contracts, which cause a panic).
//! These errors are fully composable, and extendable (in the future).
use super::{
    super::ast::ParseError,
    fmt::{
        self, FALSE, FodotDisplay, FodotOptions, FormatOptions, TRUE, display_fn,
        simple_fodot_display,
    },
    structure::StrTypeElement,
    theory::{Expr, VariableDeclRef},
    vocabulary::{
        BaseType, NotACustomType, PrimitiveType, StrDomain, SymbolStr, SymbolType, TypeStr,
    },
};
use algebraic_errors::algebraic_errors;
use core::fmt::Display;
use itertools::Itertools;
use std::error::Error;

pub mod parse;

/// Creates a wrapper of an error.
macro_rules! singleton_error {
    (
        // attributes of wrapper
        $(#[$($attribute:tt)*])*
        $vis:vis $name:ident,
        // attributes of singular field
        $(#[$($attribute_value:tt)*])*
        $vis_value:vis $value:ident $(,)?
        // a optional identifier, if given the wrapped type will not be boxed.
        $(
            , $not_boxed:ident $(,)?
        )?
    ) => {
        singleton_error! {
            if ($($not_boxed)?) {
                $(
                    #[$($attribute)*]
                )*
                $vis struct $name(
                    $(
                        #[$($attribute_value)*]
                    )*
                    $vis_value $value
                );

                impl $name {
                    pub fn get(&self) -> &$value {
                        &self.0
                    }

                    pub fn take(self) -> $value {
                        self.0
                    }

                    fn _take_alg_type(self) -> $value {
                        self.take()
                    }
                }

                impl FodotDisplay for $name {
                    fn fmt(
                        fmt: fmt::Fmt<&Self, Self::Options<'_>>,
                        f: &mut core::fmt::Formatter<'_>,
                    ) -> std::fmt::Result {
                        write!(f, "{}", fmt.with_opts(&fmt.value.0))
                    }
                }
            } else {
                $(
                    #[$($attribute)*]
                )*
                $vis struct $name(
                    $(
                        #[$($attribute_value)*]
                    )*
                    $vis_value Box<$value>
                );

                impl $name {
                    pub fn get(&self) -> &$value {
                        &self.0
                    }

                    pub fn take(self) -> $value {
                        *self.0
                    }

                    fn _take_alg_type(self) -> $value {
                        self.take()
                    }
                }

                impl FodotDisplay for $name {
                    fn fmt(
                        fmt: fmt::Fmt<&Self, Self::Options<'_>>,
                        f: &mut core::fmt::Formatter<'_>,
                    ) -> std::fmt::Result {
                        write!(f, "{}", fmt.with_opts(fmt.value.0.as_ref()))
                    }
                }
            }
        }

        impl From<$value> for $name {
            fn from(value: $value) -> $name {
                Self(value.into())
            }
        }

        impl FodotOptions for $name {
            type Options<'a> = FormatOptions;
        }

        impl Display for $name {
            fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        impl Error for $name {}
    };
    (if () { $($if:tt)* } else { $($else:tt)* }) => { $($else)* };
    (if ($($something:tt)*) { $($if:tt)* } else { $($else:tt)* }) => { $($if)* };
}

macro_rules! singleton_docs {
    () => {
        "\n\nUse this in a [Result::Err] when returning from a function."
    };
}

/// An error for parsing a boolean value.
#[non_exhaustive]
#[derive(Clone, Debug)]
pub struct ParseBoolError;

impl Error for ParseBoolError {}

impl Display for ParseBoolError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "provided value is not: `{}`, `{}`", TRUE, FALSE)
    }
}

simple_fodot_display!(ParseBoolError);

/// An error for parsing a [Int](crate::fodot::vocabulary::Int) value.
#[derive(Clone, Debug)]
pub struct ParseIntError(pub(crate) core::num::ParseIntError);

impl Error for ParseIntError {}

impl Display for ParseIntError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.0)
    }
}

simple_fodot_display!(ParseIntError);

pub use comp_core::ParseRealError;

simple_fodot_display!(ParseRealError);

/// An error for when some arguments have different
/// [Vocabularies](crate::fodot::vocabulary::Vocabulary).
#[non_exhaustive]
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct VocabMismatchError;

impl Display for VocabMismatchError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "one or more arguments have a mismatching vocabulary")
    }
}

simple_fodot_display!(VocabMismatchError);

impl Error for VocabMismatchError {}

/// An error for when a non existing symbol is requested.
///
/// Use [MissingSymbolError] in [Result::Err].
#[derive(Clone, Debug)]
pub struct MissingSymbol(pub SymbolStr);

impl Error for MissingSymbol {}

impl FodotOptions for MissingSymbol {
    type Options<'a> = FormatOptions;
}

impl FodotDisplay for MissingSymbol {
    fn fmt(
        fmt: fmt::Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        write!(f, "\"{}\" is not a symbol", fmt.with_opts(&fmt.value.0))
    }
}

impl Display for MissingSymbol {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

singleton_error! {
    /// A [MissingSymbol] stored on the heap.
    #[doc = singleton_docs!()]
    #[derive(Clone, Debug)]
    pub MissingSymbolError,
    MissingSymbol,
}

/// An error used when a symbol is being redeclared.
///
/// Use [RedeclarationError] in [Result::Err].
#[derive(Clone, Debug)]
pub struct Redeclaration(pub SymbolStr);

impl Error for Redeclaration {}

impl FodotOptions for Redeclaration {
    type Options<'a> = FormatOptions;
}

impl FodotDisplay for Redeclaration {
    fn fmt(
        fmt: fmt::Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        write!(
            f,
            "redeclaration of symbol \"{}\"",
            fmt.with_opts(&fmt.value.0)
        )
    }
}

impl Display for Redeclaration {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

singleton_error! {
    /// A [Redeclaration] stored on the heap.
    #[doc = singleton_docs!()]
    #[derive(Clone, Debug)]
    pub RedeclarationError,
    Redeclaration,
}

/// An error for when a certain type of symbol is expected but a different type of symbol was found.
///
/// Use [WrongSymbolTypeError] in [Result::Err].
#[derive(Clone, Debug)]
pub struct WrongSymbolType {
    pub found: SymbolType,
    pub expected: SymbolType,
}

impl Error for WrongSymbolType {}

impl Display for WrongSymbolType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "expected a {} found a {}",
            self.expected.sentence_name(),
            self.found.sentence_name(),
        )
    }
}

simple_fodot_display!(WrongSymbolType);
singleton_error! {
    /// A [WrongSymbolTypeError] stored on the heap.
    #[doc = singleton_docs!()]
    #[derive(Clone, Debug)]
    pub WrongSymbolTypeError,
    WrongSymbolType,
}

/// An error for when a certain type was expected but a different type was found.
///
/// Use [TypeMismatchError] in [Result::Err].
#[derive(Clone, Debug)]
pub struct TypeMismatch {
    pub found: TypeStr,
    pub expected: TypeStr,
}

impl Error for TypeMismatch {}

impl FodotOptions for TypeMismatch {
    type Options<'a> = FormatOptions;
}

impl FodotDisplay for TypeMismatch {
    fn fmt(
        fmt: fmt::Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        write!(
            f,
            "expected type \"{}\", found \"{}\"",
            fmt.with_format_opts(&fmt.value.expected),
            fmt.with_format_opts(&fmt.value.found)
        )
    }
}

impl Display for TypeMismatch {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

singleton_error! {
    /// A [TypeMismatch] stored on the heap.
    #[doc = singleton_docs!()]
    #[derive(Clone, Debug)]
    pub TypeMismatchError,
    TypeMismatch,
}

/// An error for when a certain [BaseType] is expected but a different [BaseType] was found.
#[derive(Clone, Debug)]
pub struct BaseTypeMismatchError {
    pub found: BaseType,
    pub expected: BaseType,
}

impl Error for BaseTypeMismatchError {}

impl FodotOptions for BaseTypeMismatchError {
    type Options<'a> = FormatOptions;
}

impl FodotDisplay for BaseTypeMismatchError {
    fn fmt(
        fmt: fmt::Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        write!(
            f,
            "expected base type \"{}\", found \"{}\"",
            fmt.with_format_opts(&fmt.value.expected),
            fmt.with_format_opts(&fmt.value.found)
        )
    }
}

impl Display for BaseTypeMismatchError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

/// An error for when a [Type](crate::fodot::vocabulary::Type) is not a subtype of a certain type.
///
/// Use [SubTypeMismatchError] in [Result::Err].
#[derive(Clone, Debug)]
pub struct SubTypeMismatch {
    pub found: TypeStr,
    pub expected: TypeStr,
}

impl Error for SubTypeMismatch {}

impl FodotOptions for SubTypeMismatch {
    type Options<'a> = FormatOptions;
}

impl FodotDisplay for SubTypeMismatch {
    fn fmt(
        fmt: fmt::Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        write!(
            f,
            "expected a type of subtype \"{}\", found \"{}\"",
            fmt.with_format_opts(&fmt.value.expected),
            fmt.with_format_opts(&fmt.value.found)
        )
    }
}

impl Display for SubTypeMismatch {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

singleton_error! {
    /// A [TypeMismatchError] stored on the heap.
    #[doc = singleton_docs!()]
    #[derive(Clone, Debug)]
    pub SubTypeMismatchError,
    SubTypeMismatch,
}

/// An error for trying to override type interpretations of builtin types.
#[derive(Clone, Debug)]
pub struct OverrideBuiltinTypeInterpError(pub PrimitiveType);

impl Error for OverrideBuiltinTypeInterpError {}

impl FodotOptions for OverrideBuiltinTypeInterpError {
    type Options<'a> = FormatOptions;
}

impl FodotDisplay for OverrideBuiltinTypeInterpError {
    fn fmt(
        fmt: fmt::Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        write!(
            f,
            "overriding type interpretation of builtin type {} is not allowed",
            fmt.with_format_opts(&fmt.value.0)
        )
    }
}

impl Display for OverrideBuiltinTypeInterpError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

/// An error for an operation that requires all types to have a interpretation.
#[non_exhaustive]
#[derive(Clone, Debug)]
pub struct UninterpretedTypesError;

impl Error for UninterpretedTypesError {}

impl Display for UninterpretedTypesError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "all types must be intepreted")
    }
}

simple_fodot_display!(UninterpretedTypesError);

/// An error when trying to acquire a [TypeInterp](crate::fodot::structure::TypeInterp) of a
/// builtin type.
///
/// Builtin types don't have a concrete interpretation that can be queried.
#[non_exhaustive]
#[derive(Clone, Debug)]
pub struct NoBuiltinTypeInterp;

impl Error for NoBuiltinTypeInterp {}

impl Display for NoBuiltinTypeInterp {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "builtin types don't have an interactable type interpretation"
        )
    }
}

simple_fodot_display!(NoBuiltinTypeInterp);

/// An error for when converting a value to the value of a given
/// [Type](crate::fodot::vocabulary::Type), when the given value is of the correct super type
/// but is not contained in the enumeration of the given type.
#[non_exhaustive]
#[derive(Clone, Debug)]
pub struct MissingTypeElementError;

impl Display for MissingTypeElementError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "the provided value is not contained in the provided type"
        )
    }
}

impl Error for MissingTypeElementError {}

simple_fodot_display!(MissingTypeElementError);

/// An error for when some arguments have different
/// [TypeInterps](crate::fodot::structure::TypeInterps).
#[non_exhaustive]
#[derive(Clone, Debug)]
pub struct TypeInterpsMismatchError;

impl Display for TypeInterpsMismatchError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "one or more arguments have mismatching type interpretations"
        )
    }
}

simple_fodot_display!(TypeInterpsMismatchError);

impl Error for TypeInterpsMismatchError {}

/// An error for when the amount of given arguments does not correspond with the arity of the given
/// symbol.
///
/// Use [MismatchedArityError] in [Result::Err].
#[derive(Clone, Debug)]
pub struct MismatchedArity {
    pub expected: usize,
    pub found: usize,
}

impl Display for MismatchedArity {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "expected {} ", self.expected)?;
        if 1 < self.expected {
            write!(f, "arguments")?;
        } else {
            write!(f, "argument")?;
        }
        write!(f, ", found {}", self.found)
    }
}

impl Error for MismatchedArity {}

simple_fodot_display!(MismatchedArity);
singleton_error! {
    /// A [MismatchedArity] stored on the heap.
    #[doc = singleton_docs!()]
    #[derive(Clone, Debug)]
    pub MismatchedArityError,
    MismatchedArity,
}

/// An error for when a given value is of the correct super type, but not contained in the codomain
/// type.
#[derive(Clone, Debug)]
pub struct CodomainError;

impl Display for CodomainError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "the provided value is not contained in the symbols codomain"
        )
    }
}

impl Error for CodomainError {}

simple_fodot_display!(CodomainError);

/// A conversion error from any value to FO(.) primitive elements.
#[non_exhaustive]
#[derive(Clone, Debug)]
pub struct NotAnElementError;

impl Display for NotAnElementError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "the provided value is not an FO(.) element")
    }
}

impl Error for NotAnElementError {}

simple_fodot_display!(NotAnElementError);

/// A conversion error for when converting an [Assertion](crate::fodot::theory::Assertion)
/// to an [Expr] and the assertion is a definition.
#[non_exhaustive]
#[derive(Clone, Debug)]
pub struct IsADefinitionError;

impl Display for IsADefinitionError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "a definition is not an expression")
    }
}

impl Error for IsADefinitionError {}

simple_fodot_display!(IsADefinitionError);

/// A conversion error for when converting an [Expr] to an
/// [Assertion](crate::fodot::theory::Assertion) but the expression's codomain is not a boolean
/// codomain.
#[non_exhaustive]
#[derive(Clone, Debug)]
pub struct NotBoolExpr {
    pub found: TypeStr,
}

impl Display for NotBoolExpr {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "expected a boolean codomain, found: {}", self.found)
    }
}

impl Error for NotBoolExpr {}

simple_fodot_display!(NotBoolExpr);

singleton_error! {
    /// A [DomainMismatch] stored on the heap.
    #[doc = singleton_docs!()]
    #[derive(Clone, Debug)]
    pub NotBoolExprError,
    NotBoolExpr,
}

/// A conversion error for [Expr] to
/// [Assertion](crate::fodot::theory::Assertion) when the expression still contains free variables.
#[non_exhaustive]
#[derive(Clone, Debug)]
pub struct ExprToAssertFreeVarError;

impl Display for ExprToAssertFreeVarError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "an assertion is not allowed free variables")
    }
}

impl Error for ExprToAssertFreeVarError {}

simple_fodot_display!(ExprToAssertFreeVarError);

/// An error for when trying to create a [DefinitionalRule](crate::fodot::theory::DefinitionalRule)
/// that contains free variables.
#[non_exhaustive]
#[derive(Clone, Debug)]
pub struct DefFreeVarError;

impl Display for DefFreeVarError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "a definition must not have free variables")
    }
}

impl Error for DefFreeVarError {}

simple_fodot_display!(DefFreeVarError);

/// An error for when trying to create a [Quantees](crate::fodot::theory::Quantees) with no bound
/// variables.
#[non_exhaustive]
#[derive(Clone, Debug)]
pub struct NoVarQuanteesError;

impl Display for NoVarQuanteesError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "quantees must have atleast one variable bound")
    }
}

impl Error for NoVarQuanteesError {}

simple_fodot_display!(NoVarQuanteesError);

/// A conversion error when trying to convert to a
/// [BoolExpr](crate::fodot::theory::BoolExpr).
#[non_exhaustive]
#[derive(Clone, Debug)]
pub struct NotABoolElementError;

impl Display for NotABoolElementError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "the provided value is not a boolean element")
    }
}

impl Error for NotABoolElementError {}

simple_fodot_display!(NotABoolElementError);

/// An error for an invalid definitional head expression.
#[non_exhaustive]
#[derive(Clone, Debug)]
pub struct InvalidDefHeadError;

impl Display for InvalidDefHeadError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "a definitional head must be a predicate or an \
            equality operator between a function and an expression"
        )
    }
}

impl Error for InvalidDefHeadError {}

simple_fodot_display!(InvalidDefHeadError);

/// Error for equality between two expressions with a boolean codomain.
#[non_exhaustive]
#[derive(Clone, Debug)]
pub struct BoolEqualityError;

impl Display for BoolEqualityError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "equality operator between two boolean expressions is not allowed, \
            use the equivalence operator"
        )
    }
}

impl Error for BoolEqualityError {}

simple_fodot_display!(BoolEqualityError);

/// An error for when parsing a primitive element fails.
#[non_exhaustive]
#[derive(Clone, Debug)]
pub struct ParsePrimitiveElementError;

impl Display for ParsePrimitiveElementError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "unable to parse the provided value into a primitive element"
        )
    }
}

impl Error for ParsePrimitiveElementError {}

simple_fodot_display!(ParsePrimitiveElementError);

/// An error for when parsing a base type fails.
#[non_exhaustive]
#[derive(Clone, Debug)]
pub struct ParseBaseTypeError;

impl Display for ParseBaseTypeError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "unable to parse the provided value as a base type")
    }
}

impl Error for ParseBaseTypeError {}

simple_fodot_display!(ParseBaseTypeError);

/// An error for when a value of a certain domain was expected, but a value of a different domain
/// was given.
#[non_exhaustive]
#[derive(Clone, Debug)]
pub struct DomainMismatch {
    pub expected: StrDomain,
    pub found: StrDomain,
}

impl FodotOptions for DomainMismatch {
    type Options<'a> = FormatOptions;
}

impl FodotDisplay for DomainMismatch {
    fn fmt(
        fmt: fmt::Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        write!(
            f,
            "expected domain {}, found {}",
            fmt.with_format_opts(&fmt.value.expected),
            fmt.with_format_opts(&fmt.value.found),
        )
    }
}

impl Display for DomainMismatch {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

impl Error for DomainMismatch {}

singleton_error! {
    /// A [DomainMismatch] stored on the heap.
    #[doc = singleton_docs!()]
    #[derive(Clone, Debug)]
    pub DomainMismatchError,
    DomainMismatch,
}

/// An error for when a symbol with a finite codomain is expected, but a symbol with an infinite
/// codomain was given.
#[non_exhaustive]
#[derive(Clone, Debug)]
pub struct InfiniteCodomainError;

impl Display for InfiniteCodomainError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "received a symbol with a infinite codomain, whilst a finite codomain was expected"
        )
    }
}

impl Error for InfiniteCodomainError {}

simple_fodot_display!(InfiniteCodomainError);

/// An error for when overflow occurs.
#[non_exhaustive]
#[derive(Clone, Debug)]
pub struct OverflowError;

impl Display for OverflowError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "unable to represent provided value due to overflow")
    }
}

impl Error for OverflowError {}

simple_fodot_display!(OverflowError);

/// An error when trying to define the interpretation of builtin types.
#[non_exhaustive]
#[derive(Clone, Debug)]
pub struct BuiltinTypeInterpretationError;

impl Display for BuiltinTypeInterpretationError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "cannot set the type interpretation of builtin types")
    }
}

impl Error for BuiltinTypeInterpretationError {}

simple_fodot_display!(BuiltinTypeInterpretationError);

/// An error when trying to define the interpretation of type using a bad interpretation.
#[non_exhaustive]
#[derive(Clone, Debug)]
pub struct WrongTypeInterpretation;

impl Display for WrongTypeInterpretation {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "types are unary predicates and must be intepreted as such"
        )
    }
}

impl Error for WrongTypeInterpretation {}

simple_fodot_display!(WrongTypeInterpretation);

#[derive(Clone, Debug)]
pub enum InterpretationType {
    Constant,
    Set,
    Map,
}

impl InterpretationType {
    fn name(&self) -> &'static str {
        match self {
            Self::Constant => "constant",
            Self::Set => "set",
            Self::Map => "mapping",
        }
    }
}

/// An error when trying to define the interpretation of pfunc using a bad interpretation.
#[non_exhaustive]
#[derive(Clone, Debug)]
pub struct WrongPfuncInterpretation {
    pub expected: InterpretationType,
    pub found: InterpretationType,
}

impl Display for WrongPfuncInterpretation {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "expected a {} found a {}",
            self.expected.name(),
            self.found.name()
        )
    }
}

impl Error for WrongPfuncInterpretation {}

simple_fodot_display!(WrongPfuncInterpretation);

/// An error when trying to define the interpretation of function that maps a single argument on
/// multiple different values.
#[non_exhaustive]
#[derive(Clone, Debug)]
pub struct ParseInterpMultiImage {
    pub args: Vec<StrTypeElement>,
}

impl Display for ParseInterpMultiImage {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "argument")?;
        if self.args.len() == 0 {
            write!(f, " ()")?;
        } else if let [element] = &self.args[..] {
            write!(f, " {}", element)?;
        } else {
            write!(f, "s ({})", self.args.iter().format(", "))?;
        }
        write!(f, " has been given multiple different values")
    }
}

impl Error for ParseInterpMultiImage {}

simple_fodot_display!(ParseInterpMultiImage);
singleton_error! {
    /// A [ParseInterpMultiImage] stored on the heap.
    #[doc = singleton_docs!()]
    #[derive(Clone, Debug)]
    pub ParseInterpMultiImageError,
    ParseInterpMultiImage,
}

/// An error for things that are not allowed
#[non_exhaustive]
#[derive(Clone, Debug)]
pub struct NotAllowedError {
    pub message: &'static str,
}

impl Display for NotAllowedError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.message)
    }
}

impl Error for NotAllowedError {}

simple_fodot_display!(NotAllowedError);

/// An error for things that are not allowed
#[non_exhaustive]
#[derive(Clone, Debug)]
pub struct NullaryConstructorApplicationError;

impl Display for NullaryConstructorApplicationError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "nullary constructors are always applied, even without brackets"
        )
    }
}

impl Error for NullaryConstructorApplicationError {}

simple_fodot_display!(NullaryConstructorApplicationError);

impl FodotOptions for ParseError {
    type Options<'a> = FormatOptions;
}

impl FodotDisplay for ParseError {
    fn fmt(
        fmt: fmt::Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        write!(f, "{}", fmt.value)
    }
}

/// An error for when division by zero is attempted
#[non_exhaustive]
#[derive(Clone, Debug)]
pub struct DivByZeroError;

impl Display for DivByZeroError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "division by zero is not allowed")
    }
}

impl Error for DivByZeroError {}

simple_fodot_display!(DivByZeroError);

#[non_exhaustive]
#[derive(Clone, Debug)]
pub struct NotWellDefinedExpression {
    pub causes: Vec<NotWellDefinedCause>,
}

#[non_exhaustive]
#[derive(Clone, Debug)]
pub struct NotWellDefinedCause {
    pub condition: Expr,
    pub origin: Expr,
}

impl FodotOptions for NotWellDefinedExpression {
    type Options<'a> = FormatOptions;
}

impl FodotDisplay for NotWellDefinedExpression {
    fn fmt(
        fmt: fmt::Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        write!(
            f,
            "could not verify the following well-defined conditions are satisfied: {}",
            fmt.value
                .causes
                .iter()
                .map(|f| fmt.with_format_opts(&f.condition))
                .format(", ")
        )
    }
}

impl Display for NotWellDefinedExpression {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

singleton_error! {
    /// A [NotWellDefinedExpression] stored on the heap.
    #[doc = singleton_docs!()]
    #[derive(Clone, Debug)]
    pub NotWellDefinedExpressionError,
    NotWellDefinedExpression,
}

#[derive(Clone, Debug)]
pub struct BoundVariablesInGuard {
    pub unguardable_vars: Vec<VariableDeclRef>,
}

impl FodotOptions for BoundVariablesInGuard {
    type Options<'a> = FormatOptions;
}

impl FodotDisplay for BoundVariablesInGuard {
    fn fmt(
        fmt: fmt::Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        write!(
            f,
            "cannot guard expression when bound variables are required in guard, vars required in guard: {}",
            fmt.value
                .unguardable_vars
                .iter()
                .map(|f| f.name())
                .format(", ")
        )
    }
}

impl Display for BoundVariablesInGuard {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

singleton_error! {
    /// A [BoundVariablesInGuard] stored on the heap.
    #[doc = singleton_docs!()]
    #[derive(Clone, Debug)]
    pub BoundVariablesInGuardError,
    BoundVariablesInGuard,
}

#[derive(Clone, Debug)]
pub struct MissingTypeInterps {
    pub missing: Vec<String>,
}

simple_fodot_display!(MissingTypeInterps);

impl Display for MissingTypeInterps {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self.missing.as_slice() {
            &[ref only] => write!(
                f,
                "the following type is missing an interpretation: '{}'",
                only
            ),
            rest => write!(
                f,
                "the following types are missing an interpretation: {}",
                rest.iter()
                    .map(|value| display_fn(move |f| write!(f, "'{}'", value)))
                    .format(", ")
            ),
        }
    }
}

singleton_error! {
    /// A [MissingTypeInterps] stored on the heap.
    #[doc = singleton_docs!()]
    #[derive(Clone, Debug)]
    pub MissingTypeInterpsError,
    MissingTypeInterps,
}

/// Error for when trying to change a type interpretation but pfunc interpretations exist that
/// depend on the current type interpretation.
#[derive(Clone, Debug)]
pub struct TypeInterpDependence {
    pub custom_type_name: String,
    pub pfuncs: Vec<String>,
}

simple_fodot_display!(TypeInterpDependence);

impl Display for TypeInterpDependence {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self.pfuncs.as_slice() {
            &[ref only] => write!(
                f,
                "the following pfunc has an interpretation that depends on the current type interpretation of '{}': '{}'",
                self.custom_type_name, only
            ),
            rest => write!(
                f,
                "the following pfuncs have interpretations that depend on the current type interpretation: {}",
                rest.iter()
                    .map(|value| display_fn(move |f| write!(f, "'{}'", value)))
                    .format(", ")
            ),
        }
    }
}

singleton_error! {
    /// A [TypeInterpDependence] stored on the heap.
    #[doc = singleton_docs!()]
    #[derive(Clone, Debug)]
    pub TypeInterpDependenceError,
    TypeInterpDependence,
}

/// Error returned when the given operation would make the structure inconsistent w.r.t. the
/// structure's vocabulary.
#[derive(Clone, Debug)]
pub struct InconsistentAssignment {
    pub symbol_name: String,
}

simple_fodot_display!(InconsistentAssignment);

impl Display for InconsistentAssignment {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "given assignment for symbol '{}', is inconsistent with previous assignments",
            self.symbol_name
        )
    }
}

singleton_error! {
    /// A [InconsistentAssignment] stored on the heap.
    #[doc = singleton_docs!()]
    #[derive(Clone, Debug)]
    pub InconsistenAssignmentError,
    InconsistentAssignment,
}

/// A macro called by [algebraic_errors::algebraic_errors] for creating automatically creating a
/// wrapper type.
macro_rules! create_wrapper {
    (
        sum $name:ident,
        {
            $($variant:ident),* $(,)?
        },
        {}
    ) => {};
    (
        sum $name:ident,
        {
            $($variant:ident),* $(,)?
        },
        {
            wrapper: {
                $(#[$($attribute:tt)*])*
                $wrapper_name:ident,
                $($not_boxed:ident,)?
            },
        }
    ) => {
        create_wrapper! {
            if ($($not_boxed)?) {
                $(#[$($attribute)*])*
                #[derive(Debug, Clone)]
                pub struct $wrapper_name {
                    kind: $name,
                }

                impl $wrapper_name {
                    pub fn take_kind(self) -> $name {
                        self.kind
                    }

                    pub fn kind(&self) -> &$name {
                        &self.kind
                    }

                    fn _take_alg_type(self) -> $name {
                        self.take_kind()
                    }
                    fn _from_alg_type(sum_type: $name) -> Self {
                        Self {
                            kind: sum_type,
                        }
                    }
                }
            } else {
                $(#[$($attribute)*])*
                #[derive(Debug, Clone)]
                pub struct $wrapper_name {
                    kind: Box<$name>,
                }

                impl $wrapper_name {
                    pub fn take_kind(self) -> $name {
                        *self.kind
                    }

                    pub fn kind(&self) -> &$name {
                        &self.kind
                    }

                    fn _take_alg_type(self) -> $name {
                        *self.kind
                    }
                    fn _from_alg_type(sum_type: $name) -> Self {
                        Self {
                            kind: Box::new(sum_type),
                        }
                    }
                }
            }
        }

        impl FodotOptions for $wrapper_name {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for $wrapper_name {
            fn fmt(
                fmt: $crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut core::fmt::Formatter<'_>
            ) -> core::fmt::Result {
                write!(f, "{}", fmt.with_format_opts(fmt.value.kind()))
            }
        }

        impl Error for $wrapper_name {}

        impl Display for $wrapper_name {
            fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
                write!(f, "{}", self.display())
            }
        }
    };
    (if () { $($if:tt)* } else { $($else:tt)* }) => { $($else)* };
    (if ($($something:tt)*) { $($if:tt)* } else { $($else:tt)* }) => { $($if)* };
    (
        prod $($rest:tt)*
    ) => {};
}

/// A macro called by [algebraic_errors::algebraic_errors], auto implements [FodotDisplay],
/// [FodotOptions] and [Display].
macro_rules! fodot_display_impl {
    (
        sum $name:ident,
        {
            $($variant:ident),* $(,)?
        },
        $($thing:tt)?
    ) => {
        impl FodotOptions for $name {
            type Options<'a> = FormatOptions;
        }

        impl $crate::fodot::fmt::FodotDisplay for $name {
            fn fmt(
                fmt: $crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut core::fmt::Formatter<'_>
            ) -> core::fmt::Result {
                match &fmt.value {
                    $(
                        Self::$variant(value) => {
                            write!(
                                f,
                                "{}",
                                fmt.with_format_opts(value)
                            )
                        }
                    )+
                }
            }
        }

        impl Display for $name {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }
    };
    (
        prod $($rest:tt)*
    ) => {};
}

/// Trait for extension of [ArgAddError], used in generic functions.
pub trait ArgCreationErrorExtension: Sized {
    type Error: From<Self> + From<ArgAddError> + From<MismatchedArity> + From<MismatchedArityError>;
}

impl ArgCreationErrorExtension for ParseTypeElementError {
    type Error = ParseArgCreationError;
}

impl ArgCreationErrorExtension for ConvertTypeElementError {
    type Error = ArgCreationError;
}

impl ArgCreationErrorExtension for ParseArgCreationError {
    type Error = ParseArgCreationError;
}

algebraic_errors! {
    opts: {
        expand: [
            create_wrapper,
            fodot_display_impl,
        ],
    },
    /// The error kind of [ParseSymbolError].
    #[derive(Debug, Clone)]
    pub sum ParseSymbolErrorKind {
        {
            opts: {
                wrapper: {
                    /// A symbol parse error.
                    ///
                    /// See [ParseSymbolErrorKind] for possible errors.
                    ParseSymbolError,
                },
            },
            ParseSymbolError,
        },
        MissingSymbol,
        WrongSymbolType,
    },
    /// The error kind of [ParseCustomTypeError].
    #[derive(Debug, Clone)]
    pub sum ParseCustomTypeErrorKind {
        {
            opts: {
                wrapper: {
                    /// A symbol parse error.
                    ///
                    /// See [ParseCustomTypeErrorKind] for possible errors.
                    ParseCustomTypeError,
                },
            },
            ParseCustomTypeError,
        },
        MissingSymbol,
        WrongSymbolType,
        NotACustomType,
    },
    /// The error kind of [StrSetTypeInterpError].
    #[derive(Debug, Clone)]
    pub sum StrSetTypeInterpErrorKind {
        {
            opts: {
                wrapper: {
                    /// Possible errors when trying to set a type interp when the given type is
                    /// represented as [str].
                    ///
                    /// See [StrSetTypeInterpErrorKind] for possible errors.
                    StrSetTypeInterpError,
                },
            },
            StrSetTypeInterpError,
        },
        OverrideBuiltinTypeInterpError,
        MissingSymbol,
        WrongSymbolType,
        Redeclaration,
        BaseTypeMismatchError,
    },
    /// The error kind of [TypeInterpFromStrError].
    #[derive(Debug, Clone)]
    pub sum TypeInterpFromStrErrorKind {
        {
            opts: {
                wrapper: {
                    /// Possible errors when trying to acquire a
                    /// [TypeInterp](crate::fodot::structure::TypeInterp) from a [str].
                    ///
                    /// See [TypeInterpFromStrErrorKind] for possible errors.
                    TypeInterpFromStrError,
                },
            },
            TypeInterpFromStrError,
        },
        NoBuiltinTypeInterp,
        MissingSymbol,
        WrongSymbolType,
    },
    /// The error kind of [ParseTypeElementError].
    #[derive(Debug, Clone)]
    pub sum ParseTypeElementErrorKind {
        {
            opts: {
                wrapper: {
                    /// Possible errors when trying to parse a
                    /// [TypeElement](crate::fodot::structure::TypeElement) of a
                    /// [Type](crate::fodot::vocabulary::Type).
                    ///
                    /// See [ParseTypeElementErrorKind] for possible errors.
                    ParseTypeElementError,
                    not_boxed,
                },
            },
            ParseTypeElementError,
        },
        ParseBoolError,
        ParseIntError,
        ParseRealError,
        MissingTypeElementError,
    },
    /// The error kind of [ParseRealSubTypeError].
    #[derive(Debug, Clone)]
    pub sum ParseRealSubTypeErrorKind {
        {
            opts: {
                wrapper: {
                    /// Possible errors when trying to parse a sub type of Reals.
                    ///
                    /// See [ParseRealSubTypeErrorKind] for possible errors.
                    ParseRealSubTypeError,
                },
            },
            ParseRealSubTypeError,
        },
        ParseRealError,
        MissingTypeElementError,
    },
    /// The error kind of [ConvertTypeElementError].
    #[derive(Debug, Clone)]
    pub sum ConvertTypeElementErrorKind {
        {
            opts: {
                wrapper: {
                    /// Possible errors when trying to convert a
                    /// [TypeElement](crate::fodot::structure::TypeElement) to a type element of
                    /// a specific [Type](crate::fodot::vocabulary::Type)
                    ///
                    /// See [ConvertTypeElementErrorKind] for possible errors.
                    ConvertTypeElementError,
                    not_boxed,
                },
            },
            ConvertTypeElementError,
        },
        TypeMismatch,
        MissingTypeElementError,
    },
    /// The error kind of [SetTypeInterpError].
    #[derive(Debug, Clone)]
    pub sum SetTypeInterpErrorKind {
        {
            opts: {
                wrapper: {
                    /// Possible errors when trying to set the
                    /// [TypeInterp](crate::fodot::structure::TypeInterp)s for of a certain
                    /// [Type](crate::fodot::vocabulary::Type).
                    ///
                    /// See [SetTypeInterpErrorKind] for possible errors.
                    SetTypeInterpError,
                    not_boxed,
                },
            },
            SetTypeInterpError,
        },
        BaseTypeMismatchError,
        VocabMismatchError,
    },
    /// The error kind of [SetTypeInterpError].
    #[derive(Debug, Clone)]
    pub sum SetTypeInterpIncompleteErrorKind {
        {
            opts: {
                wrapper: {
                    /// Possible errors when trying to set the
                    /// [TypeInterp](crate::fodot::structure::TypeInterp)s for of a certain
                    /// [Type](crate::fodot::vocabulary::Type).
                    ///
                    /// See [SetTypeInterpIncompleteErrorKind] for possible errors.
                    SetTypeInterpIncompleteError,
                    not_boxed,
                },
            },
            SetTypeInterpIncompleteError,
        },
        TypeInterpDependence,
        BaseTypeMismatchError,
        VocabMismatchError,
    },
    /// The error kind of [ParseArgCreationError].
    #[derive(Debug, Clone)]
    pub sum ParseArgCreationErrorKind {
        {
            opts: {
                wrapper: {
                    /// Possible errors when trying to create arguments from [str]s.
                    ///
                    /// Extends [ArgCreationError] with [ParseTypeElementError].
                    ///
                    /// See [ParseArgCreationErrorKind] for possible errors.
                    ParseArgCreationError,
                },
            },
            ParseArgCreationError,
        },
        ParseBoolError,
        ParseIntError,
        ParseRealError,
        MissingTypeElementError,
        MismatchedArity,
        TypeMismatch,
    },
    /// The error kind of [PfuncError].
    #[derive(Debug, Clone)]
    pub sum PfuncErrorKind {
        {
            opts: {
                wrapper: {
                    /// Possible errors when manipulating interpretations of
                    /// [Pfunc](crate::fodot::vocabulary::Pfunc)s.
                    ///
                    /// See [PfuncErrorKind] for possible errors.
                    PfuncError,
                },
            },
            PfuncError,
        },
        TypeInterpsMismatchError,
        DomainMismatch,
        CodomainError,
    },
    /// The error kind of [ExtendedPfuncError].
    #[derive(Debug, Clone)]
    pub sum ExtendedPfuncErrorKind {
        {
            opts: {
                wrapper: {
                    /// Possible errors when manipulating interpretations of
                    /// [Pfunc](crate::fodot::vocabulary::Pfunc)s extended with [CodomainError].
                    ///
                    /// See [ExtendedPfuncErrorKind] for possible errors.
                    ExtendedPfuncError,
                },
            },
            ExtendedPfuncError,
        },
        TypeInterpsMismatchError,
        DomainMismatch,
        TypeMismatch,
        CodomainError,
    },
    /// The error kind of [NullaryError].
    #[derive(Debug, Clone)]
    pub sum NullaryErrorKind {
        {
            opts: {
                wrapper: {
                    /// Possible errors when setting nullary symbol interpretations.
                    ///
                    /// See [NullaryErrorKind] for possible errors.
                    NullaryError,
                    not_boxed,
                },
            },
            NullaryError,
        },
        TypeInterpsMismatchError,
        CodomainError,
        TypeMismatch,
    },
    /// The error kind of [ArgAddError].
    #[derive(Debug, Clone)]
    pub sum ArgAddErrorKind {
        {
            opts: {
                wrapper: {
                    /// Possible errors when creating arguments (tuples) for
                    /// [Pfunc](crate::fodot::vocabulary::Pfunc)s.
                    ///
                    /// See [ArgAddErrorKind] for possible errors.
                    ArgAddError,
                },
            },
            ArgAddError,
        },
        MismatchedArity,
        TypeMismatch,
    },
    /// The error kind of [ParseIntSubTypeError].
    #[derive(Debug, Clone)]
    pub sum ParseIntSubTypeErrorKind {
        {
            opts: {
                wrapper: {
                    /// Possible errors when parsing a custom integer sub type.
                    ///
                    /// See [ParseIntSubTypeErrorKind] for possible errors.
                    ParseIntSubTypeError,
                },
            },
            ParseIntSubTypeError,
        },
        ParseIntError,
        MissingTypeElementError,
    },
    /// The error kind of [ArgCreationError].
    #[derive(Debug, Clone)]
    pub sum ArgCreationErrorKind {
        {
            opts: {
                wrapper: {
                    /// Possible errors when creating arguments for
                    /// [Pfunc](crate::fodot::vocabulary::Pfunc)s.
                    ///
                    /// See [ArgCreationErrorKind] for possible errors.
                    ArgCreationError,
                },
            },
            ArgCreationError,
        },
        MismatchedArity,
        TypeMismatch,
        MissingTypeElementError,
    },
    /// The error kind of [ExprToAssertionError].
    #[derive(Debug, Clone)]
    pub sum ExprToAssertionErrorKind {
        {
            opts: {
                wrapper: {
                    /// Possible errors when converting an [Expr](crate::fodot::theory::Expr) to an
                    /// [Assertion](crate::fodot::theory::Assertion).
                    ///
                    /// See [ExprToAssertionErrorKind] for possible errors.
                    ExprToAssertionError,
                },
            },
            ExprToAssertionError,
        },
        NotBoolExpr,
        ExprToAssertFreeVarError,
        NotWellDefinedExpression,
    },
    /// The error kind of [ExprToWellDefFormulaError].
    #[derive(Debug, Clone)]
    pub sum ExprToWellDefFormulaErrorKind {
        {
            opts: {
                wrapper: {
                    /// Possible errors when converting an [Expr](crate::fodot::theory::Expr) to an
                    /// [WellDefinedFormula](crate::fodot::theory::WellDefinedFormula).
                    ///
                    /// See [ExprToWellDefFormulaErrorKind] for possible errors.
                    ExprToWellDefFormulaError,
                },
            },
            ExprToWellDefFormulaError,
        },
        NotBoolExpr,
        NotWellDefinedExpression,
    },
    /// The error kind of [FormulaToAssertionError].
    #[derive(Debug, Clone)]
    pub sum FormulaToAssertionErrorKind {
        {
            opts: {
                wrapper: {
                    /// Possible errors when converting a [Formula](crate::fodot::theory::Formula) to an
                    /// [Assertion](crate::fodot::theory::Assertion).
                    ///
                    /// See [FormulaToAssertionErrorKind] for possible errors.
                    FormulaToAssertionError,
                },
            },
            FormulaToAssertionError,
        },
        ExprToAssertFreeVarError,
        NotWellDefinedExpression,
    },
    /// The error kind of [ApplyError].
    #[derive(Debug, Clone)]
    pub sum ApplyErrorKind {
        {
            opts: {
                wrapper: {
                    /// Possible errors when applying a symbol.
                    ///
                    /// See [ApplyErrorKind] for possible errors.
                    ApplyError,
                },
            },
            ApplyError,
        },
        VocabMismatchError,
        MismatchedArity,
        TypeMismatch,
    },
    /// The error kind of [ExprSubMismatchError].
    #[derive(Debug, Clone)]
    pub sum ExprSubMismatchErrorKind {
        {
            opts: {
                wrapper: {
                    /// Possible errors when creating new expressions with a possible
                    /// [SubTypeMismatch].
                    ///
                    /// See [ExprSubMismatchError] for possible errors.
                    ExprSubMismatchError,
                },
            },
            ExprSubMismatchError,
        },
        VocabMismatchError,
        TypeMismatch,
        SubTypeMismatch,
    },
    /// The error kind of [ExprBinOpError].
    #[derive(Debug, Clone)]
    pub sum ExprBinOpErrorKind {
        {
            opts: {
                wrapper: {
                    /// Possible errors when creating new [BinOp](crate::fodot::theory::BinOp)s.
                    ///
                    /// See [ExprBinOpError] for possible errors.
                    ExprBinOpError,
                },
            },
            ExprBinOpError,
        },
        VocabMismatchError,
        TypeMismatch,
        SubTypeMismatch,
        BoolEqualityError,
        DivByZeroError,
        NotBoolExpr,
    },
    /// The error kind of [ExprMismatchError].
    #[derive(Debug, Clone)]
    pub sum ExprMismatchErrorKind {
        {
            opts: {
                wrapper: {
                    /// Possible errors when creating some [Expr](crate::fodot::theory::Expr)s
                    ///
                    /// See [ExprMismatchErrorKind] for possible errors.
                    ExprMismatchError,
                },
            },
            ExprMismatchError,
        },
        VocabMismatchError,
        TypeMismatch,
    },
    /// The error kind of [DefHeadError].
    #[derive(Debug, Clone)]
    pub sum DefHeadErrorKind {
        {
            opts: {
                wrapper: {
                    /// Possible errors when creating a
                    /// [DefinitionalHead](crate::fodot::theory::DefinitionalHead).
                    ///
                    /// See [DefHeadErrorKind] for possible errors.
                    DefHeadError,
                },
            },
            DefHeadError,
        },
        InvalidDefHeadError,
        TypeMismatch,
    },
    /// The error kind of [DefRuleError].
    #[derive(Debug, Clone)]
    pub sum DefRuleErrorKind {
        {
            opts: {
                wrapper: {
                    /// Possible errors when creating a
                    /// [DefinitionalRule](crate::fodot::theory::DefinitionalRule).
                    ///
                    /// See [DefHeadErrorKind] for possible errors.
                    DefRuleError,
                },
            },
            DefRuleError,
        },
        DefFreeVarError,
        TypeMismatch,
    },
    /// The error kind of [ArgMismatchError].
    #[derive(Debug, Clone)]
    pub sum ArgMismatchKind {
        {
            opts: {
                wrapper: {
                    /// Possible errors when matching args with a domain.
                    ///
                    /// See [ArgMismatchKind] for possible errors.
                    ArgMismatchError,
                },
            },
            ArgMismatchError,
        },
        DomainMismatch,
        TypeInterpsMismatchError,
    },
    /// The error kind of [GetRangeError].
    #[derive(Debug, Clone)]
    pub sum GetRangeErrorKind {
        {
            opts: {
                wrapper: {
                    /// Possible errors when calling [get_range](crate::solver::Solver::get_range).
                    ///
                    /// See [GetRangeErrorKind] for possible errors.
                    GetRangeError,
                },
            },
            GetRangeError,
        },
        DomainMismatch,
        VocabMismatchError,
        TypeInterpsMismatchError,
        InfiniteCodomainError,
    },
    /// The error kind of [GetRangeError].
    #[derive(Debug, Clone)]
    pub sum GuardErrorKind {
        {
            opts: {
                wrapper: {
                    /// Possible errors when creating guards.
                    ///
                    /// See [GuardErrorKind] for possible errors.
                    GuardError,
                },
            },
            GuardError,
        },
        TypeMismatch,
        BoundVariablesInGuard,
    },
    /// The error kind of [WithPartialInterpsErrorKind].
    #[derive(Debug, Clone)]
    pub sum WithPartialInterpsErrorKind {
        {
            opts: {
                wrapper: {
                    /// Possible errors when attaching partial interpretations.
                    ///
                    /// See [WithPartialInterpsErrorKind] for possible errors.
                    WithPartialInterpsError,
                },
            },
            WithPartialInterpsError,
        },
        VocabMismatchError,
        MissingTypeInterps,
    },
    /// All possible errors when parsing and lowering a FO(·) specification.
    #[derive(Debug, Clone)]
    pub sum SliError {
        InvalidDefHeadError,
        DomainMismatch,
        MissingSymbol,
        WrongSymbolType,
        TypeMismatch,
        BoolEqualityError,
        MismatchedArity,
        NotBoolExpr,
        MissingTypeElementError,
        CodomainError,
        OverrideBuiltinTypeInterpError,
        BaseTypeMismatchError,
        OverflowError,
        BuiltinTypeInterpretationError,
        WrongTypeInterpretation,
        ParseBaseTypeError,
        ParseBoolError,
        ParseIntError,
        ParseRealError,
        DivByZeroError,

        DomainMismatch,
        TypeMismatch,
        CodomainError,
        WrongPfuncInterpretation,
        ParseInterpMultiImage,

        NotAllowedError,
        UninterpretedTypesError,

        Redeclaration,

        SubTypeMismatch,
        BoolEqualityError,
        MismatchedArity,
        NullaryConstructorApplicationError,
        InvalidDefHeadError,
        DefFreeVarError,
        NotWellDefinedExpression,
        BoundVariablesInGuard,
        InconsistentAssignment,
        MissingTypeInterps,

        ExprToAssertFreeVarError,
        ParseError,
    },
    extern prod MissingSymbolError(MissingSymbol),
    extern prod RedeclarationError(Redeclaration),
    extern prod WrongSymbolTypeError(WrongSymbolType),
    extern prod TypeMismatchError(TypeMismatch),
    extern prod SubTypeMismatchError(SubTypeMismatch),
    extern prod MismatchedArityError(MismatchedArity),
    extern prod DomainMismatchError(DomainMismatch),
    extern prod ParseInterpMultiImageError(ParseInterpMultiImage),
    extern prod NotBoolExprError(NotBoolExpr),
    extern prod BoundVariablesInGuardError(BoundVariablesInGuard),
    extern prod NotWellDefinedExpressionError(NotWellDefinedExpression),
    extern prod MissingTypeInterpsError(MissingTypeInterps),
    extern prod TypeInterpDependenceError(TypeInterpDependence),
    extern prod InconsistenAssignmentError(InconsistentAssignment),
}
