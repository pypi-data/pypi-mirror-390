use super::{
    DomainEnumReorder, InterpContext, LayoutVec,
    natural_join::SortMergeJoin,
    satisfying_set::{Alignable, AlignedLayout, OrScalar, PureIntFuncOps, PureSetOps},
};
use crate::{
    comp_core::{
        DiscreteSize, IndexRange, IndexRepr,
        node::QuantKind,
        structure::{DomainEnumBuilder, LexTypeEnumIterBuilder, TypeEnumIter},
        vocabulary::DomainEnum,
    },
    interp_structures::satisfying_set::align_layout,
    structure::complete,
};
use cfg_if::cfg_if;
use sli_collections::hash_set::IdHashSet;
use std::{
    cmp::Ordering,
    marker::PhantomData,
    mem::{replace, swap},
    pin::Pin,
};

cfg_if! {
    if #[cfg(feature = "64-bit")] {
        pub type RoaringBitmapRepr = croaring::bitmap64::Bitmap64;
        pub type RoaringIter<'a> = croaring::bitmap64::Bitmap64Iterator<'a>;
    } else if #[cfg(feature = "32-bit")] {
        pub type RoaringBitmapRepr = croaring::bitmap::Bitmap;
        pub type RoaringIter<'a> = croaring::bitmap::BitmapIterator<'a>;
    } else if #[cfg(target_pointer_width = "32")] {
        pub type RoaringBitmapRepr = croaring::bitmap::Bitmap;
        pub type RoaringIter<'a> = croaring::bitmap::BitmapIterator<'a>;
    } else if #[cfg(target_pointer_width = "64")] {
        pub type RoaringBitmapRepr = croaring::bitmap64::Bitmap64;
        pub type RoaringIter<'a> = croaring::bitmap64::Bitmap64Iterator<'a>;
    } else {
        std::compile_error!("Architecture pointer size does not align with \
                            float pointing number size.
                            Please specify one of the bit size features.");
    }
}

#[derive(Clone)]
pub struct RoaringDomainIter<'a, T>(RoaringIter<'a>, PhantomData<T>);

impl<'a, T> Iterator for RoaringDomainIter<'a, T>
where
    T: From<IndexRepr> + Copy + PartialEq + Eq + PartialOrd + Ord,
    DiscreteSize: From<T>,
    IndexRepr: From<T>,
{
    type Item = T;

    fn next(&mut self) -> Option<Self::Item> {
        self.0
            .next()
            .map(|f| T::from(IndexRepr::try_from(f).unwrap()))
    }
}

#[derive(Debug, Clone)]
pub struct RoaringBitmapIndex<T>(RoaringBitmapRepr, PhantomData<T>);

pub type RoaringBitmap = RoaringBitmapIndex<DomainEnum>;

impl<T> Default for RoaringBitmapIndex<T>
where
    T: From<IndexRepr> + Copy + PartialEq + Eq + PartialOrd + Ord,
    DiscreteSize: From<T>,
    IndexRepr: From<T>,
{
    fn default() -> Self {
        Self::new()
    }
}

impl<T> RoaringBitmapIndex<T>
where
    T: From<IndexRepr> + Copy + PartialEq + Eq + PartialOrd + Ord,
    DiscreteSize: From<T>,
    IndexRepr: From<T>,
{
    pub fn new() -> Self {
        RoaringBitmapIndex(RoaringBitmapRepr::new(), PhantomData)
    }

    pub fn from_range(range: IndexRange<T>) -> Self {
        RoaringBitmapIndex(
            RoaringBitmapRepr::from_range(
                DiscreteSize::from(range.start)..DiscreteSize::from(range.end),
            ),
            PhantomData,
        )
    }

    pub fn get(&self, index: T) -> bool {
        self.0.contains(index.into())
    }

    pub fn set(&mut self, index: T, value: bool) {
        if value {
            self.0.add(index.into())
        } else {
            self.0.remove(index.into())
        }
    }

    /// Returns [true] if it changed the bitmap, false otherwise
    pub fn set_checked(&mut self, index: T, value: bool) -> bool {
        if value {
            self.0.add_checked(index.into())
        } else {
            self.0.remove_checked(index.into())
        }
    }

    pub fn insert(&mut self, index: T) {
        self.0.add(index.into())
    }

    pub fn insert_checked(&mut self, index: T) -> bool {
        self.0.add_checked(index.into())
    }

    pub fn remove(&mut self, index: T) {
        self.0.remove(index.into())
    }

    pub fn iter(&self) -> RoaringDomainIter<'_, T> {
        RoaringDomainIter(self.0.iter(), PhantomData)
    }

    pub fn union(self, other: &Self) -> Self {
        RoaringBitmapIndex(self.0.or(&other.0), PhantomData)
    }

    pub fn and_inplace(&mut self, other: &Self) {
        self.0.and_inplace(&other.0)
    }

    pub fn andnot_inplace(&mut self, other: &Self) {
        self.0.andnot_inplace(&other.0)
    }

    pub fn andnot_cardinality(&self, other: &Self) -> usize {
        self.0.andnot_cardinality(&other.0).try_into().unwrap()
    }

    pub fn andnot(&self, other: &Self) -> Self {
        Self(self.0.andnot(&other.0), PhantomData)
    }

    pub fn and_cardinality(&self, other: &Self) -> usize {
        self.0.and_cardinality(&other.0).try_into().unwrap()
    }

    pub fn or_inplace(&mut self, other: &Self) {
        self.0.or_inplace(&other.0)
    }

    pub fn xor_inplace(&mut self, other: &Self) {
        self.0.xor_inplace(&other.0)
    }

    pub fn flip_inplace(&mut self, range: IndexRange<T>) {
        self.0.flip_inplace(
            DiscreteSize::try_from(range.start).unwrap()
                ..DiscreteSize::try_from(range.end).unwrap(),
        )
    }

    pub fn cardinality(&self) -> usize {
        self.0.cardinality().try_into().unwrap()
    }

    pub fn cardinality_in_range(&self, range: IndexRange<T>) -> usize {
        let indexes = DiscreteSize::try_from(range.start).unwrap()
            ..DiscreteSize::try_from(range.end).unwrap();
        let mut bit_map = RoaringBitmapRepr::new();
        bit_map.flip_inplace(indexes);
        let mask = RoaringBitmapIndex(bit_map, PhantomData);
        self.and_cardinality(&mask)
    }

    pub fn add(&mut self, value: T) {
        self.0.add(value.into())
    }

    pub fn contains(&self, value: T) -> bool {
        self.0.contains(value.into())
    }

    pub fn run_optimize(&mut self) -> bool {
        self.0.run_optimize()
    }

    pub fn negate_over_range(&mut self, range: IndexRange<T>) {
        self.0
            .flip_inplace(DiscreteSize::from(range.start)..DiscreteSize::from(range.end))
    }

    pub fn len(&self) -> usize {
        self.0.cardinality().try_into().unwrap()
    }
}

impl<A> Extend<A> for RoaringBitmapIndex<A>
where
    A: From<IndexRepr> + Copy + PartialEq + Eq + PartialOrd + Ord,
    DiscreteSize: From<A>,
    IndexRepr: From<A>,
{
    fn extend<T: IntoIterator<Item = A>>(&mut self, iter: T) {
        self.0.extend(iter.into_iter().map(|f| f.into()))
    }
}

impl<'a, T> FromIterator<T> for RoaringBitmapIndex<T>
where
    T: From<IndexRepr> + Copy + PartialEq + Eq + PartialOrd + Ord,
    DiscreteSize: From<T>,
    IndexRepr: From<T>,
{
    fn from_iter<I: IntoIterator<Item = T>>(iter: I) -> Self {
        RoaringBitmapIndex(
            RoaringBitmapRepr::from_iter(iter.into_iter().map(|f| DiscreteSize::from(f))),
            PhantomData,
        )
    }
}

impl<'a, T> IntoIterator for &'a RoaringBitmapIndex<T>
where
    T: From<IndexRepr> + Copy + PartialEq + Eq + PartialOrd + Ord,
    DiscreteSize: From<T>,
    IndexRepr: From<T>,
{
    type Item = T;
    type IntoIter = RoaringDomainIter<'a, T>;

    fn into_iter(self) -> Self::IntoIter {
        self.iter()
    }
}

impl<T: Unpin> IntoIterator for RoaringBitmapIndex<T>
where
    T: From<IndexRepr> + Copy + PartialEq + Eq + PartialOrd + Ord,
    DiscreteSize: From<T>,
    IndexRepr: From<T>,
{
    type Item = T;
    type IntoIter = RoaringIntoIter<T>;

    fn into_iter(self) -> Self::IntoIter {
        RoaringIntoIter::new(self)
    }
}

pub struct RoaringIntoIter<T: Unpin>
where
    T: From<IndexRepr> + Copy + PartialEq + Eq + PartialOrd + Ord,
    DiscreteSize: From<T>,
    IndexRepr: From<T>,
{
    // safety:
    //
    // iter must stop existing for inner to be moved anywhere.
    iter: Option<RoaringDomainIter<'static, T>>,
    bitmap: Pin<Box<RoaringBitmapIndex<T>>>,
}

impl<T: Unpin> RoaringIntoIter<T>
where
    T: From<IndexRepr> + Copy + PartialEq + Eq + PartialOrd + Ord,
    DiscreteSize: From<T>,
    IndexRepr: From<T>,
{
    pub fn new(bitmap: RoaringBitmapIndex<T>) -> Self {
        let mut ret = Self {
            iter: None,
            bitmap: Box::pin(bitmap),
        };

        let iter = ret.bitmap.iter();
        // This is safe as long as we never move inner when this field exists.
        ret.iter = Some(unsafe {
            core::mem::transmute::<RoaringDomainIter<'_, T>, RoaringDomainIter<'static, T>>(iter)
        });
        ret
    }

    pub fn recover_bitmap(self) -> RoaringBitmapIndex<T> {
        *Pin::into_inner(self.bitmap)
    }
}

impl<T: Unpin> Iterator for RoaringIntoIter<T>
where
    T: From<IndexRepr> + Copy + PartialEq + Eq + PartialOrd + Ord,
    DiscreteSize: From<T>,
    IndexRepr: From<T>,
{
    type Item = T;

    fn next(&mut self) -> Option<Self::Item> {
        if let Some(iter) = &mut self.iter {
            iter.next()
        } else {
            None
        }
    }
}

#[derive(Debug, Clone)]
pub struct RoaringSet {
    bit_set: RoaringBitmap,
    negated: bool,
    len: usize,
}

impl RoaringSet {
    pub fn new(domain_size: usize) -> Self {
        Self {
            bit_set: RoaringBitmapIndex::new(),
            negated: false,
            len: domain_size,
        }
    }

    pub fn from_raw(bit_set: RoaringBitmap, len: usize) -> Self {
        RoaringSet {
            negated: false,
            bit_set,
            len,
        }
    }

    pub fn inner(mut self) -> RoaringBitmap {
        if self.negated {
            self.bit_set.negate_over_range((0..self.len).into());
            self.bit_set
        } else {
            self.bit_set
        }
    }

    pub fn inner_raw(self) -> RoaringBitmap {
        self.bit_set
    }

    pub fn len(&self) -> usize {
        self.len
    }

    pub fn and(&mut self, other: &Self) {
        match (self.negated, other.negated) {
            (false, false) => {
                self.bit_set.and_inplace(&other.bit_set);
            }
            (false, true) => {
                self.bit_set.andnot_inplace(&other.bit_set);
            }
            (true, false) => {
                self.bit_set = other.bit_set.andnot(&self.bit_set);
                self.negated = false;
            }
            (true, true) => {
                self.bit_set.or_inplace(&other.bit_set);
            }
        }
        self.bit_set.run_optimize();
    }

    pub fn or(&mut self, other: &Self) {
        match (self.negated, other.negated) {
            (false, false) => {
                self.bit_set.or_inplace(&other.bit_set);
            }
            (false, true) => {
                self.bit_set = other.bit_set.andnot(&other.bit_set);
                self.negated = true;
            }
            (true, false) => {
                self.bit_set.andnot_inplace(&other.bit_set);
            }
            (true, true) => {
                self.bit_set.and_inplace(&other.bit_set);
            }
        }
        self.bit_set.run_optimize();
    }

    pub fn xor(&mut self, other: &Self) {
        self.bit_set.xor_inplace(&other.bit_set);
        self.negated ^= other.negated;
        self.bit_set.run_optimize();
    }

    pub fn neg(&mut self) {
        self.negated ^= true;
    }

    pub fn count(&self) -> usize {
        if !self.negated {
            self.bit_set.cardinality()
        } else {
            self.len - self.bit_set.cardinality()
        }
    }

    pub fn reorder(
        self,
        cur_layout: &LayoutVec,
        new_layout: &LayoutVec,
        context: &InterpContext,
    ) -> Self {
        let mut new_self = Self::new(new_layout.domain_len(context));
        let mut reorder = DomainEnumReorder::new_with_context(cur_layout, new_layout, context);
        for index in self.iter() {
            for new_id in reorder.index(usize::try_from(index).unwrap().into()) {
                new_self.set(new_id)
            }
        }
        new_self
    }

    pub fn set(&mut self, index: DomainEnum) {
        if !self.negated {
            self.bit_set.add(index)
        } else {
            self.bit_set.remove(index)
        }
    }

    pub fn unset(&mut self, index: DomainEnum) {
        if !self.negated {
            self.bit_set.remove(index)
        } else {
            self.bit_set.add(index)
        }
    }

    pub fn contains(&self, index: DomainEnum) -> bool {
        self.bit_set.contains(index) ^ self.negated
    }

    pub fn cardinality_in_range(&self, range: IndexRange<DomainEnum>) -> usize {
        if !self.negated {
            self.bit_set.cardinality_in_range(range)
        } else {
            range.len() - self.bit_set.cardinality_in_range(range)
        }
    }

    pub fn and_cardinality(&self, other: &Self) -> usize {
        match (self.negated, other.negated) {
            (false, false) => self.bit_set.and_cardinality(&other.bit_set),
            (false, true) => self.bit_set.andnot_cardinality(&other.bit_set),
            (true, false) => other.bit_set.andnot_cardinality(&self.bit_set),
            (true, true) => {
                let longest = self.len().max(other.len());
                longest - self.bit_set.and_cardinality(&other.bit_set)
            }
        }
    }

    fn quant(
        self,
        context: &InterpContext,
        quant_type: QuantKind,
        old_layout: &LayoutVec,
        new_layout: &LayoutVec,
    ) -> Self {
        let var_bool: Box<[_]> = old_layout
            .iter()
            .map(|f| !new_layout.contains_var(f))
            .collect();
        let new_len = new_layout.domain_len(context);
        let mut new_set = Self::new(new_len);
        let mut bools = var_bool.iter();
        let quant_amount = match quant_type {
            QuantKind::ExQuant => 0,
            QuantKind::UniQuant => LayoutVec::domain_len_of_iter(
                old_layout.iter().filter(|_| *bools.next().unwrap()),
                context,
            ),
        };
        if new_len == 1 {
            let amount = self.count();
            let val = match quant_type {
                QuantKind::ExQuant => amount > 0,
                QuantKind::UniQuant => amount == quant_amount,
            };
            if val {
                new_set.set(0.into());
            }
            return new_set;
        }

        let mut quantification = DomainEnumReorder::new(
            new_layout,
            old_layout,
            context.get_type_map(),
            context.type_interps(),
        );

        let indexes: IndexRange<DomainEnum> = IndexRange::new(0..new_len);
        for index in indexes {
            let mask = Self {
                bit_set: RoaringBitmap::from_iter(quantification.index(index)),
                negated: false,
                len: new_len,
            };
            let amount = self.and_cardinality(&mask);
            let val = match quant_type {
                QuantKind::ExQuant => amount > 0,
                QuantKind::UniQuant => amount == quant_amount,
            };
            if val {
                new_set.set(index);
            }
        }
        new_set
    }

    pub fn cardinality_agg<I: PureIntFuncOps>(
        self,
        context: &InterpContext,
        old_layout: &LayoutVec,
        new_layout: &LayoutVec,
    ) -> I {
        let new_len = new_layout.domain_len(context);
        let mut card_vec = I::new(new_len);
        if new_len == 1 {
            let amount = self.count();
            card_vec.set(
                DomainEnum::from(0),
                amount.try_into().expect("Number Too big!"),
            );
            return card_vec;
        }

        let mut quantification = DomainEnumReorder::new(
            new_layout,
            old_layout,
            context.get_type_map(),
            context.type_interps(),
        );

        let indexes: IndexRange<DomainEnum> = IndexRange::new(0..new_len);
        for index in indexes {
            let mask = Self {
                bit_set: RoaringBitmap::from_iter(quantification.index(index)),
                negated: false,
                len: new_len,
            };
            let amount = self.and_cardinality(&mask);
            card_vec.set(index, amount.try_into().expect("Number Too big!"));
        }
        card_vec
    }

    fn iter(&self) -> roaring_set::Iter<'_> {
        roaring_set::Iter::new(self)
    }
}

pub mod roaring_set {
    use crate::comp_core::{IndexRepr, vocabulary::DomainEnum};

    use super::{RoaringDomainIter, RoaringSet};

    #[derive(Clone)]
    pub struct Iter<'a> {
        roaring_iter: RoaringDomainIter<'a, DomainEnum>,
        mode: IterMode,
    }

    impl<'a> Iter<'a> {
        pub fn new(roaring_set: &'a RoaringSet) -> Self {
            let mut roaring_iter = roaring_set.bit_set.iter();
            let mode = if roaring_set.negated {
                IterMode::Negated {
                    cur: 0.into(),
                    next: roaring_iter.next(),
                    len: roaring_set.len(),
                }
            } else {
                IterMode::Normal
            };
            Self { roaring_iter, mode }
        }
    }

    #[derive(Clone, PartialEq, Eq)]
    enum IterMode {
        Negated {
            cur: DomainEnum,
            next: Option<DomainEnum>,
            len: usize,
        },
        Normal,
    }

    impl<'a> Iterator for Iter<'a> {
        type Item = DomainEnum;

        fn next(&mut self) -> Option<Self::Item> {
            match &mut self.mode {
                IterMode::Normal => self.roaring_iter.next(),
                IterMode::Negated { cur, next, len } => {
                    'outer: loop {
                        if let Some(next_inner) = next {
                            if &cur < &next_inner {
                                let ret = *cur;
                                *cur = (IndexRepr::from(*cur) + 1).into();
                                return Some(ret);
                            }
                            'inner: loop {
                                let new_next = self.roaring_iter.next();
                                if let Some(new_next) = new_next {
                                    let prev_inner = *next_inner;
                                    *next_inner = new_next;
                                    if new_next
                                        == DomainEnum::from(IndexRepr::from(*next_inner) + 1)
                                    {
                                        continue 'inner;
                                    }
                                    *cur = (IndexRepr::from(prev_inner) + 1).into();
                                    continue 'outer;
                                } else {
                                    *cur = (IndexRepr::from(*next_inner) + 1).into();
                                    *next = None;
                                    break 'outer;
                                }
                            }
                        }
                        break;
                    }
                    if IndexRepr::from(*cur) < (*len).try_into().unwrap() {
                        let ret = *cur;
                        *cur = (IndexRepr::from(*cur) + 1).into();
                        return Some(ret);
                    } else {
                        return None;
                    }
                }
            }
        }
    }

    #[cfg(test)]
    mod tests {
        use crate::interp_structures::roaring::RoaringSet;

        #[test]
        fn roaring_set_iter_1() {
            let mut roaring_iter = RoaringSet::new(4);
            roaring_iter.set(0.into());
            roaring_iter.set(3.into());
            roaring_iter.neg();
            println!("{:?}", roaring_iter.iter().collect::<Vec<_>>());
            assert!(roaring_iter.iter().eq([1.into(), 2.into(),]))
        }

        #[test]
        fn roaring_set_iter_2() {
            let mut roaring_iter = RoaringSet::new(4);
            roaring_iter.set(1.into());
            roaring_iter.set(3.into());
            roaring_iter.neg();
            println!("{:?}", roaring_iter.iter().collect::<Vec<_>>());
            assert!(roaring_iter.iter().eq([0.into(), 2.into(),]))
        }

        #[test]
        fn roaring_set_iter_3() {
            let mut roaring_iter = RoaringSet::new(4);
            roaring_iter.set(1.into());
            roaring_iter.set(2.into());
            roaring_iter.neg();
            println!("{:?}", roaring_iter.iter().collect::<Vec<_>>());
            assert!(roaring_iter.iter().eq([0.into(), 3.into(),]))
        }
    }
}

impl PureSetOps for RoaringSet {
    fn new(domain_size: usize) -> Self {
        Self::new(domain_size)
    }

    fn set(&mut self, index: DomainEnum) {
        Self::set(self, index.into())
    }

    fn unset(&mut self, index: DomainEnum) {
        Self::unset(self, index.into())
    }

    fn contains(&self, index: DomainEnum) -> bool {
        Self::contains(self, index.into())
    }

    fn from_structure(pred: &complete::immutable::PredInterp) -> Self {
        let len = pred.domain().domain_len(pred.type_interps());
        cfg_if::cfg_if! {
            if #[cfg(backend_store = "roaring")] {
                RoaringSet::from_raw(
                    pred.store.as_bit_map().clone(),
                    len,
                )
            } else {
                default_from_structure(Self::new(len), pred)
            }
        }
    }

    fn natural_join(
        mut left: (Self, LayoutVec),
        mut right: (Self, LayoutVec),
        context: &InterpContext,
    ) -> (Self, LayoutVec) {
        // find overlap
        let overlap: IdHashSet<_> = left
            .1
            .iter()
            .enumerate()
            .filter(|f| right.1.contains_var(f.1))
            .map(|f| f.1)
            .collect();
        if overlap.len() == left.1.len() && left.1 == right.1 {
            left.0.and(&right.0);
            return left;
        } else if overlap.len() == left.1.len() && left.1.len() == right.1.len() {
            align_layout(
                (&mut left.0, &mut left.1),
                (&mut right.0, &mut right.1),
                context,
            );
            left.0.and(&right.0);
            return left;
        } else if overlap.len() == 0 {
            let left_domain = left.1.get_domain(context.type_map);
            let right_domain = right.1.get_domain(context.type_map);
            let new_layout = LayoutVec::from_iter(left.1.into_iter().chain(right.1.iter()));
            let new_domain = new_layout.get_domain(context.type_map);
            let mut dom_builder = DomainEnumBuilder::new(&new_domain, context.type_interps);
            let product = itertools::Itertools::cartesian_product(left.0.iter(), right.0.iter());
            return (
                Self {
                    bit_set: RoaringBitmapIndex::from_iter(product.map(
                        |(left_value, right_value)| {
                            TypeEnumIter::new(context.type_interps, left_domain.iter(), left_value)
                                .for_each(|f| dom_builder.add_enum_arg(f).unwrap());
                            TypeEnumIter::new(
                                context.type_interps,
                                right_domain.iter(),
                                right_value,
                            )
                            .for_each(|f| dom_builder.add_enum_arg(f).unwrap());
                            let ret = dom_builder.get_index().unwrap();
                            dom_builder.reset();
                            ret
                        },
                    )),
                    negated: false,
                    len: new_layout.domain_len(context),
                },
                new_layout,
            );
        }
        let left_orig = left.1.clone();
        let right_orig = right.1.clone();
        // Sort by overlapping vars.
        // Overlapping vars must be in at the end of the layout.
        // This is because first values in a domain are least significant, and last values are most
        // significant.
        // Use ordering to make order of overlapping vars consistent.
        // We say that any non overlapping vars are equal in ordering to hopefully reduce the
        // amount of swaps.
        let cmp = |left: &_, right: &_| match (overlap.contains(left), overlap.contains(right)) {
            (true, true) => left.cmp(right),
            (true, false) => Ordering::Greater,
            (false, true) => Ordering::Less,
            (false, false) => Ordering::Equal,
        };
        left.1.sort_by(cmp);
        right.1.sort_by(cmp);
        let mut left_empty = LayoutVec::new();
        let mut right_empty = LayoutVec::new();

        // Align sets along new layout
        swap(&mut left.1, &mut left_empty);
        swap(&mut right.1, &mut right_empty);
        let left_aligned = AlignedLayout::new(left_orig, left_empty);
        let right_aligned = AlignedLayout::new(right_orig, right_empty);
        left.0.align(&left_aligned, context);
        right.0.align(&right_aligned, context);
        // swap layout back to where it came from
        swap(&mut left_aligned.take_new_layout(), &mut left.1);
        swap(&mut right_aligned.take_new_layout(), &mut right.1);

        let left_domain = left.1.get_domain(context.type_map);
        let right_domain = right.1.get_domain(context.type_map);
        let overlap_amount = overlap.len();
        let left_skip_amount = left_domain.len() - overlap_amount;
        let right_skip_amount = right_domain.len() - overlap_amount;
        let left_builder = LexTypeEnumIterBuilder::new(context.type_interps(), &left_domain);
        let right_builder = LexTypeEnumIterBuilder::new(context.type_interps(), &right_domain);

        let mj = SortMergeJoin::new(
            RoaringSet::iter(&left.0),
            RoaringSet::iter(&right.0),
            |left, right| -> Ordering {
                // First argument is least significant
                // So use LexTypeEnumIter here the arguments are in lexographical order
                // i.e. first argument is most significant
                left_builder
                    .iter_of(*left)
                    .take(overlap_amount)
                    .cmp(right_builder.iter_of(*right).take(overlap_amount))
            },
            |left1, left2| -> Ordering {
                left_builder
                    .iter_of(*left1)
                    .take(overlap_amount)
                    .cmp(left_builder.iter_of(*left2).take(overlap_amount))
            },
            |right1, right2| -> Ordering {
                right_builder
                    .iter_of(*right1)
                    .take(overlap_amount)
                    .cmp(right_builder.iter_of(*right2).take(overlap_amount))
            },
        );
        let layout_iter = left
            .1
            .iter()
            // leftover left
            .take(left_skip_amount)
            // leftover right
            .chain(right.1.iter().take(right_skip_amount))
            // overlap
            .chain(left.1.iter().skip(left_skip_amount))
            .collect();
        let new_layout = unsafe { LayoutVec::from_raw(layout_iter) };
        let new_domain = new_layout.get_domain(context.get_type_map());
        let mut dom_builder = DomainEnumBuilder::new(&new_domain, context.type_interps);
        let new_size = new_layout.domain_len(context);
        let new_set = RoaringSet {
            bit_set: RoaringBitmap::from_iter(mj.into_iter().map(|(left, right)| {
                let left_iter =
                    TypeEnumIter::new(context.type_interps(), left_domain.as_ref(), left);
                let right_iter =
                    TypeEnumIter::new(context.type_interps(), right_domain.as_ref(), right);

                for leftover_left in left_iter.clone().take(left_skip_amount) {
                    dom_builder.add_enum_arg(leftover_left).unwrap();
                }

                for leftover_right in right_iter.take(right_skip_amount) {
                    dom_builder.add_enum_arg(leftover_right).unwrap();
                }

                for overlap in left_iter.skip(left_skip_amount) {
                    dom_builder.add_enum_arg(overlap).unwrap();
                }
                let ret = dom_builder.get_index().unwrap();
                dom_builder.reset();
                ret
            })),
            negated: false,
            len: new_size,
        };
        (new_set, new_layout)
    }

    fn domain_len(&self) -> usize {
        Self::len(self)
    }

    fn or(&mut self, other: &Self) {
        Self::or(self, other)
    }

    fn and(&mut self, other: &Self) {
        Self::and(self, other)
    }

    fn xor(&mut self, other: &Self) {
        Self::xor(self, other)
    }

    fn neg(&mut self) {
        Self::neg(self)
    }

    fn quant(
        self,
        old_layout: &LayoutVec,
        new_layout: &LayoutVec,
        quant_type: QuantKind,
        context: &InterpContext,
    ) -> OrScalar<Self, bool> {
        let a = Self::quant(self, context, quant_type, old_layout, new_layout);
        if new_layout.len() == 0 {
            OrScalar::Scalar(a.contains(0.into()))
        } else {
            OrScalar::Value(a)
        }
    }

    fn cardinality(&self) -> usize {
        self.count()
    }

    fn iter<'a>(&'a self) -> impl Iterator<Item = DomainEnum> + 'a {
        self.iter().map(|f| usize::try_from(f).unwrap().into())
    }
}

impl Alignable for RoaringSet {
    fn align(&mut self, aligned_layout: &AlignedLayout, context: &InterpContext) {
        let out = replace(self, RoaringSet::new(0));
        let reordered = out.reorder(
            aligned_layout.old_layout(),
            aligned_layout.new_layout(),
            context,
        );
        *self = reordered;
    }
}

impl Extend<DomainEnum> for RoaringSet {
    fn extend<T: IntoIterator<Item = DomainEnum>>(&mut self, iter: T) {
        if !self.negated {
            self.bit_set.extend(iter)
        } else {
            let bit_set = iter.into_iter().collect();
            self.bit_set.andnot_inplace(&bit_set);
        }
    }
}
