use super::{
    complete_nullary_display, complete_nullary_symbol_methods, partial_nullary_display,
    partial_nullary_symbol_methods,
};
use crate::fodot::{
    display_as_debug,
    error::{DomainMismatch, ExtendedPfuncError, NullaryError},
    fmt::{FodotDisplay, FodotOptions, FormatOptions},
    structure::{ArgsRef, StrElement, TypeFull, pfunc::StrDeclInterp},
};
use comp_core::structure::{complete as cccomplete, partial as ccpartial};
use core::{fmt::Display, ops::Deref};
use sli_collections::iterator::Iterator;

pub mod partial {
    use super::*;
    pub mod immutable {
        use super::*;

        /// A partial immutable interpretation of a constant with a string codomain.
        #[derive(Clone)]
        pub struct StrConstInterp<'a> {
            pub(crate) interp: ccpartial::immutable::StrConstInterp<'a>,
            pub(crate) decl: StrDeclInterp<'a>,
        }

        impl<'a> Deref for StrConstInterp<'a> {
            type Target = StrDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        partial_nullary_symbol_methods! {
            (StrElement, StrElement<'a>),
            impl<'a> StrConstInterp<'a>
        }

        impl<'a> StrConstInterp<'a> {
            /// Get the interpretation
            pub fn get(&self) -> Option<StrElement<'a>> {
                self.interp.get().map(|f| self.to_str_element(f))
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
            pub fn iter(&self) -> impl Iterator<Item = (ArgsRef<'a>, StrElement<'a>)> + use<'a> {
                self.get()
                    .map(|f| (ArgsRef::empty(self.decl.domain_full()).unwrap(), f))
                    .into_iter()
            }

            /// Returns an owned iterator over all arguments and their corresponding interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, StrElement<'a>)> {
                self.iter()
            }

            /// Try converting this interpretation into its complete counterpart.
            ///
            /// This function returns the original interpretation in [Err] if the interpretation is
            /// not complete.
            pub fn try_into_complete(
                self,
            ) -> Result<complete::immutable::StrConstInterp<'a>, Self> {
                match self.interp.try_into_complete() {
                    Ok(interp) => Ok(complete::immutable::StrConstInterp {
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
            ) -> Result<complete::immutable::StrConstInterp<'b>, ()> {
                match self.interp.try_as_im_complete() {
                    Ok(interp) => Ok(complete::immutable::StrConstInterp {
                        interp,
                        decl: self.decl.clone(),
                    }),
                    Err(_) => Err(()),
                }
            }

            pub(crate) fn symb_codomain_full(&self) -> TypeFull<'a> {
                TypeFull::Str(self.codomain_full())
            }
        }

        impl FodotOptions for StrConstInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for StrConstInterp<'_> {
            fn fmt(
                fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>,
            ) -> std::fmt::Result {
                partial_nullary_display(fmt.value.name(), fmt.value.get(), fmt.options, f)
            }
        }

        impl Display for StrConstInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(StrConstInterp<'a>, gen: ('a));
    }

    pub mod mutable {
        use super::*;

        /// A partial immutable interpretation of a constant with a string codomain.
        pub struct StrConstInterp<'a> {
            pub(crate) interp: ccpartial::mutable::StrConstInterp<'a>,
            pub(crate) decl: StrDeclInterp<'a>,
        }

        impl<'a> Deref for StrConstInterp<'a> {
            type Target = StrDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        partial_nullary_symbol_methods! {
            (StrElement, StrElement<'a>),
            impl<'a> StrConstInterp<'a>
        }

        impl<'a> StrConstInterp<'a> {
            /// Get the interpretation
            pub fn get(&self) -> Option<StrElement<'a>> {
                self.interp.get().map(|f| self.to_str_element(f))
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
            pub fn iter(&self) -> impl Iterator<Item = (ArgsRef<'a>, StrElement<'a>)> + use<'a> {
                self.get()
                    .map(|f| (ArgsRef::empty(self.decl.domain_full()).unwrap(), f))
                    .into_iter()
            }

            /// Returns an owned iterator over all arguments and their corresponding interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, StrElement<'a>)> {
                self.iter()
            }

            /// Sets the interpretation to the given value.
            pub fn set(&mut self, value: Option<StrElement>) -> Result<(), NullaryError> {
                self.interp
                    .set(value.map(|f| self.lower_str_element_id(f)).transpose()?)
                    .expect("lower_str_element_id ensures type_enum is valid");
                Ok(())
            }

            pub(crate) fn symbol_set(
                &mut self,
                args: ArgsRef,
                value: Option<StrElement>,
            ) -> Result<(), ExtendedPfuncError> {
                if args.is_unit() {
                    Ok(self.set(value)?)
                } else {
                    Err(DomainMismatch {
                        expected: self.domain().str_domain(),
                        found: args.domain().as_domain().str_domain(),
                    }
                    .into())
                }
            }

            pub(crate) fn nullary_set(
                &mut self,
                value: Option<StrElement>,
            ) -> Result<(), NullaryError> {
                self.set(value)?;
                Ok(())
            }

            /// Sets the interpretation if the interpretation is unknown.
            ///
            /// Returns a [bool] which is true if the proposition was unknown, false otherwise.
            pub fn set_if_unknown(&mut self, value: StrElement) -> Result<bool, NullaryError> {
                Ok(self
                    .interp
                    .set_if_unknown(self.lower_str_element_id(value)?)
                    .unwrap())
            }

            pub(crate) fn nullary_set_if_unknown(
                &mut self,
                value: StrElement,
            ) -> Result<bool, NullaryError> {
                self.set_if_unknown(value)
            }

            pub(crate) fn symbol_set_if_unknown(
                &mut self,
                args: ArgsRef,
                value: StrElement,
            ) -> Result<bool, ExtendedPfuncError> {
                if args.is_unit() {
                    Ok(self.set_if_unknown(value)?)
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
                value: StrElement,
            ) -> Result<(), NullaryError> {
                self.set_if_unknown(value)?;
                Ok(())
            }

            /// Try converting this interpretation into its complete counterpart.
            ///
            /// This function returns the original interpretation in [Err] if the interpretation is
            /// not complete.
            pub fn try_into_complete(self) -> Result<complete::mutable::StrConstInterp<'a>, Self> {
                match self.interp.try_into_complete() {
                    Ok(interp) => Ok(complete::mutable::StrConstInterp {
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
            ) -> Result<complete::immutable::StrConstInterp<'b>, ()> {
                match self.interp.try_as_im_complete() {
                    Ok(interp) => Ok(complete::immutable::StrConstInterp {
                        interp,
                        decl: self.decl.clone(),
                    }),
                    Err(_) => Err(()),
                }
            }

            pub(crate) fn symb_codomain_full(&self) -> TypeFull<'a> {
                TypeFull::Str(self.codomain_full())
            }
        }

        impl FodotOptions for StrConstInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for StrConstInterp<'_> {
            fn fmt(
                fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>,
            ) -> std::fmt::Result {
                partial_nullary_display(fmt.value.name(), fmt.value.get(), fmt.options, f)
            }
        }

        impl Display for StrConstInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(StrConstInterp<'a>, gen: ('a));
    }
}

pub mod complete {
    use super::*;
    pub mod immutable {
        use super::*;

        /// A complete immutable interpretation of a constant with a string codomain.
        #[derive(Clone)]
        pub struct StrConstInterp<'a> {
            pub(crate) interp: cccomplete::immutable::StrConstInterp<'a>,
            pub(crate) decl: StrDeclInterp<'a>,
        }

        impl<'a> Deref for StrConstInterp<'a> {
            type Target = StrDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        complete_nullary_symbol_methods! {
            (StrElement, StrElement<'a>),
            impl<'a> StrConstInterp<'a>
        }

        impl<'a> StrConstInterp<'a> {
            /// Get the interpretation.
            pub fn get(&self) -> StrElement<'a> {
                self.to_str_element(self.interp.get())
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter(&self) -> impl Iterator<Item = (ArgsRef<'a>, StrElement<'a>)> + use<'a> {
                core::iter::once((ArgsRef::empty(self.decl.domain_full()).unwrap(), self.get()))
            }

            /// Returns an owned iterator over all arguments and their corresponding interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, StrElement<'a>)> {
                self.iter()
            }

            pub(crate) fn symb_codomain_full(&self) -> TypeFull<'a> {
                TypeFull::Str(self.codomain_full())
            }
        }

        impl FodotOptions for StrConstInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for StrConstInterp<'_> {
            fn fmt(
                fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>,
            ) -> std::fmt::Result {
                complete_nullary_display(fmt.value.name(), fmt.value.get(), fmt.options, f)
            }
        }

        impl Display for StrConstInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(StrConstInterp<'a>, gen: ('a));
    }

    pub mod mutable {
        use super::*;

        /// A complete mutable interpretation of a constant with a string codomain.
        pub struct StrConstInterp<'a> {
            pub(crate) interp: cccomplete::mutable::StrConstInterp<'a>,
            pub(crate) decl: StrDeclInterp<'a>,
        }

        impl<'a> Deref for StrConstInterp<'a> {
            type Target = StrDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        complete_nullary_symbol_methods! {
            (StrElement, StrElement<'a>),
            impl<'a> StrConstInterp<'a>
        }

        impl<'a> StrConstInterp<'a> {
            /// Get the interpretation.
            pub fn get(&self) -> StrElement<'a> {
                self.to_str_element(self.interp.get())
            }

            /// Set the interpretation.
            pub fn set(&mut self, value: StrElement) -> Result<(), NullaryError> {
                self.interp
                    .set(self.lower_str_element_id(value)?)
                    .expect("lower_str_element_id ensures type_enum is valid");
                Ok(())
            }

            pub(crate) fn symbol_set(
                &mut self,
                args: ArgsRef,
                value: StrElement,
            ) -> Result<(), ExtendedPfuncError> {
                if args.is_unit() {
                    Ok(self.set(value)?)
                } else {
                    Err(DomainMismatch {
                        expected: self.domain().str_domain(),
                        found: args.domain().as_domain().str_domain(),
                    }
                    .into())
                }
            }

            pub(crate) fn nullary_set(&mut self, value: StrElement) -> Result<(), NullaryError> {
                self.set(value)
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter(&self) -> impl Iterator<Item = (ArgsRef<'a>, StrElement<'a>)> + use<'a> {
                core::iter::once((ArgsRef::empty(self.decl.domain_full()).unwrap(), self.get()))
            }

            /// Returns an owned iterator over all arguments and their corresponding interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, StrElement<'a>)> {
                self.iter()
            }

            pub(crate) fn symb_codomain_full(&self) -> TypeFull<'a> {
                TypeFull::Str(self.codomain_full())
            }
        }

        impl FodotOptions for StrConstInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for StrConstInterp<'_> {
            fn fmt(
                fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>,
            ) -> std::fmt::Result {
                complete_nullary_display(fmt.value.name(), fmt.value.get(), fmt.options, f)
            }
        }

        impl Display for StrConstInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(StrConstInterp<'a>, gen: ('a));
    }
}
