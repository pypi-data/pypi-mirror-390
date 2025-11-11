use super::{
    complete_nullary_display, complete_nullary_symbol_methods, impl_bool_from_type_element,
    partial_nullary_display, partial_nullary_symbol_methods,
};
use crate::fodot::{
    display_as_debug,
    error::{ArgMismatchError, DomainMismatch, NullaryError},
    fmt::{FodotDisplay, FodotOptions, FormatOptions},
    structure::{ArgsRef, TypeFull, pfunc::PfuncDeclInterp},
};
use comp_core::structure::{complete as cccomplete, partial as ccpartial};
use core::{fmt::Display, ops::Deref};
use sli_collections::iterator::Iterator;

pub mod partial {
    use super::*;

    pub mod immutable {
        use super::*;

        /// A partial immutable interpretation of a proposition.
        #[derive(Clone)]
        pub struct PropInterp<'a> {
            pub(crate) interp: ccpartial::immutable::PropInterp<'a>,
            pub(crate) decl: PfuncDeclInterp<'a>,
        }

        impl<'a> Deref for PropInterp<'a> {
            type Target = PfuncDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        partial_nullary_symbol_methods! {
            (bool, bool),
            impl<'a> PropInterp<'a>
        }

        impl<'a> PropInterp<'a> {
            /// Get the interpretation
            pub fn get(&self) -> Option<bool> {
                self.interp.get()
            }

            /// Returns true if the proposition has an interpretation.
            pub fn is_complete(&self) -> bool {
                self.interp.is_complete()
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
                !self.interp.is_complete()
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter(&self) -> impl Iterator<Item = (ArgsRef<'a>, bool)> + use<'a> {
                self.get()
                    .map(|f| (ArgsRef::empty(self.decl.domain_full()).unwrap(), f))
                    .into_iter()
            }

            /// Returns an owned iterator over all arguments and their corresponding interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, bool)> {
                self.iter()
            }

            /// Try converting this interpretation into its complete counterpart.
            ///
            /// This function returns the original interpretation in [Err] if the interpretation is
            /// not complete.
            pub fn try_into_complete(self) -> Result<complete::immutable::PropInterp<'a>, Self> {
                match self.interp.try_into_complete() {
                    Ok(interp) => Ok(complete::immutable::PropInterp {
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
            ) -> Result<complete::immutable::PropInterp<'b>, ()> {
                match self.interp.try_as_im_complete() {
                    Ok(interp) => Ok(complete::immutable::PropInterp {
                        interp,
                        decl: self.decl.clone(),
                    }),
                    Err(_) => Err(()),
                }
            }

            pub(crate) fn symb_codomain_full(&self) -> TypeFull<'a> {
                TypeFull::Bool
            }
        }

        impl FodotOptions for PropInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for PropInterp<'_> {
            fn fmt(
                fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>,
            ) -> std::fmt::Result {
                partial_nullary_display(fmt.value.name(), fmt.value.get(), fmt.options, f)
            }
        }

        impl Display for PropInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(PropInterp<'a>, gen: ('a));
    }

    pub mod mutable {
        use crate::fodot::error::{ExtendedPfuncError, NullaryError};

        use super::*;

        /// A partial mutable interpretation of a proposition.
        pub struct PropInterp<'a> {
            pub(crate) interp: ccpartial::mutable::PropInterp<'a>,
            pub(crate) decl: PfuncDeclInterp<'a>,
        }

        impl<'a> Deref for PropInterp<'a> {
            type Target = PfuncDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        partial_nullary_symbol_methods! {
            (bool, bool),
            impl<'a> PropInterp<'a>
        }

        impl_bool_from_type_element!(impl<'a> PropInterp<'a>);

        impl<'a> PropInterp<'a> {
            /// Get the interpretation.
            pub fn get(&self) -> Option<bool> {
                self.interp.get()
            }

            /// Returns true if the proposition has an interpretation.
            pub fn is_complete(&self) -> bool {
                self.interp.is_complete()
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
                !self.interp.is_complete()
            }

            /// Set the interpretation.
            pub fn set(&mut self, value: Option<bool>) {
                self.interp.set(value)
            }

            pub(crate) fn nullary_set(&mut self, value: Option<bool>) -> Result<(), NullaryError> {
                Ok(self.set(value))
            }

            pub(crate) fn symbol_set(
                &mut self,
                args: ArgsRef,
                value: Option<bool>,
            ) -> Result<(), ArgMismatchError> {
                if args.is_unit() {
                    Ok(self.set(value))
                } else {
                    Err(DomainMismatch {
                        expected: self.domain().str_domain(),
                        found: args.domain().as_domain().str_domain(),
                    }
                    .into())
                }
            }

            /// Sets the interpretation if the interpretation is unknown.
            ///
            /// Returns a [bool] which is true if the proposition was unknown, false otherwise.
            pub fn set_if_unknown(&mut self, value: bool) -> bool {
                self.interp.set_if_unknown(value)
            }

            pub(crate) fn nullary_set_if_unknown(
                &mut self,
                value: bool,
            ) -> Result<bool, NullaryError> {
                Ok(self.set_if_unknown(value))
            }

            pub(crate) fn symbol_set_if_unknown(
                &mut self,
                args: ArgsRef,
                value: bool,
            ) -> Result<bool, ExtendedPfuncError> {
                if args.is_unit() {
                    Ok(self.set_if_unknown(value))
                } else {
                    Err(DomainMismatch {
                        expected: self.domain().str_domain(),
                        found: args.domain().as_domain().str_domain(),
                    }
                    .into())
                }
            }

            pub(crate) fn symbol_set_all_unknown_to_value(
                &mut self,
                value: bool,
            ) -> Result<(), NullaryError> {
                self.set_if_unknown(value);
                Ok(())
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter(&self) -> impl Iterator<Item = (ArgsRef<'a>, bool)> + use<'a> {
                self.get()
                    .map(|f| (ArgsRef::empty(self.decl.domain_full()).unwrap(), f))
                    .into_iter()
            }

            /// Returns an owned iterator over all arguments and their corresponding interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, bool)> {
                self.iter()
            }

            /// Try converting this interpretation into its complete counterpart.
            ///
            /// This function returns the original interpretation in [Err] if the interpretation is
            /// not complete.
            pub fn try_into_complete(self) -> Result<complete::mutable::PropInterp<'a>, Self> {
                match self.interp.try_into_complete() {
                    Ok(interp) => Ok(complete::mutable::PropInterp {
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
            ) -> Result<complete::immutable::PropInterp<'b>, ()> {
                match self.interp.try_as_im_complete() {
                    Ok(interp) => Ok(complete::immutable::PropInterp {
                        interp,
                        decl: self.decl.clone(),
                    }),
                    Err(_) => Err(()),
                }
            }

            pub(crate) fn symb_codomain_full(&self) -> TypeFull<'a> {
                TypeFull::Bool
            }
        }

        impl FodotOptions for PropInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for PropInterp<'_> {
            fn fmt(
                fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>,
            ) -> std::fmt::Result {
                partial_nullary_display(fmt.value.name(), fmt.value.get(), fmt.options, f)
            }
        }

        impl Display for PropInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(PropInterp<'a>, gen: ('a));
    }
}

pub mod complete {
    use super::*;
    pub mod immutable {
        use super::*;
        /// A complete immutable interpretation of a proposition.
        #[derive(Clone)]
        pub struct PropInterp<'a> {
            pub(crate) interp: cccomplete::immutable::PropInterp<'a>,
            pub(crate) decl: PfuncDeclInterp<'a>,
        }

        impl<'a> Deref for PropInterp<'a> {
            type Target = PfuncDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        complete_nullary_symbol_methods! {
            (bool, bool),
            impl<'a> PropInterp<'a>
        }

        impl<'a> PropInterp<'a> {
            /// Get the interpretation.
            pub fn get(&self) -> bool {
                self.interp.get()
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter(&self) -> impl Iterator<Item = (ArgsRef<'a>, bool)> + use<'a> {
                core::iter::once((ArgsRef::empty(self.decl.domain_full()).unwrap(), self.get()))
            }

            /// Returns an owned iterator over all arguments and their corresponding interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, bool)> {
                self.iter()
            }

            pub(crate) fn symb_codomain_full(&self) -> TypeFull<'a> {
                TypeFull::Bool
            }
        }

        impl FodotOptions for PropInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for PropInterp<'_> {
            fn fmt(
                fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>,
            ) -> std::fmt::Result {
                complete_nullary_display(fmt.value.name(), fmt.value.get(), fmt.options, f)
            }
        }

        impl Display for PropInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(PropInterp<'a>, gen: ('a));
    }

    pub mod mutable {
        use super::*;
        /// A complete mutable interpretation of a proposition.
        pub struct PropInterp<'a> {
            pub(crate) interp: cccomplete::mutable::PropInterp<'a>,
            pub(crate) decl: PfuncDeclInterp<'a>,
        }

        impl<'a> Deref for PropInterp<'a> {
            type Target = PfuncDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        complete_nullary_symbol_methods! {
            (bool, bool),
            impl<'a> PropInterp<'a>
        }

        impl_bool_from_type_element!(impl<'a> PropInterp<'a>);

        impl<'a> PropInterp<'a> {
            /// Get the interpretation.
            pub fn get(&self) -> bool {
                self.interp.get()
            }

            /// Set the interpretation.
            pub fn set(&mut self, value: bool) {
                self.interp.set(value)
            }

            pub(crate) fn nullary_set(&mut self, value: bool) -> Result<(), NullaryError> {
                Ok(self.set(value))
            }

            pub(crate) fn symbol_set(
                &mut self,
                args: ArgsRef,
                value: bool,
            ) -> Result<(), ArgMismatchError> {
                if args.is_unit() {
                    Ok(self.set(value))
                } else {
                    Err(DomainMismatch {
                        expected: self.domain().str_domain(),
                        found: args.domain().as_domain().str_domain(),
                    }
                    .into())
                }
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter(&self) -> impl Iterator<Item = (ArgsRef<'a>, bool)> + use<'a> {
                core::iter::once((ArgsRef::empty(self.decl.domain_full()).unwrap(), self.get()))
            }

            /// Returns an owned iterator over all arguments and their corresponding interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, bool)> {
                self.iter()
            }

            pub(crate) fn symb_codomain_full(&self) -> TypeFull<'a> {
                TypeFull::Bool
            }
        }

        impl FodotOptions for PropInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for PropInterp<'_> {
            fn fmt(
                fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>,
            ) -> std::fmt::Result {
                complete_nullary_display(fmt.value.name(), fmt.value.get(), fmt.options, f)
            }
        }

        impl Display for PropInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(PropInterp<'a>, gen: ('a));
    }
}
