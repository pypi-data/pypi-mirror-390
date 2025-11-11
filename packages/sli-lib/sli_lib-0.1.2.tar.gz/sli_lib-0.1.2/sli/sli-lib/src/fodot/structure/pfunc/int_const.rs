use super::{
    combined_nullaries, complete_nullary_display, complete_nullary_symbol_methods,
    impl_int_from_type_element, partial_nullary_display, partial_nullary_symbol_methods,
};
use crate::fodot::{
    display_as_debug,
    error::{CodomainError, DomainMismatch, PfuncError},
    fmt::{FodotDisplay, FodotOptions, FormatOptions},
    structure::{
        IntTypeFull, TypeFull,
        pfunc::{ArgsRef, IntTypeDeclInterp, PfuncDeclInterp},
    },
    vocabulary::Int,
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
                Int,
                IntTypeFull<'a>,
                'a,
                {
                    complete::immutable::IntConstSymbolInterp<'a>,
                    complete::immutable::IntConstSymbolInterp,
                }
            )]
            /// A combination of an [IntConstInterp] and an [IntTypeConstInterp].
            #[derive(Clone, Debug)]
            pub enum IntConstSymbolInterp<'a> {
                Int(IntConstInterp<'a>),
                IntType(IntTypeConstInterp<'a>),
            }
        }

        partial_nullary_symbol_methods! {
            (Int, Int),
            impl<'a> IntConstSymbolInterp<'a>
        }

        /// A partial immutable interpretation of a constant with an integer codomain.
        #[derive(Clone)]
        pub struct IntConstInterp<'a> {
            pub(crate) interp: ccpartial::immutable::IntConstInterp<'a>,
            pub(crate) decl: PfuncDeclInterp<'a>,
        }

        impl_int_from_type_element!(impl<'a> IntConstInterp<'a>);

        impl<'a> Deref for IntConstInterp<'a> {
            type Target = PfuncDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        impl<'a> IntConstInterp<'a> {
            /// Get the interpretation
            pub fn get(&self) -> Option<Int> {
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
            pub fn iter(&self) -> impl Iterator<Item = (ArgsRef<'a>, Int)> + use<'a> {
                self.get()
                    .map(|f| (ArgsRef::empty(self.decl.domain_full()).unwrap(), f))
                    .into_iter()
            }

            /// Returns an owned iterator over all arguments and their corresponding interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, Int)> {
                self.iter()
            }

            /// Try converting this interpretation into its complete counterpart.
            ///
            /// This function returns the original interpretation in [Err] if the interpretation is
            /// not complete.
            pub fn try_into_complete(
                self,
            ) -> Result<complete::immutable::IntConstInterp<'a>, Self> {
                match self.interp.try_into_complete() {
                    Ok(interp) => Ok(complete::immutable::IntConstInterp {
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
            ) -> Result<complete::immutable::IntConstInterp<'b>, ()> {
                match self.interp.try_as_im_complete() {
                    Ok(interp) => Ok(complete::immutable::IntConstInterp {
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

        impl FodotOptions for IntConstInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for IntConstInterp<'_> {
            fn fmt(
                fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>,
            ) -> std::fmt::Result {
                partial_nullary_display(fmt.value.name(), fmt.value.get(), fmt.options, f)
            }
        }

        impl Display for IntConstInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(IntConstInterp<'a>, gen: ('a));

        /// A partial immutable interpretation of a constant with an integer subtype as codomain.
        #[derive(Clone)]
        pub struct IntTypeConstInterp<'a> {
            pub(crate) interp: ccpartial::immutable::IntTypeConstInterp<'a>,
            pub(crate) decl: IntTypeDeclInterp<'a>,
        }

        impl<'a> Deref for IntTypeConstInterp<'a> {
            type Target = IntTypeDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        impl<'a> IntTypeConstInterp<'a> {
            /// Get the interpretation
            pub fn get(&self) -> Option<Int> {
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
            pub fn iter(&self) -> impl Iterator<Item = (ArgsRef<'a>, Int)> + use<'a> {
                self.get()
                    .map(|f| (ArgsRef::empty(self.decl.domain_full()).unwrap(), f))
                    .into_iter()
            }

            /// Returns an owned iterator over all arguments and their corresponding interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, Int)> {
                self.iter()
            }

            /// Try converting this interpretation into its complete counterpart.
            ///
            /// This function returns the original interpretation in [Err] if the interpretation is
            /// not complete.
            pub fn try_into_complete(
                self,
            ) -> Result<complete::immutable::IntTypeConstInterp<'a>, Self> {
                match self.interp.try_into_complete() {
                    Ok(interp) => Ok(complete::immutable::IntTypeConstInterp {
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
            ) -> Result<complete::immutable::IntTypeConstInterp<'b>, ()> {
                match self.interp.try_as_im_complete() {
                    Ok(interp) => Ok(complete::immutable::IntTypeConstInterp {
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

        impl FodotOptions for IntTypeConstInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for IntTypeConstInterp<'_> {
            fn fmt(
                fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>,
            ) -> std::fmt::Result {
                partial_nullary_display(fmt.value.name(), fmt.value.get(), fmt.options, f)
            }
        }

        impl Display for IntTypeConstInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(IntTypeConstInterp<'a>, gen: ('a));
    }

    pub mod mutable {
        use super::*;

        combined_nullaries! {
            #[type(
                partial,
                mutable,
                Int,
                IntTypeFull<'a>,
                'a,
                {
                    complete::mutable::IntConstSymbolInterp<'a>,
                    complete::immutable::IntConstSymbolInterp,
                }
            )]
            /// A combination of an [IntConstInterp] and an [IntTypeConstInterp].
            #[derive(Debug)]
            pub enum IntConstSymbolInterp<'a> {
                Int(IntConstInterp<'a>),
                IntType(IntTypeConstInterp<'a>),
            }
        }

        partial_nullary_symbol_methods! {
            (Int, Int),
            impl<'a> IntConstSymbolInterp<'a>
        }

        /// A partial mutable interpretation of a constant with an integer codomain.
        pub struct IntConstInterp<'a> {
            pub(crate) interp: ccpartial::mutable::IntConstInterp<'a>,
            pub(crate) decl: PfuncDeclInterp<'a>,
        }

        impl_int_from_type_element!(impl<'a> IntConstInterp<'a>);

        impl<'a> Deref for IntConstInterp<'a> {
            type Target = PfuncDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        impl<'a> IntConstInterp<'a> {
            /// Get the interpretation
            pub fn get(&self) -> Option<Int> {
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

            pub fn set(&mut self, value: Option<Int>) {
                self.interp.set(value)
            }

            fn nullary_set(&mut self, value: Option<Int>) -> Result<(), CodomainError> {
                self.set(value);
                Ok(())
            }

            /// Sets the interpretation if the interpretation is unknown.
            ///
            /// Returns a [bool] which is true if the proposition was unknown, false otherwise.
            pub fn set_if_unknown(&mut self, value: Int) -> bool {
                self.interp.set_if_unknown(value)
            }

            fn nullary_set_if_unknown(&mut self, value: Int) -> Result<bool, CodomainError> {
                Ok(self.set_if_unknown(value))
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter(&self) -> impl Iterator<Item = (ArgsRef<'a>, Int)> + use<'a> {
                self.get()
                    .map(|f| (ArgsRef::empty(self.decl.domain_full()).unwrap(), f))
                    .into_iter()
            }

            /// Returns an owned iterator over all arguments and their corresponding interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, Int)> {
                self.iter()
            }

            /// Try converting this interpretation into its complete counterpart.
            ///
            /// This function returns the original interpretation in [Err] if the interpretation is
            /// not complete.
            pub fn try_into_complete(self) -> Result<complete::mutable::IntConstInterp<'a>, Self> {
                match self.interp.try_into_complete() {
                    Ok(interp) => Ok(complete::mutable::IntConstInterp {
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
            ) -> Result<complete::immutable::IntConstInterp<'b>, ()> {
                match self.interp.try_as_im_complete() {
                    Ok(interp) => Ok(complete::immutable::IntConstInterp {
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

        impl FodotOptions for IntConstInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for IntConstInterp<'_> {
            fn fmt(
                fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>,
            ) -> std::fmt::Result {
                partial_nullary_display(fmt.value.name(), fmt.value.get(), fmt.options, f)
            }
        }

        impl Display for IntConstInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(IntConstInterp<'a>, gen: ('a));

        /// A partial mutable interpretation of a constant with an integer subtype as codomain.
        pub struct IntTypeConstInterp<'a> {
            pub(crate) interp: ccpartial::mutable::IntTypeConstInterp<'a>,
            pub(crate) decl: IntTypeDeclInterp<'a>,
        }

        impl<'a> Deref for IntTypeConstInterp<'a> {
            type Target = IntTypeDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        impl<'a> IntTypeConstInterp<'a> {
            /// Get the interpretation
            pub fn get(&self) -> Option<Int> {
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
            pub fn set(&mut self, value: Option<Int>) -> Result<(), CodomainError> {
                self.interp.set(value).map_err(|_| CodomainError)
            }

            fn nullary_set(&mut self, value: Option<Int>) -> Result<(), CodomainError> {
                self.set(value)
            }

            /// Sets the interpretation if the interpretation is unknown.
            ///
            /// Returns a [bool] which is true if the proposition was unknown, false otherwise.
            pub fn set_if_unknown(&mut self, value: Int) -> Result<bool, CodomainError> {
                self.interp.set_if_unknown(value).map_err(|_| CodomainError)
            }

            fn nullary_set_if_unknown(&mut self, value: Int) -> Result<bool, CodomainError> {
                self.set_if_unknown(value)
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter(&self) -> impl Iterator<Item = (ArgsRef<'a>, Int)> + use<'a> {
                self.get()
                    .map(|f| (ArgsRef::empty(self.decl.domain_full()).unwrap(), f))
                    .into_iter()
            }

            /// Returns an owned iterator over all arguments and their corresponding interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, Int)> {
                self.iter()
            }

            /// Try converting this interpretation into its complete counterpart.
            ///
            /// This function returns the original interpretation in [Err] if the interpretation is
            /// not complete.
            pub fn try_into_complete(
                self,
            ) -> Result<complete::mutable::IntTypeConstInterp<'a>, Self> {
                match self.interp.try_into_complete() {
                    Ok(interp) => Ok(complete::mutable::IntTypeConstInterp {
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
            ) -> Result<complete::immutable::IntTypeConstInterp<'b>, ()> {
                match self.interp.try_as_im_complete() {
                    Ok(interp) => Ok(complete::immutable::IntTypeConstInterp {
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

        impl FodotOptions for IntTypeConstInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for IntTypeConstInterp<'_> {
            fn fmt(
                fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>,
            ) -> std::fmt::Result {
                partial_nullary_display(fmt.value.name(), fmt.value.get(), fmt.options, f)
            }
        }

        impl Display for IntTypeConstInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(IntTypeConstInterp<'a>, gen: ('a));
    }
}

pub mod complete {
    use super::*;
    pub mod immutable {
        use super::*;
        combined_nullaries! {
            #[type(complete, immutable, Int, IntTypeFull<'a>, 'a)]
            /// A combination of an [IntConstInterp] and an [IntTypeConstInterp].
            #[derive(Clone, Debug)]
            pub enum IntConstSymbolInterp<'a> {
                Int(IntConstInterp<'a>),
                IntType(IntTypeConstInterp<'a>),
            }
        }

        complete_nullary_symbol_methods! {
            (Int, Int),
            impl<'a> IntConstSymbolInterp<'a>
        }

        /// A complete immutable interpretation of a constant with an integer codomain.
        #[derive(Clone)]
        pub struct IntConstInterp<'a> {
            pub(crate) interp: cccomplete::immutable::IntConstInterp<'a>,
            pub(crate) decl: PfuncDeclInterp<'a>,
        }

        impl_int_from_type_element!(impl<'a> IntConstInterp<'a>);

        impl<'a> Deref for IntConstInterp<'a> {
            type Target = PfuncDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        impl<'a> IntConstInterp<'a> {
            /// Get the interpretation.
            pub fn get(&self) -> Int {
                self.interp.get()
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter(&self) -> impl Iterator<Item = (ArgsRef<'a>, Int)> + use<'a> {
                core::iter::once((ArgsRef::empty(self.decl.domain_full()).unwrap(), self.get()))
            }

            /// Returns an owned iterator over all arguments and their corresponding interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, Int)> {
                self.iter()
            }

            pub(crate) fn symb_codomain_full(&self) -> TypeFull<'a> {
                TypeFull::Int
            }
        }

        impl FodotOptions for IntConstInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for IntConstInterp<'_> {
            fn fmt(
                fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>,
            ) -> std::fmt::Result {
                complete_nullary_display(fmt.value.name(), fmt.value.get(), fmt.options, f)
            }
        }

        impl Display for IntConstInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(IntConstInterp<'a>, gen: ('a));

        /// A complete immutable interpretation of a constant with an integer subtype as codomain.
        #[derive(Clone)]
        pub struct IntTypeConstInterp<'a> {
            pub(crate) interp: cccomplete::immutable::IntTypeConstInterp<'a>,
            pub(crate) decl: IntTypeDeclInterp<'a>,
        }

        impl<'a> Deref for IntTypeConstInterp<'a> {
            type Target = IntTypeDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        impl<'a> IntTypeConstInterp<'a> {
            /// Get the interpretation.
            pub fn get(&self) -> Int {
                self.interp.get()
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter(&self) -> impl Iterator<Item = (ArgsRef<'a>, Int)> + use<'a> {
                core::iter::once((ArgsRef::empty(self.decl.domain_full()).unwrap(), self.get()))
            }

            /// Returns an owned iterator over all arguments and their corresponding interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, Int)> {
                self.iter()
            }

            pub(crate) fn symb_codomain_full(&self) -> TypeFull<'a> {
                TypeFull::IntType(self.codomain_full())
            }
        }

        impl FodotOptions for IntTypeConstInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for IntTypeConstInterp<'_> {
            fn fmt(
                fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>,
            ) -> std::fmt::Result {
                complete_nullary_display(fmt.value.name(), fmt.value.get(), fmt.options, f)
            }
        }

        impl Display for IntTypeConstInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(IntTypeConstInterp<'a>, gen: ('a));
    }

    pub mod mutable {
        use super::*;
        combined_nullaries! {
            #[type(complete, mutable, Int, IntTypeFull<'a>, 'a)]
            /// A combination of an [IntConstInterp] and an [IntTypeConstInterp].
            #[derive(Debug)]
            pub enum IntConstSymbolInterp<'a> {
                Int(IntConstInterp<'a>),
                IntType(IntTypeConstInterp<'a>),
            }
        }

        complete_nullary_symbol_methods! {
            (Int, Int),
            impl<'a> IntConstSymbolInterp<'a>
        }

        /// A complete mutable interpretation of a constant with an integer codomain.
        pub struct IntConstInterp<'a> {
            pub(crate) interp: cccomplete::mutable::IntConstInterp<'a>,
            pub(crate) decl: PfuncDeclInterp<'a>,
        }

        impl_int_from_type_element!(impl<'a> IntConstInterp<'a>);

        impl<'a> Deref for IntConstInterp<'a> {
            type Target = PfuncDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        impl<'a> IntConstInterp<'a> {
            /// Get the interpretation.
            pub fn get(&self) -> Int {
                self.interp.get()
            }

            /// Set the interpretation.
            pub fn set(&mut self, value: Int) {
                self.interp.set(value)
            }

            fn nullary_set(&mut self, value: Int) -> Result<(), CodomainError> {
                self.set(value);
                Ok(())
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter(&self) -> impl Iterator<Item = (ArgsRef<'a>, Int)> + use<'a> {
                core::iter::once((ArgsRef::empty(self.decl.domain_full()).unwrap(), self.get()))
            }

            /// Returns an owned iterator over all arguments and their corresponding interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, Int)> {
                self.iter()
            }

            pub(crate) fn symb_codomain_full(&self) -> TypeFull<'a> {
                TypeFull::Int
            }
        }

        impl FodotOptions for IntConstInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for IntConstInterp<'_> {
            fn fmt(
                fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>,
            ) -> std::fmt::Result {
                complete_nullary_display(fmt.value.name(), fmt.value.get(), fmt.options, f)
            }
        }

        impl Display for IntConstInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(IntConstInterp<'a>, gen: ('a));

        /// A complete mutable interpretation of a constant with an integer subtype as codomain.
        pub struct IntTypeConstInterp<'a> {
            pub(crate) interp: cccomplete::mutable::IntTypeConstInterp<'a>,
            pub(crate) decl: IntTypeDeclInterp<'a>,
        }

        impl<'a> Deref for IntTypeConstInterp<'a> {
            type Target = IntTypeDeclInterp<'a>;

            fn deref(&self) -> &Self::Target {
                &self.decl
            }
        }

        impl<'a> IntTypeConstInterp<'a> {
            /// Get the interpretation.
            pub fn get(&self) -> Int {
                self.interp.get()
            }

            /// Set the interpretation.
            pub fn set(&mut self, value: Int) -> Result<(), CodomainError> {
                self.interp.set(value).map_err(|_| CodomainError)
            }

            fn nullary_set(&mut self, value: Int) -> Result<(), CodomainError> {
                self.set(value)
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter(&self) -> impl Iterator<Item = (ArgsRef<'a>, Int)> + use<'a> {
                core::iter::once((ArgsRef::empty(self.decl.domain_full()).unwrap(), self.get()))
            }

            /// Returns an owned iterator over all arguments and their corresponding interpretation.
            pub fn into_iter(self) -> impl Iterator<Item = (ArgsRef<'a>, Int)> {
                self.iter()
            }

            pub(crate) fn symb_codomain_full(&self) -> TypeFull<'a> {
                TypeFull::IntType(self.codomain_full())
            }
        }

        impl FodotOptions for IntTypeConstInterp<'_> {
            type Options<'a> = FormatOptions;
        }

        impl FodotDisplay for IntTypeConstInterp<'_> {
            fn fmt(
                fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>,
            ) -> std::fmt::Result {
                complete_nullary_display(fmt.value.name(), fmt.value.get(), fmt.options, f)
            }
        }

        impl Display for IntTypeConstInterp<'_> {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.display())
            }
        }

        display_as_debug!(IntTypeConstInterp<'a>, gen: ('a));
    }
}
