use super::{super::backend::indexes::*, CompleteFunc, FuncElementWrapper, NegatedIter};
use crate::{
    IndexRange, IndexRepr, Int, Real,
    interp_structures::roaring::RoaringBitmap,
    structure::{
        backend::{COption, CompleteIter, FuncElementUnion, PartialRef},
        traits::{SymbolInfo, ToOwnedStore, complete, partial},
    },
    vocabulary::{DomainEnum, PfuncIndex, TypeEnum},
};
use duplicate::duplicate_item;
use itertools::Either;
use sli_collections::{auto, hash_map::IdHashMap};
use sli_collections::{cell::Cell, iterator::Iterator as SIterator};
use std::collections::BTreeMap;
use std::{cmp::Ordering, iter::Peekable};

#[derive(Debug, Clone)]
pub struct RoaringBitmapCached {
    bit_map: RoaringBitmap,
    len: Cell<Option<usize>>,
}

impl Default for RoaringBitmapCached {
    fn default() -> Self {
        Self::new()
    }
}

impl From<RoaringBitmap> for RoaringBitmapCached {
    fn from(value: RoaringBitmap) -> Self {
        Self {
            bit_map: value,
            len: Cell::new(None),
        }
    }
}

impl RoaringBitmapCached {
    pub fn new() -> Self {
        Self {
            bit_map: RoaringBitmap::new(),
            len: Cell::new(Some(0)),
        }
    }

    pub fn as_bit_map(&self) -> &RoaringBitmap {
        &self.bit_map
    }

    pub fn union(self, other: &Self) -> Self {
        Self {
            bit_map: self.bit_map.union(&other.bit_map),
            len: None.into(),
        }
    }

    pub fn set(&mut self, domain_enum: DomainEnum, value: bool) {
        let changed = self.bit_map.set_checked(domain_enum, value);
        if changed {
            let old_len = self.len.take();
            let new_len = if value {
                old_len.map(|f| f + 1)
            } else {
                old_len.map(|f| f - 1)
            };
            self.len.set(new_len);
        }
    }

    pub fn insert(&mut self, value: DomainEnum) {
        if self.bit_map.insert_checked(value) {
            self.len.set(self.len.take().map(|f| f + 1))
        }
    }

    pub fn negate_over_range(&mut self, range: IndexRange<DomainEnum>) {
        self.bit_map.negate_over_range(range);
        self.len = None.into();
    }

    pub fn contains(&self, index: DomainEnum) -> bool {
        self.bit_map.contains(index)
    }

    pub fn len(&self) -> usize {
        let old_len = self.len.take();
        let actual_len = old_len.unwrap_or_else(|| self.bit_map.cardinality());
        self.len.set(Some(actual_len));
        actual_len
    }
}

impl<'a> IntoIterator for &'a RoaringBitmapCached {
    type Item = DomainEnum;
    type IntoIter = <&'a RoaringBitmap as IntoIterator>::IntoIter;

    fn into_iter(self) -> Self::IntoIter {
        (&self.bit_map).into_iter()
    }
}

impl IntoIterator for RoaringBitmapCached {
    type Item = DomainEnum;
    type IntoIter = <RoaringBitmap as IntoIterator>::IntoIter;

    fn into_iter(self) -> Self::IntoIter {
        self.bit_map.into_iter()
    }
}

impl FromIterator<DomainEnum> for RoaringBitmapCached {
    fn from_iter<T: IntoIterator<Item = DomainEnum>>(iter: T) -> Self {
        Self {
            bit_map: RoaringBitmap::from_iter(iter),
            len: Default::default(),
        }
    }
}

impl ToOwnedStore for RoaringBitmapCached {
    type Owned = Self;

    fn to_owned(&self, _common: SymbolInfo) -> Self::Owned {
        self.clone()
    }
}

impl complete::ImFunc<bool> for RoaringBitmapCached {
    fn get(&self, _: SymbolInfo, domain_enum: DomainEnum) -> bool {
        RoaringBitmapCached::contains(self, domain_enum)
    }

    fn iter_complete(&self, common: SymbolInfo) -> impl SIterator<Item = (DomainEnum, bool)> {
        CompleteIter::new(
            self.into_iter(),
            common.domain.iter_index(common.type_interps),
        )
    }

    fn into_iter_complete(self, common: SymbolInfo) -> impl SIterator<Item = (DomainEnum, bool)> {
        CompleteIter::new(
            self.into_iter(),
            common.domain.iter_index(common.type_interps),
        )
    }
}

impl complete::MutFunc<bool> for RoaringBitmapCached {
    fn set(&mut self, _: SymbolInfo, domain_enum: DomainEnum, value: bool) {
        <RoaringBitmapCached>::set(self, domain_enum, value)
    }
}

impl complete::ImPred for RoaringBitmapCached {
    fn iter_true(&self, _: SymbolInfo) -> impl SIterator<Item = DomainEnum> {
        self.into_iter()
    }

    fn into_iter_true(self, _: SymbolInfo) -> impl SIterator<Item = DomainEnum> {
        self.into_iter()
    }
}

#[derive(Clone, Debug)]
pub enum PartialRoaring {
    Partial {
        certainly_true: RoaringBitmapCached,
        certainly_false: RoaringBitmapCached,
    },
    Full(RoaringBitmapCached),
}

impl Default for PartialRoaring {
    fn default() -> Self {
        Self::Partial {
            certainly_true: Default::default(),
            certainly_false: Default::default(),
        }
    }
}

impl From<RoaringBitmapCached> for PartialRoaring {
    fn from(value: RoaringBitmapCached) -> Self {
        Self::Full(value)
    }
}

impl ToOwnedStore for PartialRoaring {
    type Owned = Self;

    fn to_owned(&self, _: crate::structure::traits::SymbolInfo) -> Self::Owned {
        self.clone()
    }
}

impl partial::ImFunc<bool> for PartialRoaring {
    type CompleteSymbol = RoaringBitmapCached;
    type CompleteSymbolRef<'a> = &'a RoaringBitmapCached;

    fn get(&self, common: SymbolInfo, domain_enum: DomainEnum) -> Option<bool> {
        match self {
            Self::Partial {
                certainly_true,
                certainly_false,
            } => {
                if complete::ImFunc::get(certainly_true, common, domain_enum) {
                    return Some(true);
                } else if complete::ImFunc::get(certainly_false, common, domain_enum) {
                    return Some(false);
                }
                return None;
            }
            Self::Full(value) => Some(complete::ImFunc::get(value, common, domain_enum)),
        }
    }

    fn into_iter_partial(self, common: SymbolInfo) -> impl SIterator<Item = (DomainEnum, bool)> {
        match self {
            Self::Partial {
                certainly_true,
                certainly_false,
            } => Either::Left(PotPredIter {
                ct: certainly_true.into_iter().peekable(),
                cf: certainly_false.into_iter().peekable(),
            }),
            Self::Full(full) => Either::Right(CompleteIter::new(
                full.into_iter(),
                common.domain.iter_index(common.type_interps),
            )),
        }
    }

    fn iter_partial(&self, common: SymbolInfo) -> impl SIterator<Item = (DomainEnum, bool)> {
        match self {
            Self::Partial {
                certainly_true,
                certainly_false,
            } => Either::Left(PotPredIter {
                ct: certainly_true.into_iter().peekable(),
                cf: certainly_false.into_iter().peekable(),
            }),
            Self::Full(full) => Either::Right(CompleteIter::new(
                full.into_iter(),
                common.domain.iter_index(common.type_interps),
            )),
        }
    }

    fn len_partial(&self, common: SymbolInfo) -> usize {
        match self {
            Self::Partial {
                certainly_true,
                certainly_false,
            } => certainly_true.len() + certainly_false.len(),
            Self::Full(_) => common.domain.domain_len(common.type_interps),
        }
    }

    fn try_as_im_complete<'a>(&'a self, _: SymbolInfo) -> Result<Self::CompleteSymbolRef<'a>, ()> {
        match self {
            Self::Partial { .. } => Err(()),
            Self::Full(full) => Ok(full),
        }
    }

    fn try_into_im_complete(self, _: SymbolInfo) -> Result<Self::CompleteSymbol, Self> {
        match self {
            Self::Partial { .. } => Err(self),
            Self::Full(full) => Ok(full),
        }
    }

    fn iter_unknown(&self, common: SymbolInfo) -> impl SIterator<Item = DomainEnum> {
        NegatedIter::new(
            partial::ImFunc::iter_partial(self, common).map(|(value, _)| value),
            common.domain.domain_len(common.type_interps),
        )
    }

    fn into_iter_unknown(self, common: SymbolInfo) -> impl SIterator<Item = DomainEnum> {
        NegatedIter::new(
            partial::ImFunc::into_iter_partial(self, common).map(|(value, _)| value),
            common.domain.domain_len(common.type_interps),
        )
    }
}

impl partial::ImPred for PartialRoaring {
    type CompletePred = RoaringBitmapCached;
    type CompletePredRef<'a> = &'a RoaringBitmapCached;

    fn try_as_im_complete<'a>(&'a self, _: SymbolInfo) -> Result<Self::CompletePredRef<'a>, ()> {
        match self {
            Self::Partial { .. } => Err(()),
            Self::Full(full) => Ok(full),
        }
    }

    fn try_into_im_complete(self, _: SymbolInfo) -> Result<Self::CompletePred, Self> {
        match self {
            Self::Partial { .. } => Err(self),
            Self::Full(full) => Ok(full),
        }
    }

    fn iter_true(&self, _: SymbolInfo) -> impl SIterator<Item = DomainEnum> {
        match self {
            Self::Partial { certainly_true, .. } => Either::Left(certainly_true.into_iter()),
            Self::Full(full) => Either::Right(full.into_iter()),
        }
    }

    fn into_iter_true(self, _: SymbolInfo) -> impl SIterator<Item = DomainEnum> {
        match self {
            Self::Partial { certainly_true, .. } => Either::Left(certainly_true.into_iter()),
            Self::Full(full) => Either::Right(full.into_iter()),
        }
    }

    fn iter_false(&self, common: SymbolInfo) -> impl SIterator<Item = DomainEnum> {
        match self {
            Self::Partial {
                certainly_false, ..
            } => Either::Left(certainly_false.into_iter()),
            Self::Full(full) => Either::Right(NegatedIter::new(
                full.into_iter(),
                common.domain.iter_index(common.type_interps).len(),
            )),
        }
    }

    fn into_iter_false(self, common: SymbolInfo) -> impl SIterator<Item = DomainEnum> {
        match self {
            Self::Partial {
                certainly_false, ..
            } => Either::Left(certainly_false.into_iter()),
            Self::Full(full) => Either::Right(NegatedIter::new(
                full.into_iter(),
                common.domain.iter_index(common.type_interps).len(),
            )),
        }
    }

    fn split_ct_cf(self, _: SymbolInfo) -> Result<(Self::CompletePred, Self::CompletePred), Self> {
        match self {
            Self::Partial {
                certainly_true,
                certainly_false,
            } => Ok((certainly_true, certainly_false)),
            Self::Full(_) => Err(self),
        }
    }

    fn split_ct_cf_ref<'a>(
        &'a self,
        _: SymbolInfo,
    ) -> Option<(Self::CompletePredRef<'a>, Self::CompletePredRef<'a>)> {
        match self {
            Self::Partial {
                certainly_true,
                certainly_false,
            } => Some((certainly_true, certainly_false)),
            Self::Full(_) => None,
        }
    }
}

impl partial::MutFunc<bool> for PartialRoaring {
    type CompleteSymbolMut = RoaringBitmapCached;
    type CompleteSymbolMutRef<'a> = &'a mut RoaringBitmapCached;

    fn set(&mut self, common: SymbolInfo, domain_enum: DomainEnum, value: Option<bool>) {
        match self {
            Self::Partial {
                certainly_true,
                certainly_false,
            } => {
                if let Some(value) = value {
                    certainly_true.set(domain_enum, value);
                    certainly_false.set(domain_enum, !value);
                } else {
                    certainly_true.set(domain_enum, false);
                    certainly_false.set(domain_enum, false);
                }
                let range = common.domain.iter_index(common.type_interps);
                if (certainly_true.len() + certainly_false.len()) == range.len() {
                    let certainly_true = std::mem::take(certainly_true);
                    *self = Self::Full(certainly_true);
                }
            }
            Self::Full(val) => match value {
                Some(value) => val.set(domain_enum, value),
                None => {
                    let range = common.domain.iter_index(common.type_interps);
                    let mut certainly_true = std::mem::take(val);
                    let mut certainly_false = certainly_true.clone();
                    certainly_false.negate_over_range(range);
                    certainly_false.set(domain_enum, false);
                    certainly_true.set(domain_enum, false);
                    *self = Self::Partial {
                        certainly_true,
                        certainly_false,
                    };
                }
            },
        }
    }

    fn fill_unknown_with(&mut self, common: SymbolInfo, value: bool) {
        if value {
            match self {
                Self::Full(_) => return,
                Self::Partial {
                    certainly_true: _,
                    certainly_false,
                } => {
                    let full = common.domain.iter_index(common.type_interps);
                    // For filling with true we can't just use the certainly false set.
                    // Since then everything that is actually false will be interpreted as
                    // true and everything that is true will be interpreted as false.
                    // This is caused by that the full state assumes that a value in
                    // the set means that this value is true in the interpretation and vice versa.
                    // As such for filling with true we negate the set over the entire domain.
                    certainly_false.negate_over_range(full);
                    *self = Self::Full(std::mem::take(certainly_false));
                }
            }
        } else {
            let ct = match self {
                Self::Full(_) => return,
                Self::Partial { certainly_true, .. } => {
                    // When we want to fill all unknown values with false all we have to do is use
                    // the set of certainly trues as the set of the full state.
                    std::mem::take(certainly_true)
                }
            };
            *self = Self::Full(ct);
        }
    }

    fn try_as_mut_complete<'a>(
        &'a mut self,
        _: SymbolInfo,
    ) -> Result<Self::CompleteSymbolMutRef<'a>, ()> {
        match self {
            Self::Full(full) => Ok(full),
            Self::Partial { .. } => Err(()),
        }
    }

    fn try_into_mut_complete(self, _: SymbolInfo) -> Result<Self::CompleteSymbolMut, Self> {
        match self {
            Self::Full(full) => Ok(full),
            Self::Partial { .. } => Err(self),
        }
    }
}

pub struct PotPredIter<I>
where
    I: Iterator,
{
    ct: Peekable<I>,
    cf: Peekable<I>,
}

impl<I> Iterator for PotPredIter<I>
where
    I: Iterator<Item = DomainEnum>,
{
    type Item = (DomainEnum, bool);

    fn next(&mut self) -> Option<Self::Item> {
        let values = (self.ct.peek(), self.cf.peek());
        let (ct, cf) = match values {
            (Some(&ct), Some(&cf)) => (ct, cf),
            (Some(&ct), None) => {
                self.ct.next();
                return Some((ct, true));
            }
            (None, Some(&cf)) => {
                self.cf.next();
                return Some((cf, false));
            }
            (None, None) => return None,
        };
        match IndexRepr::from(ct).cmp(&IndexRepr::from(cf)) {
            Ordering::Equal => {
                self.ct.next();
                Some((ct, true))
            }
            Ordering::Less => {
                self.ct.next();
                Some((ct, true))
            }
            Ordering::Greater => {
                self.cf.next();
                Some((cf, false))
            }
        }
    }
}

pub type FuncMap = BTreeMap<DomainEnum, FuncElementUnion>;

impl<T: Clone> ToOwnedStore for BTreeMap<DomainEnum, T> {
    type Owned = Self;

    fn to_owned(&self, _common: SymbolInfo) -> Self::Owned {
        self.clone()
    }
}

impl<T: Copy + auto::Auto> partial::ImFunc<T> for BTreeMap<DomainEnum, T> {
    type CompleteSymbol = CompleteFunc<Self>;
    type CompleteSymbolRef<'a>
        = CompleteFunc<&'a Self>
    where
        T: 'a;

    fn get(&self, _: SymbolInfo, domain_enum: DomainEnum) -> Option<T> {
        self.get(&domain_enum).copied()
    }

    fn into_iter_partial(self, _: SymbolInfo) -> impl SIterator<Item = (DomainEnum, T)> {
        self.into_iter()
    }

    fn iter_partial(&self, _: SymbolInfo) -> impl SIterator<Item = (DomainEnum, T)> {
        self.into_iter().map(|(&dom, &val)| (dom, val))
    }

    fn try_as_im_complete<'a>(
        &'a self,
        common: SymbolInfo,
    ) -> Result<Self::CompleteSymbolRef<'a>, ()> {
        if partial::ImFunc::len_partial(self, common)
            == common.domain.domain_len(common.type_interps)
        {
            Ok(CompleteFunc(self))
        } else {
            Err(())
        }
    }

    fn try_into_im_complete(self, common: SymbolInfo) -> Result<Self::CompleteSymbol, Self> {
        if partial::ImFunc::len_partial(&self, common)
            == common.domain.domain_len(common.type_interps)
        {
            Ok(CompleteFunc(self))
        } else {
            Err(self)
        }
    }

    fn len_partial(&self, _: SymbolInfo) -> usize {
        self.len()
    }

    fn iter_unknown(&self, common: SymbolInfo) -> impl SIterator<Item = DomainEnum> {
        NegatedIter::new(
            self.keys().copied(),
            common.domain.domain_len(common.type_interps),
        )
    }

    fn into_iter_unknown(self, common: SymbolInfo) -> impl SIterator<Item = DomainEnum> {
        NegatedIter::new(
            self.into_keys(),
            common.domain.domain_len(common.type_interps),
        )
    }
}

impl<T: Copy + auto::Auto> partial::MutFunc<T> for BTreeMap<DomainEnum, T> {
    type CompleteSymbolMut = CompleteFunc<Self>;
    type CompleteSymbolMutRef<'a>
        = CompleteFunc<&'a mut Self>
    where
        T: 'a;

    fn set(&mut self, _: SymbolInfo, domain_enum: DomainEnum, value: Option<T>) {
        if let Some(value) = value {
            self.insert(domain_enum, value);
        } else {
            self.remove(&domain_enum);
        }
    }

    fn fill_unknown_with(&mut self, common: SymbolInfo, value: T) {
        for dom in common.domain.iter_index(common.type_interps) {
            self.entry(dom).or_insert(value);
        }
    }

    fn try_as_mut_complete<'a>(
        &'a mut self,
        common: SymbolInfo,
    ) -> Result<Self::CompleteSymbolMutRef<'a>, ()> {
        if partial::ImFunc::len_partial(&self, common)
            == common.domain.domain_len(common.type_interps)
        {
            Ok(CompleteFunc(self))
        } else {
            Err(())
        }
    }

    fn try_into_mut_complete(self, common: SymbolInfo) -> Result<Self::CompleteSymbolMut, Self> {
        if partial::ImFunc::len_partial(&self, common)
            == common.domain.domain_len(common.type_interps)
        {
            Ok(CompleteFunc(self))
        } else {
            Err(self)
        }
    }
}

pub type RealFuncMap = BTreeMap<DomainEnum, Real>;

#[derive(Debug, Clone)]
pub struct RoaringStore {
    props: IdHashMap<PfuncIndex, Option<bool>>,
    consts: IdHashMap<PfuncIndex, COption<FuncElementUnion>>,
    real_consts: IdHashMap<PfuncIndex, Option<Real>>,
    preds: IdHashMap<PfuncIndex, PartialRoaring>,
    real_funcs: IdHashMap<PfuncIndex, RealFuncMap>,
    funcs: IdHashMap<PfuncIndex, FuncMap>,
}

impl Default for RoaringStore {
    fn default() -> Self {
        Self {
            props: Default::default(),
            consts: Default::default(),
            real_consts: Default::default(),
            preds: Default::default(),
            real_funcs: Default::default(),
            funcs: Default::default(),
        }
    }
}

impl partial::ImViews for RoaringStore {
    type PropView<'a> = PartialRef<'a, Option<bool>>;
    type IntConstView<'a> = PartialRef<'a, COption<Int>>;
    type RealConstView<'a> = PartialRef<'a, Option<Real>>;
    type IntTypeConstView<'a> = PartialRef<'a, COption<Int>>;
    type RealTypeConstView<'a> = PartialRef<'a, Option<Real>>;
    type StrConstView<'a> = PartialRef<'a, COption<TypeEnum>>;

    type PredView<'a> = PartialRef<'a, PartialRoaring>;
    type IntFuncView<'a> = FuncElementWrapper<Int, PartialRef<'a, FuncMap>>;
    type RealFuncView<'a> = PartialRef<'a, RealFuncMap>;
    type IntTypeFuncView<'a> = FuncElementWrapper<Int, PartialRef<'a, FuncMap>>;
    type RealTypeFuncView<'a> = PartialRef<'a, RealFuncMap>;
    type StrFuncView<'a> = FuncElementWrapper<TypeEnum, PartialRef<'a, FuncMap>>;

    fn get_prop<'a>(&'a self, index: PropIndex, _: SymbolInfo) -> Self::PropView<'a> {
        PartialRef(self.props.get(&index.index()))
    }

    #[duplicate_item(
        name index_ty ty;
        [get_int_const] [IntConstIndex] [Self::IntConstView];
        [get_int_type_const] [IntTypeConstIndex] [Self::IntTypeConstView];
        [get_str_const] [StrConstIndex] [Self::StrConstView];
    )]
    fn name<'a>(&'a self, index: index_ty, _: SymbolInfo) -> ty<'a> {
        let value = self.consts.get(&index.index());
        // This is safe since COption has a known layout, and `FuncElementUnion` and everything
        // else have the exact same size and all bit patterns in both types are allowed.
        PartialRef(unsafe {
            core::mem::transmute::<Option<&COption<FuncElementUnion>>, Option<&COption<_>>>(value)
        })
    }

    #[duplicate_item(
        name index_ty ty;
        [get_real_const] [RealConstIndex] [Self::RealConstView];
        [get_real_type_const] [RealTypeConstIndex] [Self::RealTypeConstView];
    )]
    fn name<'a>(&'a self, index: index_ty, _: SymbolInfo) -> ty<'a> {
        PartialRef(self.real_consts.get(&index.index()))
    }

    fn get_pred<'a>(&'a self, index: PredIndex, _: SymbolInfo) -> Self::PredView<'a> {
        PartialRef(self.preds.get(&index.index()))
    }

    #[duplicate_item(
        name index_ty ty;
        [get_int_func] [IntFuncIndex] [Self::IntFuncView];
        [get_int_type_func] [IntTypeFuncIndex] [Self::IntTypeFuncView];
        [get_str_func] [StrFuncIndex] [Self::StrFuncView];
    )]
    fn name<'a>(&'a self, index: index_ty, _: SymbolInfo) -> ty<'a> {
        FuncElementWrapper::new(PartialRef(self.funcs.get(&index.index())))
    }

    #[duplicate_item(
        name index_ty ty;
        [get_real_func] [RealFuncIndex] [Self::RealFuncView];
        [get_real_type_func] [RealTypeFuncIndex] [Self::RealTypeFuncView];
    )]
    fn name<'a>(&'a self, index: index_ty, _: SymbolInfo) -> ty<'a> {
        PartialRef(self.real_funcs.get(&index.index()))
    }
}

impl partial::MutViews for RoaringStore {
    type PropView<'a> = &'a mut Option<bool>;
    type IntConstView<'a> = &'a mut COption<Int>;
    type RealConstView<'a> = &'a mut Option<Real>;
    type IntTypeConstView<'a> = &'a mut COption<Int>;
    type RealTypeConstView<'a> = &'a mut Option<Real>;
    type StrConstView<'a> = &'a mut COption<TypeEnum>;

    type PredView<'a> = &'a mut PartialRoaring;
    type IntFuncView<'a> = FuncElementWrapper<Int, &'a mut FuncMap>;
    type RealFuncView<'a> = &'a mut RealFuncMap;
    type IntTypeFuncView<'a> = FuncElementWrapper<Int, &'a mut FuncMap>;
    type RealTypeFuncView<'a> = &'a mut RealFuncMap;
    type StrFuncView<'a> = FuncElementWrapper<TypeEnum, &'a mut FuncMap>;

    fn get_prop<'a>(&'a mut self, index: PropIndex, _: SymbolInfo) -> Self::PropView<'a> {
        self.props.entry(index.index()).or_default()
    }

    #[duplicate_item(
        name index_ty ty;
        [get_int_const] [IntConstIndex] [Self::IntConstView];
        [get_int_type_const] [IntTypeConstIndex] [Self::IntTypeConstView];
        [get_str_const] [StrConstIndex] [Self::StrConstView];
    )]
    fn name<'a>(&'a mut self, index: index_ty, _: SymbolInfo) -> ty<'a> {
        let func_el = self.consts.entry(index.index()).or_default();
        // This is safe since COption has a known layout, and `FuncElementUnion` and everything
        // else have the exact same size and all bit patterns in both types are allowed.
        unsafe {
            core::mem::transmute::<&'a mut COption<FuncElementUnion>, &'a mut COption<_>>(func_el)
        }
    }

    #[duplicate_item(
        name index_ty ty;
        [get_real_const] [RealConstIndex] [Self::RealConstView];
        [get_real_type_const] [RealTypeConstIndex] [Self::RealTypeConstView];
    )]
    fn name<'a>(&'a mut self, index: index_ty, _: SymbolInfo) -> ty<'a> {
        self.real_consts.entry(index.index()).or_default()
    }

    fn get_pred<'a>(&'a mut self, index: PredIndex, _: SymbolInfo) -> Self::PredView<'a> {
        self.preds.entry(index.index()).or_default()
    }

    #[duplicate_item(
        name index_ty ty;
        [get_int_func] [IntFuncIndex] [Self::IntFuncView];
        [get_int_type_func] [IntTypeFuncIndex] [Self::IntTypeFuncView];
        [get_str_func] [StrFuncIndex] [Self::StrFuncView];
    )]
    fn name<'a>(&'a mut self, index: index_ty, _: SymbolInfo) -> ty<'a> {
        FuncElementWrapper::new(self.funcs.entry(index.index()).or_default())
    }

    #[duplicate_item(
        name index_ty ty;
        [get_real_func] [RealFuncIndex] [Self::RealFuncView];
        [get_real_type_func] [RealTypeFuncIndex] [Self::RealTypeFuncView];
    )]
    fn name<'a>(&'a mut self, index: index_ty, _: SymbolInfo) -> ty<'a> {
        self.real_funcs.entry(index.index()).or_default()
    }

    #[duplicate_item(
        name index_ty;
        [reinit_int_type_const] [IntTypeConstIndex];
        [reinit_str_const] [StrConstIndex];
    )]
    fn name(&mut self, index: index_ty) {
        self.consts.remove(&index.index());
    }

    fn reinit_real_type_const(&mut self, index: RealTypeConstIndex) {
        self.real_consts.remove(&index.index());
    }

    fn reinit_pred(&mut self, index: PredIndex) {
        self.preds.remove(&index.index());
    }

    #[duplicate_item(
        name index_ty;
        [reinit_int_func] [IntFuncIndex];
        [reinit_int_type_func] [IntTypeFuncIndex];
        [reinit_str_func] [StrFuncIndex];
    )]
    fn name(&mut self, index: index_ty) {
        self.funcs.remove(&index.index());
    }

    #[duplicate_item(
        name index_ty;
        [reinit_real_func] [RealFuncIndex];
        [reinit_real_type_func] [RealTypeFuncIndex];
    )]
    fn name(&mut self, index: index_ty) {
        self.real_funcs.remove(&index.index());
    }
}

impl partial::SetInterps for RoaringStore {
    fn set_prop<'a>(
        &'a mut self,
        index: PropIndex,
        interp: <Self::PropView<'static> as ToOwnedStore>::Owned,
    ) {
        if interp.is_some() {
            self.props.insert(index.index(), interp);
        }
    }

    #[duplicate_item(
        name index_ty ty;
        [set_int_const] [IntConstIndex] [Self::IntConstView];
        [set_int_type_const] [IntTypeConstIndex] [Self::IntTypeConstView];
        [set_str_const] [StrConstIndex] [Self::StrConstView];
    )]
    fn name<'a>(&'a mut self, index: index_ty, interp: <ty<'static> as ToOwnedStore>::Owned) {
        // This is safe since COption has a known layout, and `FuncElementUnion` and everything
        // else have the exact same size and all bit patterns in both types are allowed.
        let transmuted =
            unsafe { core::mem::transmute::<COption<_>, COption<FuncElementUnion>>(interp) };
        if transmuted.is_some() {
            self.consts.insert(index.index(), transmuted);
        }
    }

    #[duplicate_item(
        name index_ty ty;
        [set_real_const] [RealConstIndex] [Self::RealConstView];
        [set_real_type_const] [RealTypeConstIndex] [Self::RealTypeConstView];
    )]
    fn name<'a>(&'a mut self, index: index_ty, interp: <ty<'static> as ToOwnedStore>::Owned) {
        if interp.is_some() {
            self.real_consts.insert(index.index(), interp);
        }
    }

    fn set_pred<'a>(
        &'a mut self,
        index: PredIndex,
        interp: <Self::PredView<'static> as ToOwnedStore>::Owned,
    ) {
        self.preds.insert(index.index(), interp);
    }

    #[duplicate_item(
        name index_ty ty;
        [set_int_func] [IntFuncIndex] [Self::IntFuncView];
        [set_int_type_func] [IntTypeFuncIndex] [Self::IntTypeFuncView];
        [set_str_func] [StrFuncIndex] [Self::StrFuncView];
    )]
    fn name<'a>(&'a mut self, index: index_ty, interp: <ty<'static> as ToOwnedStore>::Owned) {
        if interp.len() != 0 {
            self.funcs.insert(index.index(), interp.0);
        }
    }

    #[duplicate_item(
        name index_ty ty;
        [set_real_func] [RealFuncIndex] [Self::RealFuncView];
        [set_real_type_func] [RealTypeFuncIndex] [Self::RealTypeFuncView];
    )]
    fn name<'a>(&'a mut self, index: index_ty, interp: <ty<'static> as ToOwnedStore>::Owned) {
        if interp.len() != 0 {
            self.real_funcs.insert(index.index(), interp);
        }
    }
}
