use super::{
    DomainEnumReorder, roaring,
    satisfying_set::{self, OrScalar, SatSetAlias},
};
use crate::{
    Int, Real,
    structure::backend::{FuncElementUnion, NegatedIter},
    vocabulary::{DomainEnum, TypeEnum},
};
use duplicate::duplicate_item;
use paste::paste;
use std::{
    cmp::Ordering,
    collections::{BTreeMap, btree_map},
    iter::Peekable,
};

#[derive(Debug, Clone)]
pub struct Alias;

impl SatSetAlias for Alias {
    type Set = roaring::RoaringSet;
    type IntFunc = SatSetFunc<Int>;
    type RealFunc = SatSetFunc<Real>;
    type TypeEnumFunc = SatSetFunc<TypeEnum>;
}

pub type BTreeFunc<I> = BTreeMap<DomainEnum, I>;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct SatSetFunc<I> {
    map: BTreeFunc<I>,
    domain_size: usize,
}

impl<I: Default + Clone + Copy> SatSetFunc<I> {
    pub fn new(domain_size: usize) -> Self {
        Self {
            map: Default::default(),
            domain_size,
        }
    }

    pub fn get(&self, index: DomainEnum) -> Option<I> {
        self.map.get(&index).copied()
    }

    pub fn set(&mut self, index: DomainEnum, value: Option<I>) {
        if let Some(value) = value {
            self.map.insert(index, value);
        } else {
            self.map.remove(&index);
        }
    }

    pub fn iter(&self) -> btree_map::Iter<DomainEnum, I> {
        self.map.iter()
    }

    pub fn iter_mut(&mut self) -> btree_map::IterMut<DomainEnum, I> {
        self.map.iter_mut()
    }

    fn ite(mut then_term: Self, mut else_term: Self, set: &roaring::RoaringSet) -> Self {
        let card = satisfying_set::PureSetOps::cardinality(set);
        if card < satisfying_set::PureSetOps::domain_len(set) {
            satisfying_set::PureSetOps::iter(set)
                .for_each(|index| else_term.set(index, then_term.map.get(&index).copied()));
            else_term
        } else {
            NegatedIter::new(
                satisfying_set::PureSetOps::iter(set),
                satisfying_set::PureSetOps::domain_len(set),
            )
            .for_each(|index| then_term.set(index, else_term.map.get(&index).copied()));
            then_term
        }
    }

    fn ite_scalar_then(then_term: I, mut else_term: Self, set: &roaring::RoaringSet) -> Self {
        satisfying_set::PureSetOps::iter(set)
            .for_each(|index| else_term.set(index, Some(then_term)));
        else_term
    }

    fn ite_scalar_else(mut then_term: Self, else_term: I, set: &roaring::RoaringSet) -> Self {
        NegatedIter::new(
            satisfying_set::PureSetOps::iter(set),
            satisfying_set::PureSetOps::domain_len(set),
        )
        .for_each(|index| then_term.set(index, Some(else_term)));
        then_term
    }

    fn ite_scalar_then_else(then_term: I, else_term: I, set: &roaring::RoaringSet) -> Self {
        let mut new = Self::new(satisfying_set::PureSetOps::domain_len(set));
        satisfying_set::PureSetOps::iter(set).for_each(|index| new.set(index, Some(then_term)));
        NegatedIter::new(
            satisfying_set::PureSetOps::iter(set),
            satisfying_set::PureSetOps::domain_len(set),
        )
        .for_each(|index| new.set(index, Some(else_term)));
        new
    }

    fn cmp_ops<'a, F: Fn(&I, &I) -> bool>(&'a self, other: &'a Self, op: F) -> CmpIter<'a, I, F> {
        CmpIter {
            left: self.iter().peekable(),
            right: other.iter().peekable(),
            op,
        }
    }

    fn operate_on<F: FnMut(&mut I, &I)>(&mut self, other: &Self, mut op: F) {
        let mut iter_other = other.map.iter();
        let mut ovalue = iter_other.next();
        self.map.retain(|key, svalue| {
            if ovalue.is_none() {
                return false;
            }
            loop {
                match ovalue {
                    Some(oval) => match key.cmp(oval.0) {
                        Ordering::Equal => {
                            op(svalue, oval.1);
                            ovalue = iter_other.next();
                            break true;
                        }
                        Ordering::Less => {
                            break false;
                        }
                        Ordering::Greater => {
                            ovalue = iter_other.next();
                        }
                    },
                    _ => break false,
                }
            }
        })
    }

    fn align(
        &mut self,
        aligned_layout: &satisfying_set::AlignedLayout,
        context: &super::InterpContext,
    ) {
        let mut new_self = Self::new(aligned_layout.new_layout().domain_len(context));
        let mut reorder = DomainEnumReorder::new_with_context(
            aligned_layout.old_layout(),
            aligned_layout.new_layout(),
            context,
        );
        for (&index, &value) in self.iter() {
            for new_id in reorder.index(index) {
                new_self.set(new_id, Some(value))
            }
        }
        *self = new_self;
    }
}

impl Into<BTreeMap<DomainEnum, FuncElementUnion>> for SatSetFunc<Int> {
    fn into(self) -> BTreeMap<DomainEnum, FuncElementUnion> {
        // Safety: Int and FuncElementUnion have the same size, alignment and all bit patterns are
        // allowed between both.
        unsafe {
            core::mem::transmute::<BTreeMap<DomainEnum, Int>, BTreeMap<DomainEnum, FuncElementUnion>>(
                self.map,
            )
        }
    }
}

impl Into<BTreeMap<DomainEnum, Real>> for SatSetFunc<Real> {
    fn into(self) -> BTreeMap<DomainEnum, Real> {
        self.map
    }
}

impl Into<BTreeMap<DomainEnum, FuncElementUnion>> for SatSetFunc<TypeEnum> {
    fn into(self) -> BTreeMap<DomainEnum, FuncElementUnion> {
        // Safety: Real and FuncElementUnion have the same size, alignment and all bit patterns are
        // allowed between both.
        unsafe {
            core::mem::transmute::<
                BTreeMap<DomainEnum, TypeEnum>,
                BTreeMap<DomainEnum, FuncElementUnion>,
            >(self.map)
        }
    }
}

pub struct CmpIter<'a, I, F: Fn(&I, &I) -> bool> {
    left: Peekable<btree_map::Iter<'a, DomainEnum, I>>,
    right: Peekable<btree_map::Iter<'a, DomainEnum, I>>,
    op: F,
}

impl<'a, I, F: Fn(&I, &I) -> bool> Iterator for CmpIter<'a, I, F> {
    type Item = DomainEnum;

    fn next(&mut self) -> Option<Self::Item> {
        loop {
            let left = self.left.peek();
            let right = self.right.peek();
            match (left, right) {
                (Some(left), Some(right)) => match left.0.cmp(right.0) {
                    Ordering::Equal => {
                        let ret = if (self.op)(left.1, right.1) {
                            Some(*left.0)
                        } else {
                            None
                        };
                        self.left.next();
                        self.right.next();
                        if let Some(value) = ret {
                            return Some(value);
                        }
                    }
                    Ordering::Less => {
                        self.left.next();
                    }
                    Ordering::Greater => {
                        self.right.next();
                    }
                },
                _ => return None,
            }
        }
    }
}

impl satisfying_set::Set<SatSetFunc<Int>, SatSetFunc<Real>, SatSetFunc<TypeEnum>>
    for roaring::RoaringSet
{
    fn card_agg(
        self,
        old_layout: &super::LayoutVec,
        new_layout: &super::LayoutVec,
        context: &super::InterpContext,
    ) -> satisfying_set::OrScalar<SatSetFunc<Int>, Int> {
        let a: SatSetFunc<Int> =
            roaring::RoaringSet::cardinality_agg(self, context, old_layout, new_layout);
        if new_layout.len() == 0 {
            a.get(0.into())
                .map(OrScalar::Scalar)
                .unwrap_or(OrScalar::Value(a))
        } else {
            OrScalar::Value(a)
        }
    }

    fn int_ite(&self, then_term: SatSetFunc<Int>, else_term: SatSetFunc<Int>) -> SatSetFunc<Int> {
        SatSetFunc::<Int>::ite(then_term, else_term, self)
    }

    fn int_ite_scalar_then(&self, then_term: Int, else_term: SatSetFunc<Int>) -> SatSetFunc<Int> {
        SatSetFunc::<Int>::ite_scalar_then(then_term, else_term, self)
    }

    fn int_ite_scalar_else(&self, then_term: SatSetFunc<Int>, else_term: Int) -> SatSetFunc<Int> {
        SatSetFunc::<Int>::ite_scalar_else(then_term, else_term, self)
    }

    fn int_ite_scalar_then_else(&self, then_term: Int, else_term: Int) -> SatSetFunc<Int> {
        SatSetFunc::<Int>::ite_scalar_then_else(then_term, else_term, self)
    }

    fn real_ite(
        &self,
        then_term: SatSetFunc<Real>,
        else_term: SatSetFunc<Real>,
    ) -> SatSetFunc<Real> {
        SatSetFunc::<Real>::ite(then_term, else_term, self)
    }

    fn real_ite_scalar_then(
        &self,
        then_term: Real,
        else_term: SatSetFunc<Real>,
    ) -> SatSetFunc<Real> {
        SatSetFunc::<Real>::ite_scalar_then(then_term, else_term, self)
    }

    fn real_ite_scalar_else(
        &self,
        then_term: SatSetFunc<Real>,
        else_term: Real,
    ) -> SatSetFunc<Real> {
        SatSetFunc::<Real>::ite_scalar_else(then_term, else_term, self)
    }

    fn real_ite_scalar_then_else(&self, then_term: Real, else_term: Real) -> SatSetFunc<Real> {
        SatSetFunc::<Real>::ite_scalar_then_else(then_term, else_term, self)
    }

    fn type_enum_ite(
        &self,
        then_term: SatSetFunc<TypeEnum>,
        else_term: SatSetFunc<TypeEnum>,
    ) -> SatSetFunc<TypeEnum> {
        SatSetFunc::<TypeEnum>::ite(then_term, else_term, self)
    }

    fn type_enum_ite_scalar_then(
        &self,
        then_term: TypeEnum,
        else_term: SatSetFunc<TypeEnum>,
    ) -> SatSetFunc<TypeEnum> {
        SatSetFunc::<TypeEnum>::ite_scalar_then(then_term, else_term, self)
    }

    fn type_enum_ite_scalar_else(
        &self,
        then_term: SatSetFunc<TypeEnum>,
        else_term: TypeEnum,
    ) -> SatSetFunc<TypeEnum> {
        SatSetFunc::<TypeEnum>::ite_scalar_else(then_term, else_term, self)
    }

    fn type_enum_ite_scalar_then_else(
        &self,
        then_term: TypeEnum,
        else_term: TypeEnum,
    ) -> SatSetFunc<TypeEnum> {
        SatSetFunc::<TypeEnum>::ite_scalar_then_else(then_term, else_term, self)
    }
}

impl<I: Default + Copy> satisfying_set::Alignable for SatSetFunc<I> {
    fn align(
        &mut self,
        aligned_layout: &satisfying_set::AlignedLayout,
        context: &super::InterpContext,
    ) {
        Self::align(self, aligned_layout, context)
    }
}

impl satisfying_set::PureIntFuncOps for SatSetFunc<Int> {
    fn new(domain_size: usize) -> Self {
        Self {
            map: Default::default(),
            domain_size,
        }
    }

    fn domain_len(&self) -> usize {
        self.domain_size
    }
    #[duplicate_item(
        name method;
        [add] [AddAssign::add_assign];
        [sub] [SubAssign::sub_assign];
        [mult] [MulAssign::mul_assign];
        [rem] [RemAssign::rem_assign];
    )]
    paste! {
        fn name(&mut self, other: &Self) {
            self.operate_on(other, |l, r| core::ops::method(l, r))
        }

        fn [<name _scalar>](&mut self, other: Int) {
            self.iter_mut().for_each(|(_, l)| core::ops::method(l, &other))
        }
    }

    fn neg(&mut self) {
        self.iter_mut()
            .for_each(|(_, value)| *value = -(value.clone()));
    }

    fn rem_scalar_2(scalar: Int, this: &mut Self) {
        this.iter_mut()
            .for_each(|(_, r)| *r = core::ops::Rem::rem(scalar, *r))
    }

    fn get(&self, index: DomainEnum) -> Option<Int> {
        Self::get(self, index)
    }

    fn set(&mut self, index: DomainEnum, value: Int) {
        Self::set(self, index, Some(value))
    }

    fn iter<'a>(&'a self) -> impl Iterator<Item = (DomainEnum, Int)> + 'a {
        self.map.iter().map(|f| (*f.0, *f.1))
    }

    fn sum_agg(
        &self,
        old_layout: &super::LayoutVec,
        new_layout: &super::LayoutVec,
        context: &super::InterpContext,
    ) -> satisfying_set::OrScalar<Self, Int> {
        let mut new_self = Self::new(new_layout.domain_len(context));
        let mut reorder = DomainEnumReorder::new_with_context(old_layout, new_layout, context);
        for (&index, &value) in self.iter() {
            let corresponding = reorder.single(index);
            new_self
                .map
                .entry(corresponding)
                .and_modify(|f| *f += value)
                .or_insert(value);
        }
        if new_self.domain_size == 0 {
            OrScalar::Scalar(*new_self.map.first_key_value().unwrap().1)
        } else {
            OrScalar::Value(new_self)
        }
    }
}

impl satisfying_set::IntFunc<roaring::RoaringSet, SatSetFunc<Real>, SatSetFunc<TypeEnum>>
    for SatSetFunc<Int>
{
    #[duplicate_item(
        name;
        [lt];
        [le];
        [gt];
        [ge];
    )]
    paste! {
        fn name(&self, other: &Self) -> roaring::RoaringSet {
            roaring::RoaringSet::from_raw(
                self.cmp_ops(other, |l, r| Ord::cmp(l, r).[<is_ name>]()).collect(),
                self.domain_size
            )
        }

        fn [<name _scalar>](&self, s: Int) -> roaring::RoaringSet {
            roaring::RoaringSet::from_raw(
                self.iter().filter_map(|f| if Ord::cmp(f.1, &s).[<is_ name>]() { Some(*f.0) } else { None }).collect(),
                self.domain_size
            )
        }
    }

    fn eq(&self, other: &Self) -> roaring::RoaringSet {
        roaring::RoaringSet::from_raw(
            self.cmp_ops(other, |l, r| PartialEq::eq(l, r)).collect(),
            self.domain_size,
        )
    }

    fn eq_scalar(&self, s: Int) -> roaring::RoaringSet {
        roaring::RoaringSet::from_raw(
            self.iter()
                .filter_map(|f| {
                    if PartialEq::eq(f.1, &s) {
                        Some(*f.0)
                    } else {
                        None
                    }
                })
                .collect(),
            self.domain_size,
        )
    }

    fn neq(&self, other: &Self) -> roaring::RoaringSet {
        roaring::RoaringSet::from_raw(
            self.cmp_ops(other, |l, r| PartialEq::ne(l, r)).collect(),
            self.domain_size,
        )
    }

    fn neq_scalar(&self, s: Int) -> roaring::RoaringSet {
        roaring::RoaringSet::from_raw(
            self.iter()
                .filter_map(|f| {
                    if PartialEq::ne(f.1, &s) {
                        Some(*f.0)
                    } else {
                        None
                    }
                })
                .collect(),
            self.domain_size,
        )
    }
}

impl From<SatSetFunc<Int>> for SatSetFunc<Real> {
    fn from(value: SatSetFunc<Int>) -> Self {
        Self {
            map: value
                .map
                .into_iter()
                .map(|(key, value)| (key, value.into()))
                .collect(),
            domain_size: value.domain_size,
        }
    }
}

impl satisfying_set::PureRealOps for SatSetFunc<Real> {
    fn new(domain_size: usize) -> Self {
        Self {
            map: Default::default(),
            domain_size,
        }
    }

    fn domain_len(&self) -> usize {
        self.domain_size
    }

    #[duplicate_item(
        name method;
        [add] [AddAssign::add_assign];
        [sub] [SubAssign::sub_assign];
        [mult] [MulAssign::mul_assign];
    )]
    paste! {
        fn name(&mut self, other: &Self) {
            self.operate_on(other, |l, r| core::ops::method(l, r))
        }

        fn [<name _scalar>](&mut self, other: Real) {
            self.iter_mut().for_each(|(_, l)| core::ops::method(l, &other))
        }
    }

    fn neg(&mut self) {
        self.iter_mut()
            .for_each(|(_, value)| value.negate_inplace());
    }

    fn div(&mut self, other: &Self) {
        self.operate_on(other, |l, r| *l = l.div_cc(r))
    }

    fn div_scalar(&mut self, other: Real) {
        self.iter_mut().for_each(|(_, l)| *l = l.div_cc(&other))
    }

    fn div_scalar_2(other: Real, this: &mut Self) {
        this.iter_mut().for_each(|(_, l)| *l = other.div_cc(l))
    }

    fn rem(&mut self, other: &Self) {
        self.operate_on(other, |l, r| *l = l.rem_cc(r))
    }

    fn rem_scalar(&mut self, scalar: Real) {
        self.iter_mut().for_each(|(_, r)| *r = r.rem_cc(&scalar))
    }

    fn rem_scalar_2(scalar: Real, this: &mut Self) {
        this.iter_mut().for_each(|(_, r)| *r = scalar.rem_cc(r))
    }

    fn get(&self, index: DomainEnum) -> Option<Real> {
        Self::get(self, index)
    }

    fn set(&mut self, index: DomainEnum, value: Real) {
        Self::set(self, index, Some(value))
    }

    fn iter<'a>(&'a self) -> impl Iterator<Item = (DomainEnum, Real)> + 'a {
        self.map.iter().map(|f| (*f.0, *f.1))
    }

    fn sum_agg(
        &self,
        old_layout: &super::LayoutVec,
        new_layout: &super::LayoutVec,
        context: &super::InterpContext,
    ) -> satisfying_set::OrScalar<Self, Real> {
        let mut new_self = Self::new(new_layout.domain_len(context));
        let mut reorder = DomainEnumReorder::new_with_context(old_layout, new_layout, context);
        for (&index, &value) in self.iter() {
            let corresponding = reorder.single(index);
            new_self
                .map
                .entry(corresponding)
                .and_modify(|f| *f += value)
                .or_insert(value);
        }
        if new_self.domain_size == 0 {
            OrScalar::Scalar(*new_self.map.first_key_value().unwrap().1)
        } else {
            OrScalar::Value(new_self)
        }
    }
}

impl satisfying_set::RealFunc<roaring::RoaringSet, SatSetFunc<Int>, SatSetFunc<TypeEnum>>
    for SatSetFunc<Real>
{
    #[duplicate_item(
        name;
        [lt];
        [le];
        [gt];
        [ge];
    )]
    paste! {
        fn name(&self, other: &Self) -> roaring::RoaringSet {
            roaring::RoaringSet::from_raw(
                self.cmp_ops(other, |l, r| Ord::cmp(l, r).[<is_ name>]()).collect(),
                self.domain_size
            )
        }

        fn [<name _scalar>](&self, s: Real) -> roaring::RoaringSet {
            roaring::RoaringSet::from_raw(
                self.iter().filter_map(|f| if Ord::cmp(f.1, &s).[<is_ name>]() { Some(*f.0) } else { None }).collect(),
                self.domain_size
            )
        }
    }

    fn eq(&self, other: &Self) -> roaring::RoaringSet {
        roaring::RoaringSet::from_raw(
            self.cmp_ops(other, |l, r| PartialEq::eq(l, r)).collect(),
            self.domain_size,
        )
    }

    fn eq_scalar(&self, s: Real) -> roaring::RoaringSet {
        roaring::RoaringSet::from_raw(
            self.iter()
                .filter_map(|f| {
                    if PartialEq::eq(f.1, &s) {
                        Some(*f.0)
                    } else {
                        None
                    }
                })
                .collect(),
            self.domain_size,
        )
    }

    fn neq(&self, other: &Self) -> roaring::RoaringSet {
        roaring::RoaringSet::from_raw(
            self.cmp_ops(other, |l, r| PartialEq::ne(l, r)).collect(),
            self.domain_size,
        )
    }

    fn neq_scalar(&self, s: Real) -> roaring::RoaringSet {
        roaring::RoaringSet::from_raw(
            self.iter()
                .filter_map(|f| {
                    if PartialEq::ne(f.1, &s) {
                        Some(*f.0)
                    } else {
                        None
                    }
                })
                .collect(),
            self.domain_size,
        )
    }

    fn is_int(&self) -> roaring::RoaringSet {
        roaring::RoaringSet::from_raw(
            self.iter()
                .filter_map(|f| if f.1.is_integer() { Some(*f.0) } else { None })
                .collect(),
            self.domain_size,
        )
    }
}

impl satisfying_set::PureTypeEnumOps for SatSetFunc<TypeEnum> {
    fn new(domain_size: usize) -> Self {
        Self {
            map: Default::default(),
            domain_size,
        }
    }

    fn domain_len(&self) -> usize {
        self.domain_size
    }

    fn get(&self, index: DomainEnum) -> Option<TypeEnum> {
        Self::get(self, index)
    }

    fn set(&mut self, index: DomainEnum, value: TypeEnum) {
        Self::set(self, index, Some(value))
    }

    fn iter<'a>(&'a self) -> impl Iterator<Item = (DomainEnum, TypeEnum)> + 'a {
        self.map.iter().map(|f| (*f.0, *f.1))
    }
}

impl satisfying_set::TypeEnumFunc<roaring::RoaringSet, SatSetFunc<Int>, SatSetFunc<Real>>
    for SatSetFunc<TypeEnum>
{
    fn eq(&self, other: &Self) -> roaring::RoaringSet {
        roaring::RoaringSet::from_raw(
            self.cmp_ops(other, |l, r| PartialEq::eq(l, r)).collect(),
            self.domain_size,
        )
    }

    fn eq_scalar(&self, s: TypeEnum) -> roaring::RoaringSet {
        roaring::RoaringSet::from_raw(
            self.iter()
                .filter_map(|f| {
                    if PartialEq::eq(f.1, &s) {
                        Some(*f.0)
                    } else {
                        None
                    }
                })
                .collect(),
            self.domain_size,
        )
    }

    fn neq(&self, other: &Self) -> roaring::RoaringSet {
        roaring::RoaringSet::from_raw(
            self.cmp_ops(other, |l, r| PartialEq::ne(l, r)).collect(),
            self.domain_size,
        )
    }

    fn neq_scalar(&self, s: TypeEnum) -> roaring::RoaringSet {
        roaring::RoaringSet::from_raw(
            self.iter()
                .filter_map(|f| {
                    if PartialEq::ne(f.1, &s) {
                        Some(*f.0)
                    } else {
                        None
                    }
                })
                .collect(),
            self.domain_size,
        )
    }
}
