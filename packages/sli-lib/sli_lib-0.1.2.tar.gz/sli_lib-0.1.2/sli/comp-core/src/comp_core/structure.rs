//! Ssssh! Here live the dragons that be structures in SLI.
//! Each structure is abstracted away using the traits in [traits]
//! There exist two flavors of structures:
//! - [PartialStructures](PartialStructure)
//! - [CompleteStructures](CompleteStructure)
//!
//! A [PartialStructure] is a structure where not every symbol of the underlying vocabulary has an
//! interpretation and the interpretations are allowed to be partial.
//! In a [CompleteStructure] each symbol in the underlying vocabulary must have a complete
//! interpretation.
use super::{
    constraints::ParsedConstraints,
    vocabulary::{
        DomainEnum, DomainSlice, Type, TypeElementIndex, TypeEnum, TypeIndex, Vocabulary,
    },
};
use crate::comp_core::{IndexRepr, Int, Real};
use sli_collections::rc::Rc;
use std::iter::Rev;
use std::{error::Error, fmt::Debug, unimplemented};
use typed_index_collections::TiVec;

mod type_interps;
pub use type_interps::*;
mod domain_enum_builder;
pub use domain_enum_builder::*;
mod domain;
#[allow(unused)]
pub use domain::*;
pub mod applied_symb_interp;
pub mod backend;
pub mod complete;
pub mod partial;
pub mod traits;

pub type PartialTypeInterps = TiVec<TypeIndex, Option<TypeInterp>>;

#[derive(Copy, Clone, Debug)]
pub enum TypeElement {
    Bool(bool),
    Int(Int),
    Real(Real),
    Custom(TypeElementIndex),
}

impl TryFrom<TypeElement> for bool {
    type Error = ();

    fn try_from(value: TypeElement) -> Result<Self, Self::Error> {
        if let TypeElement::Bool(value) = value {
            Ok(value)
        } else {
            Err(())
        }
    }
}

impl TryFrom<TypeElement> for Int {
    type Error = ();

    fn try_from(value: TypeElement) -> Result<Int, Self::Error> {
        if let TypeElement::Int(value) = value {
            Ok(value)
        } else {
            Err(())
        }
    }
}

impl TryFrom<TypeElement> for Real {
    type Error = ();

    fn try_from(value: TypeElement) -> Result<Real, Self::Error> {
        if let TypeElement::Real(value) = value {
            Ok(value)
        } else {
            Err(())
        }
    }
}

impl TryFrom<TypeElement> for TypeElementIndex {
    type Error = ();

    fn try_from(value: TypeElement) -> Result<Self, Self::Error> {
        if let TypeElement::Custom(value) = value {
            Ok(value)
        } else {
            Err(())
        }
    }
}

impl TypeElement {
    pub fn unwrap_bool(self) -> bool {
        if let TypeElement::Bool(value) = self {
            value
        } else {
            panic!("unwrap_bool on non TypeElement::Bool");
        }
    }

    pub fn unwrap_int(self) -> Int {
        if let TypeElement::Int(value) = self {
            value
        } else {
            panic!("unwrap_int on non TypeElement::Int");
        }
    }

    pub fn unwrap_real(self) -> Real {
        if let TypeElement::Real(value) = self {
            value
        } else {
            panic!("unwrap_real on non TypeElement::Real");
        }
    }

    pub fn unwrap_type_element_index(self) -> TypeElementIndex {
        if let TypeElement::Custom(value) = self {
            value
        } else {
            panic!("unwrap_type_element_index on non TypeElement::TypeElementIndex");
        }
    }

    pub fn from_type(type_enum: TypeEnum, type_full: &TypeFull) -> Result<Self, ()> {
        match (type_full, type_enum) {
            (TypeFull::Bool, TypeEnum(0)) => Ok(false.into()),
            (TypeFull::Bool, TypeEnum(1)) => Ok(true.into()),
            (TypeFull::Bool, _) => Err(()),
            (TypeFull::IntType((_, interp)), type_enum) => {
                if let Some(value) = interp.get_checked(&type_enum) {
                    Ok(value.into())
                } else {
                    Err(())
                }
            }
            (TypeFull::RealType((_, interp)), type_enum) => {
                if let Some(value) = interp.get_checked(&type_enum) {
                    Ok(value.into())
                } else {
                    Err(())
                }
            }
            (TypeFull::Str((type_id, interp)), type_enum) => {
                if interp.contains(&type_enum) {
                    Ok(TypeElementIndex(*type_id, type_enum).into())
                } else {
                    Err(())
                }
            }
            (TypeFull::Int, _) => Err(()),
            (TypeFull::Real, _) => Err(()),
        }
    }
}

impl PartialEq for TypeElement {
    fn eq(&self, other: &Self) -> bool {
        match (self, other) {
            (Self::Bool(value1), Self::Bool(value2)) => value1 == value2,
            (Self::Int(value1), Self::Int(value2)) => value1 == value2,
            (Self::Real(value1), Self::Real(value2)) => value1 == value2,
            (Self::Custom(value1), Self::Custom(value2)) => value1 == value2,
            (Self::Int(int_val), Self::Real(real_val))
            | (Self::Real(real_val), Self::Int(int_val)) => Real::from(*int_val) == *real_val,
            _ => false,
        }
    }
}

impl Eq for TypeElement {}

impl TypeElement {
    pub fn from_opt_bool(value: Option<bool>) -> Option<TypeElement> {
        value.map(|f| TypeElement::Bool(f))
    }

    pub fn as_bool(self) -> Option<bool> {
        match self {
            TypeElement::Bool(b) => b.into(),
            _ => None,
        }
    }
}

impl From<TypeElement> for Type {
    fn from(value: TypeElement) -> Self {
        match value {
            TypeElement::Bool(_) => Type::Bool,
            TypeElement::Int(_) => Type::Int,
            TypeElement::Real(_) => Type::Real,
            TypeElement::Custom(c) => Type::Str(c.0),
        }
    }
}

impl From<bool> for TypeElement {
    fn from(value: bool) -> Self {
        Self::Bool(value)
    }
}

impl From<Int> for TypeElement {
    fn from(value: Int) -> Self {
        Self::Int(value)
    }
}

impl From<Real> for TypeElement {
    fn from(value: Real) -> Self {
        Self::Real(value)
    }
}

impl From<TypeElementIndex> for TypeElement {
    fn from(value: TypeElementIndex) -> Self {
        Self::Custom(value)
    }
}

pub use complete::CompleteStructure;
pub use partial::PartialStructure;

pub struct Model {
    structure: CompleteStructure,
    /// NOTE: A variant of this field will be used in the future.
    #[allow(unused)]
    theory: Rc<ParsedConstraints>,
}

impl AsRef<CompleteStructure> for Model {
    fn as_ref(&self) -> &CompleteStructure {
        &self.structure
    }
}

/// A comp core glob model.
#[derive(Debug, Clone)]
pub struct GlobModel {
    structure: PartialStructure,
    theory: Rc<ParsedConstraints>,
}

impl AsRef<PartialStructure> for GlobModel {
    fn as_ref(&self) -> &PartialStructure {
        &self.structure
    }
}

impl From<GlobModel> for PartialStructure {
    fn from(value: GlobModel) -> Self {
        value.structure
    }
}

impl GlobModel {
    pub fn iter_models(&self) -> CompleteModelIter {
        CompleteModelIter {
            iter: self.structure.iter_complete(),
            theory: Rc::clone(&self.theory),
        }
    }

    pub fn into_iter_models(self) -> CompleteModelIntoIter {
        CompleteModelIntoIter {
            iter: self.structure.into_iter_complete(),
            theory: self.theory,
        }
    }
}

impl partial::PartialStructure {
    pub(crate) fn into_glob_model(self, theory: Rc<ParsedConstraints>) -> GlobModel {
        GlobModel {
            structure: self,
            theory,
        }
    }
}

pub struct CompleteModelIter<'a> {
    iter: partial::CompleteStructureIter<partial::IterUnknown<'a>>,
    theory: Rc<ParsedConstraints>,
}

impl<'a> CompleteModelIter<'a> {
    pub fn disable_skip_infinite(mut self) -> Self {
        self.iter = self.iter.disable_skip_infinite();
        self
    }

    pub fn enable_skip_infinite(mut self) -> Self {
        self.iter = self.iter.enable_skip_infinite();
        self
    }

    pub fn skip_infinite(self, value: bool) -> Self {
        if value {
            self.enable_skip_infinite()
        } else {
            self.disable_skip_infinite()
        }
    }
}

impl<'a> Iterator for CompleteModelIter<'a> {
    type Item = Model;

    fn next(&mut self) -> Option<Self::Item> {
        self.iter.next().map(|structure| Model {
            structure,
            theory: Rc::clone(&self.theory),
        })
    }
}

pub struct CompleteModelIntoIter {
    iter: partial::CompleteStructureIter<partial::IntoIterUnknown>,
    theory: Rc<ParsedConstraints>,
}

impl CompleteModelIntoIter {
    pub fn disable_skip_infinite(mut self) -> Self {
        self.iter = self.iter.disable_skip_infinite();
        self
    }

    pub fn enable_skip_infinite(mut self) -> Self {
        self.iter = self.iter.enable_skip_infinite();
        self
    }

    pub fn skip_infinite(self, value: bool) -> Self {
        if value {
            self.enable_skip_infinite()
        } else {
            self.disable_skip_infinite()
        }
    }
}

impl Iterator for CompleteModelIntoIter {
    type Item = Model;

    fn next(&mut self) -> Option<Self::Item> {
        self.iter.next().map(|structure| Model {
            structure,
            theory: Rc::clone(&self.theory),
        })
    }
}

/// Trait for checking if a structure is (strictly) more/less precise than another structure.
/// A different way of viewing these methods is using subset/superset of the set of reachable
/// structures. For instance if a structure `A` can be extended to be `B`, `D` or `C`
/// and structure `D` can be extended to be `C`, then this means `D` is more precise than `A`.
/// Since the set of still reachable structures of `D` is a subset of the ones of `A`.
/// A structure is strictly more/less precise if the sets of worlds are a subset/superset but also not
/// equal to each other.
///
/// ## Note
///
/// Substructure/superstructure/precision should not trickle down to individual interpretations.
/// More concretely, a subset/superset/precision operation on individual assignments should not be
/// a thing, this is to avoid wonky situations.
pub trait Precision<Rhs: Precision<Self> + PartialEq<Self> + ?Sized = Self>:
    PartialEq<Rhs>
{
    /// `self` is more precise than `rhs` (`self` >= `rhs`) if the domains are equivalent and
    /// all values in `rhs` exist in `self`.
    /// As such if `self` and `rhs` are equal this function still returns true.
    /// Use [Precision::is_strictly_more_precise] if want to know if something is strictly precise
    /// (`self` > `rhs`)
    fn is_more_precise(&self, rhs: &Rhs) -> bool;

    /// Convenience function for:
    /// ```
    /// # use comp_core::{structure::{PartialStructure, TypeInterps}, Rc};
    /// # let type_interps = Rc::new(TypeInterps::empty());
    /// # let structure1: PartialStructure = PartialStructure::new(type_interps.clone());
    /// # let structure2: PartialStructure = PartialStructure::new(type_interps.clone());
    /// # use comp_core::structure::Precision;
    /// assert_eq!{
    ///     structure1.is_more_precise(&structure2),
    ///     structure2.is_less_precise(&structure1)
    /// };
    /// ```
    fn is_less_precise(&self, rhs: &Rhs) -> bool {
        rhs.is_more_precise(self)
    }

    /// Convenience function for:
    /// ```
    /// # use comp_core::{structure::{PartialStructure, TypeInterps}, Rc};
    /// # let type_interps = Rc::new(TypeInterps::empty());
    /// # let structure1: PartialStructure = PartialStructure::new(type_interps.clone());
    /// # let structure2: PartialStructure = PartialStructure::new(type_interps.clone());
    /// # use comp_core::structure::Precision;
    /// assert_eq!{
    ///     structure1.is_more_precise(&structure2) && !structure1.eq(&structure2),
    ///     structure1.is_strictly_more_precise(&structure2),
    /// };
    /// ```
    fn is_strictly_more_precise(&self, rhs: &Rhs) -> bool {
        self.is_more_precise(rhs) && !self.eq(rhs)
    }

    /// Convenience function for:
    /// ```
    /// # use comp_core::{structure::{PartialStructure, TypeInterps}, Rc};
    /// # let type_interps = Rc::new(TypeInterps::empty());
    /// # let structure1: PartialStructure = PartialStructure::new(type_interps.clone());
    /// # let structure2: PartialStructure = PartialStructure::new(type_interps.clone());
    /// # use comp_core::structure::Precision;
    /// assert_eq!{
    ///     structure1.is_less_precise(&structure2) && !structure1.eq(&structure2),
    ///     structure1.is_strictly_less_precise(&structure2),
    /// };
    /// ```
    fn is_strictly_less_precise(&self, rhs: &Rhs) -> bool {
        self.is_less_precise(rhs) && !self.eq(rhs)
    }
}

#[derive(Clone)]
pub struct TypeElementIter<'a, T>(TypeEnumIter<'a, T>)
where
    T: Iterator<Item = &'a Type>;

impl<'a, T> TypeElementIter<'a, T>
where
    T: Iterator<Item = &'a Type>,
{
    pub fn new(type_interps: &'a TypeInterps, domain: T, domain_enum: DomainEnum) -> Self {
        Self(TypeEnumIter::new(type_interps, domain, domain_enum))
    }
}

impl From<bool> for TypeEnum {
    fn from(value: bool) -> Self {
        match value {
            true => TypeEnum(0),
            false => TypeEnum(1),
        }
    }
}

impl TryFrom<TypeEnum> for bool {
    type Error = ();

    fn try_from(value: TypeEnum) -> Result<Self, Self::Error> {
        match value {
            TypeEnum(0) => Ok(false),
            TypeEnum(1) => Ok(true),
            _ => Err(()),
        }
    }
}

impl<'a, T> Iterator for TypeElementIter<'a, T>
where
    T: Iterator<Item = &'a Type>,
{
    type Item = TypeElement;

    fn next(&mut self) -> Option<Self::Item> {
        let (type_enum, type_full) = self.0.next_type_enum()?;
        match type_full {
            TypeFull::Bool => Some(bool::try_from(type_enum).unwrap().into()),
            TypeFull::Int => {
                unimplemented!();
            }
            TypeFull::Real => {
                unimplemented!();
            }
            TypeFull::Str((type_id, _)) => {
                TypeElement::Custom(TypeElementIndex(type_id, type_enum)).into()
            }
            TypeFull::IntType((_, interp)) => {
                let int = interp.get(&type_enum);
                TypeElement::Int(int).into()
            }
            TypeFull::RealType((_, interp)) => {
                let real = interp.get(&type_enum);
                TypeElement::Real(real).into()
            }
        }
    }

    fn size_hint(&self) -> (usize, Option<usize>) {
        self.0.size_hint()
    }
}

#[derive(Clone)]
pub struct TypeEnumIter<'a, T>
where
    T: Iterator<Item = &'a Type>,
{
    type_interps: &'a TypeInterps,
    domain_enum: DomainEnum,
    cur_domain: T,
    cur_increase: usize,
}

impl<'a, T> TypeEnumIter<'a, T>
where
    T: Iterator<Item = &'a Type>,
{
    pub fn new<I: IntoIterator<IntoIter = T>>(
        type_interps: &'a TypeInterps,
        domain: I,
        domain_enum: DomainEnum,
    ) -> Self {
        Self {
            type_interps,
            domain_enum,
            cur_domain: domain.into_iter(),
            cur_increase: 1,
        }
    }

    fn next_type_enum(&mut self) -> Option<(TypeEnum, TypeFull)> {
        if let Some(t) = self.cur_domain.next() {
            let mut next_type_enum = |interp_len: usize| {
                let func_e: IndexRepr = self.domain_enum.into();
                let ret =
                    TypeEnum((func_e / self.cur_increase as IndexRepr) % interp_len as IndexRepr);
                self.cur_increase *= interp_len;
                ret
            };
            let type_full = t.with_interps(self.type_interps);
            match type_full {
                TypeFull::Bool => (next_type_enum(2), type_full).into(),
                TypeFull::Int => {
                    unimplemented!();
                }
                TypeFull::Real => {
                    unimplemented!();
                }
                TypeFull::Str((_, interp)) => (next_type_enum(interp.len()), type_full).into(),
                TypeFull::IntType((_, interp)) => (next_type_enum(interp.len()), type_full).into(),
                TypeFull::RealType((_, interp)) => (next_type_enum(interp.len()), type_full).into(),
            }
        } else {
            None
        }
    }
}

impl<'a, T> Iterator for TypeEnumIter<'a, T>
where
    T: Iterator<Item = &'a Type>,
{
    type Item = TypeEnum;

    fn next(&mut self) -> Option<Self::Item> {
        self.next_type_enum().map(|f| f.0)
    }

    fn size_hint(&self) -> (usize, Option<usize>) {
        self.cur_domain.size_hint()
    }
}

impl<'a, T> ExactSizeIterator for TypeElementIter<'a, T> where T: Iterator<Item = &'a Type> {}

pub struct LexTypeEnumIterBuilder<'a> {
    type_interps: &'a TypeInterps,
    domain: &'a DomainSlice,
    domain_length: usize,
}

impl<'a> LexTypeEnumIterBuilder<'a> {
    pub fn new(type_interps: &'a TypeInterps, domain: &'a DomainSlice) -> Self {
        Self {
            type_interps,
            domain,
            domain_length: domain.domain_len(type_interps),
        }
    }

    pub fn iter_of(&self, domain_enum: DomainEnum) -> LexTypeEnumIter<'a> {
        LexTypeEnumIter {
            type_interps: self.type_interps,
            domain_enum,
            domain: self.domain.iter().rev(),
            cur_increase: self.domain_length,
        }
    }
}

/// An iterator over TypeEnum in lexographical order compared to [DomainEnum].
/// At the time of writing this order is the reverse order of the order of agruments.
#[derive(Clone)]
pub struct LexTypeEnumIter<'a> {
    type_interps: &'a TypeInterps,
    domain_enum: DomainEnum,
    domain: Rev<core::slice::Iter<'a, Type>>,
    cur_increase: usize,
}

impl<'a> LexTypeEnumIter<'a> {
    pub fn new(
        type_interps: &'a TypeInterps,
        domain: &'a DomainSlice,
        domain_enum: DomainEnum,
    ) -> Self {
        Self {
            type_interps,
            domain_enum,
            domain: domain.iter().rev(),
            cur_increase: domain.domain_len(type_interps),
        }
    }

    fn next_type_enum(&mut self) -> Option<(TypeEnum, TypeFull)> {
        if let Some(t) = self.domain.next() {
            let mut next_type_enum = |interp_len: usize| {
                let func_e: IndexRepr = self.domain_enum.into();
                self.cur_increase /= interp_len;
                let ret =
                    TypeEnum((func_e / self.cur_increase as IndexRepr) % interp_len as IndexRepr);
                ret
            };
            let type_full = t.with_interps(self.type_interps);
            match type_full {
                TypeFull::Bool => {
                    unimplemented!();
                }
                TypeFull::Int => {
                    unimplemented!();
                }
                TypeFull::Real => {
                    unimplemented!();
                }
                TypeFull::Str((_, interp)) => (next_type_enum(interp.len()), type_full).into(),
                TypeFull::IntType((_, interp)) => (next_type_enum(interp.len()), type_full).into(),
                TypeFull::RealType((_, interp)) => (next_type_enum(interp.len()), type_full).into(),
            }
        } else {
            None
        }
    }
}

impl<'a> Iterator for LexTypeEnumIter<'a> {
    type Item = TypeEnum;

    fn next(&mut self) -> Option<Self::Item> {
        self.next_type_enum().map(|f| f.0)
    }

    fn size_hint(&self) -> (usize, Option<usize>) {
        self.domain.size_hint()
    }
}

#[derive(Debug)]
/// An unfinished structure is one in which not all types have been interpreted yet.
/// Not to be confused with a partial structure, in which not all other symbols might not be
/// interpreted yet.
/// An unfinished structure is **never valid** from a logical standpoint.
pub struct UnfinishedStructure {
    // vocabulary: Rc<Vocabulary>,
    type_interps: PartialTypeInterps,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct UnenumeratedType;

impl core::fmt::Display for UnenumeratedType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "some types have are missing an interpretation")
    }
}

impl Error for UnenumeratedType {}

impl UnfinishedStructure {
    pub fn new() -> Self {
        Self {
            type_interps: PartialTypeInterps::new(),
            // vocabulary,
        }
    }

    pub fn add_type_interp<T>(&mut self, type_index: TypeIndex, interp: T)
    where
        T: Into<Option<TypeInterp>>,
    {
        if self.type_interps.len() < type_index.into() {
            for _ in self.type_interps.len()..type_index.into() {
                self.type_interps.push(None);
            }
        } else if self.type_interps.len() == usize::from(type_index) {
            self.type_interps.push(interp.into());
        } else {
            self.type_interps[type_index] = interp.into();
        }
    }

    pub fn finish(self, vocabulary: Rc<Vocabulary>) -> Result<TypeInterps, UnenumeratedType> {
        Ok(TypeInterps {
            vocabulary,
            interps: self
                .type_interps
                .into_iter()
                .map(|f| match f {
                    Some(interp) => Ok(interp),
                    None => Err(UnenumeratedType),
                })
                .collect::<Result<_, _>>()?,
        })
    }

    pub fn get_interp(&self, type_index: TypeIndex) -> Option<&TypeInterp> {
        match self.type_interps.get(type_index) {
            Some(Some(i)) => Some(i),
            _ => None,
        }
    }

    pub fn has_type_interpretation(&self, type_index: TypeIndex) -> bool {
        match self.type_interps.get(type_index) {
            Some(Some(_)) => true,
            None | Some(None) => false,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::{PartialStructure, partial::mutable::SymbolInterp};
    use crate::{
        comp_core::{
            structure::UnfinishedStructure,
            vocabulary::{DomainEnum, Vocabulary},
        },
        utils::tests::{vocab_add_pfunc_decl, vocab_add_types},
    };
    #[test]
    fn structure_eq() {
        let mut new_vocab = Vocabulary::new();
        let mut unfin_struct = UnfinishedStructure::new();
        vocab_add_types!({
            type 0 := { 0, 1, 2 } isa { BaseType::Int }
        }, &mut new_vocab, &mut unfin_struct);
        let id = vocab_add_pfunc_decl!(0: 0 -> Type::Bool , &mut new_vocab);
        let mut part_struct1 =
            PartialStructure::new(unfin_struct.finish(new_vocab.into()).unwrap().into());
        let mut part_struct2 = PartialStructure::new(part_struct1.rc_type_interps().clone());
        assert!(part_struct1 == part_struct2);
        let mut p = match part_struct1.get_mut(id) {
            SymbolInterp::Pred(p) => p,
            _ => unreachable!(),
        };
        p.set_i(DomainEnum(0), Some(true));
        assert!(part_struct1 != part_struct2);
        let mut p = match part_struct1.get_mut(id) {
            SymbolInterp::Pred(p) => p,
            _ => unreachable!(),
        };
        p.set_i(DomainEnum(1), Some(true));
        p.set_i(DomainEnum(2), Some(true));
        let comp_struct1 = part_struct1.try_into_complete().unwrap();
        assert!(comp_struct1 != part_struct2);
        let mut p = match part_struct2.get_mut(id) {
            SymbolInterp::Pred(p) => p,
            _ => unreachable!(),
        };
        p.set_i(DomainEnum(0), Some(true));
        p.set_i(DomainEnum(1), Some(true));
        p.set_i(DomainEnum(2), Some(true));
        assert!(comp_struct1 == part_struct2);
        let mut part_struct1 = comp_struct1.into_partial();

        let mut p = match part_struct1.get_mut(id) {
            SymbolInterp::Pred(p) => p,
            _ => unreachable!(),
        };
        p.set_i(DomainEnum(0), None);
    }

    #[macro_export]
    macro_rules! create_partial_structure_tests {
        () => {
            mod partial_tests{
            use super::*;
            use crate::{
                comp_core::{
                    structure::{
                        PartialStructure,
                        applied_symb_interp::{PfuncError, DomainError, CodomainError},
                        partial::immutable,
                        UnfinishedStructure,
                        TypeElementIndex as T,
                    },
                    vocabulary::Vocabulary,
                },
                utils::tests::vocab_add_pfunc_decl,
            };

            #[duplicate::duplicate_item(
                test_name codomain value1 value2 value3 last extra_types;
                [prop] [Bool] [true] [false] [true] [] [];
                [const_int] [Int] [0] [1] [(-3)] [] [];
                // [const_real] [Int] [0] [1] [(-3)]; // TODO
                [const_custom_str] [Str(0.into())]
                [T(0.into(), 0.into())] [T(0.into(), 1.into())] [T(0.into(), 2.into())]
                [
                    set: (0, None) => (Ok(()), prev: Ok(Some(T(0.into(), 2.into()).into()))),
                    set: (0, Some(4.into())) => (Err(PfuncError::CodomainError(CodomainError))),
                    set: (0, Some(10.into())) => (Err(PfuncError::CodomainError(CodomainError))),
                ]
                [
                    type 0 := {a, b, c} isa { BaseType::Str }
                ];
                [const_custom_int] [IntType(0.into())]
                [0] [1] [2]
                [
                    set: (0, None) => (Ok(()), prev: Ok(Some(2.into()))),
                    set: (0, Some(4.into())) => (Err(PfuncError::CodomainError(CodomainError))),
                    set: (0, Some((-1).into())) => (Err(PfuncError::CodomainError(CodomainError))),
                    fill_unknown: (-1).into() => Err(PfuncError::CodomainError(CodomainError)),
                ]
                [
                    type 0 := {0, 1, 2} isa { BaseType::Int }
                ];
            )]
            crate::test_partial_store!{
                {
                    name: test_name,
                    types: {
                        extra_types
                    },
                    func_decl: {
                        0: -> codomain
                    },
                    {
                        count: 0,
                        get: 0 => Ok(None),
                        set: (0, Some(value1.into())) => (Ok(())),
                        count: 1,
                        set: (0, Some(value2.into())) => (Ok(())),
                        set: (1, None) => (Err(PfuncError::DomainError(DomainError))),
                        set: (0, None) => (Ok(()), prev: Ok(Some(value2.into()))),
                        count: 0,
                        set_if_unknown: (0, value3.into()) => Ok(true),
                        set_if_unknown: (0, value3.into()) => Ok(false),
                        get: 0 => Ok(Some(value3.into())),
                        set: (0, None) => (Ok(()), prev: Ok(Some(value3.into()))),
                        fill_unknown: value3.into() => Ok(()),
                        get: 0 => Ok(Some(value3.into())),
                        last
                    }
                },
            }

            #[duplicate::duplicate_item(
                test_name codomain value1 value2 value3 last extra_types extra_id;
                [pred] [Bool] [true] [false] [true] [] [] [0];
                [func_int] [Int] [0] [1] [(-3)] [] [] [0];
                // [const_real] [Int] [0] [1] [(-3)]; // TODO
                [func_custom_str] [Str(0.into())]
                [T(0.into(), 0.into())] [T(0.into(), 1.into())] [T(0.into(), 2.into())]
                []
                [
                    type 0 := {a, b, c} isa { BaseType::Str }
                ] [0];
                [func_custom_int] [IntType(0.into())]
                [0] [1] [2]
                [
                    set: (0, None) => (Ok(()), prev: Ok(Some(2.into()))),
                    set: (0, Some(4.into())) => (Err(PfuncError::CodomainError(CodomainError))),
                    set: (0, Some((-1).into())) => (Err(PfuncError::CodomainError(CodomainError))),
                    fill_unknown: (-1).into() => Err(PfuncError::CodomainError(CodomainError)),
                ]
                [
                    type 0 := {0, 1, 2} isa { BaseType::Int }
                ] [ 1 ];
            )]
            crate::test_partial_store!{
                {
                    name: test_name,
                    types: {
                        extra_types
                        type extra_id := {x, y, z} isa {BaseType::Str}
                    },
                    func_decl: {
                        0: extra_id -> codomain
                    },
                    {
                        count: 0,
                        set: (0, Some(value1.into())) => (Ok(()), prev: Ok(None)),
                        count: 1,
                        set: (0, Some(value2.into())) => (Ok(()), prev: Ok(Some(value1.into()))),
                        set: (1, Some(value1.into())) => (Ok(()), prev: Ok(None)),
                        set: (3, None) => (Err(PfuncError::DomainError(DomainError))),
                        count: 2,
                        set: (0, None) => (Ok(()), prev: Ok(Some(value2.into()))),
                        count: 1,
                        set_if_unknown: (0, value3.into()) => Ok(true),
                        set_if_unknown: (0, value3.into()) => Ok(false),
                        get: 0 => Ok(Some(value3.into())),
                        set: (0, None) => (Ok(()), prev: Ok(Some(value3.into()))),
                        fill_unknown: value3.into() => Ok(()),
                        get: 0 => Ok(Some(value3.into())),
                        get: 1 => Ok(Some(value1.into())),
                        get: 2 => Ok(Some(value3.into())),
                        last
                    }
                },
            }
        }
        }
    }

    #[macro_export]
    macro_rules! create_complete_structure_tests {
        () => {
            mod complete_tests{
            use super::*;
            use crate::{
                comp_core::{
                    structure::{
                        PartialStructure,
                        applied_symb_interp::{PfuncError, DomainError, CodomainError},
                        complete::immutable,
                        UnfinishedStructure,
                        TypeElementIndex as T,
                        TypeElement as TE,
                    },
                    vocabulary::Vocabulary,
                },
                utils::tests::vocab_add_pfunc_decl,
            };

            #[duplicate::duplicate_item(
                test_name codomain value1 value2 value3 last extra_types;
                [prop] [Bool] [true] [false] [true] [] [];
                [const_int] [Int] [0] [1] [(-3)] [] [];
                // [const_real] [Int] [0] [1] [(-3)]; // TODO
                [const_custom_str] [Str(0.into())]
                [T(0.into(), 0.into())] [T(0.into(), 1.into())] [T(0.into(), 2.into())]
                [
                    set: (0, T(0.into(), 0.into()).into()) => (Ok(())),
                    set: (0, T(0.into(), 4.into()).into()) => (Err(PfuncError::CodomainError(CodomainError))),
                    set: (0, T(10.into(), 0.into()).into()) => (Err(PfuncError::CodomainError(CodomainError))),
                ]
                [
                    type 0 := {a, b, c} isa { BaseType::Str }
                ];
                [const_custom_int] [IntType(0.into())]
                [0] [1] [2]
                [
                    set: (0, 0.into()) => (Ok(())),
                    set: (0, 4.into()) => (Err(PfuncError::CodomainError(CodomainError))),
                    set: (0, (-1).into()) => (Err(PfuncError::CodomainError(CodomainError))),
                ]
                [
                    type 0 := {0, 1, 2} isa { BaseType::Int }
                ];
            )]
            crate::test_complete_store!{
                {
                    name: test_name,
                    types: {
                        extra_types
                    },
                    func_decl: {
                        0: -> codomain
                    },
                    {
                        set: (0, value1.into()) => (Ok(())),
                        set: (0, value2.into()) => (Ok(())),
                        set: (1, value1.into()) => (Err(PfuncError::DomainError(DomainError))),
                        set: (0, value3.into()) => (Ok(())),
                        get: 0 => Ok(value3.into()),
                        last
                    }
                },
            }

            #[duplicate::duplicate_item(
                test_name codomain value1 value2 value3 last extra_types next_id;
                [pred] [Bool] [true] [false] [true] [] [] [0];
                [func_int] [Int] [0] [1] [(-3)] [] [] [0];
                // [const_real] [Int] [0] [1] [(-3)]; // TODO
                [func_custom_str] [Str(0.into())]
                [T(0.into(), 0.into())] [T(0.into(), 1.into())] [T(0.into(), 2.into())]
                []
                [
                    type 0 := {a, b, c} isa { BaseType::Str }
                ] [1];
                [func_custom_int] [IntType(0.into())]
                [0] [1] [2]
                [
                    set: (0, 0.into()) => (Ok(())),
                    set: (0, 4.into()) => (Err(PfuncError::CodomainError(CodomainError))),
                    set: (0, (-1).into()) => (Err(PfuncError::CodomainError(CodomainError))),
                ]
                [
                    type 0 := {0, 1, 2} isa { BaseType::Int }
                ] [1];
            )]
            crate::test_complete_store!{
                {
                    name: test_name,
                    types: {
                        extra_types
                        type next_id := {x, y, z} isa {BaseType::Str}
                    },
                    func_decl: {
                        0: next_id -> codomain
                    },
                    {
                        set: (0, value1.into()) => (Ok(())),
                        set: (0, value2.into()) => (Ok(())),
                        set: (1, value1.into()) => (Ok(())),
                        set: (3, value1.into()) => (Err(PfuncError::DomainError(DomainError))),
                        set: (0, value3.into()) => (Ok(())),
                        get: 0 => Ok(value3.into()),
                        last
                    }
                },
            }
            }
        }
    }

    #[macro_export]
    macro_rules! test_complete_store {
        (
            $({
                name: $name:ident,
                $(types: {
                    $($types:tt)*
                },)?
                func_decl: {
                    $($decl:tt)*
                },
                {
                    $($tokens:tt)*
                }$(,)?
            }),* $(,)?
        ) => {
            $(
                #[allow(unused, non_snake_case)]
                #[test]
                fn $name() -> Result<(), Box<dyn std::error::Error>> {
                    use crate::utils::tests::vocab_add_types;
                    use crate::comp_core::vocabulary::Type;
                    use crate::comp_core::structure::TypeElement;
                    use Type::Bool as Bool;
                    use Type::Int as Int;
                    use Type::Real as Real;
                    use Type::IntType as IntType;
                    use Type::RealType as RealType;
                    use Type::Str as Str;
                    let mut vocab = Vocabulary::new();
                    let mut unfin_struct = UnfinishedStructure::new();
                    $(vocab_add_types!({$($types)*}, &mut vocab, &mut unfin_struct);)?
                    let prop = vocab_add_pfunc_decl!{
                        $($decl)*, &mut vocab
                    };
                    let mut structure =
                        PartialStructure::new(unfin_struct.finish(vocab.into())?.into());
                    structure.for_each_mut(|mut symb| {
                        match symb.codomain() {
                            Type::Bool => {
                                symb.fill_unknown_with(TypeElement::Bool(Default::default()));
                            }
                            Type::Int | Type::IntType(_) => {
                                symb.fill_unknown_with(TypeElement::Int(Default::default()));
                            }
                            Type::Real | Type::RealType(_) => {
                                symb.fill_unknown_with(TypeElement::Real(Default::default()));
                            }
                            Type::Str(_) => {
                                symb.fill_unknown_with(T(0.into(), Default::default()).into());
                            }
                        }
                    });
                    let mut structure = structure.try_into_complete().unwrap();
                    let struct_ptr: *const _ = &structure;
                    let im_symb = || -> immutable::SymbolInterp {
                        unsafe { &*struct_ptr }.get(prop)
                    };
                    let mut symbol_interp = structure.get_mut(prop);
                    crate::test_complete_store !{
                        do: im_symb, symbol_interp, $($tokens)*
                    };
                    Ok(())
                }
            )*
        };
        (
            do: $im_symb:ident, $symb_interp:ident,
            set: ($arg:expr, $set_expr:expr) => ($set_ret:expr),
            $($tokens:tt)*
        ) => {
            let set_expr: TE = $set_expr;
            let prev = $symb_interp.get($arg.into());
            let im_prev = $im_symb().get($arg.into());
            let ret = $symb_interp.set($arg.into(), set_expr);
            println!(concat!("set: (",
                             stringify!($arg), ", ",
                             stringify!($set_expr), ")",
                             " => ", stringify!($set_ret)));
            assert_eq!(ret, $set_ret);
            crate::test_complete_store !(do: $im_symb, $symb_interp, $($tokens)*);
        };
        (
            do: $im_symb:ident, $symb_interp:ident,
            get: $arg:expr => $get_ret:expr, $($tokens:tt)*
        ) => {
            println!(concat!("get: ",
                             stringify!($arg),
                             " => ", stringify!($get_ret)));
            assert_eq!($symb_interp.get($arg.into()), $get_ret);
            assert_eq!($im_symb().get($arg.into()), $get_ret);
            crate::test_complete_store!(do: $im_symb, $symb_interp, $($tokens)*);
        };
        (
            do: $im_symb:ident, $symb_interp:ident,
        ) => {};
    }

    #[macro_export]
    macro_rules! test_partial_store {
        (
            $({
                name: $name:ident,
                $(types: {
                    $($types:tt)*
                },)?
                func_decl: {
                    $($decl:tt)*
                },
                {
                    $($tokens:tt)*
                }$(,)?
            }),* $(,)?
        ) => {
            $(
                #[allow(unused, non_snake_case)]
                #[test]
                fn $name() -> Result<(), Box<dyn std::error::Error>> {
                    use crate::utils::tests::vocab_add_types;
                    use crate::comp_core::vocabulary::Type;
                    use Type::Bool as Bool;
                    use Type::Int as Int;
                    use Type::Real as Real;
                    use Type::IntType as IntType;
                    use Type::RealType as RealType;
                    use Type::Str as Str;
                    let mut vocab = Vocabulary::new();
                    let mut unfin_struct = UnfinishedStructure::new();
                    $(vocab_add_types!({$($types)*}, &mut vocab, &mut unfin_struct);)?
                    let prop = vocab_add_pfunc_decl!{
                        $($decl)*, &mut vocab
                    };
                    let mut structure =
                        PartialStructure::new(unfin_struct.finish(vocab.into())?.into());
                    let struct_ptr: *const _ = &structure;
                    let im_symb = || -> immutable::SymbolInterp {
                        unsafe { &*struct_ptr }.get(prop)
                    };
                    let mut symbol_interp = structure.get_mut(prop);
                    crate::test_partial_store !{
                        im_symb, symbol_interp, $($tokens)*
                    };
                    Ok(())
                }
            )*
        };
        (
            $im_symb:ident, $symb_interp:ident,
            set: ($arg:expr, $set_expr:expr) => ($set_ret:expr$(, prev: $prev_ret:expr)?),
            $($tokens:tt)*
        ) => {
            let set_expr: Option<_> = $set_expr;
            let prev = $symb_interp.get($arg.into());
            let im_prev = $im_symb().get($arg.into());
            let ret = $symb_interp.set($arg.into(), set_expr);
            println!(concat!("set: (",
                             stringify!($arg), ", ",
                             stringify!($set_expr), ")",
                             " => ", stringify!($set_ret)));
            assert_eq!(ret, $set_ret);
            if ret.is_ok() {
                $(assert_eq!(im_prev, $prev_ret);)?
            }
            crate::test_partial_store !($im_symb, $symb_interp, $($tokens)*);
        };
        (
            $im_symb:ident, $symb_interp:ident,
            set_if_unknown: ($arg:expr, $set_expr:expr) => $set_ret:expr, $($tokens:tt)*
        ) => {
            println!(concat!("set_if_unknown: ",
                             stringify!($arg), " ",
                             stringify!($set_expr),
                             " => ", stringify!($set_ret)));
            assert_eq!($symb_interp.set_if_unknown($arg.into(), $set_expr), $set_ret);
            let im = $im_symb().get($arg.into());
            if let Ok(im) = im {
                assert!(im.is_some());
            }
            let mut_val = $symb_interp.get($arg.into());
            if let Ok(mut_val) = mut_val {
                assert!(mut_val.is_some());
            }
            crate::test_partial_store!($im_symb, $symb_interp, $($tokens)*);
        };
        (
            $im_symb:ident, $symb_interp:ident,
            get: $arg:expr => $get_ret:expr, $($tokens:tt)*
        ) => {
            println!(concat!("get: ",
                             stringify!($arg),
                             " => ", stringify!($get_ret)));
            assert_eq!($symb_interp.get($arg.into()), $get_ret);
            assert_eq!($im_symb().get($arg.into()), $get_ret);
            crate::test_partial_store!($im_symb, $symb_interp, $($tokens)*);
        };
        (
            $im_symb:ident, $symb_interp:ident,
            fill_unknown: $value:expr => $ret:expr, $($tokens:tt)*
        ) => {
            let set_expr = $value;
            println!(concat!("fill_unknown: ",
                             stringify!($value),
                             " => ", stringify!($ret)));
            assert_eq!($symb_interp.fill_unknown_with(set_expr), $ret);
            crate::test_partial_store!($im_symb, $symb_interp, $($tokens)*);
        };
        (
            $im_symb:ident, $symb_interp:ident,
        ) => {};
        (
            $im_symb:ident, $symb_interp:ident,
            count: $count_ret:expr, $($tokens:tt)*
        ) => {
            println!(concat!("count: ",
                             stringify!($arg),
                             " => ", stringify!($get_expr)));
            assert_eq!($symb_interp.amount_known(), $count_ret);
            assert_eq!($im_symb().amount_known(), $count_ret);
            crate::test_partial_store!($im_symb, $symb_interp, $($tokens)*);
        };
        (
            $im_symb:ident, $symb_interp:ident,
        ) => {};
    }

    create_complete_structure_tests!();
    create_partial_structure_tests!();
}
