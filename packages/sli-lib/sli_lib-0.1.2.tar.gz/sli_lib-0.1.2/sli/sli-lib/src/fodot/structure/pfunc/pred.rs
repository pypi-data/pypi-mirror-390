use super::{
    complete_func_symbol_methods, complete_pred_display, func_display, impl_bool_from_type_element,
    partial_func_symbol_methods,
};
use crate::fodot::{
    TryFromCtx, display_as_debug,
    error::ArgMismatchError,
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

        /// A partial immutable interpretation of a predicate.
        #[derive(Clone)]
        pub struct PredInterp<'a> {
            pub(crate) interp: ccpartial::immutable::PredInterp<'a>,
            pub(crate) decl: PfuncDeclInterp<'a>,
        }

        impl<'a> Deref for PredInterp<'a> {
            type Target = PfuncDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        partial_func_symbol_methods! {
            (bool, bool),
            impl<'a> PredInterp<'a>
        }

        impl<'a> PredInterp<'a> {
            /// Get the interpretation of the symbol with the given arguments.
            pub fn get(&self, args: ArgsRef) -> Result<Option<bool>, ArgMismatchError> {
                let args = ArgsRef::try_from_ctx(args, self.domain_full())?;
                Ok(self.interp.get(args.domain_enum).unwrap())
            }

            /// Returns true if the interpretation is complete.
            pub fn is_complete(&self) -> bool {
                self.interp.is_complete()
            }

            /// Returns true if at least one argument has a value.
            pub fn any_known(&self) -> bool {
                self.amount_known() > 0
            }

            /// The amount of arguments of this symbol that have an interpretation.
            pub fn amount_known(&self) -> usize {
                self.interp.amount_known()
            }

            /// The amount of arguments of this symbol that don't have an interpretation.
            pub fn amount_unknown(&self) -> usize {
                self.interp.amount_unknown()
            }

            /// Returns an owned iterator over all arguments and their corresponding interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, bool)> {
                self.interp.into_iter().map(move |(dom_enum, value)| {
                    (ArgsRef::new(dom_enum, self.decl.domain_full()), value)
                })
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter<'b>(&'b self) -> impl Iterator<Item = (ArgsRef<'a>, bool)> + 'b {
                self.interp.iter().map(|(dom_enum, value)| {
                    (ArgsRef::new(dom_enum, self.decl.domain_full()), value)
                })
            }

            /// Try converting this interpretation into its complete counterpart.
            ///
            /// This function returns the original interpretation in [Err] if the interpretation is
            /// not complete.
            pub fn try_into_complete(self) -> Result<complete::immutable::PredInterp<'a>, Self> {
                match self.interp.try_into_complete() {
                    Ok(interp) => Ok(complete::immutable::PredInterp {
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
            ) -> Result<complete::immutable::PredInterp<'b>, ()> {
                match self.interp.try_as_im_complete() {
                    Ok(interp) => Ok(complete::immutable::PredInterp {
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

        impl FodotOptions for PredInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for PredInterp<'_> {
            fn fmt(
                fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>,
            ) -> std::fmt::Result {
                match fmt.value.try_as_complete() {
                    Ok(interp) => FodotDisplay::fmt(fmt.with_opts(&interp), f),
                    Err(_) => {
                        func_display(fmt.value.name(), fmt.value.iter(), false, fmt.options, f)
                    }
                }
            }
        }

        impl Display for PredInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(PredInterp<'a>, gen: ('a));
    }

    pub mod mutable {
        use crate::fodot::error::{ExtendedPfuncError, NullaryError};

        use super::*;

        /// A partial mutable interpretation of a predicate.
        pub struct PredInterp<'a> {
            pub(crate) interp: ccpartial::mutable::PredInterp<'a>,
            pub(crate) decl: PfuncDeclInterp<'a>,
        }

        impl<'a> Deref for PredInterp<'a> {
            type Target = PfuncDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        partial_func_symbol_methods! {
            (bool, bool),
            impl<'a> PredInterp<'a>
        }

        impl_bool_from_type_element!(impl<'a> PredInterp<'a>);

        impl<'a> PredInterp<'a> {
            /// Get the interpretation of the symbol with the given arguments.
            pub fn get(&self, args: ArgsRef) -> Result<Option<bool>, ArgMismatchError> {
                let args = ArgsRef::try_from_ctx(args, self.domain_full())?;
                Ok(self.interp.get(args.domain_enum).unwrap())
            }

            /// Returns true if the interpretation is complete.
            pub fn is_complete(&self) -> bool {
                self.interp.is_complete()
            }

            /// Returns true if at least one argument has a value.
            pub fn any_known(&self) -> bool {
                self.amount_known() > 0
            }

            /// The amount of arguments of this symbol that have an interpretation.
            pub fn amount_known(&self) -> usize {
                self.interp.amount_known()
            }

            /// The amount of arguments of this symbol that don't have an interpretation.
            pub fn amount_unknown(&self) -> usize {
                self.interp.amount_unknown()
            }

            /// Returns an owned iterator over all arguments and their corresponding interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, bool)> {
                self.interp.into_iter().map(move |(dom_enum, value)| {
                    (ArgsRef::new(dom_enum, self.decl.domain_full()), value)
                })
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter<'b>(&'b self) -> impl Iterator<Item = (ArgsRef<'a>, bool)> + 'b {
                self.interp.iter().map(|(dom_enum, value)| {
                    (ArgsRef::new(dom_enum, self.decl.domain_full()), value)
                })
            }

            /// Try converting this interpretation into its complete counterpart.
            ///
            /// This function returns the original interpretation in [Err] if the interpretation is
            /// not complete.
            pub fn try_into_complete(self) -> Result<complete::mutable::PredInterp<'a>, Self> {
                match self.interp.try_into_complete() {
                    Ok(interp) => Ok(complete::mutable::PredInterp {
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
            ) -> Result<complete::immutable::PredInterp<'b>, ()> {
                match self.interp.try_as_im_complete() {
                    Ok(interp) => Ok(complete::immutable::PredInterp {
                        interp,
                        decl: self.decl.clone(),
                    }),
                    Err(_) => Err(()),
                }
            }

            /// Sets the interpretation for the given argument with the given value.
            pub fn set(
                &mut self,
                args: ArgsRef,
                value: Option<bool>,
            ) -> Result<(), ArgMismatchError> {
                let args = ArgsRef::try_from_ctx(args, self.domain_full())?;
                Ok(self.interp.set(args.domain_enum, value).unwrap())
            }

            pub(crate) fn symbol_set(
                &mut self,
                args: ArgsRef,
                value: Option<bool>,
            ) -> Result<(), ArgMismatchError> {
                self.set(args, value)
            }

            /// Sets the interpretation of the given arguments if it is currently unknown.
            ///
            /// Returns true if the value was actually set, i.e. the previous interpretation was
            /// unknown.
            pub fn set_if_unknown(
                &mut self,
                args: ArgsRef,
                value: bool,
            ) -> Result<bool, ArgMismatchError> {
                let args = ArgsRef::try_from_ctx(args, self.domain_full())?;
                Ok(self.interp.set_if_unknown(args.domain_enum, value).unwrap())
            }

            pub(crate) fn symbol_set_if_unknown(
                &mut self,
                args: ArgsRef,
                value: bool,
            ) -> Result<bool, ExtendedPfuncError> {
                Ok(self.set_if_unknown(args, value)?)
            }

            /// Sets all unknown values to the given value.
            pub fn set_all_unknown_to_value(&mut self, value: bool) {
                self.interp.fill_unknown_with(value)
            }

            pub(crate) fn symbol_set_all_unknown_to_value(
                &mut self,
                value: bool,
            ) -> Result<(), NullaryError> {
                self.set_all_unknown_to_value(value);
                Ok(())
            }

            pub(crate) fn symb_codomain_full(&self) -> TypeFull<'a> {
                TypeFull::Bool
            }
        }

        impl FodotOptions for PredInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for PredInterp<'_> {
            fn fmt(
                fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>,
            ) -> std::fmt::Result {
                match fmt.value.try_as_complete() {
                    Ok(interp) => FodotDisplay::fmt(fmt.with_opts(&interp), f),
                    Err(_) => {
                        func_display(fmt.value.name(), fmt.value.iter(), false, fmt.options, f)
                    }
                }
            }
        }

        impl Display for PredInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(PredInterp<'a>, gen: ('a));
    }
}

pub mod complete {
    use super::*;

    pub mod immutable {
        use super::*;

        /// A complete immutable interpretation of a predicate.
        #[derive(Clone)]
        pub struct PredInterp<'a> {
            pub(crate) interp: cccomplete::immutable::PredInterp<'a>,
            pub(crate) decl: PfuncDeclInterp<'a>,
        }

        impl<'a> Deref for PredInterp<'a> {
            type Target = PfuncDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        complete_func_symbol_methods! {
            (bool, bool),
            impl<'a> PredInterp<'a>
        }

        impl<'a> PredInterp<'a> {
            /// Get the interpretation of the symbol with the given arguments.
            pub fn get(&self, args: ArgsRef) -> Result<bool, ArgMismatchError> {
                let args = ArgsRef::try_from_ctx(args, self.domain_full())?;
                Ok(self.interp.get(args.domain_enum).unwrap())
            }

            /// Returns an owned iterator over all arguments and their corresponding
            /// interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, bool)> {
                self.interp.into_iter().map(move |(dom_enum, value)| {
                    (ArgsRef::new(dom_enum, self.decl.domain_full()), value)
                })
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter<'b>(&'b self) -> impl Iterator<Item = (ArgsRef<'a>, bool)> + 'b {
                self.interp.iter().map(|(dom_enum, value)| {
                    (ArgsRef::new(dom_enum, self.decl.domain_full()), value)
                })
            }

            /// Returns an owned iterator over all arguments with a true interpretation.
            pub fn into_iter_true(self) -> impl Iterator<Item = ArgsRef<'a>> {
                self.interp
                    .into_iter_true()
                    .map(move |dom_enum| ArgsRef::new(dom_enum, self.decl.domain_full()))
            }

            /// Returns an iterator over all arguments with a true interpretation.
            pub fn iter_true<'b>(&'b self) -> impl Iterator<Item = ArgsRef<'a>> + 'b {
                self.interp
                    .iter_true()
                    .map(move |dom_enum| ArgsRef::new(dom_enum, self.decl.domain_full()))
            }

            pub(crate) fn symb_codomain_full(&self) -> TypeFull<'a> {
                TypeFull::Bool
            }
        }

        impl FodotOptions for PredInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for PredInterp<'_> {
            fn fmt(
                fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>,
            ) -> std::fmt::Result {
                complete_pred_display(fmt.value.name(), fmt.value.iter_true(), fmt.options, f)
            }
        }

        impl Display for PredInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(PredInterp<'a>, gen: ('a));
    }

    pub mod mutable {
        use super::*;

        /// A complete mutable interpretation of a predicate.
        pub struct PredInterp<'a> {
            pub(crate) interp: cccomplete::mutable::PredInterp<'a>,
            pub(crate) decl: PfuncDeclInterp<'a>,
        }

        impl<'a> Deref for PredInterp<'a> {
            type Target = PfuncDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        complete_func_symbol_methods! {
            (bool, bool),
            impl<'a> PredInterp<'a>
        }

        impl_bool_from_type_element!(impl<'a> PredInterp<'a>);

        impl<'a> PredInterp<'a> {
            /// Get the interpretation of the symbol with the given arguments.
            pub fn get(&self, args: ArgsRef) -> Result<bool, ArgMismatchError> {
                let args = ArgsRef::try_from_ctx(args, self.domain_full())?;
                Ok(self.interp.get(args.domain_enum).unwrap())
            }

            /// Returns an owned iterator over all arguments and their corresponding
            /// interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, bool)> {
                self.interp.into_iter().map(move |(dom_enum, value)| {
                    (ArgsRef::new(dom_enum, self.decl.domain_full()), value)
                })
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter<'b>(&'b self) -> impl Iterator<Item = (ArgsRef<'a>, bool)> + 'b {
                self.interp.iter().map(|(dom_enum, value)| {
                    (ArgsRef::new(dom_enum, self.decl.domain_full()), value)
                })
            }

            /// Returns an owned iterator over all arguments with a true interpretation.
            pub fn into_iter_true(self) -> impl Iterator<Item = ArgsRef<'a>> {
                self.interp
                    .into_iter_true()
                    .map(move |dom_enum| ArgsRef::new(dom_enum, self.decl.domain_full()))
            }

            /// Returns an iterator over all arguments with a true interpretation.
            pub fn iter_true<'b>(&'b self) -> impl Iterator<Item = ArgsRef<'a>> + 'b {
                self.interp
                    .iter_true()
                    .map(move |dom_enum| ArgsRef::new(dom_enum, self.decl.domain_full()))
            }

            /// Sets the interpretation for the given argument with the given value.
            pub fn set(&mut self, args: ArgsRef, value: bool) -> Result<(), ArgMismatchError> {
                let args = ArgsRef::try_from_ctx(args, self.domain_full())?;
                Ok(self.interp.set(args.domain_enum, value).unwrap())
            }

            pub(crate) fn symbol_set(
                &mut self,
                args: ArgsRef,
                value: bool,
            ) -> Result<(), ArgMismatchError> {
                self.set(args, value)
            }

            pub(crate) fn symb_codomain_full(&self) -> TypeFull<'a> {
                TypeFull::Bool
            }
        }

        impl FodotOptions for PredInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for PredInterp<'_> {
            fn fmt(
                fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>,
            ) -> std::fmt::Result {
                complete_pred_display(fmt.value.name(), fmt.value.iter_true(), fmt.options, f)
            }
        }

        impl Display for PredInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(PredInterp<'a>, gen: ('a));
    }
}
