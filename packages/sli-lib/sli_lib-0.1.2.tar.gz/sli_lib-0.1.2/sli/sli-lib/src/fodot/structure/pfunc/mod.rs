#[cfg(doc)]
use crate::fodot::vocabulary::Type;
use crate::fodot::vocabulary::TypeStr;
use crate::fodot::{
    error::{CodomainError, NullaryError, TypeInterpsMismatchError, TypeMismatch},
    fmt::{Fmt, FormatOptions},
    structure::{
        ArgsRef, DomainFull, DomainFullRef, IntTypeFull, PartialTypeInterps, RealTypeFull,
        StrElement, StrTypeFull, TypeElement,
    },
    vocabulary::{
        DomainRef, IntTypeRef, Pfunc, PfuncIndex, PfuncRc, PfuncRef, RealTypeRef, StrTypeRef,
        TypeRef, Vocabulary,
    },
};
use comp_core::{IndexRepr, Int, Real, vocabulary::TypeEnum};
use itertools::Itertools;
use sli_collections::iterator::Iterator;
use std::{
    fmt::{self, Display, Write},
    ops::Deref,
};

mod int_const;
mod int_func;
mod pred;
mod prop;
mod real_const;
mod real_func;
mod str_const;
mod str_func;
mod symbol_interp;

pub(super) enum PfuncDeclInterps<'a> {
    Primitive(PfuncDeclInterp<'a>),
    IntType(IntTypeDeclInterp<'a>),
    RealType(RealTypeDeclInterp<'a>),
    Str(StrDeclInterp<'a>),
}

/// A [PfuncRef] bundled with a &[PartialTypeInterps].
///
/// Used in pfunc interps.
#[derive(Clone)]
pub struct PfuncDeclInterp<'a> {
    pub(super) pfunc_decl_index: PfuncIndex,
    pub(super) type_interps: &'a PartialTypeInterps,
}

impl<'a> PfuncDeclInterp<'a> {
    /// Returns corresponding pfunc as a [PfuncRef].
    pub fn decl(&self) -> PfuncRef<'a> {
        Pfunc(self.pfunc_decl_index, self.type_interps.vocab())
    }

    /// Returns corresponding pfunc as a [PfuncRc].
    pub fn decl_rc(&self) -> PfuncRc {
        Pfunc(
            self.pfunc_decl_index,
            self.type_interps.vocab_rc().clone().into(),
        )
    }

    /// Returns corresponding [Vocabulary].
    pub fn vocab(&self) -> &'a Vocabulary {
        self.type_interps.vocab()
    }

    /// Returns corresponding [PartialTypeInterps].
    pub fn type_interps(&self) -> &'a PartialTypeInterps {
        self.type_interps
    }

    /// Returns corresponding domain as a [DomainRef].
    pub fn domain(&self) -> DomainRef<'a> {
        self.decl().domain()
    }

    /// Returns the corresponding domain as a [DomainFull].
    pub fn domain_full(&self) -> DomainFullRef<'a> {
        DomainFull(self.decl().domain().0, self.type_interps)
    }

    /// Returns the name of the pfunc.
    pub fn name(&self) -> &'a str {
        self.decl().name_ref()
    }
}

/// A [PfuncRef] bundled with a &[PartialTypeInterps] for pfuncs with an
/// [IntType](crate::fodot::vocabulary::IntType) codomain.
///
/// Used in pfunc interps.
#[derive(Clone)]
pub struct IntTypeDeclInterp<'a>(pub(super) PfuncDeclInterp<'a>);

impl<'a> Deref for IntTypeDeclInterp<'a> {
    type Target = PfuncDeclInterp<'a>;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl<'a> IntTypeDeclInterp<'a> {
    /// Returns the codomain of this pfunc as an [IntTypeFull].
    pub fn codomain_full(&self) -> IntTypeFull<'a> {
        let TypeRef::IntType(codomain) = self.decl().codomain() else {
            unreachable!()
        };
        codomain.with_partial_interps(self.type_interps).unwrap()
    }

    /// Returns the codomain of this pfunc as an [IntTypeRef].
    pub fn codomain(&self) -> IntTypeRef<'a> {
        let TypeRef::IntType(codomain) = self.decl().codomain() else {
            unreachable!()
        };
        codomain
    }

    pub(crate) fn symbol_codomain_from_type_element(
        &self,
        value: TypeElement,
    ) -> Result<Int, NullaryError> {
        match value {
            TypeElement::Int(value) => {
                if self.codomain_full().contains(value) {
                    Ok(value)
                } else {
                    Err(CodomainError.into())
                }
            }
            TypeElement::Bool(_) => Err(TypeMismatch {
                found: TypeStr::Bool,
                expected: self.codomain().name().into(),
            }
            .into()),
            TypeElement::Real(_) => Err(TypeMismatch {
                found: TypeStr::Real,
                expected: self.codomain().name().into(),
            }
            .into()),
            TypeElement::Str(value) => Err(TypeMismatch {
                found: value.decl().name().into(),
                expected: self.codomain().name().into(),
            }
            .into()),
        }
    }
}

/// A [PfuncRef] bundled with a &[PartialTypeInterps] for pfuncs with an
/// [RealType](crate::fodot::vocabulary::RealType) codomain.
///
/// Used in pfunc interps.
#[derive(Clone)]
pub struct RealTypeDeclInterp<'a>(pub(super) PfuncDeclInterp<'a>);

impl<'a> Deref for RealTypeDeclInterp<'a> {
    type Target = PfuncDeclInterp<'a>;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl<'a> RealTypeDeclInterp<'a> {
    /// Returns the codomain of this pfunc as an [RealTypeFull].
    pub fn codomain_full(&self) -> RealTypeFull<'a> {
        let TypeRef::RealType(codomain) = self.decl().codomain() else {
            unreachable!()
        };
        codomain.with_partial_interps(self.type_interps).unwrap()
    }

    /// Returns the codomain of this pfunc as an [RealTypeRef].
    pub fn codomain(&self) -> RealTypeRef<'a> {
        let TypeRef::RealType(codomain) = self.decl().codomain() else {
            unreachable!()
        };
        codomain
    }

    pub(crate) fn symbol_codomain_from_type_element(
        &self,
        value: TypeElement,
    ) -> Result<Real, NullaryError> {
        let real_value = match value {
            TypeElement::Real(value) => Ok::<_, NullaryError>(value),
            TypeElement::Bool(_) => Err(TypeMismatch {
                found: TypeStr::Bool,
                expected: self.codomain().name().into(),
            }
            .into()),
            TypeElement::Int(value) => Ok(value.into()),
            TypeElement::Str(value) => Err(TypeMismatch {
                found: value.decl().name().into(),
                expected: self.codomain().name().into(),
            }
            .into()),
        }?;
        if self.codomain_full().contains(real_value) {
            Ok(real_value)
        } else {
            Err(CodomainError.into())
        }
    }
}

/// A [PfuncRef] bundled with a &[PartialTypeInterps] for pfuncs with an
/// [RealType](crate::fodot::vocabulary::RealType) codomain.
///
/// Used in pfunc interpretations.
#[derive(Clone)]
pub struct StrDeclInterp<'a>(pub(super) PfuncDeclInterp<'a>);

impl<'a> Deref for StrDeclInterp<'a> {
    type Target = PfuncDeclInterp<'a>;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl<'a> StrDeclInterp<'a> {
    /// Returns the codomain of this pfunc as an [StrTypeFull].
    pub fn codomain_full(&self) -> StrTypeFull<'a> {
        let TypeRef::StrType(codomain) = self.decl().codomain() else {
            unreachable!()
        };
        codomain.with_partial_interps(self.type_interps).unwrap()
    }

    /// Returns the codomain of this pfunc as an [StrTypeRef].
    pub fn codomain(&self) -> StrTypeRef<'a> {
        let TypeRef::StrType(codomain) = self.decl().codomain() else {
            unreachable!()
        };
        codomain
    }

    fn to_str_element(&self, type_enum: TypeEnum) -> StrElement<'a> {
        let codomain = self.codomain_full();
        StrElement {
            value: codomain
                .interp
                .0
                .get_index(IndexRepr::from(type_enum).try_into().unwrap())
                .unwrap(),
            type_interps: self.type_interps,
            type_decl_index: codomain.type_decl_index,
        }
    }

    fn lower_str_element_id(&self, element: StrElement) -> Result<TypeEnum, NullaryError> {
        if !std::ptr::eq(self.type_interps, element.type_interps) {
            return Err(TypeInterpsMismatchError.into());
        }
        if element.type_decl_index != self.codomain().0 {
            return Err(TypeMismatch {
                expected: self.codomain().name().into(),
                found: element.decl().name().into(),
            }
            .into());
        }
        Ok(element.get_type_enum())
    }

    pub(crate) fn symbol_codomain_from_type_element<'b>(
        &self,
        value: TypeElement<'b>,
    ) -> Result<StrElement<'b>, NullaryError> {
        match value {
            TypeElement::Bool(_) => Err(TypeMismatch {
                found: TypeStr::Bool,
                expected: self.codomain().name().into(),
            }
            .into()),
            TypeElement::Real(_) => Err(TypeMismatch {
                found: TypeStr::Real,
                expected: self.codomain().name().into(),
            }
            .into()),
            TypeElement::Int(_) => Err(TypeMismatch {
                found: TypeStr::Int,
                expected: self.codomain().name().into(),
            }
            .into()),
            TypeElement::Str(value) => {
                if !core::ptr::eq(value.type_interps(), self.type_interps) {
                    Err(TypeInterpsMismatchError.into())
                } else if value.decl() != self.codomain() {
                    Err(TypeMismatch {
                        found: value.decl().name().into(),
                        expected: self.decl().name().into(),
                    }
                    .into())
                } else {
                    Ok(value)
                }
            }
        }
    }
}

fn bool_from_type_element(value: TypeElement) -> Result<bool, NullaryError> {
    match value {
        TypeElement::Bool(value) => Ok(value),
        TypeElement::Real(_) => Err(TypeMismatch {
            found: TypeStr::Real,
            expected: TypeStr::Bool,
        }
        .into()),
        TypeElement::Int(_) => Err(TypeMismatch {
            found: TypeStr::Int,
            expected: TypeStr::Bool,
        }
        .into()),
        TypeElement::Str(value) => Err(TypeMismatch {
            found: value.decl().name().into(),
            expected: TypeStr::Bool,
        }
        .into()),
    }
}

macro_rules! impl_bool_from_type_element {
    (
        impl$(<$($lt_dec:lifetime),*>)? $name:ident$(<$($lt_use:lifetime),*>)?
    ) => {
        impl$(<$($lt_dec),*>)? $name$(<$($lt_use),*>)? {
            pub(crate) fn symbol_codomain_from_type_element(
                &self,
                value: crate::fodot::structure::TypeElement
            ) -> Result<bool, crate::fodot::error::NullaryError> {
                crate::fodot::structure::pfunc::bool_from_type_element(value)
            }
        }
    };
}

use impl_bool_from_type_element;

fn prim_int_from_type_element(value: TypeElement) -> Result<Int, NullaryError> {
    match value {
        TypeElement::Int(value) => Ok(value),
        TypeElement::Real(_) => Err(TypeMismatch {
            found: TypeStr::Real,
            expected: TypeStr::Int,
        }
        .into()),
        TypeElement::Bool(_) => Err(TypeMismatch {
            found: TypeStr::Bool,
            expected: TypeStr::Int,
        }
        .into()),
        TypeElement::Str(value) => Err(TypeMismatch {
            found: value.decl().name().into(),
            expected: TypeStr::Int,
        }
        .into()),
    }
}

macro_rules! impl_int_from_type_element {
    (
        impl$(<$($lt_dec:lifetime),*>)? $name:ident$(<$($lt_use:lifetime),*>)?
    ) => {
        impl$(<$($lt_dec),*>)? $name$(<$($lt_use),*>)? {
            pub(crate) fn symbol_codomain_from_type_element(
                &self,
                value: crate::fodot::structure::TypeElement
            ) -> Result<Int, crate::fodot::error::NullaryError> {
                crate::fodot::structure::pfunc::prim_int_from_type_element(value)
            }
        }
    };
}

use impl_int_from_type_element;

fn prim_real_from_type_element(value: TypeElement) -> Result<Real, NullaryError> {
    match value {
        TypeElement::Real(value) => Ok(value),
        TypeElement::Int(_) => Err(TypeMismatch {
            found: TypeStr::Int,
            expected: TypeStr::Real,
        }
        .into()),
        TypeElement::Bool(_) => Err(TypeMismatch {
            found: TypeStr::Bool,
            expected: TypeStr::Real,
        }
        .into()),
        TypeElement::Str(value) => Err(TypeMismatch {
            found: value.decl().name().into(),
            expected: TypeStr::Real,
        }
        .into()),
    }
}
macro_rules! impl_real_from_type_element {
    (
        impl$(<$($lt_dec:lifetime),*>)? $name:ident$(<$($lt_use:lifetime),*>)?
    ) => {
        impl$(<$($lt_dec),*>)? $name$(<$($lt_use),*>)? {
            pub(crate) fn symbol_codomain_from_type_element(
                &self,
                value: crate::fodot::structure::TypeElement
            ) -> Result<Real, crate::fodot::error::NullaryError> {
                crate::fodot::structure::pfunc::prim_real_from_type_element(value)
            }
        }
    };
}

use impl_real_from_type_element;

/// Data structures for manipulating partial interpretation of pfuncs.
pub mod partial {
    use super::*;
    /// Data structures for immutable actions on partial pfunc interpretations.
    pub mod immutable {
        use super::*;

        pub use int_const::partial::immutable::*;
        pub use prop::partial::immutable::*;
        pub use real_const::partial::immutable::*;
        pub use str_const::partial::immutable::*;

        pub use int_func::partial::immutable::*;
        pub use pred::partial::immutable::*;
        pub use real_func::partial::immutable::*;
        pub use str_func::partial::immutable::*;

        pub use symbol_interp::symbols::partial::immutable::*;
    }

    /// Data structures for mutable actions on partial pfunc interpretations.
    pub mod mutable {
        use super::*;

        pub use int_const::partial::mutable::*;
        pub use prop::partial::mutable::*;
        pub use real_const::partial::mutable::*;
        pub use str_const::partial::mutable::*;

        pub use int_func::partial::mutable::*;
        pub use pred::partial::mutable::*;
        pub use real_func::partial::mutable::*;
        pub use str_func::partial::mutable::*;

        pub use symbol_interp::symbols::partial::mutable::*;
    }
}

/// Data structures for manipulating complete interpretation of pfuncs.
pub mod complete {
    use super::*;
    /// Data structures for immutable actions on complete pfunc interpretations.
    pub mod immutable {
        use super::*;

        pub use int_const::complete::immutable::*;
        pub use prop::complete::immutable::*;
        pub use real_const::complete::immutable::*;
        pub use str_const::complete::immutable::*;

        pub use int_func::complete::immutable::*;
        pub use pred::complete::immutable::*;
        pub use real_func::complete::immutable::*;
        pub use str_func::complete::immutable::*;

        pub use symbol_interp::symbols::complete::immutable::*;
    }

    /// Data structures for mutable actions on complete pfunc interpretations.
    pub mod mutable {
        use super::*;

        pub use int_const::complete::mutable::*;
        pub use prop::complete::mutable::*;
        pub use real_const::complete::mutable::*;
        pub use str_const::complete::mutable::*;

        pub use int_func::complete::mutable::*;
        pub use pred::complete::mutable::*;
        pub use real_func::complete::mutable::*;
        pub use str_func::complete::mutable::*;

        pub use symbol_interp::symbols::complete::mutable::*;
    }
}

fn partial_nullary_display(
    name: &str,
    value: Option<impl Display>,
    options: FormatOptions,
    f: &mut fmt::Formatter<'_>,
) -> fmt::Result {
    write!(f, "{} ", name)?;
    if value.is_some() {
        options.write_def_eq(f)?;
    } else {
        options.write_superset(f)?;
    }
    f.write_char(' ')?;
    match value {
        Some(value) => write!(f, "{}", value),
        None => write!(f, "?"),
    }
}

fn complete_nullary_display(
    name: &str,
    value: impl Display,
    options: FormatOptions,
    f: &mut fmt::Formatter<'_>,
) -> fmt::Result {
    write!(f, "{} ", name)?;
    options.write_def_eq(f)?;
    f.write_char(' ')?;
    write!(f, "{}", value)
}

fn func_display<'a>(
    name: &str,
    values: impl Iterator<Item = (ArgsRef<'a>, impl Display)>,
    is_complete: bool,
    options: FormatOptions,
    f: &mut fmt::Formatter<'_>,
) -> fmt::Result {
    write!(f, "{} ", name)?;
    if is_complete {
        options.write_def_eq(f)?;
    } else {
        options.write_superset(f)?;
    }
    f.write_str(" {")?;
    options.write_image_arg(f, values)?;
    f.write_str("}")
}

fn complete_pred_display<'a>(
    name: &str,
    values: impl Iterator<Item = ArgsRef<'a>>,
    options: FormatOptions,
    f: &mut fmt::Formatter<'_>,
) -> fmt::Result {
    write!(f, "{} ", name)?;
    options.write_def_eq(f)?;
    f.write_str(" {")?;
    write!(
        f,
        "{}",
        values
            .map(|f| Fmt {
                options: options.clone(),
                value: f,
            })
            .format(", ")
    )?;
    f.write_str("}")
}

use macros::*;

mod macros {
    macro_rules! common_impls {
        (
            ($name:ident<$($lt:lifetime),*>,
            $ret_lifetime:lifetime,
            ($codomain_in:ty, $codomain_out:ty) $($rest_2:tt)*),
            {$($extra:tt)*},
            $(($variant:ident $($rest:tt)*)),* $(,)?
        ) => {
            impl<$($lt),*> crate::fodot::fmt::FodotOptions for $name<$($lt),*> {
                type Options<'b> = crate::fodot::fmt::FormatOptions;
            }

            impl<$($lt),*> crate::fodot::fmt::FodotDisplay for $name<$($lt),*> {
                fn fmt(
                    fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                    f: &mut std::fmt::Formatter<'_>
                ) -> core::fmt::Result {
                    match &fmt.value {
                        $(
                            Self::$variant(interp) => crate::fodot::fmt::FodotDisplay::fmt(
                                fmt.with_opts(interp),
                                f
                            ),
                        )*
                    }
                }
            }

            impl<$($lt),*> core::fmt::Display for $name<$($lt),*> {
                fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> core::fmt::Result {
                    write!(f, "{}", crate::fodot::fmt::FodotDisplay::display(self))
                }
            }

            impl<$($lt),*> $name<$($lt),*> {
                pub fn decl(&self) -> crate::fodot::vocabulary::PfuncRef<$ret_lifetime> {
                    match self {
                        $(
                            Self::$variant(interp) => interp.decl(),
                        )*
                    }
                }

                pub fn decl_rc(&self) -> crate::fodot::vocabulary::PfuncRc {
                    match self {
                        $(
                            Self::$variant(interp) => interp.decl_rc(),
                        )*
                    }
                }

                pub fn vocab(&self) -> &$ret_lifetime crate::fodot::vocabulary::Vocabulary {
                    match self {
                        $(
                            Self::$variant(interp) => interp.vocab(),
                        )*
                    }
                }

                pub fn type_interps(&self) -> &$ret_lifetime crate::fodot::structure::PartialTypeInterps {
                    match self {
                        $(
                            Self::$variant(interp) => interp.type_interps(),
                        )*
                    }
                }

                pub fn domain(&self) -> crate::fodot::vocabulary::DomainRef<$ret_lifetime> {
                    match self {
                        $(
                            Self::$variant(interp) => interp.domain(),
                        )*
                    }
                }

                pub fn domain_full(&self) -> crate::fodot::structure::DomainFullRef<$ret_lifetime> {
                    match self {
                        $(
                            Self::$variant(interp) => interp.domain_full(),
                        )*
                    }
                }

                pub fn name(&self) -> &$ret_lifetime str {
                    match self {
                        $(
                            Self::$variant(interp) => interp.name(),
                        )*
                    }
                }
            }
        };
    }

    pub(crate) use common_impls;

    macro_rules! combined_nullaries {
        (
            #[type(
                $type:ident,
                $mutability:ident,
                $codomain:ty,
                $codomain_full_ty:ty,
                $ret_lifetime:lifetime
                $(, {$($extra:tt)*})?
            )]
            $(#[$attrs:meta])*
            $vis:vis enum $name:ident$(<$($lt:lifetime),*>)? {
                $var1:ident($var1_name:ident$(<$($lt_var1:lifetime),*>)?),
                $var2:ident($var2_name:ident$(<$($lt_var2:lifetime),*>)?) $(,)?
            }
        ) => {
            $(#[$attrs])*
            $vis enum $name<$($($lt),*)?> {
                $var1($var1_name<$($($lt_var1),*)?>),
                $var2($var2_name<$($($lt_var2),*)?>),
            }
            combined_nullaries! {
                type: $type $mutability,
                ($name<$($($lt),*)?>,
                $ret_lifetime,
                ($codomain, $codomain),
                $codomain_full_ty),
                {$($($extra)*)?},
                ($var1, $var1_name<$($($lt_var1),*)?>, itertools::Either::Left),
                ($var2, $var2_name<$($($lt_var2),*)?>, itertools::Either::Right),
            }
        };
        (
            #[type(
                $type:ident,
                $mutability:ident,
                ($codomain_in:ty, $codomain_out:ty),
                $codomain_full_ty:ty,
                $ret_lifetime:lifetime
                $(, {$($extra:tt)*})?
            )]
            $(#[$attrs:meta])*
            $vis:vis enum $name:ident$(<$($lt:lifetime),*>)? {
                $var1:ident($var1_name:ident$(<$($lt_var1:lifetime),*>)?),
                $var2:ident($var2_name:ident$(<$($lt_var2:lifetime),*>)?) $(,)?
            }
        ) => {
            $(#[$attrs])*
            $vis enum $name<$($($lt),*)?> {
                $var1($var1_name<$($($lt_var1),*)?>),
                $var2($var2_name<$($($lt_var2),*)?>),
            }
            combined_nullaries! {
                type: $type $mutability,
                $name<$($($lt),*)?>,
                $ret_lifetime,
                ($codomain_in, $codomain_out),
                $codomain_full_ty:ty,
                {$($($extra)*)?},
                ($var1, $var1_name<$($($lt_var1),*)?>, itertools::Either::Left),
                ($var2, $var2_name<$($($lt_var2),*)?>, itertools::Either::Right),
            }
        };
        (
            type: partial immutable,
            $($rest:tt)*
        ) => {
            crate::fodot::structure::pfunc::common_impls!{
                $($rest)*
            }
            combined_nullaries!{
                common:
                $($rest)*
            }
            combined_nullaries!{
                partial immutable:
                $($rest)*
            }
            combined_nullaries!{
                into partial immutable:
                $($rest)*
            }
        };
        (
            type: partial mutable,
            $($rest:tt)*
        ) => {
            crate::fodot::structure::pfunc::common_impls!{
                $($rest)*
            }
            combined_nullaries!{
                common:
                $($rest)*
            }
            combined_nullaries!{
                partial immutable:
                $($rest)*
            }
            combined_nullaries!{
                partial mutable:
                $($rest)*
            }
            combined_nullaries!{
                into partial mutable:
                $($rest)*
            }
        };
        (
            type: complete immutable,
            $($rest:tt)*
        ) => {
            crate::fodot::structure::pfunc::common_impls!{
                $($rest)*
            }
            combined_nullaries!{
                common:
                $($rest)*
            }
            combined_nullaries!{
                complete immutable:
                $($rest)*
            }
            combined_nullaries!{
                into complete immutable:
                $($rest)*
            }
        };
        (
            type: complete mutable,
            $($rest:tt)*
        ) => {
            crate::fodot::structure::pfunc::common_impls!{
                $($rest)*
            }
            combined_nullaries!{
                common:
                $($rest)*
            }
            combined_nullaries!{
                complete immutable:
                $($rest)*
            }
            combined_nullaries!{
                complete mutable:
                $($rest)*
            }
            combined_nullaries!{
                into complete mutable:
                $($rest)*
            }
        };
        (
            common:
            ($name:ident<$($lt:lifetime),*>,
            $ret_lifetime:lifetime,
            ($codomain_in:ty, $codomain_out:ty),
            $codomain_full_ty:ty),
            {$($rest_1:tt)*},
            $(($variant:ident $($rest_2:tt)*)),* $(,)?
        ) => {
            combined_nullaries! {
                common_split:
                ($name<$($lt),*>,
                $ret_lifetime,
                ($codomain_in, $codomain_out),
                $codomain_full_ty),
                {$($rest_1)*},
                $(($variant $($rest_2)*)),*
            }
            impl<$($lt),*> $name<$($lt),*> {
                // not used for immutable datastructures
                #[allow(unused)]
                pub(crate) fn symbol_codomain_from_type_element(
                    &self,
                    value: crate::fodot::structure::TypeElement,
                ) -> Result<$codomain_in, crate::fodot::error::NullaryError> {
                    match self {
                        $(
                            Self::$variant(interp) => interp.symbol_codomain_from_type_element(value),
                        )*
                    }
                }

                pub(crate) fn symb_codomain_full(&self) -> crate::fodot::structure::TypeFull<'a> {
                    match self {
                        $(
                            Self::$variant(interp) => interp.symb_codomain_full(),
                        )*
                    }
                }
            }
        };
        (
            common_split:
            ($name:ident<$($lt:lifetime),*>,
            $ret_lifetime:lifetime,
            ($codomain_in:ty, $codomain_out:ty),
            $codomain_full_ty:ty),
            {$($rest_1:tt)*},
            ($variant_1:ident $($rest_2:tt)*),
            ($variant_2:ident $($rest_3:tt)*) $(,)?
        ) => {
            impl<$($lt),*> $name<$($lt),*> {
                pub fn codomain_full(&self) -> Option<$codomain_full_ty> {
                    match self {
                        Self::$variant_1(_) => None,
                        Self::$variant_2(interp) => Some(interp.codomain_full()),
                    }
                }
            }
        };
        (
            partial immutable:
            ($name:ident<$($lt:lifetime),*>,
            $ret_lifetime:lifetime,
            ($codomain_in:ty, $codomain_out:ty) $($rest:tt)*),
            {
                $complete_prefix1:ident :: $complete_prefix2:ident :: $complete_name:ident$(<$($lt_complete:lifetime),*>)?,
                $complete_im_prefix1:ident :: $complete_im_prefix2:ident :: $complete_im_name:ident $(,)?
            },
            $(($variant:ident, $variant_name:ident<$($variant_lifetime:lifetime),*>, $iter:path)),* $(,)?
        ) => {
            impl<$($lt),*> $name<$($lt),*> {
                /// Get the interpretation
                pub fn get(&self) -> Option<$codomain_out> {
                    match self {
                        $(
                            Self::$variant(interp) => interp.get(),
                        )*
                    }
                }

                /// Returns true if the proposition has an interpretation.
                pub fn is_complete(&self) -> bool {
                    match self {
                        $(
                            Self::$variant(interp) => interp.is_complete(),
                        )*
                    }
                }

                pub(crate) fn any_known(&self) -> bool {
                    self.is_complete()
                }

                pub(crate) fn amount_known(&self) -> usize {
                    if self.is_complete() { 1 } else { 0 }
                }

                pub(crate) fn amount_unknown(&self) -> usize {
                    if self.is_complete() { 0 } else { 1 }
                }

                /// Returns true if the proposition is unknown.
                pub fn is_unknown(&self) -> bool {
                    match self {
                        $(
                            Self::$variant(interp) => !interp.is_complete(),
                        )*
                    }
                }

                pub fn iter<'zz>(&'zz self) -> impl Iterator<Item = (ArgsRef<$ret_lifetime>, $codomain_out)> + 'zz {
                    match self {
                        $(
                            Self::$variant(interp) => $iter(interp.iter()),
                        )*
                    }
                }

                pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<$ret_lifetime>, $codomain_out)> + use<$ret_lifetime> {
                    match self {
                        $(
                            Self::$variant(interp) => $iter(interp.iter()),
                        )*
                    }
                }

                pub fn try_into_complete(self) -> Result<
                    $complete_prefix1::$complete_prefix2::$complete_name<$($($lt_complete),*)?>,
                    Self
                > {
                    match self {
                        $(
                            Self::$variant(interp) => interp.try_into_complete()
                            .map($complete_prefix1::$complete_prefix2::$complete_name::$variant)
                            .map_err(Self::$variant),
                        )*
                    }
                }

                pub fn try_as_complete<'b>(&'b self) -> Result<
                    $complete_im_prefix1::$complete_im_prefix2::$complete_im_name<'b>,
                    ()
                > {
                    match self {
                        $(
                            Self::$variant(interp) => interp.try_as_complete()
                                .map($complete_im_prefix1::$complete_im_prefix2::$complete_im_name::$variant),
                        )*
                    }
                }
            }
        };
        (
            partial mutable:
            ($name:ident<$($lt:lifetime),*>,
            $ret_lifetime:lifetime,
            ($codomain_in:ty, $codomain_out:ty) $($rest_4:tt)*),
            {$($extra:tt)*},
            $(($variant:ident, $variant_name:ident<$($variant_lifetime:lifetime),*> $($rest:tt)*)),* $(,)?
        ) => {
            impl<$($lt),*> $name<$($lt),*> {
                /// Set the interpretation
                pub fn set(&mut self, value: Option<$codomain_in>) -> Result<(), CodomainError> {
                    match self {
                        $(
                            Self::$variant(interp) => interp.nullary_set(value),
                        )*
                    }
                }

                pub(crate) fn nullary_set(
                    &mut self,
                    value: Option<$codomain_in>
                ) -> Result<(), CodomainError> {
                    self.set(value)
                }

                pub(crate) fn symbol_set(
                    &mut self,
                    args: ArgsRef,
                    value: Option<$codomain_in>
                ) -> Result<(), crate::fodot::error::PfuncError> {
                    if args.is_unit() {
                        Ok(self.set(value)?)
                    } else {
                        Err(DomainMismatch {
                            expected: self.domain().str_domain(),
                            found: args.domain().as_domain().str_domain(),
                        }.into())
                    }
                }

                /// Sets the interpretation if the interpretation is unknown.
                ///
                /// Returns a [bool] which is true if the proposition was unknown, false otherwise.
                pub fn set_if_unknown(&mut self, value: $codomain_in) -> Result<bool, CodomainError> {
                    match self {
                        $(
                            Self::$variant(interp) => interp.nullary_set_if_unknown(value),
                        )*
                    }
                }

                pub(crate) fn nullary_set_if_unknown(
                    &mut self,
                    value: $codomain_in
                ) -> Result<bool, CodomainError> {
                    self.set_if_unknown(value)
                }

                pub(crate) fn symbol_set_if_unknown(
                    &mut self,
                    args: ArgsRef,
                    value: $codomain_in
                ) -> Result<bool, crate::fodot::error::ExtendedPfuncError> {
                    if args.is_unit() {
                        Ok(self.set_if_unknown(value)?)
                    } else {
                        Err(DomainMismatch {
                            expected: self.domain().str_domain(),
                            found: args.domain().as_domain().str_domain(),
                        }.into())
                    }
                }

                pub(crate) fn symbol_set_all_unknown_to_value(
                    &mut self,
                    value: $codomain_in
                ) -> Result<(), crate::fodot::error::NullaryError> {
                    self.set_if_unknown(value)?;
                    Ok(())
                }
            }
        };
        (
            complete immutable:
            ($name:ident<$($lt:lifetime),*>,
            $ret_lifetime:lifetime,
            ($codomain_in:ty, $codomain_out:ty) $($rest_3:tt)*),
            {$($extra:tt)*},
            $(($variant:ident, $variant_name:ident<$($variant_lifetime:lifetime),*>, $iter_gen:path)),* $(,)?
        ) => {
            impl<$($lt),*> $name<$($lt),*> {
                /// Get the interpretation
                pub fn get(&self) -> $codomain_out {
                    match self {
                        $(
                            Self::$variant(interp) => interp.get(),
                        )*
                    }
                }

                pub fn iter<'zz>(&'zz self) -> impl Iterator<Item = (ArgsRef<$ret_lifetime>, $codomain_out)> + 'zz {
                    match self {
                        $(
                            Self::$variant(interp) => $iter_gen(interp.iter()),
                        )*
                    }
                }

                pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<$ret_lifetime>, $codomain_out)> {
                    match self {
                        $(
                            Self::$variant(interp) => $iter_gen(interp.into_iter()),
                        )*
                    }
                }
            }
        };
        (
            complete mutable:
            ($name:ident<$($lt:lifetime),*>,
            $ret_lifetime:lifetime,
            ($codomain_in:ty, $codomain_out:ty) $($rest_2:tt)*),
            {$($extra:tt)*},
            $(($variant:ident, $variant_name:ident<$($variant_lifetime:lifetime),*> $($rest:tt)*)),* $(,)?
        ) => {
            impl<$($lt),*> $name<$($lt),*> {
                /// Set the interpretation
                pub fn set(&mut self, value: $codomain_in) -> Result<(), CodomainError> {
                    match self {
                        $(
                            Self::$variant(interp) => interp.nullary_set(value),
                        )*
                    }
                }

                pub(crate) fn nullary_set(
                    &mut self,
                    value: $codomain_in
                ) -> Result<(), CodomainError> {
                    self.set(value)
                }

                pub(crate) fn symbol_set(
                    &mut self,
                    args: ArgsRef,
                    value: $codomain_in
                ) -> Result<(), PfuncError> {
                    if args.is_unit() {
                        Ok(self.set(value)?)
                    } else {
                        Err(DomainMismatch {
                            expected: self.domain().str_domain(),
                            found: args.domain().as_domain().str_domain(),
                        }.into())
                    }
                }
            }
        };
        (
            into $kind:ident $mutability:ident:
            ($name:ident<$($lt:lifetime),*>,
            $ret_lifetime:lifetime,
            ($codomain_in:ty, $codomain_out:ty) $($rest_3:tt)*),
            {$($extra:tt)*},
            $(($variant:ident, $variant_name:ident<$($variant_lifetime:lifetime),*> $($rest:tt)*)),* $(,)?
        ) => {
            $(
                impl<$($variant_lifetime),*>
                    From<$variant_name<$($variant_lifetime),*>> for
                        crate::fodot::structure::pfunc::$kind::$mutability::SymbolInterp<$ret_lifetime>
                {
                    fn from(value: $variant_name<$($variant_lifetime),*>) -> Self {
                        $name::$variant(value).into()
                    }
                }

                impl<$($variant_lifetime),*>
                    From<$variant_name<$($variant_lifetime),*>> for
                        crate::fodot::structure::pfunc::$kind::$mutability::NullaryInterp<$ret_lifetime>
                {
                    fn from(value: $variant_name<$($variant_lifetime),*>) -> Self {
                        $name::$variant(value).into()
                    }
                }
            )*
        }
    }

    pub(crate) use combined_nullaries;

    macro_rules! combined_funcs {
        (
            #[type(
                $type:ident,
                $mutability:ident,
                ($codomain_in:ty, $codomain_out:ty),
                $codomain_full_ty:ty,
                $ret_lifetime:lifetime
                $(, {$($extra:tt)*})?
            )]
            $(#[$attrs:meta])*
            $vis:vis enum $name:ident$(<$($lt:lifetime),*>)? {
                $var1:ident($var1_name:ident$(<$($lt_var1:lifetime),*>)?),
                $var2:ident($var2_name:ident$(<$($lt_var2:lifetime),*>)?) $(,)?
            }
        ) => {
            $(#[$attrs])*
            $vis enum $name<$($($lt),*)?> {
                $var1($var1_name<$($($lt_var1),*)?>),
                $var2($var2_name<$($($lt_var2),*)?>),
            }
            combined_funcs! {
                type: $type $mutability,
                ($name<$($($lt),*)?>,
                $ret_lifetime,
                ($codomain_in, $codomain_out),
                $codomain_full_ty),
                {$($($extra)*)?},
                ($var1, $var1_name<$($($lt_var1),*)?>, Either::Left),
                ($var2, $var2_name<$($($lt_var2),*)?>, Either::Right),
            }
        };
        (
            #[type(
                $type:ident,
                $mutability:ident,
                $codomain:ty,
                $codomain_full_ty:ty,
                $ret_lifetime:lifetime
                $(, {$($extra:tt)*})?
            )]
            $(#[$attrs:meta])*
            $vis:vis enum $name:ident$(<$($lt:lifetime),*>)? {
                $var1:ident($var1_name:ident$(<$($lt_var1:lifetime),*>)?),
                $var2:ident($var2_name:ident$(<$($lt_var2:lifetime),*>)?) $(,)?
            }
        ) => {
            $(#[$attrs])*
            $vis enum $name<$($($lt),*)?> {
                $var1($var1_name<$($($lt_var1),*)?>),
                $var2($var2_name<$($($lt_var2),*)?>),
            }
            combined_funcs! {
                type: $type $mutability,
                ($name<$($($lt),*)?>,
                $ret_lifetime,
                ($codomain, $codomain),
                $codomain_full_ty),
                {$($($extra)*)?},
                ($var1, $var1_name<$($($lt_var1),*)?>, Either::Left),
                ($var2, $var2_name<$($($lt_var2),*)?>, Either::Right),
            }
        };
        (
            type: partial immutable,
            $($rest:tt)*
        ) => {
            crate::fodot::structure::pfunc::common_impls! {
                $($rest)*
            }
            combined_funcs!{
                common:
                $($rest)*
            }
            combined_funcs!{
                partial immutable:
                $($rest)*
            }
            combined_funcs!{
                into partial immutable:
                $($rest)*
            }
        };
        (
            type: partial mutable,
            $($rest:tt)*
        ) => {
            crate::fodot::structure::pfunc::common_impls!{
                $($rest)*
            }
            combined_funcs!{
                common:
                $($rest)*
            }
            combined_funcs!{
                partial immutable:
                $($rest)*
            }
            combined_funcs!{
                partial mutable:
                $($rest)*
            }
            combined_funcs!{
                into partial mutable:
                $($rest)*
            }
        };
        (
            type: complete immutable,
            $($rest:tt)*
        ) => {
            crate::fodot::structure::pfunc::common_impls!{
                $($rest)*
            }
            combined_funcs!{
                common:
                $($rest)*
            }
            combined_funcs!{
                complete immutable:
                $($rest)*
            }
            combined_funcs!{
                into complete immutable:
                $($rest)*
            }
        };
        (
            type: complete mutable,
            $($rest:tt)*
        ) => {
            crate::fodot::structure::pfunc::common_impls!{
                $($rest)*
            }
            combined_funcs!{
                common:
                $($rest)*
            }
            combined_funcs!{
                complete immutable:
                $($rest)*
            }
            combined_funcs!{
                complete mutable:
                $($rest)*
            }
            combined_funcs!{
                into complete mutable:
                $($rest)*
            }
        };
        (
            common:
            ($name:ident<$($lt:lifetime),*>,
            $ret_lifetime:lifetime,
            ($codomain_in:ty, $codomain_out:ty),
            $codomain_full_ty:ty),
            {$($rest_1:tt)*},
            $(($variant:ident $($rest_2:tt)*)),* $(,)?
        ) => {
            impl<$($lt),*> $name<$($lt),*> {
                // not used for immutable datastructures
                #[allow(unused)]
                pub(crate) fn symbol_codomain_from_type_element(
                    &self,
                    value: crate::fodot::structure::TypeElement,
                ) -> Result<$codomain_in, crate::fodot::error::NullaryError> {
                    match self {
                        $(
                            Self::$variant(interp) => interp.symbol_codomain_from_type_element(value),
                        )*
                    }
                }

                pub(crate) fn symb_codomain_full(&self) -> crate::fodot::structure::TypeFull<'a> {
                    match self {
                        $(
                            Self::$variant(interp) => interp.symb_codomain_full(),
                        )*
                    }
                }
            }
            combined_funcs! {
                common_split:
                ($name<$($lt),*>,
                $ret_lifetime,
                ($codomain_in, $codomain_out),
                $codomain_full_ty),
                {$($rest_1)*},
                $(($variant $($rest_2)*)),*
            }
        };
        (
            common_split:
            ($name:ident<$($lt:lifetime),*>,
            $ret_lifetime:lifetime,
            ($codomain_in:ty, $codomain_out:ty),
            $codomain_full_ty:ty),
            {$($rest_1:tt)*},
            ($variant_1:ident $($rest_2:tt)*),
            ($variant_2:ident $($rest_3:tt)*) $(,)?
        ) => {
            impl<$($lt),*> $name<$($lt),*> {
                pub fn codomain_full(&self) -> Option<$codomain_full_ty> {
                    match self {
                        Self::$variant_1(_) => None,
                        Self::$variant_2(interp) => Some(interp.codomain_full()),
                    }
                }
            }
        };
        (
            partial immutable:
            ($name:ident<$($lt:lifetime),*>,
            $ret_lifetime:lifetime,
            ($codomain_in:ty, $codomain_out:ty) $($rest_2:tt)*),
            {
                $complete_prefix1:ident :: $complete_prefix2:ident :: $complete_name:ident$(<$($lt_complete:lifetime),*>)?,
                $complete_im_prefix1:ident :: $complete_im_prefix2:ident :: $complete_im_name:ident $(,)?
            },
            $(($variant:ident, $variant_name:ident<$($variant_lifetime:lifetime),*>, $iter_gen:path)),* $(,)?
        ) => {
            impl<$($lt),*> $name<$($lt),*> {
                /// Get the interpretation
                pub fn get(&self, args: ArgsRef) -> Result<Option<$codomain_out>, ArgMismatchError> {
                    match self {
                        $(
                            Self::$variant(interp) => interp.get(args),
                        )*
                    }
                }

                /// Returns true if the proposition has an interpretation.
                pub fn is_complete(&self) -> bool {
                    match self {
                        $(
                            Self::$variant(interp) => interp.is_complete(),
                        )*
                    }
                }

                pub fn any_known(&self) -> bool {
                    match self {
                        $(
                            Self::$variant(interp) => interp.any_known(),
                        )*
                    }
                }

                pub fn amount_known(&self) -> usize {
                    match self {
                        $(
                            Self::$variant(interp) => interp.amount_known(),
                        )*
                    }
                }

                pub fn amount_unknown(&self) -> usize {
                    match self {
                        $(
                            Self::$variant(interp) => interp.amount_unknown(),
                        )*
                    }
                }

                pub fn iter<'zz>(&'zz self) -> impl Iterator<Item = (ArgsRef<$ret_lifetime>, $codomain_out)> + 'zz {
                    match self {
                        $(
                            Self::$variant(interp) => $iter_gen(interp.iter()),
                        )*
                    }
                }

                pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<$ret_lifetime>, $codomain_out)> {
                    match self {
                        $(
                            Self::$variant(interp) => $iter_gen(interp.into_iter()),
                        )*
                    }
                }

                pub fn try_into_complete(self) -> Result<
                    $complete_prefix1::$complete_prefix2::$complete_name<$($($lt_complete),*)?>,
                    Self
                > {
                    match self {
                        $(
                            Self::$variant(interp) => interp.try_into_complete()
                            .map($complete_prefix1::$complete_prefix2::$complete_name::$variant)
                            .map_err(Self::$variant),
                        )*
                    }
                }

                pub fn try_as_complete<'b>(&'b self) -> Result<
                    $complete_im_prefix1::$complete_im_prefix2::$complete_im_name<'b>,
                    ()
                > {
                    match self {
                        $(
                            Self::$variant(interp) => interp.try_as_complete()
                                .map($complete_im_prefix1::$complete_im_prefix2::$complete_im_name::$variant),
                        )*
                    }
                }
            }
        };
        (
            partial mutable:
            ($name:ident<$($lt:lifetime),*>,
            $ret_lifetime:lifetime,
            ($codomain_in:ty, $codomain_out:ty) $($rest3:tt)*),
            {$($extra:tt)*},
            $(($variant:ident, $variant_name:ident<$($variant_lifetime:lifetime),*>, $iter_gen:path)),* $(,)?
        ) => {
            impl<$($lt),*> $name<$($lt),*> {
                /// Set the interpretation
                pub fn set(&mut self, args: ArgsRef, value: Option<$codomain_in>) -> Result<(), PfuncError> {
                    match self {
                        $(
                            Self::$variant(interp) => Ok(interp.set(args, value)?),
                        )*
                    }
                }

                pub(crate) fn symbol_set(
                    &mut self,
                    args: ArgsRef,
                    value: Option<$codomain_in>
                ) -> Result<(), PfuncError> {
                    self.set(args, value)
                }

                pub fn set_if_unknown(&mut self, args: ArgsRef, value: $codomain_in) -> Result<bool, PfuncError> {
                    match self {
                        $(
                            Self::$variant(interp) => Ok(interp.set_if_unknown(args, value)?),
                        )*
                    }
                }

                pub(crate) fn symbol_set_if_unknown(
                    &mut self,
                    args: ArgsRef,
                    value: $codomain_in
                ) -> Result<bool, crate::fodot::error::ExtendedPfuncError> {
                    match self {
                        $(
                            Self::$variant(interp) => Ok(interp.set_if_unknown(args, value)?),
                        )*
                    }
                }

                pub fn set_all_unknown_to_value(&mut self, value: $codomain_in) -> Result<(), CodomainError>{
                    match self {
                        $(
                            Self::$variant(interp) => interp.func_set_all_unknown_to_value(value),
                        )*
                    }
                }

                pub(crate) fn symbol_set_all_unknown_to_value(
                    &mut self,
                    value: $codomain_in,
                ) -> Result<(), crate::fodot::error::NullaryError> {
                    Ok(self.set_all_unknown_to_value(value)?)
                }
            }
        };
        (
            complete immutable:
            ($name:ident<$($lt:lifetime),*>,
            $ret_lifetime:lifetime,
            ($codomain_in:ty, $codomain_out:ty) $($rest_4:tt)*),
            {$($extra:tt)*},
            $(($variant:ident, $variant_name:ident<$($variant_lifetime:lifetime),*>, $iter_gen:path)),* $(,)?
        ) => {
            impl<$($lt),*> $name<$($lt),*> {
                /// Get the interpretation
                pub fn get(&self, args: ArgsRef) -> Result<$codomain_out, ArgMismatchError> {
                    match self {
                        $(
                            Self::$variant(interp) => interp.get(args),
                        )*
                    }
                }

                pub fn iter<'zz>(&'zz self) -> impl Iterator<Item = (ArgsRef<$ret_lifetime>, $codomain_out)> + 'zz {
                    match self {
                        $(
                            Self::$variant(interp) => $iter_gen(interp.iter()),
                        )*
                    }
                }

                pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<$ret_lifetime>, $codomain_out)> {
                    match self {
                        $(
                            Self::$variant(interp) => $iter_gen(interp.into_iter()),
                        )*
                    }
                }
            }
        };
        (
            complete mutable:
            ($name:ident<$($lt:lifetime),*>,
            $ret_lifetime:lifetime,
            ($codomain_in:ty, $codomain_out:ty) $($rest32:tt)*),
            {$($extra:tt)*},
            $(($variant:ident, $variant_name:ident<$($variant_lifetime:lifetime),*>, $iter_gen:path)),* $(,)?
        ) => {
            impl<$($lt),*> $name<$($lt),*> {
                /// Set the interpretation
                pub fn set(&mut self, args: ArgsRef, value: $codomain_in) -> Result<(), PfuncError> {
                    match self {
                        $(
                            Self::$variant(interp) => Ok(interp.set(args, value)?),
                        )*
                    }
                }

                pub(crate) fn symbol_set(
                    &mut self,
                    args: ArgsRef,
                    value: $codomain_in
                ) -> Result<(), PfuncError> {
                    self.set(args, value)
                }
            }
        };
        (
            into $kind:ident $mutability:ident:
            ($name:ident<$($lt:lifetime),*>,
            $ret_lifetime:lifetime,
            ($codomain_in:ty, $codomain_out:ty) $($rest4:tt)*),
            {$($extra:tt)*},
            $(($variant:ident, $variant_name:ident<$($variant_lifetime:lifetime),*> $($rest:tt)*)),* $(,)?
        ) => {
            $(
                impl<$($variant_lifetime),*>
                    From<$variant_name<$($variant_lifetime),*>> for
                        crate::fodot::structure::pfunc::$kind::$mutability::SymbolInterp<$ret_lifetime>
                {
                    fn from(value: $variant_name<$($variant_lifetime),*>) -> Self {
                        $name::$variant(value).into()
                    }
                }

                impl<$($variant_lifetime),*>
                    From<$variant_name<$($variant_lifetime),*>> for
                        crate::fodot::structure::pfunc::$kind::$mutability::FuncInterp<$ret_lifetime>
                {
                    fn from(value: $variant_name<$($variant_lifetime),*>) -> Self {
                        $name::$variant(value).into()
                    }
                }
            )*
        }
    }

    pub(crate) use combined_funcs;

    macro_rules! partial_nullary_symbol_methods {
        (
            ($codomain_in:ty, $codomain_out:ty),
            impl$(<$($lt_def:lifetime),* $(,)?>)? $name:ident$(<$($lt_use:lifetime),* $(,)?>)?
        ) => {
            impl$(<$($lt_def),*>)? $name$(<$($lt_use),*>)? {
                pub(crate) fn symbol_get(
                    &self,
                    args: crate::fodot::structure::ArgsRef
                ) -> Result<Option<$codomain_out>, crate::fodot::error::ArgMismatchError> {
                    if args.is_unit() {
                        Ok(self.get())
                    } else {
                        Err(crate::fodot::error::DomainMismatch {
                            expected: self.domain().str_domain(),
                            found: args.domain().as_domain().str_domain(),
                        }.into())
                    }
                }
            }
        };
    }

    pub(crate) use partial_nullary_symbol_methods;

    macro_rules! complete_nullary_symbol_methods {
        (
            ($codomain_in:ty, $codomain_out:ty),
            impl$(<$($lt_def:lifetime),* $(,)?>)? $name:ident$(<$($lt_use:lifetime),* $(,)?>)?
        ) => {
            impl$(<$($lt_def),*>)? $name$(<$($lt_use),*>)? {
                pub(crate) fn symbol_get(
                    &self,
                    args: crate::fodot::structure::ArgsRef
                ) -> Result<$codomain_out, crate::fodot::error::ArgMismatchError> {
                    if args.is_unit() {
                        Ok(self.get())
                    } else {
                        Err(crate::fodot::error::DomainMismatch {
                            expected: self.domain().str_domain(),
                            found: args.domain().as_domain().str_domain(),
                        }.into())
                    }
                }
            }
        };
    }

    pub(crate) use complete_nullary_symbol_methods;

    macro_rules! partial_func_symbol_methods {
        (
            ($codomain_in:ty, $codomain_out:ty),
            impl$(<$($lt_def:lifetime),* $(,)?>)? $name:ident$(<$($lt_use:lifetime),* $(,)?>)?
        ) => {
            impl$(<$($lt_def),*>)? $name$(<$($lt_use),*>)? {
                pub(crate) fn symbol_get(
                    &self,
                    args: crate::fodot::structure::ArgsRef
                ) -> Result<Option<$codomain_out>, crate::fodot::error::ArgMismatchError> {
                    self.get(args)
                }
            }
        };
    }

    pub(crate) use partial_func_symbol_methods;

    macro_rules! complete_func_symbol_methods {
        (
            ($codomain_in:ty, $codomain_out:ty),
            impl$(<$($lt_def:lifetime),* $(,)?>)? $name:ident$(<$($lt_use:lifetime),* $(,)?>)?
        ) => {
            impl$(<$($lt_def),*>)? $name$(<$($lt_use),*>)? {
                pub(crate) fn symbol_get(
                    &self,
                    args: crate::fodot::structure::ArgsRef
                ) -> Result<$codomain_out, crate::fodot::error::ArgMismatchError> {
                    self.get(args)
                }
            }
        };
    }

    pub(crate) use complete_func_symbol_methods;
}
