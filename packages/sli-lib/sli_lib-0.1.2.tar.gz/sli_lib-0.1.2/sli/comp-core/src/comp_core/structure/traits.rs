//! Provides traits and blanket implementations for implementers of these traits.
//! Traits for partial structures and partially interpreted symbol can be found in [partial].
//! The [complete] module provides traits for complete structures and interpretations.
//!
//! Modules [partial] and [complete] provide store traits, when a structure
//! datastructure and its related datastructures implement these store traits they can be used as
//! backends for a SLI structure. This is not to make SLI structures generic, this is just for
//! clarity, only one structure backend can be used per compilation.
//! These traits are split into traits for nullaries and traits for functions (including predicates).
//! Separate predicate store traits exist as well for [partial] and [complete].
//!
//! Module [applied_symb_interp](super::applied_symb_interp) provides methods for symbol interpretation
//! for the backend implementation.
//!
//! Note also that, even though a store has no concept of a vocabulary, reusing a store (without
//! clearing its contents) for one vocabulary for a different vocabulary is not a good idea.
//!
//! # Store traits
//!
//! [partial] and [complete] contain immutable and mutable store methods for
//! constants and functions.
//! In SLI, unless otherwise specified, nullaries are FO(·) constants and propositions and
//! functions are FO(·) functions and predicates.
//! [complete] provides [complete::ImPred], and [partial] provides [partial::ImPred] containing
//! must have methods only for predicates of both flavors.
//!
//! # Adding new methods
//!
//! We can add more methods in 3 steps.
//! 1. Add and implement a method to the corresponding store trait (unless this method need not be
//! [TypeInterps](super::TypeInterps) aware).
//! Adding a default implementation can be make the process faster if this is desirable (note if
//! the method is performance minded be careful with default implementation, i.e. don't forget
//! adding non default implementation to blanket implementations).
//! 2. Add this method to the correct place somewhere in [applied_symb_interp](super::applied_symb_interp).
use super::RawTypeInterps;
use super::{IntInterp, RealInterp, StrInterp};
use crate::comp_core::{
    structure::{Int, Real},
    vocabulary::{DomainEnum, DomainSlice, TypeEnum},
};
use duplicate::duplicate_item;
use std::marker::PhantomData;
pub mod complete;
pub mod partial;

#[derive(Clone, Copy)]
pub struct SymbolInfo<'a> {
    pub type_interps: &'a RawTypeInterps,
    pub domain: &'a DomainSlice,
    pub codomain: CodomainInterp<'a>,
}

#[derive(Clone, Copy)]
pub enum CodomainInterp<'a> {
    Bool,
    Int(Option<&'a <Int as TypeInterp>::InterpType>),
    Real(Option<&'a <Real as TypeInterp>::InterpType>),
    Str(&'a <TypeEnum as TypeInterp>::InterpType),
}

pub trait ToOwnedStore {
    type Owned;

    fn to_owned(&self, common: SymbolInfo) -> Self::Owned;
}

impl<'a, T> ToOwnedStore for &'a T
where
    T: ToOwnedStore,
{
    type Owned = T::Owned;

    fn to_owned(&self, common: SymbolInfo) -> Self::Owned {
        T::to_owned(self, common)
    }
}

impl<'a, T> ToOwnedStore for &'a mut T
where
    T: ToOwnedStore,
{
    type Owned = T::Owned;

    fn to_owned(&self, common: SymbolInfo) -> Self::Owned {
        T::to_owned(self, common)
    }
}

pub trait TypeIter<S> {
    fn start(&self) -> S;
    fn next(&self, cur: S) -> Option<S>;
}

#[derive(Clone)]
pub struct PrimIter<S: PrimTypeIter> {
    phantom: PhantomData<S>,
}

impl<S: PrimTypeIter> PrimIter<S> {
    pub fn new() -> Self {
        Self {
            phantom: PhantomData,
        }
    }
}

impl<S: PrimTypeIter> TypeIter<S> for PrimIter<S> {
    fn start(&self) -> S {
        S::start()
    }

    fn next(&self, cur: S) -> Option<S> {
        cur.next()
    }
}

pub enum MixedTypeIter<'a, S: CustomTypeIter + PrimTypeIter> {
    Prim(PrimIter<S>),
    Custom(CustomIter<'a, S>),
}

impl<'a, S: CustomTypeIter + PrimTypeIter> TypeIter<S> for MixedTypeIter<'a, S> {
    fn start(&self) -> S {
        match self {
            Self::Prim(value) => value.start(),
            Self::Custom(value) => value.start(),
        }
    }

    fn next(&self, cur: S) -> Option<S> {
        match self {
            Self::Prim(value) => value.next(cur),
            Self::Custom(value) => value.next(cur),
        }
    }
}

#[derive(Clone)]
pub struct CustomIter<'a, S: CustomTypeIter> {
    codomain_interp: &'a S::InterpType,
}

impl<'a, S: CustomTypeIter> CustomIter<'a, S> {
    pub fn new(codomain_interp: &'a S::InterpType) -> Option<Self> {
        if codomain_interp.len() == 0 {
            return None;
        }
        Self { codomain_interp }.into()
    }
}

impl<'a, S: CustomTypeIter> TypeIter<S> for CustomIter<'a, S> {
    fn start(&self) -> S {
        S::start(&self.codomain_interp).unwrap()
    }

    fn next(&self, cur: S) -> Option<S> {
        cur.next(&self.codomain_interp)
    }
}

pub trait PrimTypeIter: Sized {
    fn start() -> Self;
    fn next(self) -> Option<Self>;
}

pub trait CustomTypeIter: Sized + TypeInterp {
    fn start(interp: &Self::InterpType) -> Option<Self>;
    fn next(self, interp: &Self::InterpType) -> Option<Self>;
}

impl PrimTypeIter for bool {
    fn start() -> Self {
        false
    }

    fn next(self) -> Option<Self> {
        match self {
            false => Some(true),
            true => None,
        }
    }
}

impl PrimTypeIter for Int {
    fn start() -> Self {
        0
    }

    fn next(self) -> Option<Self> {
        self.checked_add(1)
    }
}

impl PrimTypeIter for Real {
    fn start() -> Self {
        Real::from(0)
    }

    fn next(self) -> Option<Self> {
        // This is fine for now
        self.add(1.into()).ok()
    }
}

#[duplicate_item(
    item;
    [Int];
    [Real];
)]
impl CustomTypeIter for item {
    fn start(interp: &Self::InterpType) -> Option<Self> {
        if interp.len() == 0 {
            None
        } else {
            Some(interp.get(&TypeEnum(0)))
        }
    }

    fn next(self, interp: &Self::InterpType) -> Option<Self> {
        let cur = interp.get_index_of(&self).unwrap();
        let next = usize::from(cur) + 1;
        if next < interp.len() {
            interp.get(&(next).into()).into()
        } else {
            None
        }
    }
}

impl CustomTypeIter for TypeEnum {
    fn start(interp: &Self::InterpType) -> Option<Self> {
        if interp.len() == 0 {
            None
        } else {
            Some(TypeEnum(0))
        }
    }

    fn next(self, interp: &Self::InterpType) -> Option<Self> {
        let next = usize::from(self) + 1;
        if next < interp.len() {
            Some(next.into())
        } else {
            None
        }
    }
}

pub trait TypeInterp {
    type InterpType: TypeInterpMethods<Type = Self>;
}

pub trait TypeInterpMethods {
    type Type;

    fn contains(&self, value: &Self::Type) -> bool;
    fn len(&self) -> usize;
}

impl TypeInterp for Int {
    type InterpType = IntInterp;
}

impl TypeInterpMethods for IntInterp {
    type Type = Int;

    fn contains(&self, value: &Self::Type) -> bool {
        self.get_index_of(value).is_some()
    }

    fn len(&self) -> usize {
        self.len()
    }
}

impl TypeInterp for Real {
    type InterpType = RealInterp;
}

impl TypeInterpMethods for RealInterp {
    type Type = Real;

    fn contains(&self, value: &Self::Type) -> bool {
        self.get_index_of(value).is_some()
    }

    fn len(&self) -> usize {
        self.len()
    }
}

impl TypeInterp for TypeEnum {
    type InterpType = StrInterp;
}

impl TypeInterpMethods for StrInterp {
    type Type = TypeEnum;

    fn contains(&self, value: &Self::Type) -> bool {
        value.0 < self.len().try_into().unwrap()
    }

    fn len(&self) -> usize {
        self.len()
    }
}
