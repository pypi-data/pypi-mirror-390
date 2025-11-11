mod roaring;
use super::traits::{
    SymbolInfo, ToOwnedStore,
    complete::{self, MutNullary},
    partial,
};
use crate::{
    IndexRange, IndexRepr, Int, Real,
    vocabulary::{DomainEnum, TypeEnum},
};
use duplicate::duplicate_item;
use itertools::Either;
use sli_collections::iterator::Iterator as SIterator;
use std::{
    fmt::Debug,
    iter::Peekable,
    marker::PhantomData,
    mem::transmute,
    ops::{Deref, DerefMut},
};
// TODO: escape hatch for now
pub use roaring::PartialRoaring;

pub type Backend = roaring::RoaringStore;

pub mod partial_interp {
    use super::*;
    pub mod owned {
        use super::*;
        pub type Prop = <mutable_view::Prop<'static> as ToOwnedStore>::Owned;
        pub type IntConst = <mutable_view::IntConst<'static> as ToOwnedStore>::Owned;
        pub type RealConst = <mutable_view::RealConst<'static> as ToOwnedStore>::Owned;
        pub type IntTypeConst = <mutable_view::IntTypeConst<'static> as ToOwnedStore>::Owned;
        pub type RealTypeConst = <mutable_view::RealTypeConst<'static> as ToOwnedStore>::Owned;
        pub type StrConst = <mutable_view::StrConst<'static> as ToOwnedStore>::Owned;

        pub type Pred = <mutable_view::Pred<'static> as ToOwnedStore>::Owned;
        pub type IntFunc = <mutable_view::IntFunc<'static> as ToOwnedStore>::Owned;
        pub type RealFunc = <mutable_view::RealFunc<'static> as ToOwnedStore>::Owned;
        pub type IntTypeFunc = <mutable_view::IntTypeFunc<'static> as ToOwnedStore>::Owned;
        pub type RealTypeFunc = <mutable_view::RealTypeFunc<'static> as ToOwnedStore>::Owned;
        pub type StrFunc = <mutable_view::StrFunc<'static> as ToOwnedStore>::Owned;
    }

    pub mod immutable_view {
        use super::*;
        pub type Prop<'a> = <Backend as partial::ImViews>::PropView<'a>;
        pub type IntConst<'a> = <Backend as partial::ImViews>::IntConstView<'a>;
        pub type RealConst<'a> = <Backend as partial::ImViews>::RealConstView<'a>;
        pub type IntTypeConst<'a> = <Backend as partial::ImViews>::IntTypeConstView<'a>;
        pub type RealTypeConst<'a> = <Backend as partial::ImViews>::RealTypeConstView<'a>;
        pub type StrConst<'a> = <Backend as partial::ImViews>::StrConstView<'a>;

        pub type Pred<'a> = <Backend as partial::ImViews>::PredView<'a>;
        pub type IntFunc<'a> = <Backend as partial::ImViews>::IntFuncView<'a>;
        pub type RealFunc<'a> = <Backend as partial::ImViews>::RealFuncView<'a>;
        pub type IntTypeFunc<'a> = <Backend as partial::ImViews>::IntTypeFuncView<'a>;
        pub type RealTypeFunc<'a> = <Backend as partial::ImViews>::RealTypeFuncView<'a>;
        pub type StrFunc<'a> = <Backend as partial::ImViews>::StrFuncView<'a>;
    }

    pub mod mutable_view {
        use super::*;
        pub type Prop<'a> = <Backend as partial::MutViews>::PropView<'a>;
        pub type IntConst<'a> = <Backend as partial::MutViews>::IntConstView<'a>;
        pub type RealConst<'a> = <Backend as partial::MutViews>::RealConstView<'a>;
        pub type IntTypeConst<'a> = <Backend as partial::MutViews>::IntTypeConstView<'a>;
        pub type RealTypeConst<'a> = <Backend as partial::MutViews>::RealTypeConstView<'a>;
        pub type StrConst<'a> = <Backend as partial::MutViews>::StrConstView<'a>;

        pub type Pred<'a> = <Backend as partial::MutViews>::PredView<'a>;
        pub type IntFunc<'a> = <Backend as partial::MutViews>::IntFuncView<'a>;
        pub type RealFunc<'a> = <Backend as partial::MutViews>::RealFuncView<'a>;
        pub type IntTypeFunc<'a> = <Backend as partial::MutViews>::IntTypeFuncView<'a>;
        pub type RealTypeFunc<'a> = <Backend as partial::MutViews>::RealTypeFuncView<'a>;
        pub type StrFunc<'a> = <Backend as partial::MutViews>::StrFuncView<'a>;
    }
}

pub mod complete_interp {
    use super::*;
    pub mod owned {
        use super::*;
        pub type Prop = <partial_interp::owned::Prop as partial::ImNullary<bool>>::CompleteSymbol;
        pub type IntConst =
            <partial_interp::owned::IntConst as partial::ImNullary<Int>>::CompleteSymbol;
        pub type RealConst =
            <partial_interp::owned::RealConst as partial::ImNullary<Real>>::CompleteSymbol;
        pub type IntTypeConst =
            <partial_interp::owned::IntTypeConst as partial::ImNullary<Int>>::CompleteSymbol;
        pub type RealTypeConst =
            <partial_interp::owned::RealTypeConst as partial::ImNullary<Real>>::CompleteSymbol;
        pub type StrConst =
            <partial_interp::owned::StrConst as partial::ImNullary<TypeEnum>>::CompleteSymbol;

        pub type Pred = <partial_interp::owned::Pred as partial::ImFunc<bool>>::CompleteSymbol;
        pub type IntFunc = <partial_interp::owned::IntFunc as partial::ImFunc<Int>>::CompleteSymbol;
        pub type RealFunc =
            <partial_interp::owned::RealFunc as partial::ImFunc<Real>>::CompleteSymbol;
        pub type IntTypeFunc =
            <partial_interp::owned::IntTypeFunc as partial::ImFunc<Int>>::CompleteSymbol;
        pub type RealTypeFunc =
            <partial_interp::owned::RealTypeFunc as partial::ImFunc<Real>>::CompleteSymbol;
        pub type StrFunc =
            <partial_interp::owned::StrFunc as partial::ImFunc<TypeEnum>>::CompleteSymbol;
    }

    pub mod immutable_view {
        use super::*;
        pub type Prop<'a> = <partial_interp::immutable_view::Prop<'a> as partial::ImNullary<
            bool,
        >>::CompleteSymbolRef<'a>;
        pub type IntConst<'a> = <
                partial_interp::immutable_view::IntConst<'a> as partial::ImNullary<Int>
            >::CompleteSymbolRef<'a>;
        pub type RealConst<'a> = <
                partial_interp::immutable_view::RealConst<'a> as partial::ImNullary<Real>
            >::CompleteSymbolRef<'a>;
        pub type IntTypeConst<'a> = <
                partial_interp::immutable_view::IntTypeConst<'a> as partial::ImNullary<Int>
            >::CompleteSymbolRef<'a>;
        pub type RealTypeConst<'a> = <
                partial_interp::immutable_view::RealTypeConst<'a> as partial::ImNullary<Real>
            >::CompleteSymbolRef<'a>;
        pub type StrConst<'a> = <
                partial_interp::immutable_view::StrConst<'a> as partial::ImNullary<TypeEnum>
            >::CompleteSymbolRef<'a>;

        pub type Pred<'a> =
            <partial_interp::immutable_view::Pred<'a> as partial::ImFunc<bool>>::CompleteSymbolRef<
                'a,
            >;
        pub type IntFunc<'a> = <partial_interp::immutable_view::IntFunc<'a> as partial::ImFunc<
            Int,
        >>::CompleteSymbolRef<'a>;
        pub type RealFunc<'a> = <partial_interp::immutable_view::RealFunc<'a> as partial::ImFunc<
            Real,
        >>::CompleteSymbolRef<'a>;
        pub type IntTypeFunc<'a> = <
                partial_interp::immutable_view::IntTypeFunc<'a> as partial::ImFunc<Int>
            >::CompleteSymbolRef<'a>;
        pub type RealTypeFunc<'a> = <
                partial_interp::immutable_view::RealTypeFunc<'a> as partial::ImFunc<Real>
            >::CompleteSymbolRef<'a>;
        pub type StrFunc<'a> = <partial_interp::immutable_view::StrFunc<'a> as partial::ImFunc<
            TypeEnum,
        >>::CompleteSymbolRef<'a>;
    }

    pub mod mutable_view {
        use super::*;
        pub type Prop<'a> = <
                partial_interp::mutable_view::Prop<'a> as partial::MutNullary<bool>
            >::CompleteSymbolMutRef<'a>;
        pub type IntConst<'a> = <
                partial_interp::mutable_view::IntConst<'a> as partial::MutNullary<Int>
            >::CompleteSymbolMutRef<'a>;
        pub type RealConst<'a> = <
                partial_interp::mutable_view::RealConst<'a> as partial::MutNullary<Real>
            >::CompleteSymbolMutRef<'a>;
        pub type IntTypeConst<'a> = <
                partial_interp::mutable_view::IntTypeConst<'a> as partial::MutNullary<Int>
            >::CompleteSymbolMutRef<'a>;
        pub type RealTypeConst<'a> = <
                partial_interp::mutable_view::RealTypeConst<'a> as partial::MutNullary<Real>
            >::CompleteSymbolMutRef<'a>;
        pub type StrConst<'a> = <
                partial_interp::mutable_view::StrConst<'a> as partial::MutNullary<TypeEnum>
            >::CompleteSymbolMutRef<'a>;

        pub type Pred<'a> = <
                partial_interp::mutable_view::Pred<'a> as partial::MutFunc<bool>
            >::CompleteSymbolMutRef<'a>;
        pub type IntFunc<'a> = <partial_interp::mutable_view::IntFunc<'a> as partial::MutFunc<
            Int,
        >>::CompleteSymbolMutRef<'a>;
        pub type RealFunc<'a> = <partial_interp::mutable_view::RealFunc<'a> as partial::MutFunc<
            Real,
        >>::CompleteSymbolMutRef<'a>;
        pub type IntTypeFunc<'a> = <
                partial_interp::mutable_view::IntTypeFunc<'a> as partial::MutFunc<Int>
            >::CompleteSymbolMutRef<'a>;
        pub type RealTypeFunc<'a> = <
                partial_interp::mutable_view::RealTypeFunc<'a> as partial::MutFunc<Real>
            >::CompleteSymbolMutRef<'a>;
        pub type StrFunc<'a> = <partial_interp::mutable_view::StrFunc<'a> as partial::MutFunc<
            TypeEnum,
        >>::CompleteSymbolMutRef<'a>;
    }
}

pub mod indexes {
    use crate::comp_core::vocabulary::PfuncIndex;

    pub struct PropIndex(pub(in crate::comp_core::structure) PfuncIndex);
    pub struct IntConstIndex(pub(in crate::comp_core::structure) PfuncIndex);
    pub struct RealConstIndex(pub(in crate::comp_core::structure) PfuncIndex);
    pub struct IntTypeConstIndex(pub(in crate::comp_core::structure) PfuncIndex);
    pub struct RealTypeConstIndex(pub(in crate::comp_core::structure) PfuncIndex);
    pub struct StrConstIndex(pub(in crate::comp_core::structure) PfuncIndex);

    pub struct PredIndex(pub(crate) PfuncIndex);
    pub struct IntFuncIndex(pub(in crate::comp_core::structure) PfuncIndex);
    pub struct RealFuncIndex(pub(in crate::comp_core::structure) PfuncIndex);
    pub struct IntTypeFuncIndex(pub(in crate::comp_core::structure) PfuncIndex);
    pub struct RealTypeFuncIndex(pub(in crate::comp_core::structure) PfuncIndex);
    pub struct StrFuncIndex(pub(in crate::comp_core::structure) PfuncIndex);

    #[duplicate::duplicate_item(
        name;
        [PropIndex];
        [IntConstIndex];
        [RealConstIndex];
        [IntTypeConstIndex];
        [RealTypeConstIndex];
        [StrConstIndex];
        [PredIndex];
        [IntFuncIndex];
        [RealFuncIndex];
        [IntTypeFuncIndex];
        [RealTypeFuncIndex];
        [StrFuncIndex];
    )]
    impl name {
        pub fn index(&self) -> PfuncIndex {
            self.0
        }
    }
}

#[duplicate_item(
    primitive;
    [bool];
    [Int];
    [Real];
    [TypeEnum];
    [FuncElementUnion];
)]
mod complete_primitive_nullary_impl {
    #![doc(hidden)]
    use super::*;
    impl complete::ImNullary<primitive> for primitive {
        fn get(&self, _: SymbolInfo) -> primitive {
            *self
        }
    }

    impl complete::MutNullary<primitive> for primitive {
        fn set(&mut self, _: SymbolInfo, value: primitive) {
            *self = value
        }
    }
}

#[duplicate_item(
    primitive;
    [bool];
    [Int];
    [Real];
    [TypeEnum];
    [FuncElementUnion];
)]
mod partial_primitive_nullary_impl {
    #![doc(hidden)]
    use super::*;
    impl partial::ImNullary<primitive> for Option<primitive> {
        type CompleteSymbol = primitive;
        type CompleteSymbolRef<'a> = &'a primitive;

        fn get(&self, _: SymbolInfo) -> Option<primitive> {
            *self
        }

        fn try_as_im_complete<'a>(
            &'a self,
            _: SymbolInfo,
        ) -> Result<Self::CompleteSymbolRef<'a>, ()> {
            self.as_ref().ok_or(())
        }

        fn try_into_im_complete(self, _: SymbolInfo) -> Result<Self::CompleteSymbol, Self> {
            self.ok_or(self)
        }
    }

    impl partial::MutNullary<primitive> for Option<primitive> {
        type CompleteSymbolMut = primitive;
        type CompleteSymbolMutRef<'a> = &'a mut primitive;

        fn set(&mut self, _: SymbolInfo, value: Option<primitive>) {
            *self = value;
        }

        fn try_into_mut_complete(self, _: SymbolInfo) -> Result<Self::CompleteSymbolMut, Self> {
            match self {
                Some(value) => Ok(value),
                None => Err(self),
            }
        }

        fn try_as_mut_complete<'a>(
            &'a mut self,
            _: SymbolInfo,
        ) -> Result<Self::CompleteSymbolMutRef<'a>, ()> {
            match self {
                Some(value) => Ok(value),
                None => Err(()),
            }
        }
    }

    impl partial::ImNullary<primitive> for COption<primitive> {
        type CompleteSymbol = primitive;
        type CompleteSymbolRef<'a> = &'a primitive;

        fn get(&self, _: SymbolInfo) -> Option<primitive> {
            (*self).into()
        }

        fn try_as_im_complete<'a>(
            &'a self,
            _: SymbolInfo,
        ) -> Result<Self::CompleteSymbolRef<'a>, ()> {
            self.as_ref().ok_or(())
        }

        fn try_into_im_complete(self, _: SymbolInfo) -> Result<Self::CompleteSymbol, Self> {
            self.ok_or(self)
        }
    }

    impl partial::MutNullary<primitive> for COption<primitive> {
        type CompleteSymbolMut = primitive;
        type CompleteSymbolMutRef<'a> = &'a mut primitive;

        fn set(&mut self, _: SymbolInfo, value: Option<primitive>) {
            *self = value.into();
        }

        fn try_into_mut_complete(self, _: SymbolInfo) -> Result<Self::CompleteSymbolMut, Self> {
            match self {
                COption::Some(value) => Ok(value),
                COption::None => Err(self),
            }
        }

        fn try_as_mut_complete<'a>(
            &'a mut self,
            _: SymbolInfo,
        ) -> Result<Self::CompleteSymbolMutRef<'a>, ()> {
            match self {
                COption::Some(value) => Ok(value),
                COption::None => Err(()),
            }
        }
    }
}

#[derive(Clone, Copy)]
pub union FuncElementUnion {
    pub int: Int,
    pub custom: TypeEnum,
}

impl Debug for FuncElementUnion {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("FuncElementUnion")
            .field("value", &unsafe {
                transmute::<FuncElementUnion, IndexRepr>(*self)
            })
            .finish()
    }
}

impl From<Int> for FuncElementUnion {
    fn from(value: Int) -> Self {
        FuncElementUnion { int: value }
    }
}

impl From<TypeEnum> for FuncElementUnion {
    fn from(value: TypeEnum) -> Self {
        FuncElementUnion { custom: value }
    }
}

impl From<FuncElementUnion> for Int {
    fn from(value: FuncElementUnion) -> Self {
        unsafe { value.int }
    }
}

impl<'a> From<&'a FuncElementUnion> for &'a Int {
    fn from(value: &'a FuncElementUnion) -> Self {
        unsafe { transmute(value) }
    }
}

impl<'a> From<&'a FuncElementUnion> for &'a Real {
    fn from(value: &'a FuncElementUnion) -> Self {
        unsafe { transmute(value) }
    }
}

impl<'a> From<&'a FuncElementUnion> for &'a TypeEnum {
    fn from(value: &'a FuncElementUnion) -> Self {
        unsafe { transmute(value) }
    }
}

impl From<FuncElementUnion> for TypeEnum {
    fn from(value: FuncElementUnion) -> Self {
        unsafe { value.custom }
    }
}

#[duplicate_item(
    name;
    [bool];
    [Int];
    [Real];
    [FuncElementUnion];
    [TypeEnum];
)]
mod primitive_impl {
    #![doc(hidden)]
    use super::*;
    impl ToOwnedStore for name {
        type Owned = name;

        fn to_owned(&self, _common: SymbolInfo) -> name {
            *self
        }
    }

    impl ToOwnedStore for Option<name> {
        type Owned = Option<name>;

        fn to_owned(&self, _common: SymbolInfo) -> Option<name> {
            *self
        }
    }

    impl<'a> ToOwnedStore for Option<&'a name> {
        type Owned = Option<name>;

        fn to_owned(&self, _common: SymbolInfo) -> Option<name> {
            self.copied()
        }
    }
}

#[repr(transparent)]
#[derive(Clone, Debug)]
pub struct CompleteFunc<T>(T);

impl<T> Deref for CompleteFunc<T> {
    type Target = T;
    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl<T> DerefMut for CompleteFunc<T> {
    fn deref_mut(&mut self) -> &mut Self::Target {
        &mut self.0
    }
}

impl<T> ToOwnedStore for CompleteFunc<T>
where
    T: ToOwnedStore,
{
    type Owned = CompleteFunc<<T as ToOwnedStore>::Owned>;

    fn to_owned(&self, common: SymbolInfo) -> Self::Owned {
        CompleteFunc(self.0.to_owned(common))
    }
}

impl<S, T> complete::ImFunc<S> for CompleteFunc<T>
where
    T: partial::ImFunc<S>,
    S: Copy,
{
    fn get(&self, common: SymbolInfo, domain_enum: DomainEnum) -> S {
        partial::ImFunc::get(&self.0, common, domain_enum).unwrap()
    }

    fn into_iter_complete(self, common: SymbolInfo) -> impl SIterator<Item = (DomainEnum, S)> {
        partial::ImFunc::into_iter_partial(self.0, common)
    }

    fn iter_complete(&self, common: SymbolInfo) -> impl SIterator<Item = (DomainEnum, S)> {
        partial::ImFunc::iter_partial(&self.0, common)
    }
}

impl<S, T> complete::MutFunc<S> for CompleteFunc<T>
where
    T: partial::MutFunc<S>,
    S: Copy,
{
    fn set(&mut self, common: SymbolInfo, domain_enum: DomainEnum, value: S) {
        partial::MutFunc::set(&mut self.0, common, domain_enum, Some(value));
    }
}

#[repr(transparent)]
#[derive(Clone, Debug)]
pub struct FuncElementWrapper<S, T>(T, PhantomData<S>);

impl<S, T> FuncElementWrapper<S, T> {
    pub fn new(value: T) -> Self {
        Self(value, PhantomData)
    }
}

impl<S, T> Deref for FuncElementWrapper<S, T> {
    type Target = T;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl<S, T> DerefMut for FuncElementWrapper<S, T> {
    fn deref_mut(&mut self) -> &mut Self::Target {
        &mut self.0
    }
}

impl<S, T> ToOwnedStore for FuncElementWrapper<S, T>
where
    T: ToOwnedStore,
{
    type Owned = FuncElementWrapper<S, T::Owned>;

    fn to_owned(&self, common: SymbolInfo) -> Self::Owned {
        FuncElementWrapper::new(self.0.to_owned(common))
    }
}

impl<S, T> complete::ImNullary<S> for FuncElementWrapper<S, T>
where
    S: Copy + core::convert::From<FuncElementUnion>,
    T: complete::ImNullary<FuncElementUnion>,
{
    fn get(&self, common: SymbolInfo) -> S {
        <T as complete::ImNullary<_>>::get(&self.0, common).into()
    }
}

impl<S, T> complete::MutNullary<S> for FuncElementWrapper<S, T>
where
    S: Copy + core::convert::From<FuncElementUnion>,
    T: complete::MutNullary<FuncElementUnion>,
    FuncElementUnion: core::convert::From<S>,
{
    fn set(&mut self, common: SymbolInfo, value: S) {
        <T as MutNullary<_>>::set(&mut self.0, common, value.into())
    }
}

impl<S, T> partial::ImNullary<S> for FuncElementWrapper<S, T>
where
    S: Copy + core::convert::From<FuncElementUnion>,
    T: partial::ImNullary<FuncElementUnion>,
{
    type CompleteSymbol = FuncElementWrapper<S, T::CompleteSymbol>;
    type CompleteSymbolRef<'a>
        = FuncElementWrapper<S, T::CompleteSymbolRef<'a>>
    where
        S: 'a,
        T: 'a;

    fn get(&self, common: SymbolInfo) -> Option<S> {
        <T as partial::ImNullary<_>>::get(&self.0, common).map(|f| f.into())
    }

    fn try_as_im_complete<'a>(
        &'a self,
        common: SymbolInfo,
    ) -> Result<Self::CompleteSymbolRef<'a>, ()> {
        <T as partial::ImNullary<_>>::try_as_im_complete(&self.0, common)
            .map(FuncElementWrapper::new)
    }

    fn try_into_im_complete(self, common: SymbolInfo) -> Result<Self::CompleteSymbol, Self> {
        <T as partial::ImNullary<_>>::try_into_im_complete(self.0, common)
            .map(FuncElementWrapper::new)
            .map_err(FuncElementWrapper::new)
    }
}

impl<S, T> partial::MutNullary<S> for FuncElementWrapper<S, T>
where
    S: Copy + core::convert::From<FuncElementUnion>,
    T: partial::MutNullary<FuncElementUnion>,
    FuncElementUnion: core::convert::From<S>,
{
    type CompleteSymbolMut = FuncElementWrapper<S, T::CompleteSymbolMut>;
    type CompleteSymbolMutRef<'a>
        = FuncElementWrapper<S, T::CompleteSymbolMutRef<'a>>
    where
        Self: 'a;

    fn set(&mut self, common: SymbolInfo, value: Option<S>) {
        <T as partial::MutNullary<_>>::set(&mut self.0, common, value.map(|f| f.into()))
    }

    fn try_as_mut_complete<'a>(
        &'a mut self,
        common: SymbolInfo,
    ) -> Result<Self::CompleteSymbolMutRef<'a>, ()> {
        <T as partial::MutNullary<_>>::try_as_mut_complete(&mut self.0, common)
            .map(FuncElementWrapper::new)
    }

    fn try_into_mut_complete(self, common: SymbolInfo) -> Result<Self::CompleteSymbolMut, Self> {
        <T as partial::MutNullary<_>>::try_into_mut_complete(self.0, common)
            .map(FuncElementWrapper::new)
            .map_err(FuncElementWrapper::new)
    }
}

impl<S, T> complete::ImFunc<S> for FuncElementWrapper<S, T>
where
    S: Copy + core::convert::From<FuncElementUnion>,
    T: complete::ImFunc<FuncElementUnion>,
{
    fn get(&self, common: SymbolInfo, domain_enum: DomainEnum) -> S {
        <T as complete::ImFunc<_>>::get(&self.0, common, domain_enum).into()
    }

    fn iter_complete(&self, common: SymbolInfo) -> impl SIterator<Item = (DomainEnum, S)> {
        <T as complete::ImFunc<_>>::iter_complete(&self.0, common)
            .map(|(dom, val)| (dom, val.into()))
    }

    fn into_iter_complete(self, common: SymbolInfo) -> impl SIterator<Item = (DomainEnum, S)> {
        <T as complete::ImFunc<_>>::into_iter_complete(self.0, common)
            .map(|(dom, val)| (dom, val.into()))
    }
}

impl<S, T> complete::MutFunc<S> for FuncElementWrapper<S, T>
where
    S: Copy + core::convert::From<FuncElementUnion>,
    T: complete::MutFunc<FuncElementUnion>,
    FuncElementUnion: core::convert::From<S>,
{
    fn set(&mut self, common: SymbolInfo, domain_enum: DomainEnum, value: S) {
        <T as complete::MutFunc<_>>::set(&mut self.0, common, domain_enum, value.into())
    }
}

impl<S, T> partial::ImFunc<S> for FuncElementWrapper<S, T>
where
    S: Copy + core::convert::From<FuncElementUnion>,
    T: partial::ImFunc<FuncElementUnion>,
{
    type CompleteSymbol = FuncElementWrapper<S, T::CompleteSymbol>;
    type CompleteSymbolRef<'a>
        = FuncElementWrapper<S, T::CompleteSymbolRef<'a>>
    where
        S: 'a,
        T: 'a;

    fn get(&self, common: SymbolInfo, domain_enum: DomainEnum) -> Option<S> {
        <T as partial::ImFunc<_>>::get(&self.0, common, domain_enum).map(S::from)
    }

    fn iter_partial(&self, common: SymbolInfo) -> impl SIterator<Item = (DomainEnum, S)> {
        <T as partial::ImFunc<_>>::iter_partial(&self.0, common).map(|(dom, val)| (dom, val.into()))
    }

    fn into_iter_partial(self, common: SymbolInfo) -> impl SIterator<Item = (DomainEnum, S)> {
        <T as partial::ImFunc<_>>::into_iter_partial(self.0, common)
            .map(|(dom, val)| (dom, val.into()))
    }

    fn try_as_im_complete<'a>(
        &'a self,
        common: SymbolInfo,
    ) -> Result<Self::CompleteSymbolRef<'a>, ()> {
        <T as partial::ImFunc<_>>::try_as_im_complete(&self.0, common).map(FuncElementWrapper::new)
    }

    fn try_into_im_complete(self, common: SymbolInfo) -> Result<Self::CompleteSymbol, Self> {
        <T as partial::ImFunc<_>>::try_into_im_complete(self.0, common)
            .map(FuncElementWrapper::new)
            .map_err(FuncElementWrapper::new)
    }

    fn len_partial(&self, common: SymbolInfo) -> usize {
        <T as partial::ImFunc<_>>::len_partial(&self.0, common)
    }

    fn iter_unknown(&self, common: SymbolInfo) -> impl SIterator<Item = DomainEnum> {
        <T as partial::ImFunc<_>>::iter_unknown(&self.0, common)
    }

    fn into_iter_unknown(self, common: SymbolInfo) -> impl SIterator<Item = DomainEnum> {
        <T as partial::ImFunc<_>>::into_iter_unknown(self.0, common)
    }
}

impl<S, T> partial::MutFunc<S> for FuncElementWrapper<S, T>
where
    S: Copy + core::convert::From<FuncElementUnion>,
    T: partial::MutFunc<FuncElementUnion>,
    FuncElementUnion: core::convert::From<S>,
{
    type CompleteSymbolMut = FuncElementWrapper<S, T::CompleteSymbolMut>;
    type CompleteSymbolMutRef<'a>
        = FuncElementWrapper<S, T::CompleteSymbolMutRef<'a>>
    where
        Self: 'a;

    fn set(&mut self, common: SymbolInfo, domain_enum: DomainEnum, value: Option<S>) {
        <T as partial::MutFunc<_>>::set(
            &mut self.0,
            common,
            domain_enum,
            value.map(FuncElementUnion::from),
        )
    }

    fn fill_unknown_with(&mut self, common: SymbolInfo, value: S) {
        <T as partial::MutFunc<_>>::fill_unknown_with(&mut self.0, common, value.into())
    }

    fn try_as_mut_complete<'a>(
        &'a mut self,
        common: SymbolInfo,
    ) -> Result<Self::CompleteSymbolMutRef<'a>, ()> {
        <T as partial::MutFunc<_>>::try_as_mut_complete(&mut self.0, common)
            .map(FuncElementWrapper::new)
    }

    fn try_into_mut_complete(self, common: SymbolInfo) -> Result<Self::CompleteSymbolMut, Self> {
        <T as partial::MutFunc<_>>::try_into_mut_complete(self.0, common)
            .map(FuncElementWrapper::new)
            .map_err(FuncElementWrapper::new)
    }
}

#[repr(transparent)]
#[derive(Debug, Clone)]
pub struct PartialRef<'a, T>(pub Option<&'a T>);

impl<'a, T> ToOwnedStore for PartialRef<'a, T>
where
    T: ToOwnedStore,
    <T as ToOwnedStore>::Owned: Default,
{
    type Owned = T::Owned;

    fn to_owned(&self, common: SymbolInfo) -> Self::Owned {
        match &self.0 {
            Some(value) => <T as ToOwnedStore>::to_owned(value, common),
            None => Default::default(),
        }
    }
}

impl<'a, S, T> partial::ImNullary<S> for PartialRef<'a, T>
where
    S: Copy,
    &'a T: partial::ImNullary<S>,
    <T as ToOwnedStore>::Owned: Default,
    T: ToOwnedStore,
{
    type CompleteSymbol = <&'a T as partial::ImNullary<S>>::CompleteSymbol;
    type CompleteSymbolRef<'b>
        = <&'a T as partial::ImNullary<S>>::CompleteSymbolRef<'b>
    where
        Self: 'b;

    fn get(&self, common: SymbolInfo) -> Option<S> {
        match &self.0 {
            Some(value) => <&'a T as partial::ImNullary<_>>::get(value, common),
            None => None,
        }
    }

    fn try_into_im_complete(self, common: SymbolInfo) -> Result<Self::CompleteSymbol, Self> {
        match self.0 {
            Some(value) => <&'a T as partial::ImNullary<_>>::try_into_im_complete(value, common)
                .map_err(|f| Self(Some(f))),
            None => Err(Self(None)),
        }
    }

    fn try_as_im_complete<'b>(
        &'b self,
        common: SymbolInfo,
    ) -> Result<Self::CompleteSymbolRef<'b>, ()> {
        match &self.0 {
            Some(value) => <&'a T as partial::ImNullary<_>>::try_as_im_complete(value, common),
            None => Err(()),
        }
    }
}

impl<'a, S, T> partial::ImFunc<S> for PartialRef<'a, T>
where
    S: Copy,
    &'a T: partial::ImFunc<S>,
    <T as ToOwnedStore>::Owned: Default,
    T: ToOwnedStore,
{
    type CompleteSymbol = <&'a T as partial::ImFunc<S>>::CompleteSymbol;
    type CompleteSymbolRef<'b>
        = <&'a T as partial::ImFunc<S>>::CompleteSymbolRef<'b>
    where
        Self: 'b;

    fn get(&self, common: SymbolInfo, domain_enum: DomainEnum) -> Option<S> {
        match &self.0 {
            Some(value) => <&T as partial::ImFunc<_>>::get(value, common, domain_enum),
            None => None,
        }
    }

    fn into_iter_partial(self, common: SymbolInfo) -> impl SIterator<Item = (DomainEnum, S)> {
        match self.0 {
            Some(value) => {
                Either::Left(<&T as partial::ImFunc<_>>::into_iter_partial(value, common))
            }
            None => Either::Right(core::iter::empty()),
        }
    }

    fn iter_partial(&self, common: SymbolInfo) -> impl SIterator<Item = (DomainEnum, S)> {
        match &self.0 {
            Some(value) => Either::Left(<&T as partial::ImFunc<_>>::iter_partial(value, common)),
            None => Either::Right(core::iter::empty()),
        }
    }

    fn try_into_im_complete(self, common: SymbolInfo) -> Result<Self::CompleteSymbol, Self> {
        match self.0 {
            Some(value) => <&T as partial::ImFunc<_>>::try_into_im_complete(value, common)
                .map_err(|f| PartialRef(Some(f))),
            None => Err(PartialRef(None)),
        }
    }

    fn try_as_im_complete<'b>(
        &'b self,
        common: SymbolInfo,
    ) -> Result<Self::CompleteSymbolRef<'b>, ()> {
        match &self.0 {
            Some(value) => <&T as partial::ImFunc<_>>::try_as_im_complete(value, common),
            None => Err(()),
        }
    }

    fn len_partial(&self, common: SymbolInfo) -> usize {
        match &self.0 {
            Some(value) => <&T as partial::ImFunc<_>>::len_partial(value, common),
            None => 0,
        }
    }

    fn iter_unknown(&self, common: SymbolInfo) -> impl SIterator<Item = DomainEnum> {
        match &self.0 {
            Some(value) => Either::Left(<&T as partial::ImFunc<_>>::iter_unknown(value, common)),
            None => Either::Right(common.domain.iter_index(common.type_interps)),
        }
    }

    fn into_iter_unknown(self, common: SymbolInfo) -> impl SIterator<Item = DomainEnum> {
        match self.0 {
            Some(value) => {
                Either::Left(<&T as partial::ImFunc<_>>::into_iter_unknown(value, common))
            }
            None => Either::Right(common.domain.iter_index(common.type_interps)),
        }
    }
}

impl<'a, T> partial::ImPred for PartialRef<'a, T>
where
    &'a T: partial::ImPred,
    <T as ToOwnedStore>::Owned: Default,
    T: ToOwnedStore,
{
    type CompletePred = <&'a T as partial::ImPred>::CompletePred;
    type CompletePredRef<'b>
        = <&'a T as partial::ImPred>::CompletePredRef<'b>
    where
        Self: 'b;

    fn try_as_im_complete<'b>(
        &'b self,
        common: SymbolInfo,
    ) -> Result<Self::CompletePredRef<'b>, ()> {
        match &self.0 {
            Some(value) => <&T as partial::ImPred>::try_as_im_complete(value, common),
            None => Err(()),
        }
    }

    fn try_into_im_complete(self, common: SymbolInfo) -> Result<Self::CompletePred, Self> {
        match self.0 {
            Some(value) => <&T as partial::ImPred>::try_into_im_complete(value, common)
                .map_err(|f| Self(Some(f))),
            None => Err(self),
        }
    }

    fn iter_true(&self, common: SymbolInfo) -> impl SIterator<Item = DomainEnum> {
        match &self.0 {
            Some(value) => Either::Left(<&T as partial::ImPred>::iter_true(value, common)),
            None => Either::Right(core::iter::empty()),
        }
    }

    fn into_iter_true(self, common: SymbolInfo) -> impl SIterator<Item = DomainEnum> {
        match self.0 {
            Some(value) => Either::Left(<&T as partial::ImPred>::into_iter_true(value, common)),
            None => Either::Right(core::iter::empty()),
        }
    }

    fn iter_false(&self, common: SymbolInfo) -> impl SIterator<Item = DomainEnum> {
        match &self.0 {
            Some(value) => Either::Left(<&T as partial::ImPred>::iter_false(value, common)),
            None => Either::Right(core::iter::empty()),
        }
    }

    fn into_iter_false(self, common: SymbolInfo) -> impl SIterator<Item = DomainEnum> {
        match self.0 {
            Some(value) => Either::Left(<&T as partial::ImPred>::into_iter_false(value, common)),
            None => Either::Right(core::iter::empty()),
        }
    }

    fn split_ct_cf(
        self,
        common: SymbolInfo,
    ) -> Result<(Self::CompletePred, Self::CompletePred), Self> {
        match self.0 {
            Some(value) => <&T as partial::ImPred>::split_ct_cf(value, common)
                .map_err(|value| Self(Some(value))),
            None => Err(self),
        }
    }

    fn split_ct_cf_ref<'b>(
        &'b self,
        common: SymbolInfo,
    ) -> Option<(Self::CompletePredRef<'b>, Self::CompletePredRef<'b>)> {
        match &self.0 {
            Some(value) => <&T as partial::ImPred>::split_ct_cf_ref(value, common),
            None => None,
        }
    }
}

/// An [Option] with a guarenteed layout.
///
/// This allows transmuting and other unsafe things to work.
#[repr(C)]
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum COption<V> {
    Some(V),
    None,
}

impl<V> From<Option<V>> for COption<V> {
    fn from(value: Option<V>) -> Self {
        match value {
            Some(value) => Self::Some(value),
            None => Self::None,
        }
    }
}

impl<V> Into<Option<V>> for COption<V> {
    fn into(self) -> Option<V> {
        match self {
            Self::Some(value) => Some(value),
            Self::None => None,
        }
    }
}

impl<V: Clone> ToOwnedStore for COption<V> {
    type Owned = COption<V>;

    fn to_owned(&self, _: SymbolInfo) -> Self::Owned {
        self.clone()
    }
}

impl<V> Default for COption<V> {
    fn default() -> Self {
        Self::None
    }
}

impl<V> COption<V> {
    pub fn as_ref(&self) -> COption<&V> {
        match self {
            Self::Some(val) => COption::Some(val),
            Self::None => COption::None,
        }
    }

    pub fn ok_or<T>(self, value: T) -> Result<V, T> {
        match self {
            Self::Some(val) => Ok(val),
            Self::None => Err(value),
        }
    }

    pub fn map<T, F: FnOnce(V) -> T>(self, func: F) -> COption<T> {
        match self {
            Self::Some(value) => COption::Some(func(value)),
            Self::None => COption::None,
        }
    }

    pub fn is_some(&self) -> bool {
        matches!(self, Self::Some(_))
    }

    pub fn is_none(&self) -> bool {
        matches!(self, Self::None)
    }
}

/// A immutable option (as far as `ImNullary` and `ImFunc` are concerned)
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum IOption<V> {
    Some(V),
    None,
}

pub struct CompleteIter<T>
where
    T: Iterator<Item = DomainEnum>,
{
    iter: Peekable<T>,
    domain_range: IndexRange<DomainEnum>,
}

impl<T> CompleteIter<T>
where
    T: Iterator<Item = DomainEnum>,
{
    pub fn new(iter: T, domain_range: IndexRange<DomainEnum>) -> Self {
        CompleteIter {
            iter: iter.peekable(),
            domain_range,
        }
    }
}

impl<T> Iterator for CompleteIter<T>
where
    T: Iterator<Item = DomainEnum>,
{
    type Item = (T::Item, bool);

    fn next(&mut self) -> Option<Self::Item> {
        match self.iter.peek() {
            Some(&val) => {
                debug_assert!(usize::from(val) < usize::from(self.domain_range.end));
                if val == self.domain_range.start {
                    _ = self.domain_range.next();
                    _ = self.iter.next();
                    Some((val, true))
                } else {
                    self.domain_range.next().map(|f| (f, false))
                }
            }
            None => self.domain_range.next().map(|f| (f, false)),
        }
    }
}

/// Negates the given iterator over the domain, the iterator must be sorted.
pub struct NegatedIter<T: SIterator> {
    iter: Peekable<T>,
    cur: usize,
    end: usize,
}

impl<T: SIterator<Item = DomainEnum>> NegatedIter<T> {
    pub fn new(iter: T, end: usize) -> Self {
        Self {
            iter: iter.peekable(),
            cur: 0,
            end,
        }
    }
}

impl<T: SIterator<Item = DomainEnum>> Iterator for NegatedIter<T> {
    type Item = DomainEnum;

    fn next(&mut self) -> Option<Self::Item> {
        match self.iter.peek() {
            Some(value) => {
                let mut cur = *value;
                loop {
                    if IndexRepr::try_from(cur).unwrap() == self.cur.try_into().unwrap() {
                        self.cur += 1;
                    } else {
                        break;
                    }
                    self.iter.next(); // remove current peak
                    let Some(&new_value) = self.iter.peek() else {
                        break;
                    };
                    cur = new_value;
                }
            }
            None => {}
        }
        if self.cur < self.end {
            let ret = self.cur;
            self.cur += 1;
            Some(ret.into())
        } else {
            None
        }
    }
}
