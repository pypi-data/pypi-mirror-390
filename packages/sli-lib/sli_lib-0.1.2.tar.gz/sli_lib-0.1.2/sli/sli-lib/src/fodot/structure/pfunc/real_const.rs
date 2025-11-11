use super::{
    combined_nullaries, complete_nullary_display, complete_nullary_symbol_methods,
    impl_real_from_type_element, partial_nullary_display, partial_nullary_symbol_methods,
};
use crate::fodot::{
    display_as_debug,
    error::{CodomainError, DomainMismatch, PfuncError},
    fmt::{FodotDisplay, FodotOptions, FormatOptions},
    structure::{
        ArgsRef, RealTypeFull, TypeFull,
        pfunc::{PfuncDeclInterp, RealTypeDeclInterp},
    },
    vocabulary::Real,
};
use comp_core::structure::{complete as cccomplete, partial as ccpartial};
use core::{fmt::Display, ops::Deref};
use sli_collections::iterator::Iterator;

pub mod partial {
    use super::*;
    pub mod immutable {
        use super::*;
        combined_nullaries! {
            #[type(
                partial,
                immutable,
                Real,
                RealTypeFull<'a>,
                'a,
                {
                    complete::immutable::RealConstSymbolInterp<'a>,
                    complete::immutable::RealConstSymbolInterp,
                }
            )]
            /// A combination of an [RealConstInterp] and an [RealTypeConstInterp].
            #[derive(Clone, Debug)]
            pub enum RealConstSymbolInterp<'a> {
                Real(RealConstInterp<'a>),
                RealType(RealTypeConstInterp<'a>),
            }
        }

        partial_nullary_symbol_methods! {
            (Real, Real),
            impl<'a> RealConstSymbolInterp<'a>
        }

        /// A partial immutable interpretation of a constant with a real codomain.
        #[derive(Clone)]
        pub struct RealConstInterp<'a> {
            pub(crate) interp: ccpartial::immutable::RealConstInterp<'a>,
            pub(crate) decl: PfuncDeclInterp<'a>,
        }

        impl<'a> Deref for RealConstInterp<'a> {
            type Target = PfuncDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        impl_real_from_type_element!(impl<'a> RealConstInterp<'a>);

        impl<'a> RealConstInterp<'a> {
            /// Get the interpretation
            pub fn get(&self) -> Option<Real> {
                self.interp.get()
            }

            /// Returns true if the proposition has an interpretation.
            pub fn is_complete(&self) -> bool {
                self.interp.is_complete()
            }

            /// Returns true if the proposition is unknown.
            pub fn is_unknown(&self) -> bool {
                !self.interp.is_complete()
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter(&self) -> impl Iterator<Item = (ArgsRef<'a>, Real)> + use<'a> {
                self.get()
                    .map(|f| (ArgsRef::empty(self.decl.domain_full()).unwrap(), f))
                    .into_iter()
            }

            /// Returns an owned iterator over all arguments and their corresponding interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, Real)> {
                self.iter()
            }

            /// Try converting this interpretation into its complete counterpart.
            ///
            /// This function returns the original interpretation in [Err] if the interpretation is
            /// not complete.
            pub fn try_into_complete(
                self,
            ) -> Result<complete::immutable::RealConstInterp<'a>, Self> {
                match self.interp.try_into_complete() {
                    Ok(interp) => Ok(complete::immutable::RealConstInterp {
                        interp,
                        decl: self.decl,
                    }),
                    Err(interp) => Err(Self {
                        interp,
                        decl: self.decl,
                    }),
                }
            }

            /// Try converting this interpretation into its complete immutable counterpart.
            ///
            /// This function returns [Err] if the interpretation is not complete.
            pub fn try_as_complete<'b>(
                &'b self,
            ) -> Result<complete::immutable::RealConstInterp<'b>, ()> {
                match self.interp.try_as_im_complete() {
                    Ok(interp) => Ok(complete::immutable::RealConstInterp {
                        interp,
                        decl: self.decl.clone(),
                    }),
                    Err(_) => Err(()),
                }
            }

            pub(crate) fn symb_codomain_full(&self) -> TypeFull<'a> {
                TypeFull::Real
            }
        }

        impl FodotOptions for RealConstInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for RealConstInterp<'_> {
            fn fmt(
                fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>,
            ) -> std::fmt::Result {
                partial_nullary_display(fmt.value.name(), fmt.value.get(), fmt.options, f)
            }
        }

        impl Display for RealConstInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(RealConstInterp<'a>, gen: ('a));

        /// A partial immutable interpretation of a constant with a real subtype as codomain.
        #[derive(Clone)]
        pub struct RealTypeConstInterp<'a> {
            pub(crate) interp: ccpartial::immutable::RealTypeConstInterp<'a>,
            pub(crate) decl: RealTypeDeclInterp<'a>,
        }

        impl<'a> Deref for RealTypeConstInterp<'a> {
            type Target = RealTypeDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        impl<'a> RealTypeConstInterp<'a> {
            /// Get the interpretation
            pub fn get(&self) -> Option<Real> {
                self.interp.get()
            }

            /// Returns true if the proposition has an interpretation.
            pub fn is_complete(&self) -> bool {
                self.interp.is_complete()
            }

            /// Returns true if the proposition is unknown.
            pub fn is_unknown(&self) -> bool {
                !self.interp.is_complete()
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter(&self) -> impl Iterator<Item = (ArgsRef<'a>, Real)> + use<'a> {
                self.get()
                    .map(|f| (ArgsRef::empty(self.decl.domain_full()).unwrap(), f))
                    .into_iter()
            }

            /// Returns an owned iterator over all arguments and their corresponding interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, Real)> {
                self.iter()
            }

            /// Try converting this interpretation into its complete counterpart.
            ///
            /// This function returns the original interpretation in [Err] if the interpretation is
            /// not complete.
            pub fn try_into_complete(
                self,
            ) -> Result<complete::immutable::RealTypeConstInterp<'a>, Self> {
                match self.interp.try_into_complete() {
                    Ok(interp) => Ok(complete::immutable::RealTypeConstInterp {
                        interp,
                        decl: self.decl,
                    }),
                    Err(interp) => Err(Self {
                        interp,
                        decl: self.decl,
                    }),
                }
            }

            /// Try converting this interpretation into its complete immutable counterpart.
            ///
            /// This function returns [Err] if the interpretation is not complete.
            pub fn try_as_complete<'b>(
                &'b self,
            ) -> Result<complete::immutable::RealTypeConstInterp<'b>, ()> {
                match self.interp.try_as_im_complete() {
                    Ok(interp) => Ok(complete::immutable::RealTypeConstInterp {
                        interp,
                        decl: self.decl.clone(),
                    }),
                    Err(_) => Err(()),
                }
            }

            pub(crate) fn symb_codomain_full(&self) -> TypeFull<'a> {
                TypeFull::RealType(self.codomain_full())
            }
        }

        impl FodotOptions for RealTypeConstInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for RealTypeConstInterp<'_> {
            fn fmt(
                fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>,
            ) -> std::fmt::Result {
                partial_nullary_display(fmt.value.name(), fmt.value.get(), fmt.options, f)
            }
        }

        impl Display for RealTypeConstInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(RealTypeConstInterp<'a>, gen: ('a));
    }

    pub mod mutable {
        use super::*;

        combined_nullaries! {
            #[type(
                partial,
                mutable,
                Real,
                RealTypeFull<'a>,
                'a,
                {
                    complete::mutable::RealConstSymbolInterp<'a>,
                    complete::immutable::RealConstSymbolInterp,
                }
            )]
            /// A combination of an [RealConstInterp] and an [RealTypeConstInterp].
            #[derive(Debug)]
            pub enum RealConstSymbolInterp<'a> {
                Real(RealConstInterp<'a>),
                RealType(RealTypeConstInterp<'a>),
            }
        }

        partial_nullary_symbol_methods! {
            (Real, Real),
            impl<'a> RealConstSymbolInterp<'a>
        }

        /// A partial mutable interpretation of a constant with an real codomain.
        pub struct RealConstInterp<'a> {
            pub(crate) interp: ccpartial::mutable::RealConstInterp<'a>,
            pub(crate) decl: PfuncDeclInterp<'a>,
        }

        impl<'a> Deref for RealConstInterp<'a> {
            type Target = PfuncDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        impl_real_from_type_element!(impl<'a> RealConstInterp<'a>);

        impl<'a> RealConstInterp<'a> {
            /// Get the interpretation
            pub fn get(&self) -> Option<Real> {
                self.interp.get()
            }

            /// Returns true if the proposition has an interpretation.
            pub fn is_complete(&self) -> bool {
                self.interp.is_complete()
            }

            /// Returns true if the proposition is unknown.
            pub fn is_unknown(&self) -> bool {
                !self.interp.is_complete()
            }

            pub fn set(&mut self, value: Option<Real>) {
                self.interp.set(value)
            }

            fn nullary_set(&mut self, value: Option<Real>) -> Result<(), CodomainError> {
                self.set(value);
                Ok(())
            }

            /// Sets the interpretation if the interpretation is unknown.
            ///
            /// Returns a [bool] which is true if the proposition was unknown, false otherwise.
            pub fn set_if_unknown(&mut self, value: Real) -> bool {
                self.interp.set_if_unknown(value)
            }

            fn nullary_set_if_unknown(&mut self, value: Real) -> Result<bool, CodomainError> {
                Ok(self.set_if_unknown(value))
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter(&self) -> impl Iterator<Item = (ArgsRef<'a>, Real)> + use<'a> {
                self.get()
                    .map(|f| (ArgsRef::empty(self.decl.domain_full()).unwrap(), f))
                    .into_iter()
            }

            /// Returns an owned iterator over all arguments and their corresponding interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, Real)> {
                self.iter()
            }

            /// Try converting this interpretation into its complete counterpart.
            ///
            /// This function returns the original interpretation in [Err] if the interpretation is
            /// not complete.
            pub fn try_into_complete(self) -> Result<complete::mutable::RealConstInterp<'a>, Self> {
                match self.interp.try_into_complete() {
                    Ok(interp) => Ok(complete::mutable::RealConstInterp {
                        interp,
                        decl: self.decl,
                    }),
                    Err(interp) => Err(Self {
                        interp,
                        decl: self.decl,
                    }),
                }
            }

            /// Try converting this interpretation into its complete immutable counterpart.
            ///
            /// This function returns [Err] if the interpretation is not complete.
            pub fn try_as_complete<'b>(
                &'b self,
            ) -> Result<complete::immutable::RealConstInterp<'b>, ()> {
                match self.interp.try_as_im_complete() {
                    Ok(interp) => Ok(complete::immutable::RealConstInterp {
                        interp,
                        decl: self.decl.clone(),
                    }),
                    Err(_) => Err(()),
                }
            }

            pub(crate) fn symb_codomain_full(&self) -> TypeFull<'a> {
                TypeFull::Real
            }
        }

        impl FodotOptions for RealConstInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for RealConstInterp<'_> {
            fn fmt(
                fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>,
            ) -> std::fmt::Result {
                partial_nullary_display(fmt.value.name(), fmt.value.get(), fmt.options, f)
            }
        }

        impl Display for RealConstInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(RealConstInterp<'a>, gen: ('a));

        /// A partial immutable interpretation of a constant with a real subtype as codomain.
        pub struct RealTypeConstInterp<'a> {
            pub(crate) interp: ccpartial::mutable::RealTypeConstInterp<'a>,
            pub(crate) decl: RealTypeDeclInterp<'a>,
        }

        impl<'a> Deref for RealTypeConstInterp<'a> {
            type Target = RealTypeDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        impl<'a> RealTypeConstInterp<'a> {
            /// Get the interpretation
            pub fn get(&self) -> Option<Real> {
                self.interp.get()
            }

            /// Returns true if the proposition has an interpretation.
            pub fn is_complete(&self) -> bool {
                self.interp.is_complete()
            }

            /// Returns true if the proposition is unknown.
            pub fn is_unknown(&self) -> bool {
                !self.interp.is_complete()
            }

            /// Sets the interpretation to the given value.
            pub fn set(&mut self, value: Option<Real>) -> Result<(), CodomainError> {
                self.interp.set(value).map_err(|_| CodomainError)
            }

            fn nullary_set(&mut self, value: Option<Real>) -> Result<(), CodomainError> {
                self.set(value)
            }

            /// Sets the interpretation if the interpretation is unknown.
            ///
            /// Returns a [bool] which is true if the proposition was unknown, false otherwise.
            pub fn set_if_unknown(&mut self, value: Real) -> Result<bool, CodomainError> {
                self.interp.set_if_unknown(value).map_err(|_| CodomainError)
            }

            fn nullary_set_if_unknown(&mut self, value: Real) -> Result<bool, CodomainError> {
                self.set_if_unknown(value)
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter(&self) -> impl Iterator<Item = (ArgsRef<'a>, Real)> + use<'a> {
                self.get()
                    .map(|f| (ArgsRef::empty(self.decl.domain_full()).unwrap(), f))
                    .into_iter()
            }

            /// Returns an owned iterator over all arguments and their corresponding interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, Real)> {
                self.iter()
            }

            /// Try converting this interpretation into its complete counterpart.
            ///
            /// This function returns the original interpretation in [Err] if the interpretation is
            /// not complete.
            pub fn try_into_complete(
                self,
            ) -> Result<complete::mutable::RealTypeConstInterp<'a>, Self> {
                match self.interp.try_into_complete() {
                    Ok(interp) => Ok(complete::mutable::RealTypeConstInterp {
                        interp,
                        decl: self.decl,
                    }),
                    Err(interp) => Err(Self {
                        interp,
                        decl: self.decl,
                    }),
                }
            }

            /// Try converting this interpretation into its complete immutable counterpart.
            ///
            /// This function returns [Err] if the interpretation is not complete.
            pub fn try_as_complete<'b>(
                &'b self,
            ) -> Result<complete::immutable::RealTypeConstInterp<'b>, ()> {
                match self.interp.try_as_im_complete() {
                    Ok(interp) => Ok(complete::immutable::RealTypeConstInterp {
                        interp,
                        decl: self.decl.clone(),
                    }),
                    Err(_) => Err(()),
                }
            }

            pub(crate) fn symb_codomain_full(&self) -> TypeFull<'a> {
                TypeFull::RealType(self.codomain_full())
            }
        }

        impl FodotOptions for RealTypeConstInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for RealTypeConstInterp<'_> {
            fn fmt(
                fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>,
            ) -> std::fmt::Result {
                partial_nullary_display(fmt.value.name(), fmt.value.get(), fmt.options, f)
            }
        }

        impl Display for RealTypeConstInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(RealTypeConstInterp<'a>, gen: ('a));
    }
}

pub mod complete {
    use super::*;
    pub mod immutable {
        use super::*;
        combined_nullaries! {
            #[type(complete, immutable, Real, RealTypeFull<'a>, 'a)]
            #[derive(Clone, Debug)]
            pub enum RealConstSymbolInterp<'a> {
                Real(RealConstInterp<'a>),
                RealType(RealTypeConstInterp<'a>),
            }
        }

        complete_nullary_symbol_methods! {
            (Real, Real),
            impl<'a> RealConstSymbolInterp<'a>
        }

        /// A complete immutable interpretation of a constant with a real codomain.
        #[derive(Clone)]
        pub struct RealConstInterp<'a> {
            pub(crate) interp: cccomplete::immutable::RealConstInterp<'a>,
            pub(crate) decl: PfuncDeclInterp<'a>,
        }

        impl<'a> Deref for RealConstInterp<'a> {
            type Target = PfuncDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        impl_real_from_type_element!(impl<'a> RealConstInterp<'a>);

        impl<'a> RealConstInterp<'a> {
            /// Get the interpretation.
            pub fn get(&self) -> Real {
                self.interp.get()
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter(&self) -> impl Iterator<Item = (ArgsRef<'a>, Real)> + use<'a> {
                core::iter::once((ArgsRef::empty(self.decl.domain_full()).unwrap(), self.get()))
            }

            /// Returns an owned iterator over all arguments and their corresponding interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, Real)> {
                self.iter()
            }

            pub(crate) fn symb_codomain_full(&self) -> TypeFull<'a> {
                TypeFull::Real
            }
        }

        impl FodotOptions for RealConstInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for RealConstInterp<'_> {
            fn fmt(
                fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>,
            ) -> std::fmt::Result {
                complete_nullary_display(fmt.value.name(), fmt.value.get(), fmt.options, f)
            }
        }

        impl Display for RealConstInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(RealConstInterp<'a>, gen: ('a));

        /// A complete immutable interpretation of a constant with a real subtype as codomain.
        #[derive(Clone)]
        pub struct RealTypeConstInterp<'a> {
            pub(crate) interp: cccomplete::immutable::RealTypeConstInterp<'a>,
            pub(crate) decl: RealTypeDeclInterp<'a>,
        }

        impl<'a> Deref for RealTypeConstInterp<'a> {
            type Target = RealTypeDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        impl<'a> RealTypeConstInterp<'a> {
            /// Get the interpretation.
            pub fn get(&self) -> Real {
                self.interp.get()
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter(&self) -> impl Iterator<Item = (ArgsRef<'a>, Real)> + use<'a> {
                core::iter::once((ArgsRef::empty(self.decl.domain_full()).unwrap(), self.get()))
            }

            /// Returns an owned iterator over all arguments and their corresponding interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, Real)> {
                self.iter()
            }

            pub(crate) fn symb_codomain_full(&self) -> TypeFull<'a> {
                TypeFull::RealType(self.codomain_full())
            }
        }

        impl FodotOptions for RealTypeConstInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for RealTypeConstInterp<'_> {
            fn fmt(
                fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>,
            ) -> std::fmt::Result {
                complete_nullary_display(fmt.value.name(), fmt.value.get(), fmt.options, f)
            }
        }

        impl Display for RealTypeConstInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(RealTypeConstInterp<'a>, gen: ('a));
    }

    pub mod mutable {
        use super::*;
        combined_nullaries! {
            #[type(complete, mutable, Real, RealTypeFull<'a>, 'a)]
            /// A combination of an [RealConstInterp] and an [RealTypeConstInterp].
            #[derive(Debug)]
            pub enum RealConstSymbolInterp<'a> {
                Real(RealConstInterp<'a>),
                RealType(RealTypeConstInterp<'a>),
            }
        }

        complete_nullary_symbol_methods! {
            (Real, Real),
            impl<'a> RealConstSymbolInterp<'a>
        }

        /// A complete mutable interpretation of a constant with a real codomain.
        pub struct RealConstInterp<'a> {
            pub(crate) interp: cccomplete::mutable::RealConstInterp<'a>,
            pub(crate) decl: PfuncDeclInterp<'a>,
        }

        impl<'a> Deref for RealConstInterp<'a> {
            type Target = PfuncDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        impl_real_from_type_element!(impl<'a> RealConstInterp<'a>);

        impl<'a> RealConstInterp<'a> {
            /// Get the interpretation.
            pub fn get(&self) -> Real {
                self.interp.get()
            }

            /// Set the interpretation.
            pub fn set(&mut self, value: Real) {
                self.interp.set(value)
            }

            fn nullary_set(&mut self, value: Real) -> Result<(), CodomainError> {
                self.set(value);
                Ok(())
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter(&self) -> impl Iterator<Item = (ArgsRef<'a>, Real)> + use<'a> {
                core::iter::once((ArgsRef::empty(self.decl.domain_full()).unwrap(), self.get()))
            }

            /// Returns an owned iterator over all arguments and their corresponding interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, Real)> {
                self.iter()
            }

            pub(crate) fn symb_codomain_full(&self) -> TypeFull<'a> {
                TypeFull::Real
            }
        }

        impl FodotOptions for RealConstInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for RealConstInterp<'_> {
            fn fmt(
                fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>,
            ) -> std::fmt::Result {
                complete_nullary_display(fmt.value.name(), fmt.value.get(), fmt.options, f)
            }
        }

        impl Display for RealConstInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(RealConstInterp<'a>, gen: ('a));

        /// A complete mutable interpretation of a constant with a real subtype as codomain.
        pub struct RealTypeConstInterp<'a> {
            pub(crate) interp: cccomplete::mutable::RealTypeConstInterp<'a>,
            pub(crate) decl: RealTypeDeclInterp<'a>,
        }

        impl<'a> Deref for RealTypeConstInterp<'a> {
            type Target = RealTypeDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        impl<'a> RealTypeConstInterp<'a> {
            /// Get the interpretation.
            pub fn get(&self) -> Real {
                self.interp.get()
            }

            /// Set the interpretation.
            pub fn set(&mut self, value: Real) -> Result<(), CodomainError> {
                self.interp.set(value).map_err(|_| CodomainError)
            }

            fn nullary_set(&mut self, value: Real) -> Result<(), CodomainError> {
                self.set(value)
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter(&self) -> impl Iterator<Item = (ArgsRef<'a>, Real)> + use<'a> {
                core::iter::once((ArgsRef::empty(self.decl.domain_full()).unwrap(), self.get()))
            }

            /// Returns an owned iterator over all arguments and their corresponding interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, Real)> {
                self.iter()
            }

            pub(crate) fn symb_codomain_full(&self) -> TypeFull<'a> {
                TypeFull::RealType(self.codomain_full())
            }
        }

        impl FodotOptions for RealTypeConstInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for RealTypeConstInterp<'_> {
            fn fmt(
                fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>,
            ) -> std::fmt::Result {
                complete_nullary_display(fmt.value.name(), fmt.value.get(), fmt.options, f)
            }
        }

        impl Display for RealTypeConstInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(RealTypeConstInterp<'a>, gen: ('a));
    }
}
