use super::{TypeElementIter, TypeEnumIter};
use crate::comp_core::{
    IndexRange, IndexRepr, Int, Real,
    vocabulary::{
        BaseType, DomainEnum, PfuncIndex, SymbolFull, Type, TypeEnum, TypeIndex, Vocabulary,
    },
};
use core::fmt::Display;
use indexmap::IndexSet;
use sli_collections::rc::Rc;
use std::{
    error::Error,
    mem::transmute,
    ops::{ControlFlow, Range, RangeInclusive},
};
use typed_index_collections::TiVec;

#[derive(Debug, PartialEq, Eq, Clone)]
/// Represents the domain of values of a non-infinite type.
pub enum TypeInterp {
    Int(Rc<IntInterp>),
    Real(Rc<RealInterp>),
    Custom(Rc<StrInterp>),
}

impl From<IntInterp> for TypeInterp {
    fn from(value: IntInterp) -> Self {
        Self::Int(value.into())
    }
}

impl From<Rc<IntInterp>> for TypeInterp {
    fn from(value: Rc<IntInterp>) -> Self {
        Self::Int(value)
    }
}

impl From<RealInterp> for TypeInterp {
    fn from(value: RealInterp) -> Self {
        Self::Real(value.into())
    }
}

impl From<Rc<RealInterp>> for TypeInterp {
    fn from(value: Rc<RealInterp>) -> Self {
        Self::Real(value)
    }
}

impl From<StrInterp> for TypeInterp {
    fn from(value: StrInterp) -> Self {
        Self::Custom(value.into())
    }
}

impl From<Rc<StrInterp>> for TypeInterp {
    fn from(value: Rc<StrInterp>) -> Self {
        Self::Custom(value)
    }
}

impl TypeInterp {
    pub fn len(&self) -> usize {
        use self::TypeInterp as T;
        match self {
            T::Int(i) => i.len(),
            T::Real(r) => r.len(),
            T::Custom(c) => c.len(),
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
/// Represents a domain of integer values.
/// Can be both an enumeration of individual integers, or a range.
pub enum IntInterp {
    Range(Range<Int>),
    Arbitrary(IndexSet<Int>),
}

pub type IntRange = Range<Int>;
pub type ArbitraryIntInterp = IndexSet<Int>;

#[derive(Clone, Debug)]
#[non_exhaustive]
pub struct OverflowError;

impl Display for OverflowError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "overflow occured")
    }
}

impl Error for OverflowError {}

impl IntInterp {
    pub fn new() -> Self {
        Self::Arbitrary(IndexSet::default())
    }

    pub fn get_index_of(&self, val: &Int) -> Option<TypeEnum> {
        match self {
            Self::Range(r) => {
                if r.contains(val) {
                    Some(unsafe { transmute(val - r.start) })
                } else {
                    None
                }
            }
            Self::Arbitrary(i) => i.get_index_of(val).map(|f| f.into()),
        }
    }

    pub fn len(&self) -> usize {
        match self {
            Self::Range(r) => (r.end - r.start) as usize,
            Self::Arbitrary(i) => i.len(),
        }
    }

    pub fn get(&self, index: &TypeEnum) -> Int {
        match self {
            Self::Range(r) => {
                let val = unsafe { transmute::<TypeEnum, Int>(*index) } + r.start;
                // TODO make panicking version and non-panicking version
                if !r.contains(&val) {
                    panic!("Index {:?} out of bounds", index);
                }
                val
            }
            Self::Arbitrary(i) => i[usize::from(*index)],
        }
    }

    pub fn get_checked(&self, index: &TypeEnum) -> Option<Int> {
        match self {
            Self::Range(r) => {
                let val = unsafe { transmute::<TypeEnum, Int>(*index) } + r.start;
                if !r.contains(&val) { None } else { Some(val) }
            }
            Self::Arbitrary(i) => i.as_slice().get_index(usize::from(*index)).copied(),
        }
    }

    pub fn contains(&self, value: &Int) -> bool {
        self.get_index_of(value).is_some()
    }

    /// Checks if the minimum and maximum value of a domain can be represented.
    /// When start is equal to Int::MIN and end to Int::MAX we are unable to represent the length
    /// between these two numbers which later code relies on.
    pub fn valid_range(start: Int, end: Int) -> bool {
        (end - start) as IndexRepr <= IndexRepr::MAX
    }

    pub fn try_from_iterator<T>(value: T) -> Result<Self, OverflowError>
    where
        T: IntoIterator<Item = Int>,
    {
        let mut it = value.into_iter();
        let start = it.next();
        if let Some(start) = start {
            let mut expected_next = start + 1;
            let mut is_range = ControlFlow::Continue(());
            while let Some(b) = it.next() {
                if !(start <= b && b <= expected_next) {
                    is_range = ControlFlow::Break(b);
                    break;
                } else if b == expected_next {
                    expected_next += 1;
                    if !Self::valid_range(start, expected_next) {
                        return Err(OverflowError);
                    }
                }
            }
            match is_range {
                ControlFlow::Continue(_) => Ok(Self::Range(start..expected_next)),
                ControlFlow::Break(b) => {
                    let mut set = IndexSet::from_iter(start..expected_next);
                    set.insert(b);
                    set.extend(it);
                    Ok(Self::Arbitrary(set))
                }
            }
        } else {
            Ok(Self::Arbitrary(IndexSet::new()))
        }
    }

    pub fn iter(&self) -> IntInterpIter {
        self.into_iter()
    }
}

impl TryFrom<Range<Int>> for IntInterp {
    type Error = OverflowError;

    fn try_from(value: Range<Int>) -> Result<Self, Self::Error> {
        if IntInterp::valid_range(value.start, value.end) {
            Ok(Self::Range(value))
        } else {
            Err(OverflowError)
        }
    }
}

impl TryFrom<RangeInclusive<Int>> for IntInterp {
    type Error = OverflowError;

    fn try_from(value: RangeInclusive<Int>) -> Result<Self, Self::Error> {
        if IntInterp::valid_range(*value.start(), *value.end() + 1) {
            Ok(Self::Range(*value.start()..*value.end() + 1))
        } else {
            Err(OverflowError)
        }
    }
}

impl<'a> IntoIterator for &'a IntInterp {
    type Item = Int;
    type IntoIter = IntInterpIter<'a>;

    fn into_iter(self) -> Self::IntoIter {
        match self {
            IntInterp::Range(r) => IntInterpIter::Range(r.clone().into_iter()),
            IntInterp::Arbitrary(i) => IntInterpIter::Slice(i.as_slice().into_iter()),
        }
    }
}

#[derive(Clone, Debug)]
pub enum IntInterpIter<'a> {
    Range(std::ops::Range<Int>),
    Slice(indexmap::set::Iter<'a, Int>),
}

impl<'a> Iterator for IntInterpIter<'a> {
    type Item = Int;

    fn next(&mut self) -> Option<Self::Item> {
        match self {
            IntInterpIter::Range(r) => r.next(),
            IntInterpIter::Slice(s) => s.next().copied(),
        }
    }
}

impl Into<Option<TypeInterp>> for IntInterp {
    fn into(self) -> Option<TypeInterp> {
        Some(self.into())
    }
}

#[derive(Debug, PartialEq, Eq, Clone)]
/// Represents a domain of real values.
pub struct RealInterp(IndexSet<Real>);

impl From<IndexSet<Real>> for RealInterp {
    fn from(value: IndexSet<Real>) -> Self {
        Self(value)
    }
}

impl RealInterp {
    pub fn new() -> Self {
        Self(IndexSet::new())
    }

    pub fn get_index_of(&self, val: &Real) -> Option<TypeEnum> {
        self.0.get_index_of(val).map(|f| f.into())
    }

    pub fn len(&self) -> usize {
        self.0.len()
    }

    pub fn get(&self, index: &TypeEnum) -> Real {
        self.0[usize::from(*index)]
    }

    pub fn get_checked(&self, index: &TypeEnum) -> Option<Real> {
        self.0.as_slice().get_index(usize::from(*index)).copied()
    }

    pub fn contains(&self, value: &Real) -> bool {
        self.get_index_of(value).is_some()
    }

    pub fn insert(&mut self, val: Real) -> bool {
        self.0.insert(val)
    }

    pub fn iter(&self) -> <&Self as IntoIterator>::IntoIter {
        self.into_iter()
    }
}

impl<'a> IntoIterator for &'a RealInterp {
    type Item = &'a Real;
    type IntoIter = indexmap::set::Iter<'a, Real>;

    fn into_iter(self) -> Self::IntoIter {
        (&self.0).into_iter()
    }
}

impl FromIterator<Real> for RealInterp {
    fn from_iter<T: IntoIterator<Item = Real>>(iter: T) -> Self {
        Self(IndexSet::from_iter(iter))
    }
}

impl Into<Option<TypeInterp>> for RealInterp {
    fn into(self) -> Option<TypeInterp> {
        Some(self.into())
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
/// Represents a domain of string values.
pub struct StrInterp(usize);

impl StrInterp {
    pub fn new(len: usize) -> Self {
        Self(len)
    }

    pub fn len(&self) -> usize {
        self.0
    }

    pub fn contains(&self, index: &TypeEnum) -> bool {
        IndexRange::new(0..self.0).contains(*index)
    }

    pub fn iter(&self) -> <&Self as IntoIterator>::IntoIter {
        self.into_iter()
    }
}

impl<'a> IntoIterator for &'a StrInterp {
    type Item = TypeEnum;
    type IntoIter = IndexRange<TypeEnum>;

    fn into_iter(self) -> Self::IntoIter {
        IndexRange::new(0..self.0)
    }
}

impl Into<Option<TypeInterp>> for StrInterp {
    fn into(self) -> Option<TypeInterp> {
        Some(self.into())
    }
}

#[derive(Debug, Clone)]
/// Represents an interpreted type.
/// Types can be either built-in (`Bool`, `Int`, `Real`) or user-defined.
/// Note that `Int` and `Real` logically represent infinite ranges, from -inf to +inf.
/// `IntType` and `RealType` present finite subsets of resp. integer and real numbers.
/// `Str` represents an enumeration of strings.
pub enum TypeFull<'a> {
    Bool,
    Int,
    Real,
    IntType((TypeIndex, &'a IntInterp)),
    RealType((TypeIndex, &'a RealInterp)),
    Str((TypeIndex, &'a StrInterp)),
}

impl<'a> TypeFull<'a> {
    pub fn from_type<'b, T: AsRef<TypeInterps>>(type_e: Type, type_interps: &'a T) -> Self {
        match type_e {
            Type::Bool => TypeFull::Bool,
            Type::Int => TypeFull::Int,
            Type::Real => TypeFull::Real,
            Type::IntType(t) => {
                let interp = match &type_interps.as_ref()[t] {
                    TypeInterp::Int(i) => i,
                    _ => unreachable!(),
                };
                TypeFull::IntType((t, interp))
            }
            Type::RealType(t) => {
                let interp = match &type_interps.as_ref()[t] {
                    TypeInterp::Real(i) => i,
                    _ => unreachable!(),
                };
                TypeFull::RealType((t, interp))
            }
            Type::Str(t) => {
                let interp = match &type_interps.as_ref()[t] {
                    TypeInterp::Custom(i) => i,
                    _ => unreachable!(),
                };
                TypeFull::Str((t, interp))
            }
        }
    }
}

pub type RawTypeInterps = TiVec<TypeIndex, TypeInterp>;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct TypeInterps {
    pub(super) vocabulary: Rc<Vocabulary>,
    pub(super) interps: RawTypeInterps,
}

impl AsRef<TypeInterps> for TypeInterps {
    fn as_ref(&self) -> &TypeInterps {
        self
    }
}

impl AsRef<RawTypeInterps> for TypeInterps {
    fn as_ref(&self) -> &RawTypeInterps {
        &self.interps
    }
}

impl std::ops::Deref for TypeInterps {
    type Target = TiVec<TypeIndex, TypeInterp>;

    fn deref(&self) -> &Self::Target {
        &self.interps
    }
}

impl TypeInterps {
    pub fn empty() -> Self {
        let vocabulary = Rc::new(Vocabulary::new());
        TypeInterps {
            vocabulary,
            interps: Default::default(),
        }
    }

    pub fn vocab(&self) -> &Vocabulary {
        &self.vocabulary
    }

    pub fn interps(&self) -> &RawTypeInterps {
        &self.interps
    }

    pub fn mut_interps(&mut self) -> &mut RawTypeInterps {
        &mut self.interps
    }

    pub fn try_from_raw(vocab: Rc<Vocabulary>, raw: RawTypeInterps) -> Result<Self, ()> {
        for (id, interp) in raw.iter_enumerated() {
            match (vocab.types[id].super_type, interp) {
                (BaseType::Int, TypeInterp::Int(_)) => {}
                (BaseType::Real, TypeInterp::Real(_)) => {}
                (BaseType::Str, TypeInterp::Custom(_)) => {}
                _ => return Err(()),
            }
        }
        Ok(Self {
            vocabulary: vocab,
            interps: raw,
        })
    }

    pub fn pfuncs(&self, index: PfuncIndex) -> SymbolFull {
        self.vocabulary.pfuncs(index).with_interps(self)
    }

    pub fn type_element_iter<'a, T, R>(
        &'a self,
        domain: T,
        domain_enum: DomainEnum,
    ) -> TypeElementIter<'a, R>
    where
        T: IntoIterator<Item = &'a Type, IntoIter = R>,
        R: Iterator<Item = &'a Type>,
    {
        TypeElementIter::new(self, domain.into_iter(), domain_enum)
    }

    pub(crate) fn type_enum_iter<'a, T, R>(
        &'a self,
        domain: T,
        domain_enum: DomainEnum,
    ) -> TypeEnumIter<'a, R>
    where
        T: IntoIterator<Item = &'a Type, IntoIter = R>,
        R: Iterator<Item = &'a Type>,
    {
        TypeEnumIter::new(self, domain.into_iter(), domain_enum)
    }
}

#[cfg(test)]
mod tests {
    use super::IntInterp;
    use crate::comp_core::{
        structure::{TypeInterp, UnfinishedStructure},
        vocabulary::{BaseType, TypeDecl, Vocabulary},
    };
    use std::error::Error;

    #[test]
    fn test_int_interp_1() -> Result<(), Box<dyn Error>> {
        let mut vocab = Vocabulary::new();
        let type_id = vocab.add_type_decl(TypeDecl {
            super_type: BaseType::Str,
        });
        let mut unfin_structure = UnfinishedStructure::new();
        let enumeration = [0, 1, 0, 2, 2, 3, 4];
        let expected = 0..5;
        let int_interp = IntInterp::try_from_iterator(enumeration)?;
        if let IntInterp::Range(r) = &int_interp {
            assert_eq!(*r, expected);
        } else {
            unreachable!()
        }
        unfin_structure.add_type_interp(type_id, int_interp);
        let interp = unfin_structure.get_interp(type_id).unwrap();
        if let TypeInterp::Int(interp) = interp {
            if let IntInterp::Range(r) = interp.as_ref() {
                assert_eq!(*r, expected);
            } else {
                unreachable!()
            }
        } else {
            unreachable!();
        }

        Ok(())
    }

    #[test]
    fn test_int_interp_2() -> Result<(), Box<dyn Error>> {
        let mut vocab = Vocabulary::new();
        let type_id = vocab.add_type_decl(TypeDecl {
            super_type: BaseType::Str,
        });
        let mut unfin_structure = UnfinishedStructure::new();
        let enumeration = [0, 3, 2, 3, 5, 7];
        let expected_enum = [0, 3, 2, 5, 7];
        let int_interp = IntInterp::try_from_iterator(enumeration)?;
        let mut expected = expected_enum.iter().copied();
        if let IntInterp::Arbitrary(interp) = &int_interp {
            for i in interp {
                assert_eq!(Some(*i), expected.next());
            }
        } else {
            unreachable!();
        }
        assert_eq!(None, expected.next());

        unfin_structure.add_type_interp(type_id, int_interp);
        let interp = unfin_structure.get_interp(type_id).unwrap();
        if let TypeInterp::Int(interp) = interp {
            if let IntInterp::Arbitrary(interp) = interp.as_ref() {
                let mut expected = expected_enum.iter().copied();
                for i in interp {
                    assert_eq!(Some(*i), expected.next());
                }
            } else {
                unreachable!();
            }
            assert_eq!(None, expected.next());
        } else {
            unreachable!();
        }

        Ok(())
    }
}
