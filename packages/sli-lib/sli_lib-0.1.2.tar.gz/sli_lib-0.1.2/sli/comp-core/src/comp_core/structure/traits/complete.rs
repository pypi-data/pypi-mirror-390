use super::{DomainEnum, SymbolInfo, ToOwnedStore};
use duplicate::duplicate_item;
use sli_collections::iterator::Iterator;

pub trait ImNullary<S: Copy>: ToOwnedStore {
    fn get(&self, common: SymbolInfo) -> S;
}

pub trait MutNullary<S: Copy>: ImNullary<S> {
    fn set(&mut self, common: SymbolInfo, value: S);
}

pub trait ImFunc<S: Copy>: ToOwnedStore {
    fn get(&self, common: SymbolInfo, domain_enum: DomainEnum) -> S;
    fn iter_complete(&self, common: SymbolInfo) -> impl Iterator<Item = (DomainEnum, S)>;
    fn into_iter_complete(self, common: SymbolInfo) -> impl Iterator<Item = (DomainEnum, S)>;
}

pub trait MutFunc<S: Copy>: ImFunc<S> {
    fn set(&mut self, common: SymbolInfo, domain_enum: DomainEnum, value: S);
}

pub trait ImPred: ImFunc<bool> {
    fn iter_true(&self, common: SymbolInfo) -> impl Iterator<Item = DomainEnum>;
    fn into_iter_true(self, common: SymbolInfo) -> impl Iterator<Item = DomainEnum>;
}

pub trait Nullary<S: Copy>: ImNullary<S> + MutNullary<S> + Clone + ToOwnedStore {}

impl<T, S> Nullary<S> for T
where
    T: ImNullary<S> + MutNullary<S> + Clone + ToOwnedStore,
    S: Copy,
{
}

pub trait Func<S: Copy>: ImFunc<S> + MutFunc<S> + Clone + ToOwnedStore {}

impl<T, S> Func<S> for T
where
    T: ImFunc<S> + MutFunc<S> + Clone + ToOwnedStore,
    S: Copy,
{
}

#[duplicate_item(
    reference(type);
    [&'a type];
    [&'a mut type];
)]
impl<'a, S, T> ImNullary<S> for reference([T])
where
    S: Copy,
    T: ImNullary<S>,
{
    fn get(&self, common: SymbolInfo) -> S {
        <T as ImNullary<S>>::get(self, common)
    }
}

impl<'a, S, T> MutNullary<S> for &'a mut T
where
    S: Copy,
    T: MutNullary<S>,
{
    fn set(&mut self, common: SymbolInfo, value: S) {
        <T as MutNullary<S>>::set(self, common, value)
    }
}

#[duplicate_item(
    reference(type);
    [&'a type];
    [&'a mut type];
)]
impl<'a, S, T> ImFunc<S> for reference([T])
where
    S: Copy,
    T: ImFunc<S>,
{
    fn get(&self, common: SymbolInfo, domain_enum: DomainEnum) -> S {
        <T as ImFunc<S>>::get(self, common, domain_enum)
    }

    fn iter_complete(&self, common: SymbolInfo) -> impl Iterator<Item = (DomainEnum, S)> {
        <T as ImFunc<S>>::iter_complete(self, common)
    }

    fn into_iter_complete(self, common: SymbolInfo) -> impl Iterator<Item = (DomainEnum, S)> {
        <T as ImFunc<S>>::iter_complete(self, common)
    }
}

#[duplicate_item(
    reference(type);
    [&'a type];
    [&'a mut type];
)]
impl<'a, T> ImPred for reference([T])
where
    T: ImPred,
{
    fn iter_true(&self, common: SymbolInfo) -> impl Iterator<Item = DomainEnum> {
        <T as ImPred>::iter_true(self, common)
    }

    fn into_iter_true(self, common: SymbolInfo) -> impl Iterator<Item = DomainEnum> {
        <T as ImPred>::iter_true(self, common)
    }
}

impl<'a, S, T> MutFunc<S> for &'a mut T
where
    S: Copy,
    T: MutFunc<S>,
{
    fn set(&mut self, common: SymbolInfo, domain_enum: DomainEnum, value: S) {
        <T as MutFunc<S>>::set(self, common, domain_enum, value)
    }
}
