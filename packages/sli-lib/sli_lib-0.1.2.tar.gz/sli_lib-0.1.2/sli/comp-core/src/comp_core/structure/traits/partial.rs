use super::{DomainEnum, SymbolInfo, ToOwnedStore, complete};
use crate::{
    Int, Real,
    structure::backend::indexes::*,
    vocabulary::{PfuncIndex, TypeEnum, Vocabulary},
};
use duplicate::duplicate_item;
use sli_collections::iterator::Iterator;

/// Immutable store methods for partially interpreted constants
pub trait ImNullary<S: Copy>: ToOwnedStore + Sized {
    type CompleteSymbol: complete::ImNullary<S>;
    type CompleteSymbolRef<'a>: complete::ImNullary<S>
    where
        Self: 'a;
    /// Partial store get method
    fn get(&self, common: SymbolInfo) -> Option<S>;
    fn try_into_im_complete(self, common: SymbolInfo) -> Result<Self::CompleteSymbol, Self>;
    fn try_as_im_complete<'a>(
        &'a self,
        common: SymbolInfo,
    ) -> Result<Self::CompleteSymbolRef<'a>, ()>;
}

/// Mutable store methods for partially interpreted constants
pub trait MutNullary<S: Copy>: ImNullary<S> {
    type CompleteSymbolMut: complete::MutNullary<S>;
    type CompleteSymbolMutRef<'a>: complete::MutNullary<S>
    where
        Self: 'a;
    /// Partial store set method
    fn set(&mut self, common: SymbolInfo, value: Option<S>);
    fn try_into_mut_complete(self, common: SymbolInfo) -> Result<Self::CompleteSymbolMut, Self>;
    fn try_as_mut_complete<'a>(
        &'a mut self,
        common: SymbolInfo,
    ) -> Result<Self::CompleteSymbolMutRef<'a>, ()>;
}

/// Immutable store methods for partially interpreted functions
pub trait ImFunc<S: Copy>: ToOwnedStore + Sized {
    type CompleteSymbol: complete::ImFunc<S>;
    type CompleteSymbolRef<'a>: complete::ImFunc<S>
    where
        Self: 'a;
    fn get(&self, common: SymbolInfo, domain_enum: DomainEnum) -> Option<S>;
    fn try_into_im_complete(self, common: SymbolInfo) -> Result<Self::CompleteSymbol, Self>;
    fn try_as_im_complete<'a>(
        &'a self,
        common: SymbolInfo,
    ) -> Result<Self::CompleteSymbolRef<'a>, ()>;
    fn iter_partial(&self, common: SymbolInfo) -> impl Iterator<Item = (DomainEnum, S)>;
    fn into_iter_partial(self, common: SymbolInfo) -> impl Iterator<Item = (DomainEnum, S)>;
    fn iter_unknown(&self, common: SymbolInfo) -> impl Iterator<Item = DomainEnum>;
    fn into_iter_unknown(self, common: SymbolInfo) -> impl Iterator<Item = DomainEnum>;
    fn len_partial(&self, common: SymbolInfo) -> usize;
}

pub trait ImPred: ToOwnedStore + Sized + ImFunc<bool> {
    // We don't reuse the methods from ImFunc because constraining a GAT with lifetimes is
    // currently not properly doable, which causes reasonable things to fail because of whacky
    // lifetimes.
    type CompletePred: complete::ImPred;
    type CompletePredRef<'a>: complete::ImPred
    where
        Self: 'a;
    fn try_into_im_complete(self, common: SymbolInfo) -> Result<Self::CompletePred, Self>;
    fn try_as_im_complete<'a>(
        &'a self,
        common: SymbolInfo,
    ) -> Result<Self::CompletePredRef<'a>, ()>;
    fn iter_true(&self, common: SymbolInfo) -> impl Iterator<Item = DomainEnum>;
    fn into_iter_true(self, common: SymbolInfo) -> impl Iterator<Item = DomainEnum>;
    fn iter_false(&self, common: SymbolInfo) -> impl Iterator<Item = DomainEnum>;
    fn into_iter_false(self, common: SymbolInfo) -> impl Iterator<Item = DomainEnum>;
    fn split_ct_cf(
        self,
        common: SymbolInfo,
    ) -> Result<(Self::CompletePred, Self::CompletePred), Self>;
    fn split_ct_cf_ref<'a>(
        &'a self,
        common: SymbolInfo,
    ) -> Option<(Self::CompletePredRef<'a>, Self::CompletePredRef<'a>)>;
}

/// Mutable store methods for partially function constants
pub trait MutFunc<S: Copy>: ImFunc<S> {
    type CompleteSymbolMut: complete::MutFunc<S>;
    type CompleteSymbolMutRef<'a>: complete::MutFunc<S>
    where
        Self: 'a;

    fn set(&mut self, common: SymbolInfo, domain_enum: DomainEnum, value: Option<S>);
    fn fill_unknown_with(&mut self, common: SymbolInfo, value: S);
    fn try_into_mut_complete(self, common: SymbolInfo) -> Result<Self::CompleteSymbolMut, Self>;
    fn try_as_mut_complete<'a>(
        &'a mut self,
        common: SymbolInfo,
    ) -> Result<Self::CompleteSymbolMutRef<'a>, ()>;
}

pub trait ImViews: Clone + Default {
    type PropView<'a>: ImNullary<bool> + Clone + ToOwnedStore
    where
        Self: 'a;
    type IntConstView<'a>: ImNullary<Int> + Clone + ToOwnedStore
    where
        Self: 'a;
    type RealConstView<'a>: ImNullary<Real> + Clone + ToOwnedStore
    where
        Self: 'a;
    type IntTypeConstView<'a>: ImNullary<Int> + Clone + ToOwnedStore
    where
        Self: 'a;
    type RealTypeConstView<'a>: ImNullary<Real> + Clone + ToOwnedStore
    where
        Self: 'a;
    type StrConstView<'a>: ImNullary<TypeEnum> + Clone + ToOwnedStore
    where
        Self: 'a;

    type PredView<'a>: ImPred + Clone + ToOwnedStore
    where
        Self: 'a;
    type IntFuncView<'a>: ImFunc<Int> + Clone + ToOwnedStore
    where
        Self: 'a;
    type RealFuncView<'a>: ImFunc<Real> + Clone + ToOwnedStore
    where
        Self: 'a;
    type IntTypeFuncView<'a>: ImFunc<Int> + Clone + ToOwnedStore
    where
        Self: 'a;
    type RealTypeFuncView<'a>: ImFunc<Real> + Clone + ToOwnedStore
    where
        Self: 'a;
    type StrFuncView<'a>: ImFunc<TypeEnum> + Clone + ToOwnedStore
    where
        Self: 'a;

    fn get_prop<'a>(&'a self, index: PropIndex, common: SymbolInfo) -> Self::PropView<'a>;
    fn get_int_const<'a>(
        &'a self,
        index: IntConstIndex,
        common: SymbolInfo,
    ) -> Self::IntConstView<'a>;
    fn get_real_const<'a>(
        &'a self,
        index: RealConstIndex,
        common: SymbolInfo,
    ) -> Self::RealConstView<'a>;
    fn get_int_type_const<'a>(
        &'a self,
        index: IntTypeConstIndex,
        common: SymbolInfo,
    ) -> Self::IntTypeConstView<'a>;
    fn get_real_type_const<'a>(
        &'a self,
        index: RealTypeConstIndex,
        common: SymbolInfo,
    ) -> Self::RealTypeConstView<'a>;
    fn get_str_const<'a>(
        &'a self,
        index: StrConstIndex,
        common: SymbolInfo,
    ) -> Self::StrConstView<'a>;
    fn get_pred<'a>(&'a self, index: PredIndex, common: SymbolInfo) -> Self::PredView<'a>;
    fn get_int_func<'a>(&'a self, index: IntFuncIndex, common: SymbolInfo)
    -> Self::IntFuncView<'a>;
    fn get_real_func<'a>(
        &'a self,
        index: RealFuncIndex,
        common: SymbolInfo,
    ) -> Self::RealFuncView<'a>;
    fn get_int_type_func<'a>(
        &'a self,
        index: IntTypeFuncIndex,
        common: SymbolInfo,
    ) -> Self::IntTypeFuncView<'a>;
    fn get_real_type_func<'a>(
        &'a self,
        index: RealTypeFuncIndex,
        common: SymbolInfo,
    ) -> Self::RealTypeFuncView<'a>;
    fn get_str_func<'a>(&'a self, index: StrFuncIndex, common: SymbolInfo)
    -> Self::StrFuncView<'a>;
}

pub trait MutViews {
    type PropView<'a>: MutNullary<bool> + ToOwnedStore
    where
        Self: 'a;
    type IntConstView<'a>: MutNullary<Int> + ToOwnedStore
    where
        Self: 'a;
    type RealConstView<'a>: MutNullary<Real> + ToOwnedStore
    where
        Self: 'a;
    type IntTypeConstView<'a>: MutNullary<Int> + ToOwnedStore
    where
        Self: 'a;
    type RealTypeConstView<'a>: MutNullary<Real> + ToOwnedStore
    where
        Self: 'a;
    type StrConstView<'a>: MutNullary<TypeEnum> + ToOwnedStore
    where
        Self: 'a;

    type PredView<'a>: MutFunc<bool> + ImPred + ToOwnedStore
    where
        Self: 'a;
    type IntFuncView<'a>: MutFunc<Int> + ToOwnedStore
    where
        Self: 'a;
    type RealFuncView<'a>: MutFunc<Real> + ToOwnedStore
    where
        Self: 'a;
    type IntTypeFuncView<'a>: MutFunc<Int> + ToOwnedStore
    where
        Self: 'a;
    type RealTypeFuncView<'a>: MutFunc<Real> + ToOwnedStore
    where
        Self: 'a;
    type StrFuncView<'a>: MutFunc<TypeEnum> + ToOwnedStore
    where
        Self: 'a;

    fn reinit(&mut self, index: PfuncIndex, vocab: &Vocabulary) {
        use crate::vocabulary::Type;
        let pfunc = vocab.pfuncs(index);
        match (pfunc.domain.as_ref(), pfunc.codomain) {
            ([], Type::IntType(_)) => self.reinit_int_type_const(IntTypeConstIndex(index)),
            ([], Type::RealType(_)) => self.reinit_real_type_const(RealTypeConstIndex(index)),
            ([], Type::Str(_)) => self.reinit_str_const(StrConstIndex(index)),
            ([], _) => (),
            ([..], Type::Bool) => self.reinit_pred(PredIndex(index)),
            ([..], Type::Int) => self.reinit_int_func(IntFuncIndex(index)),
            ([..], Type::Real) => self.reinit_real_func(RealFuncIndex(index)),
            ([..], Type::IntType(_)) => self.reinit_int_type_func(IntTypeFuncIndex(index)),
            ([..], Type::RealType(_)) => self.reinit_real_type_func(RealTypeFuncIndex(index)),
            ([..], Type::Str(_)) => self.reinit_str_func(StrFuncIndex(index)),
        }
    }

    fn reinit_int_type_const(&mut self, index: IntTypeConstIndex);
    fn reinit_real_type_const(&mut self, index: RealTypeConstIndex);
    fn reinit_str_const(&mut self, index: StrConstIndex);
    fn reinit_pred(&mut self, index: PredIndex);
    fn reinit_int_func(&mut self, index: IntFuncIndex);
    fn reinit_real_func(&mut self, index: RealFuncIndex);
    fn reinit_int_type_func(&mut self, index: IntTypeFuncIndex);
    fn reinit_real_type_func(&mut self, index: RealTypeFuncIndex);
    fn reinit_str_func(&mut self, index: StrFuncIndex);

    fn get_prop<'a>(&'a mut self, index: PropIndex, common: SymbolInfo) -> Self::PropView<'a>;
    fn get_int_const<'a>(
        &'a mut self,
        index: IntConstIndex,
        common: SymbolInfo,
    ) -> Self::IntConstView<'a>;
    fn get_real_const<'a>(
        &'a mut self,
        index: RealConstIndex,
        common: SymbolInfo,
    ) -> Self::RealConstView<'a>;
    fn get_int_type_const<'a>(
        &'a mut self,
        index: IntTypeConstIndex,
        common: SymbolInfo,
    ) -> Self::IntTypeConstView<'a>;
    fn get_real_type_const<'a>(
        &'a mut self,
        index: RealTypeConstIndex,
        common: SymbolInfo,
    ) -> Self::RealTypeConstView<'a>;
    fn get_str_const<'a>(
        &'a mut self,
        index: StrConstIndex,
        common: SymbolInfo,
    ) -> Self::StrConstView<'a>;
    fn get_pred<'a>(&'a mut self, index: PredIndex, common: SymbolInfo) -> Self::PredView<'a>;
    fn get_int_func<'a>(
        &'a mut self,
        index: IntFuncIndex,
        common: SymbolInfo,
    ) -> Self::IntFuncView<'a>;
    fn get_real_func<'a>(
        &'a mut self,
        index: RealFuncIndex,
        common: SymbolInfo,
    ) -> Self::RealFuncView<'a>;
    fn get_int_type_func<'a>(
        &'a mut self,
        index: IntTypeFuncIndex,
        common: SymbolInfo,
    ) -> Self::IntTypeFuncView<'a>;
    fn get_real_type_func<'a>(
        &'a mut self,
        index: RealTypeFuncIndex,
        common: SymbolInfo,
    ) -> Self::RealTypeFuncView<'a>;
    fn get_str_func<'a>(
        &'a mut self,
        index: StrFuncIndex,
        common: SymbolInfo,
    ) -> Self::StrFuncView<'a>;
}

pub trait SetInterps: ImViews {
    fn set_prop<'a>(
        &'a mut self,
        index: PropIndex,
        interp: <Self::PropView<'static> as ToOwnedStore>::Owned,
    );
    fn set_int_const<'a>(
        &'a mut self,
        index: IntConstIndex,
        interp: <Self::IntConstView<'static> as ToOwnedStore>::Owned,
    );
    fn set_real_const<'a>(
        &'a mut self,
        index: RealConstIndex,
        interp: <Self::RealConstView<'static> as ToOwnedStore>::Owned,
    );
    fn set_int_type_const<'a>(
        &'a mut self,
        index: IntTypeConstIndex,
        interp: <Self::IntTypeConstView<'static> as ToOwnedStore>::Owned,
    );
    fn set_real_type_const<'a>(
        &'a mut self,
        index: RealTypeConstIndex,
        interp: <Self::RealTypeConstView<'static> as ToOwnedStore>::Owned,
    );
    fn set_str_const<'a>(
        &'a mut self,
        index: StrConstIndex,
        interp: <Self::StrConstView<'static> as ToOwnedStore>::Owned,
    );
    fn set_pred<'a>(
        &'a mut self,
        index: PredIndex,
        interp: <Self::PredView<'static> as ToOwnedStore>::Owned,
    );
    fn set_int_func<'a>(
        &'a mut self,
        index: IntFuncIndex,
        interp: <Self::IntFuncView<'static> as ToOwnedStore>::Owned,
    );
    fn set_real_func<'a>(
        &'a mut self,
        index: RealFuncIndex,
        interp: <Self::RealFuncView<'static> as ToOwnedStore>::Owned,
    );
    fn set_int_type_func<'a>(
        &'a mut self,
        index: IntTypeFuncIndex,
        interp: <Self::IntTypeFuncView<'static> as ToOwnedStore>::Owned,
    );
    fn set_real_type_func<'a>(
        &'a mut self,
        index: RealTypeFuncIndex,
        interp: <Self::RealTypeFuncView<'static> as ToOwnedStore>::Owned,
    );
    fn set_str_func<'a>(
        &'a mut self,
        index: StrFuncIndex,
        interp: <Self::StrFuncView<'static> as ToOwnedStore>::Owned,
    );
}

#[duplicate_item(
    reference(type) reference2(type) ptr_ty;
    [&'a type] [&type] [*const _];
    [&'a mut type] [&mut type] [*mut _];
)]
impl<'a, S, T> ImNullary<S> for reference([T])
where
    S: Copy,
    T: ImNullary<S>,
{
    type CompleteSymbol = <T as ImNullary<S>>::CompleteSymbolRef<'a>;
    type CompleteSymbolRef<'b>
        = <T as ImNullary<S>>::CompleteSymbolRef<'b>
    where
        Self: 'b;

    fn get(&self, common: SymbolInfo) -> Option<S> {
        <T as ImNullary<S>>::get(self, common)
    }

    fn try_as_im_complete<'b>(
        &'b self,
        common: SymbolInfo,
    ) -> Result<Self::CompleteSymbolRef<'b>, ()> {
        <T as ImNullary<S>>::try_as_im_complete(self, common)
    }

    fn try_into_im_complete(self, common: SymbolInfo) -> Result<Self::CompleteSymbol, Self> {
        let slf_ptr = self as ptr_ty;
        match <T as ImNullary<S>>::try_as_im_complete(self, common) {
            Ok(value) => return Ok(value),
            Err(_) => (),
        }
        Err(
            // Fuck you this is safe!!
            // Because the &'a mut borrow only lasts if Ok is returned.
            // We can only be here if Err is returned, as such the mutable borrow is no longer
            // being borrowed
            unsafe { reference2([*(slf_ptr)]) },
        )
    }
}

impl<'a, S, T> MutNullary<S> for &'a mut T
where
    S: Copy,
    T: MutNullary<S>,
{
    type CompleteSymbolMut = T::CompleteSymbolMutRef<'a>;
    type CompleteSymbolMutRef<'b>
        = T::CompleteSymbolMutRef<'b>
    where
        Self: 'b;

    fn set(&mut self, common: SymbolInfo, value: Option<S>) {
        <T as MutNullary<_>>::set(self, common, value)
    }

    fn try_as_mut_complete<'b>(
        &'b mut self,
        common: SymbolInfo,
    ) -> Result<Self::CompleteSymbolMutRef<'b>, ()> {
        <T as MutNullary<_>>::try_as_mut_complete(self, common)
    }

    fn try_into_mut_complete(self, common: SymbolInfo) -> Result<Self::CompleteSymbolMut, Self> {
        let slf_ptr = self as *mut _;
        match <T as MutNullary<_>>::try_as_mut_complete(self, common) {
            Ok(value) => return Ok(value),
            Err(_) => (),
        }
        Err(
            // Fuck you this is safe!!
            // Because the &'a mut borrow only lasts if Ok is returned
            // We can only be here if Err is returned, as such the mutable borrow is no longer
            // being borrowed
            unsafe { &mut *slf_ptr },
        )
    }
}

#[duplicate_item(
    reference(type) reference2(type) ptr_ty;
    [&'a type] [&type] [*const _];
    [&'a mut type] [&mut type] [*mut _];
)]
impl<'a, S, T> ImFunc<S> for reference([T])
where
    S: Copy,
    T: ImFunc<S>,
{
    type CompleteSymbol = <T as ImFunc<S>>::CompleteSymbolRef<'a>;
    type CompleteSymbolRef<'b>
        = <T as ImFunc<S>>::CompleteSymbolRef<'b>
    where
        Self: 'b;

    fn get(&self, common: SymbolInfo, domain_enum: DomainEnum) -> Option<S> {
        <T as ImFunc<S>>::get(&self, common, domain_enum)
    }

    fn try_as_im_complete<'b>(
        &'b self,
        common: SymbolInfo,
    ) -> Result<Self::CompleteSymbolRef<'b>, ()> {
        <T as ImFunc<S>>::try_as_im_complete(self, common)
    }

    fn try_into_im_complete(self, common: SymbolInfo) -> Result<Self::CompleteSymbol, Self> {
        let slf_ptr = self as ptr_ty;
        match <T as ImFunc<S>>::try_as_im_complete(self, common) {
            Ok(value) => return Ok(value),
            Err(_) => (),
        }
        Err(
            // Fuck you this is safe!!
            // Because the &'a mut borrow only lasts if Ok is returned
            // We can only be here if Err is returned, as such the mutable borrow is no longer
            // being borrowed
            unsafe { reference2([*(slf_ptr)]) },
        )
    }

    fn len_partial(&self, common: SymbolInfo) -> usize {
        <T as ImFunc<S>>::len_partial(self, common)
    }

    fn into_iter_partial(self, common: SymbolInfo) -> impl Iterator<Item = (DomainEnum, S)> {
        <T as ImFunc<S>>::iter_partial(self, common)
    }

    fn iter_partial(&self, common: SymbolInfo) -> impl Iterator<Item = (DomainEnum, S)> {
        <T as ImFunc<S>>::iter_partial(self, common)
    }

    fn iter_unknown(&self, common: SymbolInfo) -> impl Iterator<Item = DomainEnum> {
        <T as ImFunc<S>>::iter_unknown(self, common)
    }

    fn into_iter_unknown(self, common: SymbolInfo) -> impl Iterator<Item = DomainEnum> {
        <T as ImFunc<S>>::iter_unknown(self, common)
    }
}

impl<'a, S, T> MutFunc<S> for &'a mut T
where
    S: Copy,
    T: MutFunc<S>,
{
    type CompleteSymbolMut = T::CompleteSymbolMutRef<'a>;
    type CompleteSymbolMutRef<'b>
        = T::CompleteSymbolMutRef<'b>
    where
        Self: 'b;
    fn set(&mut self, common: SymbolInfo, domain_enum: DomainEnum, value: Option<S>) {
        <T as MutFunc<_>>::set(self, common, domain_enum, value)
    }

    fn fill_unknown_with(&mut self, common: SymbolInfo, value: S) {
        <T as MutFunc<_>>::fill_unknown_with(self, common, value)
    }

    fn try_as_mut_complete<'b>(
        &'b mut self,
        common: SymbolInfo,
    ) -> Result<Self::CompleteSymbolMutRef<'b>, ()> {
        <T as MutFunc<_>>::try_as_mut_complete(self, common)
    }

    fn try_into_mut_complete(self, common: SymbolInfo) -> Result<Self::CompleteSymbolMut, Self> {
        let slf_ptr = self as *mut _;
        match <T as MutFunc<_>>::try_as_mut_complete(self, common) {
            Ok(value) => return Ok(value),
            Err(_) => (),
        }
        Err(
            // Fuck you this is safe!!
            // Because the &'a mut borrow only lasts if Ok is returned
            // We can only be here if Err is returned, as such the mutable borrow is no longer
            // being borrowed
            unsafe { &mut *slf_ptr },
        )
    }
}

#[duplicate_item(
    reference(type) reference2(type) ptr_ty;
    [&'a type] [&type] [*const _];
    [&'a mut type] [&mut type] [*mut _];
)]
impl<'a, T> ImPred for reference([T])
where
    T: ImPred,
{
    type CompletePred = <T as ImPred>::CompletePredRef<'a>;
    type CompletePredRef<'b>
        = <T as ImPred>::CompletePredRef<'b>
    where
        Self: 'b;

    fn try_as_im_complete<'b>(
        &'b self,
        common: SymbolInfo,
    ) -> Result<Self::CompletePredRef<'b>, ()> {
        <T as ImPred>::try_as_im_complete(self, common)
    }

    fn try_into_im_complete(self, common: SymbolInfo) -> Result<Self::CompletePred, Self> {
        let slf_ptr = self as ptr_ty;
        match <T as ImPred>::try_as_im_complete(self, common) {
            Ok(value) => return Ok(value),
            Err(_) => (),
        }
        Err(
            // Fuck you this is safe!!
            // Because the &'a mut borrow only lasts if Ok is returned
            // We can only be here if Err is returned, as such the mutable borrow is no longer
            // being borrowed
            unsafe { reference2([*(slf_ptr)]) },
        )
    }

    fn iter_true(&self, common: SymbolInfo) -> impl Iterator<Item = DomainEnum> {
        <T as ImPred>::iter_true(self, common)
    }

    fn into_iter_true(self, common: SymbolInfo) -> impl Iterator<Item = DomainEnum> {
        <T as ImPred>::iter_true(self, common)
    }

    fn iter_false(&self, common: SymbolInfo) -> impl Iterator<Item = DomainEnum> {
        <T as ImPred>::iter_false(self, common)
    }

    fn into_iter_false(self, common: SymbolInfo) -> impl Iterator<Item = DomainEnum> {
        <T as ImPred>::iter_false(self, common)
    }

    fn split_ct_cf(
        self,
        common: SymbolInfo,
    ) -> Result<(Self::CompletePred, Self::CompletePred), Self> {
        let slf_ptr = self as ptr_ty;
        match <T as ImPred>::split_ct_cf_ref(self, common) {
            Some(value) => return Ok(value),
            None => (),
        }
        Err(
            // Fuck you this is safe!!
            // Because the &'a mut borrow only lasts if Ok is returned
            // We can only be here if Err is returned, as such the mutable borrow is no longer
            // being borrowed
            unsafe { reference2([*(slf_ptr)]) },
        )
    }

    fn split_ct_cf_ref<'b>(
        &'b self,
        common: SymbolInfo,
    ) -> Option<(Self::CompletePredRef<'b>, Self::CompletePredRef<'b>)> {
        <T as ImPred>::split_ct_cf_ref(self, common)
    }
}
