use super::{
    combined_funcs, complete_func_symbol_methods, func_display, impl_int_from_type_element,
    partial_func_symbol_methods,
};
use crate::fodot::{
    TryFromCtx, display_as_debug,
    error::{ArgMismatchError, CodomainError, PfuncError},
    fmt::{FodotDisplay, FodotOptions, FormatOptions},
    structure::{
        ArgsRef, IntTypeFull, TypeFull,
        pfunc::{IntTypeDeclInterp, PfuncDeclInterp},
    },
    vocabulary::Int,
};
use comp_core::structure::{
    applied_symb_interp as ccap, complete as cccomplete, partial as ccpartial,
};
use core::{fmt::Display, ops::Deref};
use itertools::Either;
use sli_collections::iterator::Iterator;

pub mod partial {
    use super::*;
    pub mod immutable {
        use super::*;
        combined_funcs! {
            #[type(
                partial,
                immutable,
                Int,
                IntTypeFull<'a>,
                'a,
                {
                    complete::immutable::IntFuncSymbolInterp<'a>,
                    complete::immutable::IntFuncSymbolInterp,
                }
            )]
            /// A combination of an [IntFuncInterp] and an [IntTypeFuncInterp].
            #[derive(Clone, Debug)]
            pub enum IntFuncSymbolInterp<'a> {
                Int(IntFuncInterp<'a>),
                IntType(IntTypeFuncInterp<'a>),
            }
        }

        partial_func_symbol_methods! {
            (Int, Int),
            impl<'a> IntFuncSymbolInterp<'a>
        }

        /// A partial immutable interpretation of a function with an integer codomain.
        #[derive(Clone)]
        pub struct IntFuncInterp<'a> {
            pub(crate) interp: ccpartial::immutable::IntFuncInterp<'a>,
            pub(crate) decl: PfuncDeclInterp<'a>,
        }

        impl<'a> Deref for IntFuncInterp<'a> {
            type Target = PfuncDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        impl_int_from_type_element!(impl<'a> IntFuncInterp<'a>);

        impl<'a> IntFuncInterp<'a> {
            /// Get the interpretation of the symbol with the given arguments.
            pub fn get(&self, args: ArgsRef) -> Result<Option<Int>, ArgMismatchError> {
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

            /// Returns an owned iterator over all arguments and their corresponding
            /// interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, Int)> {
                self.interp.into_iter().map(move |(dom_enum, value)| {
                    (ArgsRef::new(dom_enum, self.decl.domain_full()), value)
                })
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter<'b>(&'b self) -> impl Iterator<Item = (ArgsRef<'a>, Int)> + 'b {
                self.interp.iter().map(|(dom_enum, value)| {
                    (ArgsRef::new(dom_enum, self.decl.domain_full()), value)
                })
            }

            /// Try converting this interpretation into its complete counterpart.
            ///
            /// This function returns the original interpretation in [Err] if the interpretation is
            /// not complete.
            pub fn try_into_complete(self) -> Result<complete::immutable::IntFuncInterp<'a>, Self> {
                match self.interp.try_into_complete() {
                    Ok(interp) => Ok(complete::immutable::IntFuncInterp {
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
            ) -> Result<complete::immutable::IntFuncInterp<'b>, ()> {
                match self.interp.try_as_im_complete() {
                    Ok(interp) => Ok(complete::immutable::IntFuncInterp {
                        interp,
                        decl: self.decl.clone(),
                    }),
                    Err(_) => Err(()),
                }
            }

            pub(crate) fn symb_codomain_full(&self) -> TypeFull<'a> {
                TypeFull::Int
            }
        }

        impl FodotOptions for IntFuncInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for IntFuncInterp<'_> {
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

        impl Display for IntFuncInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(IntFuncInterp<'a>, gen: ('a));

        /// A partial immutable interpretation of a function with an integer subtype as codomain.
        #[derive(Clone)]
        pub struct IntTypeFuncInterp<'a> {
            pub(crate) interp: ccpartial::immutable::IntTypeFuncInterp<'a>,
            pub(crate) decl: IntTypeDeclInterp<'a>,
        }

        impl<'a> Deref for IntTypeFuncInterp<'a> {
            type Target = IntTypeDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        impl<'a> IntTypeFuncInterp<'a> {
            /// Get the interpretation of the symbol with the given arguments.
            pub fn get(&self, args: ArgsRef) -> Result<Option<Int>, ArgMismatchError> {
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

            /// Returns an owned iterator over all arguments and their corresponding
            /// interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, Int)> {
                self.interp.into_iter().map(move |(dom_enum, value)| {
                    (ArgsRef::new(dom_enum, self.decl.domain_full()), value)
                })
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter<'b>(&'b self) -> impl Iterator<Item = (ArgsRef<'a>, Int)> + 'b {
                self.interp.iter().map(|(dom_enum, value)| {
                    (ArgsRef::new(dom_enum, self.decl.domain_full()), value)
                })
            }

            /// Try converting this interpretation into its complete counterpart.
            ///
            /// This function returns the original interpretation in [Err] if the interpretation is
            /// not complete.
            pub fn try_into_complete(
                self,
            ) -> Result<complete::immutable::IntTypeFuncInterp<'a>, Self> {
                match self.interp.try_into_complete() {
                    Ok(interp) => Ok(complete::immutable::IntTypeFuncInterp {
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
            ) -> Result<complete::immutable::IntTypeFuncInterp<'b>, ()> {
                match self.interp.try_as_im_complete() {
                    Ok(interp) => Ok(complete::immutable::IntTypeFuncInterp {
                        interp,
                        decl: self.decl.clone(),
                    }),
                    Err(_) => Err(()),
                }
            }

            pub(crate) fn symb_codomain_full(&self) -> TypeFull<'a> {
                TypeFull::IntType(self.codomain_full())
            }
        }

        impl FodotOptions for IntTypeFuncInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for IntTypeFuncInterp<'_> {
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

        impl Display for IntTypeFuncInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(IntTypeFuncInterp<'a>, gen: ('a));
    }

    pub mod mutable {
        use super::*;
        combined_funcs! {
            #[type(
                partial,
                mutable,
                Int,
                IntTypeFull<'a>,
                'a,
                {
                    complete::mutable::IntFuncSymbolInterp<'a>,
                    complete::immutable::IntFuncSymbolInterp,
                }
            )]
            /// A combination of an [IntFuncInterp] and an [IntTypeFuncInterp].
            #[derive(Debug)]
            pub enum IntFuncSymbolInterp<'a> {
                Int(IntFuncInterp<'a>),
                IntType(IntTypeFuncInterp<'a>),
            }
        }

        partial_func_symbol_methods! {
            (Int, Int),
            impl<'a> IntFuncSymbolInterp<'a>
        }

        /// A partial mutable interpretation of a function with an integer codomain.
        pub struct IntFuncInterp<'a> {
            pub(crate) interp: ccpartial::mutable::IntFuncInterp<'a>,
            pub(crate) decl: PfuncDeclInterp<'a>,
        }

        impl<'a> Deref for IntFuncInterp<'a> {
            type Target = PfuncDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        impl_int_from_type_element!(impl<'a> IntFuncInterp<'a>);

        impl<'a> IntFuncInterp<'a> {
            /// Get the interpretation of the symbol with the given arguments.
            pub fn get(&self, args: ArgsRef) -> Result<Option<Int>, ArgMismatchError> {
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

            /// Returns an owned iterator over all arguments and their corresponding
            /// interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, Int)> {
                self.interp.into_iter().map(move |(dom_enum, value)| {
                    (ArgsRef::new(dom_enum, self.decl.domain_full()), value)
                })
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter<'b>(&'b self) -> impl Iterator<Item = (ArgsRef<'a>, Int)> + 'b {
                self.interp.iter().map(|(dom_enum, value)| {
                    (ArgsRef::new(dom_enum, self.decl.domain_full()), value)
                })
            }

            /// Try converting this interpretation into its complete counterpart.
            ///
            /// This function returns the original interpretation in [Err] if the interpretation is
            /// not complete.
            pub fn try_into_complete(self) -> Result<complete::mutable::IntFuncInterp<'a>, Self> {
                match self.interp.try_into_complete() {
                    Ok(interp) => Ok(complete::mutable::IntFuncInterp {
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
            ) -> Result<complete::immutable::IntFuncInterp<'b>, ()> {
                match self.interp.try_as_im_complete() {
                    Ok(interp) => Ok(complete::immutable::IntFuncInterp {
                        interp,
                        decl: self.decl.clone(),
                    }),
                    Err(_) => Err(()),
                }
            }

            /// Sets the interpretation for the given argument with the given value.
            pub fn set(&mut self, args: ArgsRef, value: Option<Int>) -> Result<(), PfuncError> {
                let args = ArgsRef::try_from_ctx(args, self.domain_full())?;
                Ok(self.interp.set(args.domain_enum, value).unwrap())
            }

            /// Sets the interpretation of the given arguments if it is currently unknown.
            ///
            /// Returns true if the value was actually set, i.e. the previous interpretation was
            /// unknown.
            pub fn set_if_unknown(
                &mut self,
                args: ArgsRef,
                value: Int,
            ) -> Result<bool, ArgMismatchError> {
                let args = ArgsRef::try_from_ctx(args, self.domain_full())?;
                Ok(self.interp.set_if_unknown(args.domain_enum, value).unwrap())
            }

            /// Sets all unknown values to the given value.
            pub fn set_all_unknown_to_value(&mut self, value: Int) {
                self.interp.fill_unknown_with(value)
            }

            fn func_set_all_unknown_to_value(&mut self, value: Int) -> Result<(), CodomainError> {
                Ok(self.set_all_unknown_to_value(value))
            }

            pub(crate) fn symb_codomain_full(&self) -> TypeFull<'a> {
                TypeFull::Int
            }
        }

        impl FodotOptions for IntFuncInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for IntFuncInterp<'_> {
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

        impl Display for IntFuncInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(IntFuncInterp<'a>, gen: ('a));

        /// A partial mutable interpretation of a function with an integer subtype as codomain.
        pub struct IntTypeFuncInterp<'a> {
            pub(crate) interp: ccpartial::mutable::IntTypeFuncInterp<'a>,
            pub(crate) decl: IntTypeDeclInterp<'a>,
        }

        impl<'a> Deref for IntTypeFuncInterp<'a> {
            type Target = IntTypeDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        impl<'a> IntTypeFuncInterp<'a> {
            /// Get the interpretation of the symbol with the given arguments.
            pub fn get(&self, args: ArgsRef) -> Result<Option<Int>, ArgMismatchError> {
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

            /// Returns an owned iterator over all arguments and their corresponding
            /// interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, Int)> {
                self.interp.into_iter().map(move |(dom_enum, value)| {
                    (ArgsRef::new(dom_enum, self.decl.domain_full()), value)
                })
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter<'b>(&'b self) -> impl Iterator<Item = (ArgsRef<'a>, Int)> + 'b {
                self.interp.iter().map(|(dom_enum, value)| {
                    (ArgsRef::new(dom_enum, self.decl.domain_full()), value)
                })
            }

            /// Try converting this interpretation into its complete counterpart.
            ///
            /// This function returns the original interpretation in [Err] if the interpretation is
            /// not complete.
            pub fn try_into_complete(
                self,
            ) -> Result<complete::mutable::IntTypeFuncInterp<'a>, Self> {
                match self.interp.try_into_complete() {
                    Ok(interp) => Ok(complete::mutable::IntTypeFuncInterp {
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
            ) -> Result<complete::immutable::IntTypeFuncInterp<'b>, ()> {
                match self.interp.try_as_im_complete() {
                    Ok(interp) => Ok(complete::immutable::IntTypeFuncInterp {
                        interp,
                        decl: self.decl.clone(),
                    }),
                    Err(_) => Err(()),
                }
            }

            /// Sets the interpretation for the given argument with the given value.
            pub fn set(&mut self, args: ArgsRef, value: Option<Int>) -> Result<(), PfuncError> {
                let args = ArgsRef::try_from_ctx(args, self.domain_full())?;
                self.interp
                    .set(args.domain_enum, value)
                    .map_err(|f| match f {
                        ccap::PfuncError::DomainError(_) => unreachable!(),
                        ccap::PfuncError::CodomainError(_) => CodomainError.into(),
                    })
            }

            /// Sets the interpretation of the given arguments if it is currently unknown.
            ///
            /// Returns true if the value was actually set, i.e. the previous interpretation was
            /// unknown.
            pub fn set_if_unknown(
                &mut self,
                args: ArgsRef,
                value: Int,
            ) -> Result<bool, PfuncError> {
                let args = ArgsRef::try_from_ctx(args, self.domain_full())?;
                self.interp
                    .set_if_unknown(args.domain_enum, value)
                    .map_err(|f| match f {
                        ccap::PfuncError::DomainError(_) => unreachable!(),
                        ccap::PfuncError::CodomainError(_) => CodomainError.into(),
                    })
            }

            /// Sets all unknown values to the given value.
            pub fn set_all_unknown_to_value(&mut self, value: Int) -> Result<(), CodomainError> {
                self.interp
                    .fill_unknown_with(value)
                    .map_err(|_| CodomainError)
            }

            fn func_set_all_unknown_to_value(&mut self, value: Int) -> Result<(), CodomainError> {
                self.set_all_unknown_to_value(value)
            }

            pub(crate) fn symb_codomain_full(&self) -> TypeFull<'a> {
                TypeFull::IntType(self.codomain_full())
            }
        }

        impl FodotOptions for IntTypeFuncInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for IntTypeFuncInterp<'_> {
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

        impl Display for IntTypeFuncInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(IntTypeFuncInterp<'a>, gen: ('a));
    }
}

pub mod complete {
    use super::*;
    pub mod immutable {
        use super::*;
        combined_funcs! {
            #[type(complete, immutable, Int, IntTypeFull<'a>, 'a)]
            #[derive(Clone, Debug)]
            /// A combination of an [IntFuncInterp] and an [IntTypeFuncInterp].
            pub enum IntFuncSymbolInterp<'a> {
                Int(IntFuncInterp<'a>),
                IntType(IntTypeFuncInterp<'a>),
            }
        }

        complete_func_symbol_methods! {
            (Int, Int),
            impl<'a> IntFuncSymbolInterp<'a>
        }

        /// A complete immutable interpretation of a function with an integer codomain.
        #[derive(Clone)]
        pub struct IntFuncInterp<'a> {
            pub(crate) interp: cccomplete::immutable::IntFuncInterp<'a>,
            pub(crate) decl: PfuncDeclInterp<'a>,
        }

        impl<'a> Deref for IntFuncInterp<'a> {
            type Target = PfuncDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        impl_int_from_type_element!(impl<'a> IntFuncInterp<'a>);

        impl<'a> IntFuncInterp<'a> {
            /// Get the interpretation of the symbol with the given arguments.
            pub fn get(&self, args: ArgsRef) -> Result<Int, ArgMismatchError> {
                let args = ArgsRef::try_from_ctx(args, self.domain_full())?;
                Ok(self.interp.get(args.domain_enum).unwrap())
            }

            /// Returns an owned iterator over all arguments and their corresponding
            /// interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, Int)> {
                self.interp.into_iter().map(move |(dom_enum, value)| {
                    (ArgsRef::new(dom_enum, self.decl.domain_full()), value)
                })
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter<'b>(&'b self) -> impl Iterator<Item = (ArgsRef<'a>, Int)> + 'b {
                self.interp.iter().map(|(dom_enum, value)| {
                    (ArgsRef::new(dom_enum, self.decl.domain_full()), value)
                })
            }

            pub(crate) fn symb_codomain_full(&self) -> TypeFull<'a> {
                TypeFull::Int
            }
        }

        impl FodotOptions for IntFuncInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for IntFuncInterp<'_> {
            fn fmt(
                fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>,
            ) -> std::fmt::Result {
                func_display(fmt.value.name(), fmt.value.iter(), true, fmt.options, f)
            }
        }

        impl Display for IntFuncInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(IntFuncInterp<'a>, gen: ('a));

        /// A complete immutable interpretation of a function with an integer subtype as codomain.
        #[derive(Clone)]
        pub struct IntTypeFuncInterp<'a> {
            pub(crate) interp: cccomplete::immutable::IntTypeFuncInterp<'a>,
            pub(crate) decl: IntTypeDeclInterp<'a>,
        }

        impl<'a> Deref for IntTypeFuncInterp<'a> {
            type Target = IntTypeDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        impl<'a> IntTypeFuncInterp<'a> {
            /// Get the interpretation of the symbol with the given arguments.
            pub fn get(&self, args: ArgsRef) -> Result<Int, ArgMismatchError> {
                let args = ArgsRef::try_from_ctx(args, self.domain_full())?;
                Ok(self.interp.get(args.domain_enum).unwrap())
            }

            /// Returns an owned iterator over all arguments and their corresponding
            /// interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, Int)> {
                self.interp.into_iter().map(move |(dom_enum, value)| {
                    (ArgsRef::new(dom_enum, self.decl.domain_full()), value)
                })
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter<'b>(&'b self) -> impl Iterator<Item = (ArgsRef<'a>, Int)> + 'b {
                self.interp.iter().map(|(dom_enum, value)| {
                    (ArgsRef::new(dom_enum, self.decl.domain_full()), value)
                })
            }

            pub(crate) fn symb_codomain_full(&self) -> TypeFull<'a> {
                TypeFull::IntType(self.codomain_full())
            }
        }

        impl FodotOptions for IntTypeFuncInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for IntTypeFuncInterp<'_> {
            fn fmt(
                fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>,
            ) -> std::fmt::Result {
                func_display(fmt.value.name(), fmt.value.iter(), true, fmt.options, f)
            }
        }

        impl Display for IntTypeFuncInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(IntTypeFuncInterp<'a>, gen: ('a));
    }

    pub mod mutable {
        use super::*;
        combined_funcs! {
            #[type(complete, mutable, Int, IntTypeFull<'a>, 'a)]
            #[derive(Debug)]
            /// A combination of an [IntFuncInterp] and an [IntTypeFuncInterp].
            pub enum IntFuncSymbolInterp<'a> {
                Int(IntFuncInterp<'a>),
                IntType(IntTypeFuncInterp<'a>),
            }
        }

        complete_func_symbol_methods! {
            (Int, Int),
            impl<'a> IntFuncSymbolInterp<'a>
        }

        /// A complete mutable interpretation of a function with an integer codomain.
        pub struct IntFuncInterp<'a> {
            pub(crate) interp: cccomplete::mutable::IntFuncInterp<'a>,
            pub(crate) decl: PfuncDeclInterp<'a>,
        }

        impl_int_from_type_element!(impl<'a> IntFuncInterp<'a>);

        impl<'a> Deref for IntFuncInterp<'a> {
            type Target = PfuncDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        impl<'a> IntFuncInterp<'a> {
            /// Get the interpretation of the symbol with the given arguments.
            pub fn get(&self, args: ArgsRef) -> Result<Int, ArgMismatchError> {
                let args = ArgsRef::try_from_ctx(args, self.domain_full())?;
                Ok(self.interp.get(args.domain_enum).unwrap())
            }

            /// Returns an owned iterator over all arguments and their corresponding
            /// interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, Int)> {
                self.interp.into_iter().map(move |(dom_enum, value)| {
                    (ArgsRef::new(dom_enum, self.decl.domain_full()), value)
                })
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter<'b>(&'b self) -> impl Iterator<Item = (ArgsRef<'a>, Int)> + 'b {
                self.interp.iter().map(|(dom_enum, value)| {
                    (ArgsRef::new(dom_enum, self.decl.domain_full()), value)
                })
            }

            /// Sets the interpretation for the given argument with the given value.
            pub fn set(&mut self, args: ArgsRef, value: Int) -> Result<(), ArgMismatchError> {
                let args = ArgsRef::try_from_ctx(args, self.domain_full())?;
                Ok(self.interp.set(args.domain_enum, value).unwrap())
            }

            pub(crate) fn symb_codomain_full(&self) -> TypeFull<'a> {
                TypeFull::Int
            }
        }

        impl FodotOptions for IntFuncInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for IntFuncInterp<'_> {
            fn fmt(
                fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>,
            ) -> std::fmt::Result {
                func_display(fmt.value.name(), fmt.value.iter(), true, fmt.options, f)
            }
        }

        impl Display for IntFuncInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(IntFuncInterp<'a>, gen: ('a));

        /// A complete mutable interpretation of a function with an integer subtype as codomain.
        pub struct IntTypeFuncInterp<'a> {
            pub(crate) interp: cccomplete::mutable::IntTypeFuncInterp<'a>,
            pub(crate) decl: IntTypeDeclInterp<'a>,
        }

        impl<'a> Deref for IntTypeFuncInterp<'a> {
            type Target = IntTypeDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        impl<'a> IntTypeFuncInterp<'a> {
            /// Get the interpretation of the symbol with the given arguments.
            pub fn get(&self, args: ArgsRef) -> Result<Int, ArgMismatchError> {
                let args = ArgsRef::try_from_ctx(args, self.domain_full())?;
                Ok(self.interp.get(args.domain_enum).unwrap())
            }

            /// Returns an owned iterator over all arguments and their corresponding
            /// interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, Int)> {
                self.interp.into_iter().map(move |(dom_enum, value)| {
                    (ArgsRef::new(dom_enum, self.decl.domain_full()), value)
                })
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter<'b>(&'b self) -> impl Iterator<Item = (ArgsRef<'a>, Int)> + 'b {
                self.interp.iter().map(|(dom_enum, value)| {
                    (ArgsRef::new(dom_enum, self.decl.domain_full()), value)
                })
            }

            /// Sets the interpretation for the given argument with the given value.
            pub fn set(&mut self, args: ArgsRef, value: Int) -> Result<(), PfuncError> {
                let args = ArgsRef::try_from_ctx(args, self.domain_full())?;
                self.interp
                    .set(args.domain_enum, value)
                    .map_err(|f| match f {
                        ccap::PfuncError::DomainError(_) => unreachable!(),
                        ccap::PfuncError::CodomainError(_) => CodomainError.into(),
                    })
            }

            pub(crate) fn symb_codomain_full(&self) -> TypeFull<'a> {
                TypeFull::IntType(self.codomain_full())
            }
        }

        impl FodotOptions for IntTypeFuncInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for IntTypeFuncInterp<'_> {
            fn fmt(
                fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>,
            ) -> std::fmt::Result {
                func_display(fmt.value.name(), fmt.value.iter(), true, fmt.options, f)
            }
        }

        impl Display for IntTypeFuncInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(IntTypeFuncInterp<'a>, gen: ('a));
    }
}
