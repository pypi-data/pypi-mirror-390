use super::{complete_func_symbol_methods, func_display, partial_func_symbol_methods};
use crate::fodot::{
    TryFromCtx, display_as_debug,
    error::{ArgMismatchError, ExtendedPfuncError, NullaryError},
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

        /// A partial immutable interpretation of a function with a string codomain.
        #[derive(Clone)]
        pub struct StrFuncInterp<'a> {
            pub(crate) interp: ccpartial::immutable::StrFuncInterp<'a>,
            pub(crate) decl: StrDeclInterp<'a>,
        }

        partial_func_symbol_methods! {
            (StrElement, StrElement<'a>),
            impl<'a> StrFuncInterp<'a>
        }

        impl<'a> Deref for StrFuncInterp<'a> {
            type Target = StrDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        impl<'a> StrFuncInterp<'a> {
            /// Get the interpretation of the symbol with the given arguments.
            pub fn get(&self, args: ArgsRef) -> Result<Option<StrElement<'a>>, ArgMismatchError> {
                let args = ArgsRef::try_from_ctx(args, self.domain_full())?;
                Ok(self
                    .interp
                    .get(args.domain_enum)
                    .unwrap()
                    .map(|f| self.to_str_element(f)))
            }

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
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, StrElement<'a>)> {
                self.interp.into_iter().map(move |(dom_enum, value)| {
                    (
                        ArgsRef::new(dom_enum, self.decl.domain_full()),
                        self.decl.to_str_element(value),
                    )
                })
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter<'b>(&'b self) -> impl Iterator<Item = (ArgsRef<'a>, StrElement<'a>)> + 'b {
                self.interp.iter().map(|(dom_enum, value)| {
                    (
                        ArgsRef::new(dom_enum, self.decl.domain_full()),
                        self.decl.to_str_element(value),
                    )
                })
            }

            /// Try converting this interpretation into its complete counterpart.
            ///
            /// This function returns the original interpretation in [Err] if the interpretation is
            /// not complete.
            pub fn try_into_complete(self) -> Result<complete::immutable::StrFuncInterp<'a>, Self> {
                match self.interp.try_into_complete() {
                    Ok(interp) => Ok(complete::immutable::StrFuncInterp {
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
            ) -> Result<complete::immutable::StrFuncInterp<'b>, ()> {
                match self.interp.try_as_im_complete() {
                    Ok(interp) => Ok(complete::immutable::StrFuncInterp {
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

        impl FodotOptions for StrFuncInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for StrFuncInterp<'_> {
            fn fmt(
                fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>,
            ) -> std::fmt::Result {
                func_display(fmt.value.name(), fmt.value.iter(), false, fmt.options, f)
            }
        }

        impl Display for StrFuncInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(StrFuncInterp<'a>, gen: ('a));
    }

    pub mod mutable {
        use super::*;

        /// A partial mutable interpretation of a function with a string codomain.
        pub struct StrFuncInterp<'a> {
            pub(crate) interp: ccpartial::mutable::StrFuncInterp<'a>,
            pub(crate) decl: StrDeclInterp<'a>,
        }

        partial_func_symbol_methods! {
            (StrElement, StrElement<'a>),
            impl<'a> StrFuncInterp<'a>
        }

        impl<'a> Deref for StrFuncInterp<'a> {
            type Target = StrDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        impl<'a> StrFuncInterp<'a> {
            /// Get the interpretation of the symbol with the given arguments.
            pub fn get(&self, args: ArgsRef) -> Result<Option<StrElement<'a>>, ArgMismatchError> {
                let args = ArgsRef::try_from_ctx(args, self.domain_full())?;
                Ok(self
                    .interp
                    .get(args.domain_enum)
                    .unwrap()
                    .map(|f| self.to_str_element(f)))
            }

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
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, StrElement<'a>)> {
                self.interp.into_iter().map(move |(dom_enum, value)| {
                    (
                        ArgsRef::new(dom_enum, self.decl.domain_full()),
                        self.decl.to_str_element(value),
                    )
                })
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter<'b>(&'b self) -> impl Iterator<Item = (ArgsRef<'a>, StrElement<'a>)> + 'b {
                self.interp.iter().map(|(dom_enum, value)| {
                    (
                        ArgsRef::new(dom_enum, self.decl.domain_full()),
                        self.decl.to_str_element(value),
                    )
                })
            }

            /// Try converting this interpretation into its complete counterpart.
            ///
            /// This function returns the original interpretation in [Err] if the interpretation is
            /// not complete.
            pub fn try_into_complete(self) -> Result<complete::mutable::StrFuncInterp<'a>, Self> {
                match self.interp.try_into_complete() {
                    Ok(interp) => Ok(complete::mutable::StrFuncInterp {
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
            ) -> Result<complete::immutable::StrFuncInterp<'b>, ()> {
                match self.interp.try_as_im_complete() {
                    Ok(interp) => Ok(complete::immutable::StrFuncInterp {
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
                value: Option<StrElement>,
            ) -> Result<(), ExtendedPfuncError> {
                let args = ArgsRef::try_from_ctx(args, self.domain_full())?;
                Ok(self
                    .interp
                    .set(
                        args.domain_enum,
                        value
                            .map(|f| self.decl.lower_str_element_id(f))
                            .transpose()?,
                    )
                    .unwrap())
            }

            pub(crate) fn symbol_set(
                &mut self,
                args: ArgsRef,
                value: Option<StrElement>,
            ) -> Result<(), ExtendedPfuncError> {
                self.set(args, value)
            }

            /// Sets the interpretation of the given arguments if it is currently unknown.
            ///
            /// Returns true if the value was actually set, i.e. the previous interpretation was
            /// unknown.
            pub fn set_if_unknown(
                &mut self,
                args: ArgsRef,
                value: StrElement,
            ) -> Result<bool, ExtendedPfuncError> {
                let args = ArgsRef::try_from_ctx(args, self.domain_full())?;
                Ok(self
                    .interp
                    .set_if_unknown(args.domain_enum, self.decl.lower_str_element_id(value)?)
                    .unwrap())
            }

            pub(crate) fn symbol_set_if_unknown(
                &mut self,
                args: ArgsRef,
                value: StrElement,
            ) -> Result<bool, ExtendedPfuncError> {
                self.set_if_unknown(args, value)
            }

            /// Sets all unknown values to the given value.
            pub fn set_all_unknown_to_value(
                &mut self,
                value: StrElement,
            ) -> Result<(), NullaryError> {
                Ok(self
                    .interp
                    .fill_unknown_with(self.decl.lower_str_element_id(value)?)
                    .unwrap())
            }

            pub(crate) fn symbol_set_all_unknown_to_value(
                &mut self,
                value: StrElement,
            ) -> Result<(), NullaryError> {
                self.set_all_unknown_to_value(value)
            }

            pub(crate) fn symb_codomain_full(&self) -> TypeFull<'a> {
                TypeFull::Str(self.codomain_full())
            }
        }

        impl FodotOptions for StrFuncInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for StrFuncInterp<'_> {
            fn fmt(
                fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>,
            ) -> std::fmt::Result {
                func_display(fmt.value.name(), fmt.value.iter(), false, fmt.options, f)
            }
        }

        impl Display for StrFuncInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(StrFuncInterp<'a>, gen: ('a));
    }
}

pub mod complete {
    use super::*;
    pub mod immutable {
        use super::*;

        /// A complete immutable interpretation of a function with a string codomain.
        #[derive(Clone)]
        pub struct StrFuncInterp<'a> {
            pub(crate) interp: cccomplete::immutable::StrFuncInterp<'a>,
            pub(crate) decl: StrDeclInterp<'a>,
        }

        complete_func_symbol_methods! {
            (StrElement, StrElement<'a>),
            impl<'a> StrFuncInterp<'a>
        }

        impl<'a> Deref for StrFuncInterp<'a> {
            type Target = StrDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        impl<'a> StrFuncInterp<'a> {
            /// Get the interpretation of the symbol with the given arguments.
            pub fn get(&self, args: ArgsRef) -> Result<StrElement<'a>, ArgMismatchError> {
                let args = ArgsRef::try_from_ctx(args, self.domain_full())?;
                Ok(self
                    .decl
                    .to_str_element(self.interp.get(args.domain_enum).unwrap()))
            }

            /// Returns an owned iterator over all arguments and their corresponding interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, StrElement<'a>)> {
                self.interp.into_iter().map(move |(dom_enum, value)| {
                    (
                        ArgsRef::new(dom_enum, self.decl.domain_full()),
                        self.decl.to_str_element(value),
                    )
                })
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter<'b>(&'b self) -> impl Iterator<Item = (ArgsRef<'a>, StrElement<'a>)> + 'b {
                self.interp.iter().map(|(dom_enum, value)| {
                    (
                        ArgsRef::new(dom_enum, self.decl.domain_full()),
                        self.decl.to_str_element(value),
                    )
                })
            }

            pub(crate) fn symb_codomain_full(&self) -> TypeFull<'a> {
                TypeFull::Str(self.codomain_full())
            }
        }

        impl FodotOptions for StrFuncInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for StrFuncInterp<'_> {
            fn fmt(
                fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>,
            ) -> std::fmt::Result {
                func_display(fmt.value.name(), fmt.value.iter(), true, fmt.options, f)
            }
        }

        impl Display for StrFuncInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(StrFuncInterp<'a>, gen: ('a));
    }

    pub mod mutable {
        use super::*;

        /// A complete mutable interpretation of a function with a string codomain.
        pub struct StrFuncInterp<'a> {
            pub(crate) interp: cccomplete::mutable::StrFuncInterp<'a>,
            pub(crate) decl: StrDeclInterp<'a>,
        }

        complete_func_symbol_methods! {
            (StrElement, StrElement<'a>),
            impl<'a> StrFuncInterp<'a>
        }

        impl<'a> Deref for StrFuncInterp<'a> {
            type Target = StrDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        impl<'a> StrFuncInterp<'a> {
            /// Get the interpretation of the symbol with the given arguments.
            pub fn get(&self, args: ArgsRef) -> Result<StrElement<'a>, ArgMismatchError> {
                let args = ArgsRef::try_from_ctx(args, self.domain_full())?;
                Ok(self
                    .decl
                    .to_str_element(self.interp.get(args.domain_enum).unwrap()))
            }

            /// Returns an owned iterator over all arguments and their corresponding interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, StrElement<'a>)> {
                self.interp.into_iter().map(move |(dom_enum, value)| {
                    (
                        ArgsRef::new(dom_enum, self.decl.domain_full()),
                        self.decl.to_str_element(value),
                    )
                })
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter<'b>(&'b self) -> impl Iterator<Item = (ArgsRef<'a>, StrElement<'a>)> + 'b {
                self.interp.iter().map(|(dom_enum, value)| {
                    (
                        ArgsRef::new(dom_enum, self.decl.domain_full()),
                        self.decl.to_str_element(value),
                    )
                })
            }

            /// Sets the interpretation for the given argument with the given value.
            pub fn set(
                &mut self,
                args: ArgsRef,
                value: StrElement,
            ) -> Result<(), ExtendedPfuncError> {
                let args = ArgsRef::try_from_ctx(args, self.domain_full())?;
                Ok(self
                    .interp
                    .set(args.domain_enum, self.decl.lower_str_element_id(value)?)
                    .unwrap())
            }

            pub(crate) fn symbol_set(
                &mut self,
                args: ArgsRef,
                value: StrElement,
            ) -> Result<(), ExtendedPfuncError> {
                self.set(args, value)
            }

            pub(crate) fn symb_codomain_full(&self) -> TypeFull<'a> {
                TypeFull::Str(self.codomain_full())
            }
        }

        impl FodotOptions for StrFuncInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for StrFuncInterp<'_> {
            fn fmt(
                fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>,
            ) -> std::fmt::Result {
                func_display(fmt.value.name(), fmt.value.iter(), true, fmt.options, f)
            }
        }

        impl Display for StrFuncInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(StrFuncInterp<'a>, gen: ('a));
    }
}
