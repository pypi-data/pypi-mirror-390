pub use super::applied_symb_interp::partial::{immutable, mutable, owned};
use super::{
    Precision, TypeFull, TypeInterps,
    applied_symb_interp::{
        CustomFuncCommon, CustomNullaryCommon, IntConstCommon, IntFuncCommon, IntTypeConstCommon,
        IntTypeFuncCommon, PredCommon, PrimFuncCommon, PrimNullaryCommon, PropCommon,
        RealConstCommon, RealFuncCommon, RealTypeConstCommon, RealTypeFuncCommon, StrConstCommon,
        StrFuncCommon, SymbolInfoHolder,
    },
    backend::{self, indexes::*},
    complete::CompleteStructure,
    traits::{
        self,
        partial::{MutViews, SetInterps},
    },
};
use crate::{
    Int, Real,
    structure::traits::{CustomTypeIter, PrimTypeIter},
    vocabulary::{Domain, DomainEnum, PfuncIndex, SymbolFull, TypeEnum, Vocabulary},
};
use sli_collections::{iterator::Iterator as SIterator, rc::Rc};
use std::ptr::addr_of_mut;

/// A comp core partial structure.
#[derive(Debug, Clone)]
pub struct PartialStructure {
    type_interps: Rc<TypeInterps>,
    pub(crate) store: backend::Backend,
}

impl Eq for PartialStructure {}

impl PartialEq for PartialStructure {
    fn eq(&self, other: &Self) -> bool {
        if &self.type_interps != &other.type_interps {
            return false;
        }
        if self.iter_known().count() != other.iter_known().count() {
            return false;
        }
        self.iter_known().all(|a| {
            let b = other.get(a.pfunc_index());
            if a.amount_known() != b.amount_known() {
                return false;
            }
            a.iter()
                .all(|(arg, value)| b.get_i(arg).map(|f| f == value).unwrap_or(false))
        })
    }
}

impl PartialEq<CompleteStructure> for PartialStructure {
    fn eq(&self, other: &CompleteStructure) -> bool {
        if self.rc_type_interps() != other.rc_type_interps() {
            return false;
        }
        other.iter().all(|a| {
            let b = self.get(a.pfunc_index());
            if a.domain().domain_len(other.type_interps()) != b.amount_known() {
                return false;
            }
            a.iter()
                .all(|(arg, value)| b.get_i(arg).map(|f| f == value).unwrap_or(false))
        })
    }
}

impl Precision for PartialStructure {
    fn is_more_precise(&self, rhs: &Self) -> bool {
        if self.type_interps != rhs.type_interps {
            return false;
        }
        rhs.iter_known().all(|a| {
            let b = self.get(a.pfunc_index());
            a.iter()
                .all(|(arg, value)| b.get_i(arg).map(|f| f == value).unwrap_or(false))
        })
    }
}

impl Precision<CompleteStructure> for PartialStructure {
    fn is_more_precise(&self, rhs: &CompleteStructure) -> bool {
        self.eq(rhs)
    }

    fn is_strictly_more_precise(&self, _: &CompleteStructure) -> bool {
        // A PartialStructure can never be strictly more precise than a CompleteStructure
        false
    }
}

impl AsRef<TypeInterps> for PartialStructure {
    fn as_ref(&self) -> &TypeInterps {
        &self.type_interps
    }
}

impl From<CompleteStructure> for PartialStructure {
    fn from(value: CompleteStructure) -> Self {
        value.0
    }
}

impl PartialStructure {
    /// Creates an empty [PartialStructure] with the given [TypeInterps].
    pub fn new(type_interps: Rc<TypeInterps>) -> Self {
        Self {
            type_interps,
            store: Default::default(),
        }
    }

    pub fn from_raw(type_interps: Rc<TypeInterps>, store: backend::Backend) -> Self {
        Self {
            type_interps,
            store,
        }
    }

    /// Build a [PartialStructure] from [TypeInterps] and a [backend::Backend].
    ///
    /// # Correctness
    ///
    /// Calling this function with backend interpretations in the backend that got initialized from a
    /// different vocabulary is a logical error.
    /// Calling this function with backend interpretations that got initialized with different type
    /// interpretations is also a logical error (even if these interpretations are empty!).
    /// It is allowed to call this function with different type interps and backend interpretations
    /// if these interpretations got re-initialized using the `reinit-*` methods from
    /// [traits::partial::MutViews].
    pub fn into_raw(self) -> (Rc<TypeInterps>, backend::Backend) {
        (self.type_interps, self.store)
    }

    pub fn take_backend(&mut self) -> backend::Backend {
        core::mem::take(&mut self.store)
    }

    pub fn reinit_pfunc(&mut self, pfunc: PfuncIndex) {
        self.store.reinit(pfunc, self.type_interps.vocab());
    }

    /// The [Vocabulary] of the structure.
    pub fn vocab(&self) -> &Vocabulary {
        self.type_interps.vocab()
    }

    /// The [Vocabulary] of the structure, as a pointer to an [Rc].
    pub fn rc_vocab(&self) -> &Rc<Vocabulary> {
        &self.type_interps.vocabulary
    }

    /// The [TypeInterps] of the structure.
    pub fn type_interps(&self) -> &TypeInterps {
        &self.type_interps
    }

    /// The [TypeInterps] of the structure, as a pointer to an [Rc].
    pub fn rc_type_interps(&self) -> &Rc<TypeInterps> {
        &self.type_interps
    }

    /// An iterator over all interpretations.
    pub fn iter(&self) -> impl SIterator<Item = immutable::SymbolInterp> {
        self.vocab().iter_pfuncs().map(|i| self.get(i))
    }

    /// Modifies all interpretations with the given function.
    pub fn for_each_mut<F: FnMut(mutable::SymbolInterp)>(&mut self, mut func: F) {
        for index in self.vocab().iter_pfuncs() {
            func(self.get_mut(index))
        }
    }

    /// An iterator over all interpretations with at least one interpretation.
    pub fn iter_known(&self) -> impl SIterator<Item = immutable::SymbolInterp> {
        self.iter().filter(|i| i.any_known())
    }

    pub fn is_complete(&self) -> bool {
        self.iter().all(|f| f.is_complete())
    }

    /// Tries converting this [PartialStructure] to a [CompleteStructure].
    pub fn try_into_complete(self) -> Result<CompleteStructure, Self> {
        if self.is_complete() {
            Ok(CompleteStructure(self))
        } else {
            Err(self)
        }
    }

    /// Returns an iterator over all [CompleteStructure]s that are an extension of this
    /// [PartialStructure].
    ///
    /// Skips infinite values by default.
    pub fn iter_complete(&self) -> CompleteStructureIter<IterUnknown> {
        CompleteStructureIter::new_ref(self)
    }

    /// Returns an owning iterator over all [CompleteStructure]s that are an extension of this
    /// [PartialStructure].
    ///
    /// Skips infinite values by default.
    pub fn into_iter_complete(self) -> CompleteStructureIter<IntoIterUnknown> {
        CompleteStructureIter::new_owned(self)
    }

    fn iter_unknown<'b>(&'b self) -> IterUnknown<'b> {
        IterUnknown {
            iter: Box::new(self.iter().flat_map(|f| {
                let index = f.pfunc_index();
                core::iter::repeat(index).zip(f.into_iter_unknown())
            })),
            structure: self,
        }
    }

    fn into_iter_unknown(self) -> IntoIterUnknown {
        IntoIterUnknown::new(self)
    }

    fn iter_irrelevant_symbols<'a>(
        &'a self,
        type_interps: &'a TypeInterps,
    ) -> impl SIterator<Item = PfuncIndex> + 'a {
        type_interps.vocab().iter_pfuncs().filter(move |f| {
            let b = self.get(*f);
            b.amount_unknown() != 0
        })
    }

    /// Get the interpretation of the given pfunc.
    pub fn get(&self, index: PfuncIndex) -> immutable::SymbolInterp {
        let symb = self
            .type_interps
            .vocabulary
            .pfuncs(index)
            .with_interps(&self.type_interps);
        self.get_store(index, symb)
    }

    pub(crate) fn get_store<'a>(
        &'a self,
        index: PfuncIndex,
        symb: SymbolFull<'a>,
    ) -> immutable::SymbolInterp<'a> {
        match &symb {
            SymbolFull {
                domain: Domain([]),
                codomain: TypeFull::Bool,
                ..
            } => {
                let common = PropCommon(prim_nullary_common(&symb));
                immutable::PropInterp {
                    store: traits::partial::ImViews::get_prop(
                        &self.store,
                        PropIndex(index),
                        common.symbol_info(),
                    ),
                    common,
                }
                .into()
            }
            SymbolFull {
                domain: Domain([]),
                codomain: TypeFull::Int,
                ..
            } => {
                let common = IntConstCommon(prim_nullary_common(&symb));
                immutable::IntConstInterp {
                    store: traits::partial::ImViews::get_int_const(
                        &self.store,
                        IntConstIndex(index),
                        common.symbol_info(),
                    ),
                    common,
                }
                .into()
            }
            SymbolFull {
                domain: Domain([]),
                codomain: TypeFull::IntType((type_index, codomain_interp)),
                ..
            } => {
                let common = IntTypeConstCommon(CustomNullaryCommon {
                    vocabulary: &self.type_interps.vocabulary,
                    type_interps: &self.type_interps,
                    index: symb.index,
                    codomain_interp,
                    type_index: *type_index,
                });
                immutable::IntTypeConstInterp {
                    store: traits::partial::ImViews::get_int_const(
                        &self.store,
                        IntConstIndex(index),
                        common.symbol_info(),
                    ),
                    common,
                }
                .into()
            }
            SymbolFull {
                domain: Domain([]),
                codomain: TypeFull::Real,
                ..
            } => {
                let common = RealConstCommon(prim_nullary_common(&symb));
                immutable::RealConstInterp {
                    store: traits::partial::ImViews::get_real_const(
                        &self.store,
                        RealConstIndex(index),
                        common.symbol_info(),
                    ),
                    common,
                }
                .into()
            }
            SymbolFull {
                domain: Domain([]),
                codomain: TypeFull::RealType((type_index, codomain_interp)),
                ..
            } => {
                let common = RealTypeConstCommon(CustomNullaryCommon {
                    vocabulary: &self.type_interps.vocabulary,
                    type_interps: &self.type_interps,
                    index: symb.index,
                    codomain_interp,
                    type_index: *type_index,
                });
                immutable::RealTypeConstInterp {
                    store: traits::partial::ImViews::get_real_const(
                        &self.store,
                        RealConstIndex(index),
                        common.symbol_info(),
                    ),
                    common,
                }
                .into()
            }
            SymbolFull {
                domain: Domain([]),
                codomain: TypeFull::Str((type_index, codomain_interp)),
                ..
            } => {
                let common = StrConstCommon(CustomNullaryCommon {
                    vocabulary: &self.type_interps.vocabulary,
                    type_interps: &self.type_interps,
                    index: symb.index,
                    codomain_interp,
                    type_index: *type_index,
                });
                immutable::StrConstInterp {
                    store: traits::partial::ImViews::get_str_const(
                        &self.store,
                        StrConstIndex(index),
                        common.symbol_info(),
                    ),
                    common,
                }
                .into()
            }
            SymbolFull {
                codomain: TypeFull::Bool,
                ..
            } => {
                let common = PredCommon(prim_func_common(&symb));
                immutable::PredInterp {
                    store: traits::partial::ImViews::get_pred(
                        &self.store,
                        PredIndex(index),
                        common.symbol_info(),
                    ),
                    common,
                }
                .into()
            }
            SymbolFull {
                codomain: TypeFull::Int,
                ..
            } => {
                let common = IntFuncCommon(prim_func_common(&symb));
                immutable::IntFuncInterp {
                    store: traits::partial::ImViews::get_int_func(
                        &self.store,
                        IntFuncIndex(index),
                        common.symbol_info(),
                    ),
                    common,
                }
                .into()
            }
            SymbolFull {
                codomain: TypeFull::Real,
                ..
            } => {
                let common = RealFuncCommon(prim_func_common(&symb));
                immutable::RealFuncInterp {
                    store: traits::partial::ImViews::get_real_func(
                        &self.store,
                        RealFuncIndex(index),
                        common.symbol_info(),
                    ),
                    common,
                }
                .into()
            }
            SymbolFull {
                domain,
                codomain: TypeFull::IntType((type_index, codomain_interp)),
                ..
            } => {
                let common = IntTypeFuncCommon(CustomFuncCommon {
                    vocabulary: &self.type_interps.vocabulary,
                    type_interps: &self.type_interps,
                    index: symb.index,
                    codomain_interp,
                    type_index: *type_index,
                    domain,
                });
                immutable::IntTypeFuncInterp {
                    store: traits::partial::ImViews::get_int_func(
                        &self.store,
                        IntFuncIndex(index),
                        common.symbol_info(),
                    ),
                    common,
                }
                .into()
            }
            SymbolFull {
                domain,
                codomain: TypeFull::RealType((type_index, codomain_interp)),
                ..
            } => {
                let common = RealTypeFuncCommon(CustomFuncCommon {
                    vocabulary: &self.type_interps.vocabulary,
                    type_interps: &self.type_interps,
                    index: symb.index,
                    codomain_interp,
                    type_index: *type_index,
                    domain,
                });
                immutable::RealTypeFuncInterp {
                    store: traits::partial::ImViews::get_real_func(
                        &self.store,
                        RealFuncIndex(index),
                        common.symbol_info(),
                    ),
                    common,
                }
                .into()
            }
            SymbolFull {
                domain,
                codomain: TypeFull::Str((type_index, codomain_interp)),
                ..
            } => {
                let common = StrFuncCommon(CustomFuncCommon {
                    vocabulary: &self.type_interps.vocabulary,
                    type_interps: &self.type_interps,
                    index: symb.index,
                    codomain_interp,
                    type_index: *type_index,
                    domain,
                });
                immutable::StrFuncInterp {
                    store: traits::partial::ImViews::get_str_func(
                        &self.store,
                        StrFuncIndex(index),
                        common.symbol_info(),
                    ),
                    common,
                }
                .into()
            }
        }
    }

    /// Get a mutable interpretation of the given pfunc.
    pub fn get_mut(&mut self, index: PfuncIndex) -> mutable::SymbolInterp {
        let symb = self
            .type_interps
            .vocabulary
            .pfuncs(index)
            .with_interps(&self.type_interps);
        Self::get_mut_store(&mut self.store, index, symb)
    }

    pub(crate) fn split(&mut self) -> (&mut backend::Backend, &TypeInterps) {
        (&mut self.store, &self.type_interps)
    }

    pub(crate) fn get_mut_store<'a>(
        store: &'a mut backend::Backend,
        index: PfuncIndex,
        symb: SymbolFull<'a>,
    ) -> mutable::SymbolInterp<'a> {
        match &symb {
            SymbolFull {
                domain: Domain([]),
                codomain: TypeFull::Bool,
                ..
            } => {
                let common = PropCommon(prim_nullary_common(&symb));
                mutable::PropInterp {
                    store: traits::partial::MutViews::get_prop(
                        store,
                        PropIndex(index),
                        common.symbol_info(),
                    ),
                    common,
                }
                .into()
            }
            SymbolFull {
                domain: Domain([]),
                codomain: TypeFull::Int,
                ..
            } => {
                let common = IntConstCommon(prim_nullary_common(&symb));
                mutable::IntConstInterp {
                    store: traits::partial::MutViews::get_int_const(
                        store,
                        IntConstIndex(index),
                        common.symbol_info(),
                    ),
                    common,
                }
                .into()
            }
            SymbolFull {
                domain: Domain([]),
                codomain: TypeFull::IntType((type_index, codomain_interp)),
                ..
            } => {
                let common = IntTypeConstCommon(CustomNullaryCommon {
                    vocabulary: &symb.type_interps.vocabulary,
                    type_interps: &symb.type_interps,
                    index: symb.index,
                    codomain_interp,
                    type_index: *type_index,
                });
                mutable::IntTypeConstInterp {
                    store: traits::partial::MutViews::get_int_const(
                        store,
                        IntConstIndex(index),
                        common.symbol_info(),
                    ),
                    common,
                }
                .into()
            }
            SymbolFull {
                domain: Domain([]),
                codomain: TypeFull::Real,
                ..
            } => {
                let common = RealConstCommon(prim_nullary_common(&symb));
                mutable::RealConstInterp {
                    store: traits::partial::MutViews::get_real_const(
                        store,
                        RealConstIndex(index),
                        common.symbol_info(),
                    ),
                    common,
                }
                .into()
            }
            SymbolFull {
                domain: Domain([]),
                codomain: TypeFull::RealType((type_index, codomain_interp)),
                ..
            } => {
                let common = RealTypeConstCommon(CustomNullaryCommon {
                    vocabulary: &symb.type_interps.vocabulary,
                    type_interps: &symb.type_interps,
                    index: symb.index,
                    codomain_interp,
                    type_index: *type_index,
                });
                mutable::RealTypeConstInterp {
                    store: traits::partial::MutViews::get_real_const(
                        store,
                        RealConstIndex(index),
                        common.symbol_info(),
                    ),
                    common,
                }
                .into()
            }
            SymbolFull {
                domain: Domain([]),
                codomain: TypeFull::Str((type_index, codomain_interp)),
                ..
            } => {
                let common = StrConstCommon(CustomNullaryCommon {
                    vocabulary: &symb.type_interps.vocabulary,
                    type_interps: &symb.type_interps,
                    index: symb.index,
                    codomain_interp,
                    type_index: *type_index,
                });
                mutable::StrConstInterp {
                    store: traits::partial::MutViews::get_str_const(
                        store,
                        StrConstIndex(index),
                        common.symbol_info(),
                    ),
                    common,
                }
                .into()
            }
            SymbolFull {
                codomain: TypeFull::Bool,
                ..
            } => {
                let common = PredCommon(prim_func_common(&symb));
                mutable::PredInterp {
                    store: traits::partial::MutViews::get_pred(
                        store,
                        PredIndex(index),
                        common.symbol_info(),
                    ),
                    common,
                }
                .into()
            }
            SymbolFull {
                codomain: TypeFull::Int,
                ..
            } => {
                let common = IntFuncCommon(prim_func_common(&symb));
                mutable::IntFuncInterp {
                    store: traits::partial::MutViews::get_int_func(
                        store,
                        IntFuncIndex(index),
                        common.symbol_info(),
                    ),
                    common,
                }
                .into()
            }
            SymbolFull {
                codomain: TypeFull::Real,
                ..
            } => {
                let common = RealFuncCommon(prim_func_common(&symb));
                mutable::RealFuncInterp {
                    store: traits::partial::MutViews::get_real_func(
                        store,
                        RealFuncIndex(index),
                        common.symbol_info(),
                    ),
                    common,
                }
                .into()
            }
            SymbolFull {
                domain,
                codomain: TypeFull::IntType((type_index, codomain_interp)),
                ..
            } => {
                let common = IntTypeFuncCommon(CustomFuncCommon {
                    vocabulary: &symb.type_interps.vocabulary,
                    type_interps: &symb.type_interps,
                    index: symb.index,
                    codomain_interp,
                    type_index: *type_index,
                    domain,
                });
                mutable::IntTypeFuncInterp {
                    store: traits::partial::MutViews::get_int_func(
                        store,
                        IntFuncIndex(index),
                        common.symbol_info(),
                    ),
                    common,
                }
                .into()
            }
            SymbolFull {
                domain,
                codomain: TypeFull::RealType((type_index, codomain_interp)),
                ..
            } => {
                let common = RealTypeFuncCommon(CustomFuncCommon {
                    vocabulary: &symb.type_interps.vocabulary,
                    type_interps: &symb.type_interps,
                    index: symb.index,
                    codomain_interp,
                    type_index: *type_index,
                    domain,
                });
                mutable::RealTypeFuncInterp {
                    store: traits::partial::MutViews::get_real_func(
                        store,
                        RealFuncIndex(index),
                        common.symbol_info(),
                    ),
                    common,
                }
                .into()
            }
            SymbolFull {
                domain,
                codomain: TypeFull::Str((type_index, codomain_interp)),
                ..
            } => {
                let common = StrFuncCommon(CustomFuncCommon {
                    vocabulary: &symb.type_interps.vocabulary,
                    type_interps: &symb.type_interps,
                    index: symb.index,
                    codomain_interp,
                    type_index: *type_index,
                    domain,
                });
                mutable::StrFuncInterp {
                    store: traits::partial::MutViews::get_str_func(
                        store,
                        StrFuncIndex(index),
                        common.symbol_info(),
                    ),
                    common,
                }
                .into()
            }
        }
    }

    /// Sets the interpretation of the given pfunc for the given index.
    ///
    /// This method does no extra checks for the passed index.
    pub fn set_with_index(&mut self, interp: owned::SymbolInterp, index: PfuncIndex) {
        match interp {
            owned::SymbolInterp::Prop(interp) => {
                self.store.set_prop(PropIndex(index), interp.store)
            }
            owned::SymbolInterp::IntConst(owned::IntCoConstInterp::Int(interp)) => {
                self.store.set_int_const(IntConstIndex(index), interp.store)
            }
            owned::SymbolInterp::IntConst(owned::IntCoConstInterp::IntType(interp)) => self
                .store
                .set_int_type_const(IntTypeConstIndex(index), interp.store),
            owned::SymbolInterp::RealConst(owned::RealCoConstInterp::Real(interp)) => self
                .store
                .set_real_const(RealConstIndex(index), interp.store),
            owned::SymbolInterp::RealConst(owned::RealCoConstInterp::RealType(interp)) => self
                .store
                .set_real_type_const(RealTypeConstIndex(index), interp.store),
            owned::SymbolInterp::StrConst(interp) => {
                self.store.set_str_const(StrConstIndex(index), interp.store)
            }
            owned::SymbolInterp::Pred(interp) => {
                self.store.set_pred(PredIndex(index), interp.store)
            }
            owned::SymbolInterp::IntFunc(owned::IntCoFuncInterp::Int(interp)) => {
                self.store.set_int_func(IntFuncIndex(index), interp.store)
            }
            owned::SymbolInterp::IntFunc(owned::IntCoFuncInterp::IntType(interp)) => self
                .store
                .set_int_type_func(IntTypeFuncIndex(index), interp.store),
            owned::SymbolInterp::RealFunc(owned::RealCoFuncInterp::Real(interp)) => {
                self.store.set_real_func(RealFuncIndex(index), interp.store)
            }
            owned::SymbolInterp::RealFunc(owned::RealCoFuncInterp::RealType(interp)) => self
                .store
                .set_real_type_func(RealTypeFuncIndex(index), interp.store),
            owned::SymbolInterp::StrFunc(interp) => {
                self.store.set_str_func(StrFuncIndex(index), interp.store)
            }
        }
    }

    /// Sets the interpretation of the given pfunc.
    pub fn set(&mut self, interp: owned::SymbolInterp) {
        let index = interp.pfunc_index();
        self.set_with_index(interp, index)
    }
}

pub trait UnknownIterator: Iterator<Item = (PfuncIndex, DomainEnum)> {
    fn structure(&self) -> &PartialStructure;
    fn reset(&mut self);
}

pub struct IntoIterUnknown {
    // This is a self referential struct!!,
    // i.e. `iter` has a pointer to `structure`.
    // The following invariants must always be upheld!
    // As long as `iter` exists, `structure` may never move!
    //
    // Unfortunately, this has to be a boxed dyn object because the iterator is unnamable and the
    // compiler is unable to infer its type if we make this struct generic :(.
    // Hopefully TAIT stabilizes soon...
    iter: Box<dyn SIterator<Item = (PfuncIndex, DomainEnum)>>,
    structure: Box<PartialStructure>,
}

impl IntoIterUnknown {
    pub fn new(structure: PartialStructure) -> IntoIterUnknown {
        use core::mem::MaybeUninit;
        let mut uninited_iter = MaybeUninit::uninit();
        let boxed_structure = Box::new(structure);
        let structure_iter = Box::new(boxed_structure.iter_unknown());
        // Safety: we promise to never move the structure in `boxed_structure` for as long as this
        // iterator exists, as such the iterator will be valid for as long as this instance
        // of `IntoIterUnknown` exists.
        let structure_iter = unsafe {
            core::mem::transmute::<
                Box<dyn SIterator<Item = (PfuncIndex, DomainEnum)> + '_>,
                Box<dyn SIterator<Item = (PfuncIndex, DomainEnum)> + 'static>,
            >(structure_iter)
        };
        let ptr: *mut IntoIterUnknown = uninited_iter.as_mut_ptr();
        // Safety: ptr is a valid address to a IntoIterUnknown.
        unsafe { addr_of_mut!((*ptr).structure).write(boxed_structure) };
        // Safety: ptr is a valid address to a IntoIterUnknown.
        unsafe { addr_of_mut!((*ptr).iter).write(structure_iter) };
        // Safety: all fields have been initialized
        unsafe { uninited_iter.assume_init() }
    }

    pub fn structure(&self) -> &PartialStructure {
        &self.structure
    }
}

impl Iterator for IntoIterUnknown {
    type Item = (PfuncIndex, DomainEnum);

    fn next(&mut self) -> Option<Self::Item> {
        self.iter.next()
    }
}

impl UnknownIterator for IntoIterUnknown {
    fn structure(&self) -> &PartialStructure {
        Self::structure(self)
    }

    fn reset(&mut self) {
        let new_iter = Box::new(self.structure.iter_unknown());
        // Safety: we promise to never move the structure in `boxed_structure` for as long as this
        // iterator exists, as such the iterator will be valid for as long as this instance
        // of `IntoIterUnknown` exists.
        let new_iter = unsafe {
            core::mem::transmute::<
                Box<dyn SIterator<Item = (PfuncIndex, DomainEnum)> + '_>,
                Box<dyn SIterator<Item = (PfuncIndex, DomainEnum)> + 'static>,
            >(new_iter)
        };
        self.iter = new_iter;
    }
}

pub struct IterUnknown<'a> {
    // Unfortunately this dyn object must be created to be able to make CompleteStructureIter a
    // named type.
    // May TAIT come save us from this blasphemy.
    iter: Box<dyn SIterator<Item = (PfuncIndex, DomainEnum)> + 'a>,
    structure: &'a PartialStructure,
}

impl<'a> IterUnknown<'a> {
    pub fn structure(&self) -> &'a PartialStructure {
        self.structure
    }
}

impl<'a> Iterator for IterUnknown<'a> {
    type Item = (PfuncIndex, DomainEnum);

    fn next(&mut self) -> Option<Self::Item> {
        self.iter.next()
    }
}

impl<'a> UnknownIterator for IterUnknown<'a> {
    fn structure(&self) -> &PartialStructure {
        Self::structure(self)
    }

    fn reset(&mut self) {
        self.iter = Box::new(self.structure.iter_unknown());
    }
}

/// An iterator over all [CompleteStructure]s that are an extension of the given
/// [PartialStructure].
pub struct CompleteStructureIter<I: UnknownIterator> {
    cur_symbol: I,
    cur: Option<CompleteStructure>,
    first_next: bool,
    pub skip_infinite: bool,
}

pub type IterCompleteStructure<'a> = CompleteStructureIter<IterUnknown<'a>>;
pub type IntoIterCompleteStructure = CompleteStructureIter<IntoIterUnknown>;

impl CompleteStructureIter<IntoIterUnknown> {
    pub fn new_owned(partial_structure: PartialStructure) -> Self {
        Self {
            cur_symbol: partial_structure.into_iter_unknown(),
            cur: None,
            first_next: true,
            skip_infinite: true,
        }
    }
}

impl<'a> CompleteStructureIter<IterUnknown<'a>> {
    pub fn new_ref(partial_structure: &'a PartialStructure) -> Self {
        Self {
            cur_symbol: partial_structure.iter_unknown(),
            cur: None,
            first_next: true,
            skip_infinite: true,
        }
    }
}

impl<I: UnknownIterator> CompleteStructureIter<I> {
    pub fn enable_skip_infinite(mut self) -> Self {
        self.skip_infinite = true;
        self
    }

    pub fn disable_skip_infinite(mut self) -> Self {
        self.skip_infinite = false;
        self
    }
}

impl<I: UnknownIterator> CompleteStructureIter<I> {
    fn first_complete(&self) -> Option<CompleteStructure> {
        let mut cur = self.partial_structure().clone();
        let type_interps = self.type_interps().as_ref();
        let mut broken = false;
        macro_rules! early_ret {
            ($val:expr) => {
                if let Some(val) = $val {
                    val
                } else {
                    broken = true;
                    break;
                }
            };
        }

        for irrelevant_symb in self
            .partial_structure()
            .iter_irrelevant_symbols(type_interps)
        {
            let symb = cur.get_mut(irrelevant_symb);
            match symb {
                mutable::SymbolInterp::Prop(mut b_symb) => {
                    let _ = b_symb.set(Some(bool::start()));
                }
                mutable::SymbolInterp::Pred(mut b_symb) => {
                    let _ = b_symb.fill_unknown_with(bool::start());
                }
                mutable::SymbolInterp::IntConst(mut int_symb) => {
                    if let Some(interp) = int_symb.codomain_interp() {
                        let _ =
                            int_symb.set(Some(early_ret!(<Int as CustomTypeIter>::start(interp))));
                    } else {
                        let _ = int_symb.set(Some(<Int as PrimTypeIter>::start()));
                    }
                }
                mutable::SymbolInterp::IntFunc(mut int_symb) => {
                    if let Some(interp) = int_symb.codomain_interp() {
                        let _ = int_symb
                            .fill_unknown_with(early_ret!(<Int as CustomTypeIter>::start(interp)));
                    } else {
                        let _ = int_symb.fill_unknown_with(<Int as PrimTypeIter>::start());
                    }
                }
                mutable::SymbolInterp::RealConst(mut r_symb) => {
                    if let Some(interp) = r_symb.codomain_interp() {
                        let _ =
                            r_symb.set(Some(early_ret!(<Real as CustomTypeIter>::start(interp))));
                    } else {
                        let _ = r_symb.set(Some(<Real as PrimTypeIter>::start().into()));
                    }
                }
                mutable::SymbolInterp::RealFunc(mut r_symb) => {
                    if let Some(interp) = r_symb.codomain_interp() {
                        let _ = r_symb
                            .fill_unknown_with(early_ret!(<Real as CustomTypeIter>::start(interp)));
                    } else {
                        let _ = r_symb.fill_unknown_with(<Real as PrimTypeIter>::start().into());
                    }
                }
                mutable::SymbolInterp::StrConst(mut s_symb) => {
                    let _ = s_symb.set(Some(early_ret!(TypeEnum::start(s_symb.codomain_interp()))));
                }
                mutable::SymbolInterp::StrFunc(mut s_symb) => {
                    let _ = s_symb
                        .fill_unknown_with(early_ret!(TypeEnum::start(s_symb.codomain_interp())));
                }
            }
        }
        // Happens when there is a function with a codomain that is an empty set.
        // i.e.
        // type A := {}
        // T: -> A
        if broken {
            return None;
        }
        let cur = cur
            .try_into_complete()
            .map_err(|_| ())
            .expect("must be complete");
        Some(cur)
    }

    pub fn partial_structure(&self) -> &PartialStructure {
        self.cur_symbol.structure()
    }

    pub fn type_interps(&self) -> &Rc<TypeInterps> {
        self.partial_structure().rc_type_interps()
    }
}

impl<I: UnknownIterator> Iterator for CompleteStructureIter<I> {
    type Item = CompleteStructure;

    fn next(&mut self) -> Option<Self::Item> {
        if self.first_next {
            let ret = self.first_complete();
            self.first_next = false;
            self.cur = ret.clone();
            return ret;
        }
        if let Some(cur) = &mut self.cur {
            // This loop sets numbers to irrelevant symbols.
            // It works similar to the manner we write a sequence of binary numbers:
            // Start all values at an initial value here 0 (done in initialization, above).
            // 0 0 0
            // Set right most 'digit' to the next value if it has a next value, if it does stop
            // the loop and return current value (here the next value of 0 is 1, 1 has no next
            // value).
            // 0 0 1
            // For the next model, we try to set next value on the rightmost digit. Since
            // this has no next digit, we return it to its initial value, and try the next value
            // on the next digit.
            //  loop 1    loop 2
            // 0 0 0 -> 0 1 0
            // We iterated over all complete structures when we try to set the left-most
            // 'digit' with the next value but it does not have one, so for `1 1 1`.
            let reset;
            loop {
                let (cur_func, cur_domain_enum) = Iterator::next(&mut self.cur_symbol)?;
                let mut symb_interp = cur.get_mut(cur_func);
                let completed = match symb_interp.codomain_full() {
                    TypeFull::Bool => {
                        let value = symb_interp.get_i(cur_domain_enum).unwrap_bool();
                        if let Some(next_value) = value.next() {
                            symb_interp.set_i(cur_domain_enum, next_value.into());
                            false
                        } else {
                            symb_interp.set_i(cur_domain_enum, bool::start().into());
                            true
                        }
                    }
                    TypeFull::Int => {
                        if self.skip_infinite {
                            true
                        } else {
                            let value: Int = symb_interp.get_i(cur_domain_enum).unwrap_int();
                            let (next, completed) = <Int as PrimTypeIter>::next(value)
                                .map(|f| (f, false))
                                .unwrap_or_else(|| (<Int as PrimTypeIter>::start(), true));
                            symb_interp.set_i(cur_domain_enum, next.into());
                            completed
                        }
                    }
                    TypeFull::IntType((_, interp)) => {
                        let value: Int = symb_interp.get_i(cur_domain_enum).unwrap_int();
                        let (next, completed) = <Int as CustomTypeIter>::next(value, interp)
                            .map(|f| (f, false))
                            .unwrap_or_else(|| {
                                (
                                    // start must be Some other wise we would not have been
                                    // able to create the first complete structure
                                    <Int as CustomTypeIter>::start(interp).unwrap(),
                                    true,
                                )
                            });
                        symb_interp.set_i(cur_domain_enum, next.into());
                        completed
                    }
                    TypeFull::Real => {
                        if self.skip_infinite {
                            true
                        } else {
                            let value: Real = symb_interp.get_i(cur_domain_enum).unwrap_real();
                            let (next, completed) = <Real as PrimTypeIter>::next(value)
                                .map(|f| (f, false))
                                .unwrap_or_else(|| (<Real as PrimTypeIter>::start(), true));
                            symb_interp.set_i(cur_domain_enum, next.into());
                            completed
                        }
                    }
                    TypeFull::RealType((_, interp)) => {
                        let value: Real = symb_interp.get_i(cur_domain_enum).unwrap_real();
                        let (next, completed) = <Real as CustomTypeIter>::next(value, interp)
                            .map(|f| (f, false))
                            .unwrap_or_else(|| {
                                (<Real as CustomTypeIter>::start(interp).unwrap(), true)
                            });
                        symb_interp.set_i(cur_domain_enum, next.into());
                        completed
                    }
                    TypeFull::Str((index, interp)) => {
                        let value: TypeEnum = symb_interp
                            .get_i(cur_domain_enum)
                            .unwrap_type_element_index()
                            .1;
                        let (next, completed) =
                            <TypeEnum as CustomTypeIter>::next(value.into(), interp)
                                .map(|f| (f, false))
                                .unwrap_or_else(|| {
                                    (<TypeEnum as CustomTypeIter>::start(interp).unwrap(), true)
                                });
                        symb_interp.set_i(cur_domain_enum, next.with_type(index).into());
                        completed
                    }
                };
                if !completed {
                    // Not the last element, exit loop and start from beginning
                    reset = true;
                    break;
                }
            }
            if reset {
                self.cur_symbol.reset();
            }
            return Some(cur.clone());
        } else {
            return None;
        }
    }
}

fn prim_nullary_common<'a>(symb: &SymbolFull<'a>) -> PrimNullaryCommon<'a> {
    PrimNullaryCommon {
        vocabulary: symb.vocabulary,
        type_interps: symb.type_interps,
        index: symb.index,
    }
}

fn prim_func_common<'a>(symb: &SymbolFull<'a>) -> PrimFuncCommon<'a> {
    PrimFuncCommon {
        vocabulary: symb.vocabulary,
        type_interps: symb.type_interps,
        domain: symb.domain,
        index: symb.index,
    }
}
