use super::{
    combined_funcs, complete_func_symbol_methods, func_display, impl_real_from_type_element,
    partial_func_symbol_methods,
};
use crate::fodot::{
    TryFromCtx, display_as_debug,
    error::{ArgMismatchError, CodomainError, PfuncError},
    fmt::{FodotDisplay, FodotOptions, FormatOptions},
    structure::{
        ArgsRef, RealTypeFull, TypeFull,
        pfunc::{PfuncDeclInterp, RealTypeDeclInterp},
    },
    vocabulary::Real,
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
                Real,
                RealTypeFull<'a>,
                'a,
                {
                    complete::immutable::RealFuncSymbolInterp<'a>,
                    complete::immutable::RealFuncSymbolInterp,
                }
            )]
            /// A combination of an [RealFuncInterp] and an [RealTypeFuncInterp].
            #[derive(Clone, Debug)]
            pub enum RealFuncSymbolInterp<'a> {
                Real(RealFuncInterp<'a>),
                RealType(RealTypeFuncInterp<'a>),
            }
        }

        partial_func_symbol_methods! {
            (Real, Real),
            impl<'a> RealFuncSymbolInterp<'a>
        }

        /// A partial immutable interpretation of a function with a real codomain.
        #[derive(Clone)]
        pub struct RealFuncInterp<'a> {
            pub(crate) interp: ccpartial::immutable::RealFuncInterp<'a>,
            pub(crate) decl: PfuncDeclInterp<'a>,
        }

        impl<'a> Deref for RealFuncInterp<'a> {
            type Target = PfuncDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        impl_real_from_type_element!(impl<'a> RealFuncInterp<'a>);

        impl<'a> RealFuncInterp<'a> {
            /// Get the interpretation of the symbol with the given arguments.
            pub fn get(&self, args: ArgsRef) -> Result<Option<Real>, ArgMismatchError> {
                let args = ArgsRef::try_from_ctx(args, self.domain_full())?;
                Ok(self.interp.get(args.domain_enum).unwrap())
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
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, Real)> {
                self.interp.into_iter().map(move |(dom_enum, value)| {
                    (ArgsRef::new(dom_enum, self.decl.domain_full()), value)
                })
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter<'b>(&'b self) -> impl Iterator<Item = (ArgsRef<'a>, Real)> + 'b {
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
            ) -> Result<complete::immutable::RealFuncInterp<'a>, Self> {
                match self.interp.try_into_complete() {
                    Ok(interp) => Ok(complete::immutable::RealFuncInterp {
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
            ) -> Result<complete::immutable::RealFuncInterp<'b>, ()> {
                match self.interp.try_as_im_complete() {
                    Ok(interp) => Ok(complete::immutable::RealFuncInterp {
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

        impl FodotOptions for RealFuncInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for RealFuncInterp<'_> {
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

        impl Display for RealFuncInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(RealFuncInterp<'a>, gen: ('a));

        /// A partial immutable interpretation of a constant with a real subtype as codomain.
        #[derive(Clone)]
        pub struct RealTypeFuncInterp<'a> {
            pub(crate) interp: ccpartial::immutable::RealTypeFuncInterp<'a>,
            pub(crate) decl: RealTypeDeclInterp<'a>,
        }

        impl<'a> Deref for RealTypeFuncInterp<'a> {
            type Target = RealTypeDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        impl<'a> RealTypeFuncInterp<'a> {
            /// Get the interpretation of the symbol with the given arguments.
            pub fn get(&self, args: ArgsRef) -> Result<Option<Real>, ArgMismatchError> {
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
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, Real)> {
                self.interp.into_iter().map(move |(dom_enum, value)| {
                    (ArgsRef::new(dom_enum, self.decl.domain_full()), value)
                })
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter<'b>(&'b self) -> impl Iterator<Item = (ArgsRef<'a>, Real)> + 'b {
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
            ) -> Result<complete::immutable::RealTypeFuncInterp<'a>, Self> {
                match self.interp.try_into_complete() {
                    Ok(interp) => Ok(complete::immutable::RealTypeFuncInterp {
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
            ) -> Result<complete::immutable::RealTypeFuncInterp<'b>, ()> {
                match self.interp.try_as_im_complete() {
                    Ok(interp) => Ok(complete::immutable::RealTypeFuncInterp {
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

        impl FodotOptions for RealTypeFuncInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for RealTypeFuncInterp<'_> {
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

        impl Display for RealTypeFuncInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(RealTypeFuncInterp<'a>, gen: ('a));
    }

    pub mod mutable {
        use super::*;
        combined_funcs! {
            #[type(
                partial,
                mutable,
                Real,
                RealTypeFull<'a>,
                'a,
                {
                    complete::mutable::RealFuncSymbolInterp<'a>,
                    complete::immutable::RealFuncSymbolInterp,
                }
            )]
            /// A combination of an [RealFuncInterp] and an [RealTypeFuncInterp].
            #[derive(Debug)]
            pub enum RealFuncSymbolInterp<'a> {
                Real(RealFuncInterp<'a>),
                RealType(RealTypeFuncInterp<'a>),
            }
        }

        partial_func_symbol_methods! {
            (Real, Real),
            impl<'a> RealFuncSymbolInterp<'a>
        }

        /// A partial mutable interpretation of a function with a real codomain.
        pub struct RealFuncInterp<'a> {
            pub(crate) interp: ccpartial::mutable::RealFuncInterp<'a>,
            pub(crate) decl: PfuncDeclInterp<'a>,
        }

        impl<'a> Deref for RealFuncInterp<'a> {
            type Target = PfuncDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        impl_real_from_type_element!(impl<'a> RealFuncInterp<'a>);

        impl<'a> RealFuncInterp<'a> {
            /// Get the interpretation of the symbol with the given arguments.
            pub fn get(&self, args: ArgsRef) -> Result<Option<Real>, ArgMismatchError> {
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
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, Real)> {
                self.interp.into_iter().map(move |(dom_enum, value)| {
                    (ArgsRef::new(dom_enum, self.decl.domain_full()), value)
                })
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter<'b>(&'b self) -> impl Iterator<Item = (ArgsRef<'a>, Real)> + 'b {
                self.interp.iter().map(|(dom_enum, value)| {
                    (ArgsRef::new(dom_enum, self.decl.domain_full()), value)
                })
            }

            /// Try converting this interpretation into its complete counterpart.
            ///
            /// This function returns the original interpretation in [Err] if the interpretation is
            /// not complete.
            pub fn try_into_complete(self) -> Result<complete::mutable::RealFuncInterp<'a>, Self> {
                match self.interp.try_into_complete() {
                    Ok(interp) => Ok(complete::mutable::RealFuncInterp {
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
            ) -> Result<complete::immutable::RealFuncInterp<'b>, ()> {
                match self.interp.try_as_im_complete() {
                    Ok(interp) => Ok(complete::immutable::RealFuncInterp {
                        interp,
                        decl: self.decl.clone(),
                    }),
                    Err(_) => Err(()),
                }
            }

            pub fn set(
                &mut self,
                args: ArgsRef,
                value: Option<Real>,
            ) -> Result<(), ArgMismatchError> {
                let args = ArgsRef::try_from_ctx(args, self.domain_full())?;
                Ok(self.interp.set(args.domain_enum, value).unwrap())
            }

            pub fn set_if_unknown(
                &mut self,
                args: ArgsRef,
                value: Real,
            ) -> Result<bool, ArgMismatchError> {
                let args = ArgsRef::try_from_ctx(args, self.domain_full())?;
                Ok(self.interp.set_if_unknown(args.domain_enum, value).unwrap())
            }

            pub fn set_all_unknown_to_value(&mut self, value: Real) {
                self.interp.fill_unknown_with(value)
            }

            fn func_set_all_unknown_to_value(&mut self, value: Real) -> Result<(), CodomainError> {
                Ok(self.set_all_unknown_to_value(value))
            }

            pub(crate) fn symb_codomain_full(&self) -> TypeFull<'a> {
                TypeFull::Real
            }
        }

        impl FodotOptions for RealFuncInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for RealFuncInterp<'_> {
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

        impl Display for RealFuncInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(RealFuncInterp<'a>, gen: ('a));

        /// A partial mutable interpretation of a function with a real subtype as codomain.
        pub struct RealTypeFuncInterp<'a> {
            pub(crate) interp: ccpartial::mutable::RealTypeFuncInterp<'a>,
            pub(crate) decl: RealTypeDeclInterp<'a>,
        }

        impl<'a> Deref for RealTypeFuncInterp<'a> {
            type Target = RealTypeDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        impl<'a> RealTypeFuncInterp<'a> {
            /// Get the interpretation of the symbol with the given arguments.
            pub fn get(&self, args: ArgsRef) -> Result<Option<Real>, ArgMismatchError> {
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
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, Real)> {
                self.interp.into_iter().map(move |(dom_enum, value)| {
                    (ArgsRef::new(dom_enum, self.decl.domain_full()), value)
                })
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter<'b>(&'b self) -> impl Iterator<Item = (ArgsRef<'a>, Real)> + 'b {
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
            ) -> Result<complete::mutable::RealTypeFuncInterp<'a>, Self> {
                match self.interp.try_into_complete() {
                    Ok(interp) => Ok(complete::mutable::RealTypeFuncInterp {
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
            ) -> Result<complete::immutable::RealTypeFuncInterp<'b>, ()> {
                match self.interp.try_as_im_complete() {
                    Ok(interp) => Ok(complete::immutable::RealTypeFuncInterp {
                        interp,
                        decl: self.decl.clone(),
                    }),
                    Err(_) => Err(()),
                }
            }

            /// Sets the interpretation for the given argument with the given value.
            pub fn set(&mut self, args: ArgsRef, value: Option<Real>) -> Result<(), PfuncError> {
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
                value: Real,
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
            pub fn set_all_unknown_to_value(&mut self, value: Real) -> Result<(), CodomainError> {
                self.interp
                    .fill_unknown_with(value)
                    .map_err(|_| CodomainError)
            }

            fn func_set_all_unknown_to_value(&mut self, value: Real) -> Result<(), CodomainError> {
                self.set_all_unknown_to_value(value)
            }

            pub(crate) fn symb_codomain_full(&self) -> TypeFull<'a> {
                TypeFull::RealType(self.codomain_full())
            }
        }

        impl FodotOptions for RealTypeFuncInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for RealTypeFuncInterp<'_> {
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

        impl Display for RealTypeFuncInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(RealTypeFuncInterp<'a>, gen: ('a));
    }
}

pub mod complete {
    use super::*;
    pub mod immutable {
        use super::*;
        combined_funcs! {
            #[type(complete, immutable, Real, RealTypeFull<'a>, 'a)]
            #[derive(Clone, Debug)]
            /// A combination of an [RealFuncInterp] and an [RealTypeFuncInterp].
            pub enum RealFuncSymbolInterp<'a> {
                Real(RealFuncInterp<'a>),
                RealType(RealTypeFuncInterp<'a>),
            }
        }

        complete_func_symbol_methods! {
            (Real, Real),
            impl<'a> RealFuncSymbolInterp<'a>
        }

        /// A complete immutable interpretation of a function with a real codomain.
        #[derive(Clone)]
        pub struct RealFuncInterp<'a> {
            pub(crate) interp: cccomplete::immutable::RealFuncInterp<'a>,
            pub(crate) decl: PfuncDeclInterp<'a>,
        }

        impl<'a> Deref for RealFuncInterp<'a> {
            type Target = PfuncDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        impl_real_from_type_element!(impl<'a> RealFuncInterp<'a>);

        impl<'a> RealFuncInterp<'a> {
            /// Get the interpretation of the symbol with the given arguments.
            pub fn get(&self, args: ArgsRef) -> Result<Real, ArgMismatchError> {
                let args = ArgsRef::try_from_ctx(args, self.domain_full())?;
                Ok(self.interp.get(args.domain_enum).unwrap())
            }

            /// Returns an owned iterator over all arguments and their corresponding interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, Real)> {
                self.interp.into_iter().map(move |(dom_enum, value)| {
                    (ArgsRef::new(dom_enum, self.decl.domain_full()), value)
                })
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter<'b>(&'b self) -> impl Iterator<Item = (ArgsRef<'a>, Real)> + 'b {
                self.interp.iter().map(|(dom_enum, value)| {
                    (ArgsRef::new(dom_enum, self.decl.domain_full()), value)
                })
            }

            pub(crate) fn symb_codomain_full(&self) -> TypeFull<'a> {
                TypeFull::Real
            }
        }

        impl FodotOptions for RealFuncInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for RealFuncInterp<'_> {
            fn fmt(
                fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>,
            ) -> std::fmt::Result {
                func_display(fmt.value.name(), fmt.value.iter(), true, fmt.options, f)
            }
        }

        impl Display for RealFuncInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(RealFuncInterp<'a>, gen: ('a));

        /// A complete immutable interpretation of a function with a real subtype as codomain.
        #[derive(Clone)]
        pub struct RealTypeFuncInterp<'a> {
            pub(crate) interp: cccomplete::immutable::RealTypeFuncInterp<'a>,
            pub(crate) decl: RealTypeDeclInterp<'a>,
        }

        impl<'a> Deref for RealTypeFuncInterp<'a> {
            type Target = RealTypeDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        impl<'a> RealTypeFuncInterp<'a> {
            /// Get the interpretation of the symbol with the given arguments.
            pub fn get(&self, args: ArgsRef) -> Result<Real, ArgMismatchError> {
                let args = ArgsRef::try_from_ctx(args, self.domain_full())?;
                Ok(self.interp.get(args.domain_enum).unwrap())
            }

            /// Returns an owned iterator over all arguments and their corresponding interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, Real)> {
                self.interp.into_iter().map(move |(dom_enum, value)| {
                    (ArgsRef::new(dom_enum, self.decl.domain_full()), value)
                })
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter<'b>(&'b self) -> impl Iterator<Item = (ArgsRef<'a>, Real)> + 'b {
                self.interp.iter().map(|(dom_enum, value)| {
                    (ArgsRef::new(dom_enum, self.decl.domain_full()), value)
                })
            }

            pub(crate) fn symb_codomain_full(&self) -> TypeFull<'a> {
                TypeFull::RealType(self.codomain_full())
            }
        }

        impl FodotOptions for RealTypeFuncInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for RealTypeFuncInterp<'_> {
            fn fmt(
                fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>,
            ) -> std::fmt::Result {
                func_display(fmt.value.name(), fmt.value.iter(), true, fmt.options, f)
            }
        }

        impl Display for RealTypeFuncInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(RealTypeFuncInterp<'a>, gen: ('a));
    }

    pub mod mutable {
        use super::*;
        combined_funcs! {
            #[type(complete, mutable, Real, RealTypeFull<'a>, 'a)]
            /// A combination of an [RealFuncInterp] and an [RealTypeFuncInterp].
            #[derive(Debug)]
            pub enum RealFuncSymbolInterp<'a> {
                Real(RealFuncInterp<'a>),
                RealType(RealTypeFuncInterp<'a>),
            }
        }

        complete_func_symbol_methods! {
            (Real, Real),
            impl<'a> RealFuncSymbolInterp<'a>
        }

        /// A complete mutable interpretation of a function with a real codomain.
        pub struct RealFuncInterp<'a> {
            pub(crate) interp: cccomplete::mutable::RealFuncInterp<'a>,
            pub(crate) decl: PfuncDeclInterp<'a>,
        }

        impl<'a> Deref for RealFuncInterp<'a> {
            type Target = PfuncDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        impl_real_from_type_element!(impl<'a> RealFuncInterp<'a>);

        impl<'a> RealFuncInterp<'a> {
            /// Get the interpretation of the symbol with the given arguments.
            pub fn get(&self, args: ArgsRef) -> Result<Real, ArgMismatchError> {
                let args = ArgsRef::try_from_ctx(args, self.domain_full())?;
                Ok(self.interp.get(args.domain_enum).unwrap())
            }

            /// Returns an owned iterator over all arguments and their corresponding interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, Real)> {
                self.interp.into_iter().map(move |(dom_enum, value)| {
                    (ArgsRef::new(dom_enum, self.decl.domain_full()), value)
                })
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter<'b>(&'b self) -> impl Iterator<Item = (ArgsRef<'a>, Real)> + 'b {
                self.interp.iter().map(|(dom_enum, value)| {
                    (ArgsRef::new(dom_enum, self.decl.domain_full()), value)
                })
            }

            /// Sets the interpretation for the given argument with the given value.
            pub fn set(&mut self, args: ArgsRef, value: Real) -> Result<(), ArgMismatchError> {
                let args = ArgsRef::try_from_ctx(args, self.domain_full())?;
                Ok(self.interp.set(args.domain_enum, value).unwrap())
            }

            pub(crate) fn symb_codomain_full(&self) -> TypeFull<'a> {
                TypeFull::Real
            }
        }

        impl FodotOptions for RealFuncInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for RealFuncInterp<'_> {
            fn fmt(
                fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>,
            ) -> std::fmt::Result {
                func_display(fmt.value.name(), fmt.value.iter(), true, fmt.options, f)
            }
        }

        impl Display for RealFuncInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(RealFuncInterp<'a>, gen: ('a));

        /// A complete mutable interpretation of a function with a real subtype as codomain.
        pub struct RealTypeFuncInterp<'a> {
            pub(crate) interp: cccomplete::mutable::RealTypeFuncInterp<'a>,
            pub(crate) decl: RealTypeDeclInterp<'a>,
        }

        impl<'a> Deref for RealTypeFuncInterp<'a> {
            type Target = RealTypeDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        impl<'a> RealTypeFuncInterp<'a> {
            /// Get the interpretation of the symbol with the given arguments.
            pub fn get(&self, args: ArgsRef) -> Result<Real, ArgMismatchError> {
                let args = ArgsRef::try_from_ctx(args, self.domain_full())?;
                Ok(self.interp.get(args.domain_enum).unwrap())
            }

            /// Returns an owned iterator over all arguments and their corresponding interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, Real)> {
                self.interp.into_iter().map(move |(dom_enum, value)| {
                    (ArgsRef::new(dom_enum, self.decl.domain_full()), value)
                })
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter<'b>(&'b self) -> impl Iterator<Item = (ArgsRef<'a>, Real)> + 'b {
                self.interp.iter().map(|(dom_enum, value)| {
                    (ArgsRef::new(dom_enum, self.decl.domain_full()), value)
                })
            }

            /// Sets the interpretation for the given argument with the given value.
            pub fn set(&mut self, args: ArgsRef, value: Real) -> Result<(), PfuncError> {
                let args = ArgsRef::try_from_ctx(args, self.domain_full())?;
                self.interp
                    .set(args.domain_enum, value)
                    .map_err(|f| match f {
                        ccap::PfuncError::DomainError(_) => unreachable!(),
                        ccap::PfuncError::CodomainError(_) => CodomainError.into(),
                    })
            }

            pub(crate) fn symb_codomain_full(&self) -> TypeFull<'a> {
                TypeFull::RealType(self.codomain_full())
            }
        }

        impl FodotOptions for RealTypeFuncInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for RealTypeFuncInterp<'_> {
            fn fmt(
                fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>,
            ) -> std::fmt::Result {
                func_display(fmt.value.name(), fmt.value.iter(), true, fmt.options, f)
            }
        }

        impl Display for RealTypeFuncInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(RealTypeFuncInterp<'a>, gen: ('a));
    }
}
