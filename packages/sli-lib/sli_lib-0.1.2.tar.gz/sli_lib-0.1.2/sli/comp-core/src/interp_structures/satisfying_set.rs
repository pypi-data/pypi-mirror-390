use std::fmt::Debug;

use super::{InterpContext, LayoutVec};
use crate::{
    comp_core::{
        Int, Real,
        constraints::BoundVarId,
        node::QuantKind,
        structure::TypeElement,
        vocabulary::{DomainEnum, TypeElementIndex, TypeEnum, TypeIndex},
    },
    structure::complete,
};
use duplicate::duplicate_item;

#[derive(Debug, Clone, Eq, PartialEq)]
pub enum OrScalar<T, S> {
    Value(T),
    Scalar(S),
}

impl<S: SatSetAlias> From<OrScalar<LayoutSatSet<S>, bool>> for LayoutSymbol<S> {
    fn from(value: OrScalar<LayoutSatSet<S>, bool>) -> Self {
        match value {
            OrScalar::Value(value) => value.into(),
            OrScalar::Scalar(value) => value.into(),
        }
    }
}

impl<T, S> OrScalar<T, S> {
    pub fn map_to_single<N, F1, F2>(self, f1: F1, f2: F2) -> N
    where
        F1: FnOnce(T) -> N,
        F2: FnOnce(S) -> N,
    {
        match self {
            Self::Value(v) => f1(v.into()),
            Self::Scalar(v) => f2(v.into()),
        }
    }

    pub fn map<F1, F2, D, C>(self, f1: F1, f2: F2) -> OrScalar<D, C>
    where
        F1: FnOnce(T) -> D,
        F2: FnOnce(S) -> C,
    {
        match self {
            Self::Value(v) => OrScalar::Value(f1(v)),
            Self::Scalar(v) => OrScalar::Scalar(f2(v)),
        }
    }

    pub fn map_value<D, F>(self, f: F) -> OrScalar<D, S>
    where
        F: FnOnce(T) -> D,
    {
        match self {
            Self::Value(v) => OrScalar::Value(f(v)),
            Self::Scalar(s) => OrScalar::Scalar(s),
        }
    }

    pub fn value(self) -> Option<T> {
        match self {
            Self::Value(v) => Some(v),
            Self::Scalar(_) => None,
        }
    }

    pub fn as_ref(&self) -> OrScalar<&T, &S> {
        match self {
            OrScalar::Value(value) => OrScalar::Value(value),
            OrScalar::Scalar(value) => OrScalar::Scalar(value),
        }
    }
}

fn add_missing(to_add: &[BoundVarId], mut layout: LayoutVec) -> LayoutVec {
    for &add in to_add.iter() {
        if !layout.contains_var(add) {
            layout.add_var(add);
        }
    }
    layout
}

fn align(goal: &[BoundVarId], mut layout: LayoutVec) -> Result<LayoutVec, ()> {
    for (i, &add) in goal.iter().enumerate() {
        if let Some(j) = layout.var_loc(add) {
            if i == j {
                continue;
            }
            layout.reorder(j, i);
        } else {
            return Err(());
        }
    }
    Ok(layout)
}

fn align_layouts(mut layout1: LayoutVec, mut layout2: LayoutVec) -> (AlignedLayout, AlignedLayout) {
    let old_layout1 = layout1.clone();
    let old_layout2 = layout2.clone();
    if layout1 == layout2 {
        return (
            AlignedLayout {
                old_layout: old_layout1,
                new_layout: layout1,
            },
            AlignedLayout {
                old_layout: old_layout2,
                new_layout: layout2,
            },
        );
    }
    layout1 = add_missing(layout2.as_slice(), layout1);
    layout2 = add_missing(layout1.as_slice(), layout2);
    debug_assert!(layout1.len() == layout2.len());
    if old_layout1.len() < old_layout2.len() {
        layout1 =
            align(layout2.as_slice(), layout1).expect("Reached unreachable in reordering layouts");
    } else {
        layout2 =
            align(layout1.as_slice(), layout2).expect("Reached unreachable in reordering layouts");
    }
    debug_assert!(layout1 == layout2);
    (
        AlignedLayout {
            old_layout: old_layout1,
            new_layout: layout1,
        },
        AlignedLayout {
            old_layout: old_layout2,
            new_layout: layout2,
        },
    )
}

#[derive(Debug, Clone)]
pub struct AlignedLayout {
    old_layout: LayoutVec,
    new_layout: LayoutVec,
}

impl AlignedLayout {
    pub(super) fn new(old_layout: LayoutVec, new_layout: LayoutVec) -> Self {
        Self {
            old_layout,
            new_layout,
        }
    }

    pub fn is_different(&self) -> bool {
        self.old_layout() != self.new_layout()
    }

    pub fn old_layout(&self) -> &LayoutVec {
        &self.old_layout
    }

    pub fn new_layout(&self) -> &LayoutVec {
        &self.new_layout
    }

    pub fn take_new_layout(self) -> LayoutVec {
        self.new_layout
    }

    pub fn take_both(self) -> (LayoutVec, LayoutVec) {
        (self.old_layout, self.new_layout)
    }
}

pub fn default_from_structure<S: PureSetOps>(
    mut empty_set: S,
    pred: &complete::immutable::PredInterp,
) -> S {
    for value in pred.iter_true() {
        PureSetOps::set(&mut empty_set, value);
    }
    empty_set
}

pub trait PureSetOps: Sized + Alignable {
    fn new(domain_size: usize) -> Self;

    fn from_structure(pred: &complete::immutable::PredInterp) -> Self {
        default_from_structure(
            Self::new(pred.domain().domain_len(pred.type_interps())),
            pred,
        )
    }

    fn domain_len(&self) -> usize;

    fn natural_join(
        mut left: (Self, LayoutVec),
        mut right: (Self, LayoutVec),
        context: &InterpContext,
    ) -> (Self, LayoutVec) {
        // standard natural join implementation
        if left.1 == right.1 {
            left.0.and(&right.0);
            return left;
        } else {
            align_layout(
                (&mut left.0, &mut left.1),
                (&mut right.0, &mut right.1),
                context,
            );
            left.0.and(&right.0);
            left
        }
    }

    fn or(&mut self, other: &Self);
    fn and(&mut self, other: &Self);
    fn xor(&mut self, other: &Self);
    fn neg(&mut self);
    fn quant(
        self,
        old_layout: &LayoutVec,
        new_layout: &LayoutVec,
        quant_type: QuantKind,
        context: &InterpContext,
    ) -> OrScalar<Self, bool>;
    fn cardinality(&self) -> usize;
    fn set(&mut self, index: DomainEnum);
    fn unset(&mut self, index: DomainEnum);
    fn contains(&self, index: DomainEnum) -> bool;
    fn iter<'a>(&'a self) -> impl Iterator<Item = DomainEnum> + 'a;
}

pub trait Set<I, R, T>: PureSetOps
where
    I: IntFunc<Self, R, T>,
    R: RealFunc<Self, I, T>,
    T: TypeEnumFunc<Self, I, R>,
{
    fn card_agg(
        self,
        old_layout: &LayoutVec,
        new_layout: &LayoutVec,
        context: &InterpContext,
    ) -> OrScalar<I, Int>;
    fn type_enum_ite(&self, then_term: T, else_term: T) -> T;
    fn type_enum_ite_scalar_then(&self, then_term: TypeEnum, else_term: T) -> T;
    fn type_enum_ite_scalar_else(&self, then_term: T, else_term: TypeEnum) -> T;
    fn type_enum_ite_scalar_then_else(&self, then_term: TypeEnum, else_term: TypeEnum) -> T;
    fn int_ite(&self, then_term: I, else_term: I) -> I;
    fn int_ite_scalar_then(&self, then_term: Int, else_term: I) -> I;
    fn int_ite_scalar_else(&self, then_term: I, else_term: Int) -> I;
    fn int_ite_scalar_then_else(&self, then_term: Int, else_term: Int) -> I;
    fn real_ite(&self, then_term: R, else_term: R) -> R;
    fn real_ite_scalar_then(&self, then_term: Real, else_term: R) -> R;
    fn real_ite_scalar_else(&self, then_term: R, else_term: Real) -> R;
    fn real_ite_scalar_then_else(&self, then_term: Real, else_term: Real) -> R;
}

pub trait PureIntFuncOps: Sized + Alignable {
    fn new(domain_size: usize) -> Self;
    fn domain_len(&self) -> usize;

    fn add(&mut self, other: &Self);
    fn add_scalar(&mut self, other: Int);
    fn sub(&mut self, other: &Self);
    fn sub_scalar(&mut self, other: Int);
    fn mult(&mut self, other: &Self);
    fn mult_scalar(&mut self, other: Int);
    fn rem(&mut self, other: &Self);
    fn rem_scalar(&mut self, scalar: Int);
    fn rem_scalar_2(scalar: Int, this: &mut Self);
    fn neg(&mut self);
    fn sum_agg(
        &self,
        old_layout: &LayoutVec,
        new_layout: &LayoutVec,
        context: &InterpContext,
    ) -> OrScalar<Self, Int>;
    fn set(&mut self, index: DomainEnum, value: Int);
    fn get(&self, index: DomainEnum) -> Option<Int>;
    fn iter<'a>(&'a self) -> impl Iterator<Item = (DomainEnum, Int)> + 'a;
}

pub trait IntFunc<S, R, T>: PureIntFuncOps
where
    S: Set<Self, R, T>,
    R: RealFunc<S, Self, T>,
    T: TypeEnumFunc<S, Self, R>,
{
    fn lt(&self, other: &Self) -> S;
    fn lt_scalar(&self, s: Int) -> S;
    fn le(&self, other: &Self) -> S;
    fn le_scalar(&self, s: Int) -> S;
    fn gt(&self, other: &Self) -> S;
    fn gt_scalar(&self, s: Int) -> S;
    fn ge(&self, other: &Self) -> S;
    fn ge_scalar(&self, s: Int) -> S;
    fn eq(&self, other: &Self) -> S;
    fn eq_scalar(&self, s: Int) -> S;
    fn neq(&self, other: &Self) -> S;
    fn neq_scalar(&self, s: Int) -> S;
}

pub trait PureRealOps: Sized + Alignable {
    fn new(domain_size: usize) -> Self;
    fn domain_len(&self) -> usize;

    fn add(&mut self, other: &Self);
    fn add_scalar(&mut self, other: Real);
    fn sub(&mut self, other: &Self);
    fn sub_scalar(&mut self, other: Real);
    fn mult(&mut self, other: &Self);
    fn mult_scalar(&mut self, other: Real);
    fn div(&mut self, other: &Self);
    fn div_scalar(&mut self, other: Real);
    fn div_scalar_2(other: Real, this: &mut Self);
    fn rem(&mut self, other: &Self);
    fn rem_scalar(&mut self, scalar: Real);
    fn rem_scalar_2(scalar: Real, this: &mut Self);
    fn neg(&mut self);
    fn sum_agg(
        &self,
        old_layout: &LayoutVec,
        new_layout: &LayoutVec,
        context: &InterpContext,
    ) -> OrScalar<Self, Real>;
    fn set(&mut self, index: DomainEnum, value: Real);
    fn get(&self, index: DomainEnum) -> Option<Real>;
    fn iter<'a>(&'a self) -> impl Iterator<Item = (DomainEnum, Real)> + 'a;
}

pub trait RealFunc<S, I, T>: PureRealOps + From<I>
where
    S: Set<I, Self, T>,
    I: IntFunc<S, Self, T>,
    T: TypeEnumFunc<S, I, Self>,
{
    fn lt(&self, other: &Self) -> S;
    fn lt_scalar(&self, s: Real) -> S;
    fn le(&self, other: &Self) -> S;
    fn le_scalar(&self, s: Real) -> S;
    fn gt(&self, other: &Self) -> S;
    fn gt_scalar(&self, s: Real) -> S;
    fn ge(&self, other: &Self) -> S;
    fn ge_scalar(&self, s: Real) -> S;
    fn eq(&self, other: &Self) -> S;
    fn eq_scalar(&self, s: Real) -> S;
    fn neq(&self, other: &Self) -> S;
    fn neq_scalar(&self, s: Real) -> S;
    fn is_int(&self) -> S;
}

pub trait PureTypeEnumOps: Sized + Alignable {
    fn new(domain_size: usize) -> Self;
    fn domain_len(&self) -> usize;

    fn set(&mut self, index: DomainEnum, value: TypeEnum);
    fn iter<'a>(&'a self) -> impl Iterator<Item = (DomainEnum, TypeEnum)> + 'a;
    fn get(&self, index: DomainEnum) -> Option<TypeEnum>;
}

pub trait TypeEnumFunc<S, I, R>: PureTypeEnumOps
where
    S: Set<I, R, Self>,
    I: IntFunc<S, R, Self>,
    R: RealFunc<S, I, Self>,
{
    fn eq(&self, other: &Self) -> S;
    fn eq_scalar(&self, s: TypeEnum) -> S;
    fn neq(&self, other: &Self) -> S;
    fn neq_scalar(&self, s: TypeEnum) -> S;
}

pub trait Alignable: Sized {
    fn align(&mut self, aligned_layout: &AlignedLayout, context: &InterpContext);
}

pub(super) fn align_layout<L: Alignable, R: Alignable>(
    left: (&mut L, &mut LayoutVec),
    right: (&mut R, &mut LayoutVec),
    context: &InterpContext,
) {
    let (backend1, old_layout1) = left;
    let (backend2, old_layout2) = right;
    let (aligned_layout1, aligned_layout2) =
        align_layouts(old_layout1.clone(), old_layout2.clone());
    if aligned_layout1.is_different() {
        backend1.align(&aligned_layout1, context)
    }
    *old_layout1 = aligned_layout1.take_new_layout();
    if aligned_layout2.is_different() {
        backend2.align(&aligned_layout2, context)
    }
    *old_layout2 = aligned_layout2.take_new_layout();
}

pub trait SatSetAlias: Debug {
    type Set: Set<Self::IntFunc, Self::RealFunc, Self::TypeEnumFunc> + Debug + Clone;
    type IntFunc: IntFunc<Self::Set, Self::RealFunc, Self::TypeEnumFunc> + Debug + Clone;
    type RealFunc: RealFunc<Self::Set, Self::IntFunc, Self::TypeEnumFunc> + Debug + Clone;
    type TypeEnumFunc: TypeEnumFunc<Self::Set, Self::IntFunc, Self::RealFunc> + Debug + Clone;
}

#[derive(Debug, Clone)]
pub struct LayoutSatSet<S: SatSetAlias> {
    backend: S::Set,
    layout: LayoutVec,
}

impl<S: SatSetAlias> LayoutSatSet<S> {
    pub fn new(domain_size: usize, layout: LayoutVec) -> Self {
        Self {
            backend: S::Set::new(domain_size),
            layout,
        }
    }

    /// Variable Ids start from 0 to n where n is the size of the predicate domain.
    pub fn with_new_vars(pred: &complete::immutable::PredInterp) -> Self {
        Self {
            backend: S::Set::from_structure(pred),
            layout: pred
                .domain()
                .iter()
                .enumerate()
                .map(|(var, _)| BoundVarId::from(var))
                .collect(),
        }
    }

    pub fn from_raw(backend: S::Set, layout: LayoutVec) -> Self {
        Self { backend, layout }
    }

    pub fn layout(&self) -> &LayoutVec {
        &self.layout
    }

    pub(crate) fn mut_layout(&mut self) -> &mut LayoutVec {
        &mut self.layout
    }

    pub fn or(mut self, mut other: Self, context: &InterpContext) -> Self {
        align_layout(
            (&mut self.backend, &mut self.layout),
            (&mut other.backend, &mut other.layout),
            context,
        );
        self.backend.or(&other.backend);
        self
    }

    pub fn or_scalar(self, other: bool) -> OrScalar<Self, bool> {
        if other {
            OrScalar::Scalar(true)
        } else {
            OrScalar::Value(self)
        }
    }

    pub fn and(self, other: Self, context: &InterpContext) -> Self {
        let val = S::Set::natural_join(
            (self.backend, self.layout),
            (other.backend, other.layout),
            context,
        );
        return Self {
            backend: val.0,
            layout: val.1,
        };
    }

    pub fn and_scalar(self, other: bool) -> OrScalar<Self, bool> {
        if other {
            OrScalar::Value(self)
        } else {
            OrScalar::Scalar(false)
        }
    }

    pub fn xor(mut self, mut other: Self, context: &InterpContext) -> Self {
        align_layout(
            (&mut self.backend, &mut self.layout),
            (&mut other.backend, &mut other.layout),
            context,
        );
        self.backend.xor(&other.backend);
        self
    }

    pub fn xor_scalar(self, other: bool) -> OrScalar<Self, bool> {
        if other {
            OrScalar::Value(self.neg())
        } else {
            OrScalar::Value(self)
        }
    }

    pub fn neg(mut self) -> Self {
        self.backend.neg();
        self
    }

    pub fn quant(
        mut self,
        vars: &[BoundVarId],
        quant_type: QuantKind,
        context: &InterpContext,
    ) -> OrScalar<Self, bool> {
        let old_layout = self.layout.clone();
        self.layout
            .elim(old_layout.iter().map(|f| vars.contains(&f)));
        self.backend
            .quant(&old_layout, &self.layout, quant_type, context)
            .map_value(|f| Self {
                backend: f,
                layout: self.layout,
            })
    }

    pub fn exists(self, vars: &[BoundVarId], context: &InterpContext) -> OrScalar<Self, bool> {
        if vars.len() == 0 {
            OrScalar::Value(self)
        } else {
            self.quant(vars, QuantKind::ExQuant, context)
        }
    }

    pub fn universal(self, vars: &[BoundVarId], context: &InterpContext) -> OrScalar<Self, bool> {
        if vars.len() == 0 {
            OrScalar::Value(self)
        } else {
            self.quant(vars, QuantKind::UniQuant, context)
        }
    }

    pub fn card_agg(
        mut self,
        vars: &[BoundVarId],
        context: &InterpContext,
    ) -> OrScalar<LayoutIntFunc<S>, Int> {
        let old_layout = self.layout.clone();
        let unquantified_len = old_layout.unquantified_len(vars, context);
        self.layout
            .elim(old_layout.iter().map(|f| vars.contains(&f)));
        self.backend
            .card_agg(&old_layout, &self.layout, context)
            .map(
                |mut f| {
                    f.mult_scalar(unquantified_len.try_into().expect("Too big"));
                    LayoutIntFunc {
                        backend: f,
                        layout: self.layout,
                    }
                },
                |f| f * Int::try_from(unquantified_len).expect("Too big"),
            )
    }

    pub fn cardinality(&self) -> usize {
        self.backend.cardinality()
    }

    pub fn set(&mut self, index: DomainEnum) {
        self.backend.set(index)
    }

    pub fn unset(&mut self, index: DomainEnum) {
        self.backend.unset(index)
    }

    pub fn contains(&self, index: DomainEnum) -> bool {
        self.backend.contains(index)
    }

    pub fn iter<'a>(&'a self) -> impl Iterator<Item = DomainEnum> + 'a {
        self.backend.iter()
    }

    pub fn inner_ref(&self) -> &S::Set {
        &self.backend
    }

    pub fn inner(self) -> S::Set {
        self.backend
    }

    pub fn try_as_bool(&self) -> Option<bool> {
        if self.layout.len() == 0 {
            if self.contains(0.into()) {
                Some(true)
            } else {
                Some(false)
            }
        } else {
            None
        }
    }
}

#[duplicate_item(
    ite ite_scalar_then ite_scalar_else ite_scalar_then_else scalar Data DataConstr;
    [int_ite] [int_ite_scalar_then] [int_ite_scalar_else]
    [int_ite_scalar_then_else] [Int] [LayoutIntFunc<S>] [LayoutIntFunc];
    [real_ite] [real_ite_scalar_then] [real_ite_scalar_else]
    [real_ite_scalar_then_else] [Real] [LayoutRealFunc<S>] [LayoutRealFunc];
)]
impl<S: SatSetAlias> LayoutSatSet<S> {
    pub fn ite(
        mut self,
        mut then_term: Data,
        mut else_term: Data,
        context: &InterpContext,
    ) -> Data {
        align_layout(
            (&mut self.backend, &mut self.layout),
            (&mut then_term.backend, &mut then_term.layout),
            context,
        );
        align_layout(
            (&mut then_term.backend, &mut then_term.layout),
            (&mut else_term.backend, &mut else_term.layout),
            context,
        );
        DataConstr {
            backend: self.backend.ite(then_term.backend, else_term.backend),
            layout: self.layout,
        }
    }

    pub fn ite_scalar_then(
        mut self,
        then_term: scalar,
        mut else_term: Data,
        context: &InterpContext,
    ) -> Data {
        align_layout(
            (&mut self.backend, &mut self.layout),
            (&mut else_term.backend, &mut else_term.layout),
            context,
        );
        DataConstr {
            backend: self.backend.ite_scalar_then(then_term, else_term.backend),
            layout: self.layout,
        }
    }

    pub fn ite_scalar_else(
        mut self,
        mut then_term: Data,
        else_term: scalar,
        context: &InterpContext,
    ) -> Data {
        align_layout(
            (&mut self.backend, &mut self.layout),
            (&mut then_term.backend, &mut then_term.layout),
            context,
        );
        DataConstr {
            backend: self.backend.ite_scalar_else(then_term.backend, else_term),
            layout: self.layout,
        }
    }

    pub fn ite_scalar_then_else(self, then_term: scalar, else_term: scalar) -> Data {
        DataConstr {
            backend: self.backend.ite_scalar_then_else(then_term, else_term),
            layout: self.layout,
        }
    }
}

impl<S: SatSetAlias> LayoutSatSet<S> {
    pub fn type_enum_ite(
        mut self,
        mut then_term: LayoutTypeEnumFunc<S>,
        mut else_term: LayoutTypeEnumFunc<S>,
        context: &InterpContext,
    ) -> Result<LayoutTypeEnumFunc<S>, VecError> {
        if then_term.type_part != else_term.type_part {
            return Err(VecError::TypeMismatch);
        }
        align_layout(
            (&mut self.backend, &mut self.layout),
            (&mut then_term.backend, &mut then_term.layout),
            context,
        );
        align_layout(
            (&mut then_term.backend, &mut then_term.layout),
            (&mut else_term.backend, &mut else_term.layout),
            context,
        );
        Ok(LayoutTypeEnumFunc {
            backend: self
                .backend
                .type_enum_ite(then_term.backend, else_term.backend),
            layout: self.layout,
            type_part: then_term.type_part,
        })
    }

    pub fn type_enum_ite_scalar_then(
        mut self,
        then_term: TypeElementIndex,
        mut else_term: LayoutTypeEnumFunc<S>,
        context: &InterpContext,
    ) -> Result<LayoutTypeEnumFunc<S>, VecError> {
        if then_term.0 != else_term.type_part {
            return Err(VecError::TypeMismatch);
        }
        align_layout(
            (&mut self.backend, &mut self.layout),
            (&mut else_term.backend, &mut else_term.layout),
            context,
        );
        Ok(LayoutTypeEnumFunc {
            backend: self
                .backend
                .type_enum_ite_scalar_then(then_term.1, else_term.backend),
            layout: self.layout,
            type_part: else_term.type_part,
        })
    }

    pub fn type_enum_ite_scalar_else(
        mut self,
        mut then_term: LayoutTypeEnumFunc<S>,
        else_term: TypeElementIndex,
        context: &InterpContext,
    ) -> Result<LayoutTypeEnumFunc<S>, VecError> {
        if then_term.type_part != else_term.0 {
            return Err(VecError::TypeMismatch);
        }
        align_layout(
            (&mut self.backend, &mut self.layout),
            (&mut then_term.backend, &mut then_term.layout),
            context,
        );
        Ok(LayoutTypeEnumFunc {
            backend: self
                .backend
                .type_enum_ite_scalar_else(then_term.backend, else_term.1),
            layout: self.layout,
            type_part: then_term.type_part,
        })
    }

    pub fn type_enum_ite_scalar_then_else(
        self,
        then_term: TypeElementIndex,
        else_term: TypeElementIndex,
    ) -> Result<LayoutTypeEnumFunc<S>, VecError> {
        if then_term.0 != else_term.0 {
            return Err(VecError::TypeMismatch);
        }
        Ok(LayoutTypeEnumFunc {
            backend: self
                .backend
                .type_enum_ite_scalar_then_else(then_term.1, else_term.1),
            layout: self.layout,
            type_part: then_term.0,
        })
    }
}

#[derive(Debug, Clone)]
pub struct LayoutIntFunc<S: SatSetAlias> {
    backend: S::IntFunc,
    layout: LayoutVec,
}

impl<S: SatSetAlias> LayoutIntFunc<S> {
    pub fn new(domain_size: usize, layout: LayoutVec) -> Self {
        Self {
            backend: S::IntFunc::new(domain_size),
            layout,
        }
    }

    pub fn layout(&self) -> &LayoutVec {
        &self.layout
    }

    pub fn mut_layout(&mut self) -> &mut LayoutVec {
        &mut self.layout
    }

    pub fn inner(self) -> S::IntFunc {
        self.backend
    }

    pub fn lt(mut self, mut other: Self, context: &InterpContext) -> LayoutSatSet<S> {
        align_layout(
            (&mut self.backend, &mut self.layout),
            (&mut other.backend, &mut other.layout),
            context,
        );
        LayoutSatSet {
            backend: self.backend.lt(&other.backend),
            layout: self.layout,
        }
    }

    pub fn lt_scalar(self, s: Int) -> LayoutSatSet<S> {
        LayoutSatSet {
            backend: self.backend.lt_scalar(s),
            layout: self.layout,
        }
    }

    pub fn le(mut self, mut other: Self, context: &InterpContext) -> LayoutSatSet<S> {
        align_layout(
            (&mut self.backend, &mut self.layout),
            (&mut other.backend, &mut other.layout),
            context,
        );
        LayoutSatSet {
            backend: self.backend.le(&other.backend),
            layout: self.layout,
        }
    }

    pub fn le_scalar(self, s: Int) -> LayoutSatSet<S> {
        LayoutSatSet {
            backend: self.backend.le_scalar(s),
            layout: self.layout,
        }
    }

    pub fn gt(mut self, mut other: Self, context: &InterpContext) -> LayoutSatSet<S> {
        align_layout(
            (&mut self.backend, &mut self.layout),
            (&mut other.backend, &mut other.layout),
            context,
        );
        LayoutSatSet {
            backend: self.backend.gt(&other.backend),
            layout: self.layout,
        }
    }

    pub fn gt_scalar(self, s: Int) -> LayoutSatSet<S> {
        LayoutSatSet {
            backend: self.backend.gt_scalar(s),
            layout: self.layout,
        }
    }

    pub fn ge(mut self, mut other: Self, context: &InterpContext) -> LayoutSatSet<S> {
        align_layout(
            (&mut self.backend, &mut self.layout),
            (&mut other.backend, &mut other.layout),
            context,
        );
        LayoutSatSet {
            backend: self.backend.ge(&other.backend),
            layout: self.layout,
        }
    }

    pub fn ge_scalar(self, s: Int) -> LayoutSatSet<S> {
        LayoutSatSet {
            backend: self.backend.ge_scalar(s),
            layout: self.layout,
        }
    }

    pub fn eq(mut self, mut other: Self, context: &InterpContext) -> LayoutSatSet<S> {
        align_layout(
            (&mut self.backend, &mut self.layout),
            (&mut other.backend, &mut other.layout),
            context,
        );
        LayoutSatSet {
            backend: self.backend.eq(&other.backend),
            layout: self.layout,
        }
    }

    pub fn eq_scalar(self, s: Int) -> LayoutSatSet<S> {
        LayoutSatSet {
            backend: self.backend.eq_scalar(s),
            layout: self.layout,
        }
    }

    pub fn neq(mut self, mut other: Self, context: &InterpContext) -> LayoutSatSet<S> {
        align_layout(
            (&mut self.backend, &mut self.layout),
            (&mut other.backend, &mut other.layout),
            context,
        );
        LayoutSatSet {
            backend: self.backend.neq(&other.backend),
            layout: self.layout,
        }
    }

    pub fn neq_scalar(self, s: Int) -> LayoutSatSet<S> {
        LayoutSatSet {
            backend: self.backend.neq_scalar(s),
            layout: self.layout,
        }
    }

    pub fn add(mut self, mut other: Self, context: &InterpContext) -> Self {
        align_layout(
            (&mut self.backend, &mut self.layout),
            (&mut other.backend, &mut other.layout),
            context,
        );
        self.backend.add(&other.backend);
        self
    }

    pub fn add_scalar(mut self, s: Int) -> Self {
        self.backend.add_scalar(s);
        self
    }

    pub fn sub(mut self, mut other: Self, context: &InterpContext) -> Self {
        align_layout(
            (&mut self.backend, &mut self.layout),
            (&mut other.backend, &mut other.layout),
            context,
        );
        self.backend.sub(&other.backend);
        self
    }

    pub fn sub_scalar(mut self, s: Int) -> Self {
        self.backend.sub_scalar(s);
        self
    }

    pub fn mult(mut self, mut other: Self, context: &InterpContext) -> Self {
        align_layout(
            (&mut self.backend, &mut self.layout),
            (&mut other.backend, &mut other.layout),
            context,
        );
        self.backend.mult(&other.backend);
        self
    }

    pub fn mult_scalar(mut self, s: Int) -> Self {
        self.backend.mult_scalar(s);
        self
    }

    pub fn rem(mut self, mut other: Self, context: &InterpContext) -> Self {
        align_layout(
            (&mut self.backend, &mut self.layout),
            (&mut other.backend, &mut other.layout),
            context,
        );
        self.backend.rem(&other.backend);
        self
    }

    pub fn rem_scalar(mut self, s: Int) -> Self {
        self.backend.rem_scalar(s);
        self
    }

    pub fn rem_scalar_2(s: Int, mut this: Self) -> Self {
        PureIntFuncOps::rem_scalar_2(s, &mut this.backend);
        this
    }

    pub fn neg(mut self) -> Self {
        self.backend.neg();
        self
    }

    pub fn get(&self, index: DomainEnum) -> Option<Int> {
        self.backend.get(index)
    }

    pub fn sum_agg(mut self, vars: &[BoundVarId], context: &InterpContext) -> OrScalar<Self, Int> {
        let old_layout = self.layout.clone();
        let unquantified_len = old_layout.unquantified_len(vars, context);
        self.layout
            .elim(old_layout.iter().map(|f| vars.contains(&f)));
        self.backend
            .sum_agg(&old_layout, &self.layout, context)
            .map(
                |mut f| {
                    f.mult_scalar(unquantified_len.try_into().expect("Too big"));
                    Self {
                        backend: f,
                        layout: self.layout,
                    }
                },
                |f| f * Int::try_from(unquantified_len).expect("Too big"),
            )
    }

    pub fn set(&mut self, index: DomainEnum, value: Int) {
        self.backend.set(index, value)
    }

    pub fn try_as_int(&self) -> Option<Int> {
        if self.layout.len() == 0 {
            self.get(0.into())
        } else {
            None
        }
    }
}

#[derive(Debug, Clone)]
pub struct LayoutRealFunc<S: SatSetAlias> {
    backend: S::RealFunc,
    layout: LayoutVec,
}

impl<S: SatSetAlias> From<LayoutIntFunc<S>> for LayoutRealFunc<S> {
    fn from(value: LayoutIntFunc<S>) -> Self {
        Self {
            backend: value.backend.into(),
            layout: value.layout,
        }
    }
}

impl<S: SatSetAlias> LayoutRealFunc<S> {
    pub fn new(domain_size: usize, layout: LayoutVec) -> Self {
        Self {
            backend: S::RealFunc::new(domain_size),
            layout,
        }
    }

    pub fn inner(self) -> S::RealFunc {
        self.backend
    }

    pub fn layout(&self) -> &LayoutVec {
        &self.layout
    }

    pub fn mut_layout(&mut self) -> &mut LayoutVec {
        &mut self.layout
    }

    pub fn lt(mut self, mut other: Self, context: &InterpContext) -> LayoutSatSet<S> {
        align_layout(
            (&mut self.backend, &mut self.layout),
            (&mut other.backend, &mut other.layout),
            context,
        );
        LayoutSatSet {
            backend: self.backend.lt(&other.backend),
            layout: self.layout,
        }
    }

    pub fn lt_scalar(self, s: Real) -> LayoutSatSet<S> {
        LayoutSatSet {
            backend: self.backend.lt_scalar(s),
            layout: self.layout,
        }
    }

    pub fn le(mut self, mut other: Self, context: &InterpContext) -> LayoutSatSet<S> {
        align_layout(
            (&mut self.backend, &mut self.layout),
            (&mut other.backend, &mut other.layout),
            context,
        );
        LayoutSatSet {
            backend: self.backend.le(&other.backend),
            layout: self.layout,
        }
    }

    pub fn le_scalar(self, s: Real) -> LayoutSatSet<S> {
        LayoutSatSet {
            backend: self.backend.le_scalar(s),
            layout: self.layout,
        }
    }

    pub fn gt(mut self, mut other: Self, context: &InterpContext) -> LayoutSatSet<S> {
        align_layout(
            (&mut self.backend, &mut self.layout),
            (&mut other.backend, &mut other.layout),
            context,
        );
        LayoutSatSet {
            backend: self.backend.gt(&other.backend),
            layout: self.layout,
        }
    }

    pub fn gt_scalar(self, s: Real) -> LayoutSatSet<S> {
        LayoutSatSet {
            backend: self.backend.gt_scalar(s),
            layout: self.layout,
        }
    }

    pub fn ge(mut self, mut other: Self, context: &InterpContext) -> LayoutSatSet<S> {
        align_layout(
            (&mut self.backend, &mut self.layout),
            (&mut other.backend, &mut other.layout),
            context,
        );
        LayoutSatSet {
            backend: self.backend.ge(&other.backend),
            layout: self.layout,
        }
    }

    pub fn ge_scalar(self, s: Real) -> LayoutSatSet<S> {
        LayoutSatSet {
            backend: self.backend.ge_scalar(s),
            layout: self.layout,
        }
    }

    pub fn eq(mut self, mut other: Self, context: &InterpContext) -> LayoutSatSet<S> {
        align_layout(
            (&mut self.backend, &mut self.layout),
            (&mut other.backend, &mut other.layout),
            context,
        );
        LayoutSatSet {
            backend: self.backend.eq(&other.backend),
            layout: self.layout,
        }
    }

    pub fn eq_scalar(self, s: Real) -> LayoutSatSet<S> {
        LayoutSatSet {
            backend: self.backend.eq_scalar(s),
            layout: self.layout,
        }
    }

    pub fn neq(mut self, mut other: Self, context: &InterpContext) -> LayoutSatSet<S> {
        align_layout(
            (&mut self.backend, &mut self.layout),
            (&mut other.backend, &mut other.layout),
            context,
        );
        LayoutSatSet {
            backend: self.backend.neq(&other.backend),
            layout: self.layout,
        }
    }

    pub fn neq_scalar(self, s: Real) -> LayoutSatSet<S> {
        LayoutSatSet {
            backend: self.backend.neq_scalar(s),
            layout: self.layout,
        }
    }

    pub fn add(mut self, mut other: Self, context: &InterpContext) -> Self {
        align_layout(
            (&mut self.backend, &mut self.layout),
            (&mut other.backend, &mut other.layout),
            context,
        );
        self.backend.add(&other.backend);
        self
    }

    pub fn add_scalar(mut self, s: Real) -> Self {
        self.backend.add_scalar(s);
        self
    }

    pub fn sub(mut self, mut other: Self, context: &InterpContext) -> Self {
        align_layout(
            (&mut self.backend, &mut self.layout),
            (&mut other.backend, &mut other.layout),
            context,
        );
        self.backend.sub(&other.backend);
        self
    }

    pub fn sub_scalar(mut self, s: Real) -> Self {
        self.backend.sub_scalar(s);
        self
    }

    pub fn mult(mut self, mut other: Self, context: &InterpContext) -> Self {
        align_layout(
            (&mut self.backend, &mut self.layout),
            (&mut other.backend, &mut other.layout),
            context,
        );
        self.backend.mult(&other.backend);
        self
    }

    pub fn mult_scalar(mut self, s: Real) -> Self {
        self.backend.mult_scalar(s);
        self
    }

    pub fn div(mut self, mut other: Self, context: &InterpContext) -> Self {
        align_layout(
            (&mut self.backend, &mut self.layout),
            (&mut other.backend, &mut other.layout),
            context,
        );
        self.backend.div(&other.backend);
        self
    }

    pub fn div_scalar(mut self, s: Real) -> Self {
        self.backend.div_scalar(s);
        self
    }

    pub fn div_scalar_2(s: Real, mut this: Self) -> Self {
        PureRealOps::div_scalar_2(s, &mut this.backend);
        this
    }

    pub fn rem(mut self, mut other: Self, context: &InterpContext) -> Self {
        align_layout(
            (&mut self.backend, &mut self.layout),
            (&mut other.backend, &mut other.layout),
            context,
        );
        self.backend.rem(&other.backend);
        self
    }

    pub fn rem_scalar(mut self, s: Real) -> Self {
        self.backend.rem_scalar(s);
        self
    }

    pub fn rem_scalar_2(s: Real, mut this: Self) -> Self {
        PureRealOps::rem_scalar_2(s, &mut this.backend);
        this
    }

    pub fn neg(mut self) -> Self {
        self.backend.neg();
        self
    }

    pub fn is_int(self) -> LayoutSatSet<S> {
        LayoutSatSet {
            backend: self.backend.is_int(),
            layout: self.layout,
        }
    }

    pub fn get(&self, index: DomainEnum) -> Option<Real> {
        self.backend.get(index)
    }

    pub fn sum_agg(mut self, vars: &[BoundVarId], context: &InterpContext) -> OrScalar<Self, Real> {
        let old_layout = self.layout.clone();
        let unquantified_len = old_layout.unquantified_len(vars, context);
        self.layout
            .elim(old_layout.iter().map(|f| vars.contains(&f)));
        self.backend
            .sum_agg(&old_layout, &self.layout, context)
            .map(
                |mut f| {
                    f.mult_scalar(unquantified_len.try_into().expect("Too big"));
                    Self {
                        backend: f,
                        layout: self.layout,
                    }
                },
                |f| Real::mult(f, unquantified_len.try_into().expect("Too big")).expect("Too big"),
            )
    }

    pub fn set(&mut self, index: DomainEnum, value: Real) {
        self.backend.set(index, value)
    }

    pub fn try_as_real(&self) -> Option<Real> {
        if self.layout.len() == 0 {
            self.get(0.into())
        } else {
            None
        }
    }
}

#[derive(Debug, Clone)]
pub struct LayoutTypeEnumFunc<S: SatSetAlias> {
    backend: S::TypeEnumFunc,
    layout: LayoutVec,
    type_part: TypeIndex,
}

impl<S: SatSetAlias> LayoutTypeEnumFunc<S> {
    pub fn new(domain_size: usize, layout: LayoutVec, type_index: TypeIndex) -> Self {
        Self {
            backend: S::TypeEnumFunc::new(domain_size),
            layout,
            type_part: type_index,
        }
    }

    pub fn inner(self) -> S::TypeEnumFunc {
        self.backend
    }

    pub fn layout(&self) -> &LayoutVec {
        &self.layout
    }

    pub fn mut_layout(&mut self) -> &mut LayoutVec {
        &mut self.layout
    }

    pub fn eq(mut self, mut other: Self, context: &InterpContext) -> LayoutSatSet<S> {
        align_layout(
            (&mut self.backend, &mut self.layout),
            (&mut other.backend, &mut other.layout),
            context,
        );
        LayoutSatSet {
            backend: self.backend.eq(&other.backend),
            layout: self.layout,
        }
    }

    pub fn eq_scalar(self, s: TypeEnum) -> LayoutSatSet<S> {
        LayoutSatSet {
            backend: self.backend.eq_scalar(s),
            layout: self.layout,
        }
    }

    pub fn neq(mut self, mut other: Self, context: &InterpContext) -> LayoutSatSet<S> {
        align_layout(
            (&mut self.backend, &mut self.layout),
            (&mut other.backend, &mut other.layout),
            context,
        );
        LayoutSatSet {
            backend: self.backend.neq(&other.backend),
            layout: self.layout,
        }
    }

    pub fn neq_scalar(self, s: TypeEnum) -> LayoutSatSet<S> {
        LayoutSatSet {
            backend: self.backend.neq_scalar(s),
            layout: self.layout,
        }
    }

    pub fn len(&self) -> usize {
        self.backend.domain_len()
    }

    pub fn get(&self, index: DomainEnum) -> Option<TypeElementIndex> {
        self.backend
            .get(index)
            .map(|f| TypeElementIndex(self.get_type_index(), f))
    }

    pub fn try_as_type_element(&self) -> Option<TypeElementIndex> {
        if self.layout.len() == 0 {
            self.get(0.into()).into()
        } else {
            None
        }
    }

    pub fn get_type_index(&self) -> TypeIndex {
        self.type_part
    }

    pub fn set(&mut self, index: DomainEnum, value: TypeEnum) {
        self.backend.set(index, value)
    }
}

#[derive(Debug, Clone)]
pub enum LayoutSymbol<S>
where
    S: SatSetAlias,
{
    Scalar(TypeElement),
    Predicate(LayoutSatSet<S>),
    Int(LayoutIntFunc<S>),
    Real(LayoutRealFunc<S>),
    TypeEnum(LayoutTypeEnumFunc<S>),
}

impl<S> From<bool> for LayoutSymbol<S>
where
    S: SatSetAlias,
{
    fn from(value: bool) -> Self {
        Self::Scalar(value.into())
    }
}

impl<S> From<LayoutSatSet<S>> for LayoutSymbol<S>
where
    S: SatSetAlias,
{
    fn from(value: LayoutSatSet<S>) -> Self {
        Self::Predicate(value)
    }
}

impl<S> From<LayoutIntFunc<S>> for LayoutSymbol<S>
where
    S: SatSetAlias,
{
    fn from(value: LayoutIntFunc<S>) -> Self {
        Self::Int(value)
    }
}

impl<S> From<LayoutRealFunc<S>> for LayoutSymbol<S>
where
    S: SatSetAlias,
{
    fn from(value: LayoutRealFunc<S>) -> Self {
        Self::Real(value)
    }
}

impl<S> From<LayoutTypeEnumFunc<S>> for LayoutSymbol<S>
where
    S: SatSetAlias,
{
    fn from(value: LayoutTypeEnumFunc<S>) -> Self {
        Self::TypeEnum(value)
    }
}

impl<S> From<TypeElement> for LayoutSymbol<S>
where
    S: SatSetAlias,
{
    fn from(value: TypeElement) -> Self {
        Self::Scalar(value)
    }
}

impl<S> From<Int> for LayoutSymbol<S>
where
    S: SatSetAlias,
{
    fn from(value: Int) -> Self {
        Self::Scalar(value.into())
    }
}

impl<S> From<Real> for LayoutSymbol<S>
where
    S: SatSetAlias,
{
    fn from(value: Real) -> Self {
        Self::Scalar(value.into())
    }
}

impl<S> From<TypeElementIndex> for LayoutSymbol<S>
where
    S: SatSetAlias,
{
    fn from(value: TypeElementIndex) -> Self {
        Self::Scalar(value.into())
    }
}

#[derive(Debug)]
pub enum VecError {
    TypeMismatch,
}

impl<S: SatSetAlias> LayoutSymbol<S> {
    pub(crate) fn mut_layout(&mut self) -> Option<&mut LayoutVec> {
        match self {
            Self::Real(real) => Some(real.mut_layout()),
            Self::Int(int) => Some(int.mut_layout()),
            Self::Predicate(pred) => Some(pred.mut_layout()),
            Self::TypeEnum(custom) => Some(custom.mut_layout()),
            Self::Scalar(_) => None,
        }
    }

    pub fn or(self, other: Self, context: &InterpContext) -> Result<Self, VecError> {
        let sv = match (self, other) {
            (Self::Predicate(p1), Self::Predicate(p2)) => Self::Predicate(p1.or(p2, context)),
            (Self::Predicate(p), Self::Scalar(TypeElement::Bool(s)))
            | (Self::Scalar(TypeElement::Bool(s)), Self::Predicate(p)) => p
                .or_scalar(s)
                .map_to_single(Self::Predicate, |f| Self::Scalar(f.into())),
            (Self::Scalar(TypeElement::Bool(b1)), Self::Scalar(TypeElement::Bool(b2))) => {
                Self::Scalar((b1 | b2).into())
            }
            _ => return Err(VecError::TypeMismatch),
        };
        Ok(sv.try_as_scalar())
    }

    pub fn xor(self, other: Self, context: &InterpContext) -> Result<Self, VecError> {
        let sv = match (self, other) {
            (Self::Predicate(p1), Self::Predicate(p2)) => Self::Predicate(p1.xor(p2, context)),
            (Self::Predicate(p), Self::Scalar(TypeElement::Bool(s)))
            | (Self::Scalar(TypeElement::Bool(s)), Self::Predicate(p)) => p
                .xor_scalar(s)
                .map_to_single(Self::Predicate, |f| Self::Scalar(f.into())),
            (Self::Scalar(TypeElement::Bool(b1)), Self::Scalar(TypeElement::Bool(b2))) => {
                Self::Scalar((b1 ^ b2).into())
            }
            _ => return Err(VecError::TypeMismatch),
        };
        Ok(sv.try_as_scalar())
    }

    pub fn and(self, other: Self, context: &InterpContext) -> Result<Self, VecError> {
        let sv = match (self, other) {
            (Self::Predicate(p1), Self::Predicate(p2)) => Self::Predicate(p1.and(p2, context)),
            (Self::Predicate(p), Self::Scalar(TypeElement::Bool(s)))
            | (Self::Scalar(TypeElement::Bool(s)), Self::Predicate(p)) => p
                .and_scalar(s)
                .map_to_single(Self::Predicate, |f| Self::Scalar(f.into())),
            (Self::Scalar(TypeElement::Bool(b1)), Self::Scalar(TypeElement::Bool(b2))) => {
                Self::Scalar((b1 & b2).into())
            }
            _ => return Err(VecError::TypeMismatch),
        };
        Ok(sv.try_as_scalar())
    }

    pub fn neg(self) -> Result<Self, VecError> {
        match self {
            Self::Predicate(p1) => {
                let res = p1.neg();
                if let Some(b) = res.try_as_bool() {
                    Ok(b.into())
                } else {
                    Ok(Self::Predicate(res.into()))
                }
            }
            Self::Scalar(TypeElement::Bool(b)) => Ok(Self::Scalar((!b).into())),
            _ => Err(VecError::TypeMismatch),
        }
    }

    pub fn num_neg(self) -> Result<Self, VecError> {
        match self {
            Self::Int(value) => Ok(value.neg().into()),
            Self::Real(value) => Ok(value.neg().into()),
            Self::Scalar(TypeElement::Int(b)) => Ok(Self::Scalar((-b).into())),
            Self::Scalar(TypeElement::Real(b)) => Ok(Self::Scalar((-b).into())),
            _ => Err(VecError::TypeMismatch),
        }
    }

    pub fn lt(self, other: Self, context: &InterpContext) -> Result<Self, VecError> {
        let sv = match (self, other) {
            (Self::Int(i1), Self::Int(i2)) => i1.lt(i2, context).into(),
            // Int Scalar
            (Self::Int(i), Self::Scalar(TypeElement::Int(s))) => i.lt_scalar(s).into(),
            (Self::Scalar(TypeElement::Int(s)), Self::Int(i)) => i.gt_scalar(s).into(),
            // Real
            (Self::Real(r1), Self::Real(r2)) => r1.lt(r2, context).into(),
            // Real Int
            (Self::Real(r), Self::Int(i)) => r.lt(i.into(), context).into(),
            (Self::Int(i), Self::Real(r)) => LayoutRealFunc::from(i).lt(r, context).into(),
            // Real scalar
            (Self::Real(r), Self::Scalar(TypeElement::Real(s_r))) => r.lt_scalar(s_r.into()).into(),
            (Self::Scalar(TypeElement::Real(s_r)), Self::Real(r)) => r.gt_scalar(s_r.into()).into(),
            // Real Int scalar
            (Self::Real(r), Self::Scalar(TypeElement::Int(s_i))) => r.lt_scalar(s_i.into()).into(),
            (Self::Scalar(TypeElement::Int(s_i)), Self::Real(r)) => r.gt_scalar(s_i.into()).into(),
            // Int Real scalar
            (Self::Int(i), Self::Scalar(TypeElement::Real(s_r))) => {
                LayoutRealFunc::from(i).lt_scalar(s_r.into()).into()
            }
            (Self::Scalar(TypeElement::Real(s_r)), Self::Int(i)) => {
                LayoutRealFunc::from(i).gt_scalar(s_r.into()).into()
            }
            // Scalars
            (Self::Scalar(TypeElement::Int(i1)), Self::Scalar(TypeElement::Int(i2))) => {
                Self::Scalar((i1 < i2).into())
            }
            (Self::Scalar(TypeElement::Int(i)), Self::Scalar(TypeElement::Real(r))) => {
                TypeElement::from(i < r).into()
            }
            (Self::Scalar(TypeElement::Real(r)), Self::Scalar(TypeElement::Int(i))) => {
                TypeElement::from(r < i).into()
            }
            (Self::Scalar(TypeElement::Real(r1)), Self::Scalar(TypeElement::Real(r2))) => {
                Self::Scalar((r1 < r2).into())
            }
            _ => return Err(VecError::TypeMismatch),
        };
        Ok(sv.try_as_scalar())
    }

    pub fn le(self, other: Self, context: &InterpContext) -> Result<Self, VecError> {
        let sv = match (self, other) {
            (Self::Int(i1), Self::Int(i2)) => i1.le(i2, context).into(),
            // Int Scalar
            (Self::Int(i), Self::Scalar(TypeElement::Int(s))) => i.le_scalar(s).into(),
            (Self::Scalar(TypeElement::Int(s)), Self::Int(i)) => i.ge_scalar(s).into(),
            // Real
            (Self::Real(r1), Self::Real(r2)) => r1.le(r2, context).into(),
            // Real Int
            (Self::Real(r), Self::Int(i)) => r.le(i.into(), context).into(),
            (Self::Int(i), Self::Real(r)) => LayoutRealFunc::from(i).le(r, context).into(),
            // Real scalar
            (Self::Real(r), Self::Scalar(TypeElement::Real(s_r))) => r.le_scalar(s_r.into()).into(),
            (Self::Scalar(TypeElement::Real(s_r)), Self::Real(r)) => r.ge_scalar(s_r.into()).into(),
            // Real Int scalar
            (Self::Real(r), Self::Scalar(TypeElement::Int(s_i))) => r.le_scalar(s_i.into()).into(),
            (Self::Scalar(TypeElement::Int(s_i)), Self::Real(r)) => r.ge_scalar(s_i.into()).into(),
            // Int Real scalar
            (Self::Int(i), Self::Scalar(TypeElement::Real(s_r))) => {
                LayoutRealFunc::from(i).le_scalar(s_r.into()).into()
            }
            (Self::Scalar(TypeElement::Real(s_r)), Self::Int(i)) => {
                LayoutRealFunc::from(i).ge_scalar(s_r.into()).into()
            }
            // Scalars
            (Self::Scalar(TypeElement::Int(i1)), Self::Scalar(TypeElement::Int(i2))) => {
                Self::Scalar((i1 <= i2).into())
            }
            (Self::Scalar(TypeElement::Int(i)), Self::Scalar(TypeElement::Real(r))) => {
                TypeElement::from(i <= r).into()
            }
            (Self::Scalar(TypeElement::Real(r)), Self::Scalar(TypeElement::Int(i))) => {
                TypeElement::from(r <= i).into()
            }
            (Self::Scalar(TypeElement::Real(r1)), Self::Scalar(TypeElement::Real(r2))) => {
                Self::Scalar((r1 <= r2).into())
            }
            _ => return Err(VecError::TypeMismatch),
        };
        Ok(sv.try_as_scalar())
    }

    pub fn gt(self, other: Self, context: &InterpContext) -> Result<Self, VecError> {
        let sv = match (self, other) {
            (Self::Int(i1), Self::Int(i2)) => i1.gt(i2, context).into(),
            // Int Scalar
            (Self::Int(i), Self::Scalar(TypeElement::Int(s))) => i.gt_scalar(s).into(),
            (Self::Scalar(TypeElement::Int(s)), Self::Int(i)) => i.lt_scalar(s).into(),
            // Real
            (Self::Real(r1), Self::Real(r2)) => r1.gt(r2, context).into(),
            // Real Int
            (Self::Real(r), Self::Int(i)) => r.gt(i.into(), context).into(),
            (Self::Int(i), Self::Real(r)) => LayoutRealFunc::from(i).gt(r, context).into(),
            // Real scalar
            (Self::Real(r), Self::Scalar(TypeElement::Real(s_r))) => r.gt_scalar(s_r.into()).into(),
            (Self::Scalar(TypeElement::Real(s_r)), Self::Real(r)) => r.lt_scalar(s_r.into()).into(),
            // Real Int scalar
            (Self::Real(r), Self::Scalar(TypeElement::Int(s_i))) => r.gt_scalar(s_i.into()).into(),
            (Self::Scalar(TypeElement::Int(s_i)), Self::Real(r)) => r.lt_scalar(s_i.into()).into(),
            // Int Real scalar
            (Self::Int(i), Self::Scalar(TypeElement::Real(s_r))) => {
                LayoutRealFunc::from(i).gt_scalar(s_r.into()).into()
            }
            (Self::Scalar(TypeElement::Real(s_r)), Self::Int(i)) => {
                LayoutRealFunc::from(i).lt_scalar(s_r.into()).into()
            }
            // Scalars
            (Self::Scalar(TypeElement::Int(i1)), Self::Scalar(TypeElement::Int(i2))) => {
                Self::Scalar((i1 > i2).into())
            }
            (Self::Scalar(TypeElement::Int(i)), Self::Scalar(TypeElement::Real(r))) => {
                TypeElement::from(i > r).into()
            }
            (Self::Scalar(TypeElement::Real(r)), Self::Scalar(TypeElement::Int(i))) => {
                TypeElement::from(r > i).into()
            }
            (Self::Scalar(TypeElement::Real(r1)), Self::Scalar(TypeElement::Real(r2))) => {
                Self::Scalar((r1 > r2).into())
            }
            _ => return Err(VecError::TypeMismatch),
        };
        Ok(sv.try_as_scalar())
    }

    pub fn ge(self, other: Self, context: &InterpContext) -> Result<Self, VecError> {
        let sv = match (self, other) {
            (Self::Int(i1), Self::Int(i2)) => i1.ge(i2, context).into(),
            // Int Scalar
            (Self::Int(i), Self::Scalar(TypeElement::Int(s))) => i.ge_scalar(s).into(),
            (Self::Scalar(TypeElement::Int(s)), Self::Int(i)) => i.le_scalar(s).into(),
            // Real
            (Self::Real(r1), Self::Real(r2)) => r1.ge(r2, context).into(),
            // Real Int
            (Self::Real(r), Self::Int(i)) => r.ge(i.into(), context).into(),
            (Self::Int(i), Self::Real(r)) => LayoutRealFunc::from(i).ge(r, context).into(),
            // Real scalar
            (Self::Real(r), Self::Scalar(TypeElement::Real(s_r))) => r.ge_scalar(s_r.into()).into(),
            (Self::Scalar(TypeElement::Real(s_r)), Self::Real(r)) => r.le_scalar(s_r.into()).into(),
            // Real Int scalar
            (Self::Real(r), Self::Scalar(TypeElement::Int(s_i))) => r.ge_scalar(s_i.into()).into(),
            (Self::Scalar(TypeElement::Int(s_i)), Self::Real(r)) => r.le_scalar(s_i.into()).into(),
            // Int Real scalar
            (Self::Int(i), Self::Scalar(TypeElement::Real(s_r))) => {
                LayoutRealFunc::from(i).ge_scalar(s_r.into()).into()
            }
            (Self::Scalar(TypeElement::Real(s_r)), Self::Int(i)) => {
                LayoutRealFunc::from(i).le_scalar(s_r.into()).into()
            }
            // Scalars
            (Self::Scalar(TypeElement::Int(i1)), Self::Scalar(TypeElement::Int(i2))) => {
                Self::Scalar((i1 >= i2).into())
            }
            (Self::Scalar(TypeElement::Int(i)), Self::Scalar(TypeElement::Real(r))) => {
                TypeElement::from(i >= r).into()
            }
            (Self::Scalar(TypeElement::Real(r)), Self::Scalar(TypeElement::Int(i))) => {
                TypeElement::from(r >= i).into()
            }
            (Self::Scalar(TypeElement::Real(r1)), Self::Scalar(TypeElement::Real(r2))) => {
                Self::Scalar((r1 >= r2).into())
            }
            _ => return Err(VecError::TypeMismatch),
        };
        Ok(sv.try_as_scalar())
    }

    pub fn eq(self, other: Self, context: &InterpContext) -> Result<Self, VecError> {
        let sv = match (self, other) {
            // Int
            (Self::Int(i1), Self::Int(i2)) => i1.eq(i2, context).into(),
            // Custom
            (Self::TypeEnum(d1), Self::TypeEnum(d2)) => {
                let bv = d1.eq(d2, context);
                bv.into()
            }
            // Real
            (Self::Real(r1), Self::Real(r2)) => r1.eq(r2, context).into(),
            // Real Int
            (Self::Real(r), Self::Int(i)) | (Self::Int(i), Self::Real(r)) => {
                r.eq(i.into(), context).into()
            }
            // Real scalar
            (Self::Real(r), Self::Scalar(TypeElement::Real(s_r)))
            | (Self::Scalar(TypeElement::Real(s_r)), Self::Real(r)) => {
                r.eq_scalar(s_r.into()).into()
            }
            // Real Int scalar
            (Self::Real(r), Self::Scalar(TypeElement::Int(s_i)))
            | (Self::Scalar(TypeElement::Int(s_i)), Self::Real(r)) => {
                r.eq_scalar(s_i.into()).into()
            }
            // Int Real scalar
            (Self::Int(i), Self::Scalar(TypeElement::Real(s_r)))
            | (Self::Scalar(TypeElement::Real(s_r)), Self::Int(i)) => {
                LayoutRealFunc::from(i).eq_scalar(s_r.into()).into()
            }
            // Custom scalar
            (Self::Scalar(TypeElement::Custom(s)), Self::TypeEnum(i))
            | (Self::TypeEnum(i), Self::Scalar(TypeElement::Custom(s))) => i.eq_scalar(s.1).into(),
            // Int scalar
            (Self::Scalar(TypeElement::Int(s)), Self::Int(i))
            | (Self::Int(i), Self::Scalar(TypeElement::Int(s))) => i.eq_scalar(s).into(),
            // Scalar
            (Self::Scalar(e1), Self::Scalar(e2)) => Self::Scalar((e1 == e2).into()),
            _ => return Err(VecError::TypeMismatch),
        };
        Ok(sv.try_as_scalar())
    }

    pub fn neq(self, other: Self, context: &InterpContext) -> Result<Self, VecError> {
        let sv = match (self, other) {
            // Int
            (Self::Int(i1), Self::Int(i2)) => i1.neq(i2, context).into(),
            // Custom
            (Self::TypeEnum(d1), Self::TypeEnum(d2)) => {
                let bv = d1.neq(d2, context);
                bv.into()
            }
            // Real
            (Self::Real(r1), Self::Real(r2)) => r1.neq(r2, context).into(),
            // Real Int
            (Self::Real(r), Self::Int(i)) | (Self::Int(i), Self::Real(r)) => {
                r.neq(i.into(), context).into()
            }
            // Real scalar
            (Self::Real(r), Self::Scalar(TypeElement::Real(s_r)))
            | (Self::Scalar(TypeElement::Real(s_r)), Self::Real(r)) => {
                r.neq_scalar(s_r.into()).into()
            }
            // Real Int scalar
            (Self::Real(r), Self::Scalar(TypeElement::Int(s_i)))
            | (Self::Scalar(TypeElement::Int(s_i)), Self::Real(r)) => {
                r.neq_scalar(s_i.into()).into()
            }
            // Int Real scalar
            (Self::Int(i), Self::Scalar(TypeElement::Real(s_r)))
            | (Self::Scalar(TypeElement::Real(s_r)), Self::Int(i)) => {
                LayoutRealFunc::from(i).neq_scalar(s_r.into()).into()
            }
            // Custom scalar
            (Self::Scalar(TypeElement::Custom(s)), Self::TypeEnum(i))
            | (Self::TypeEnum(i), Self::Scalar(TypeElement::Custom(s))) => i.neq_scalar(s.1).into(),
            // Int scalar
            (Self::Scalar(TypeElement::Int(s)), Self::Int(i))
            | (Self::Int(i), Self::Scalar(TypeElement::Int(s))) => i.neq_scalar(s).into(),
            // Scalar
            (Self::Scalar(e1), Self::Scalar(e2)) => Self::Scalar((e1 != e2).into()),
            _ => return Err(VecError::TypeMismatch),
        };
        Ok(sv.try_as_scalar())
    }

    pub fn add(self, other: Self, context: &InterpContext) -> Result<Self, VecError> {
        let sv = match (self, other) {
            // Int
            (Self::Int(i1), Self::Int(i2)) => i1.add(i2, context).into(),
            // Int scalar
            (Self::Scalar(TypeElement::Int(s)), Self::Int(i))
            | (Self::Int(i), Self::Scalar(TypeElement::Int(s))) => i.add_scalar(s).into(),
            // Real
            (Self::Real(r1), Self::Real(r2)) => r1.add(r2, context).into(),
            // Real Int
            (Self::Real(r), Self::Int(i)) | (Self::Int(i), Self::Real(r)) => {
                r.add(i.into(), context).into()
            }
            // Real scalar
            (Self::Real(r), Self::Scalar(TypeElement::Real(s_r)))
            | (Self::Scalar(TypeElement::Real(s_r)), Self::Real(r)) => {
                r.add_scalar(s_r.into()).into()
            }
            // Real Int scalar
            (Self::Real(r), Self::Scalar(TypeElement::Int(s_i)))
            | (Self::Scalar(TypeElement::Int(s_i)), Self::Real(r)) => {
                r.add_scalar(s_i.into()).into()
            }
            // Int Real scalar
            (Self::Int(i), Self::Scalar(TypeElement::Real(s_r)))
            | (Self::Scalar(TypeElement::Real(s_r)), Self::Int(i)) => {
                LayoutRealFunc::from(i).add_scalar(s_r.into()).into()
            }
            // Scalars
            (Self::Scalar(TypeElement::Int(i1)), Self::Scalar(TypeElement::Int(i2))) => {
                Self::Scalar((i1 + i2).into())
            }
            (Self::Scalar(TypeElement::Real(r)), Self::Scalar(TypeElement::Int(i)))
            | (Self::Scalar(TypeElement::Int(i)), Self::Scalar(TypeElement::Real(r))) => {
                r.add(i.into()).expect("Float overflow").into()
            }
            (Self::Scalar(TypeElement::Real(rl)), Self::Scalar(TypeElement::Real(rr))) => {
                rl.add(rr.into()).expect("Float overflow").into()
            }
            _ => return Err(VecError::TypeMismatch),
        };
        Ok(sv.try_as_scalar())
    }

    pub fn sub(self, other: Self, context: &InterpContext) -> Result<Self, VecError> {
        let sv = match (self, other) {
            // Int
            (Self::Int(i1), Self::Int(i2)) => i1.sub(i2, context).into(),
            // Int scalar
            (Self::Scalar(TypeElement::Int(s)), Self::Int(i))
            | (Self::Int(i), Self::Scalar(TypeElement::Int(s))) => i.sub_scalar(s).into(),
            // Real
            (Self::Real(r1), Self::Real(r2)) => r1.sub(r2, context).into(),
            // Real Int
            (Self::Real(r), Self::Int(i)) | (Self::Int(i), Self::Real(r)) => {
                r.sub(i.into(), context).into()
            }
            // Real scalar
            (Self::Real(r), Self::Scalar(TypeElement::Real(s_r)))
            | (Self::Scalar(TypeElement::Real(s_r)), Self::Real(r)) => {
                r.sub_scalar(s_r.into()).into()
            }
            // Real Int scalar
            (Self::Real(r), Self::Scalar(TypeElement::Int(s_i)))
            | (Self::Scalar(TypeElement::Int(s_i)), Self::Real(r)) => {
                r.sub_scalar(s_i.into()).into()
            }
            // Int Real scalar
            (Self::Int(i), Self::Scalar(TypeElement::Real(s_r)))
            | (Self::Scalar(TypeElement::Real(s_r)), Self::Int(i)) => {
                LayoutRealFunc::from(i).sub_scalar(s_r.into()).into()
            }
            // Scalars
            (Self::Scalar(TypeElement::Int(i1)), Self::Scalar(TypeElement::Int(i2))) => {
                Self::Scalar((i1 - i2).into())
            }
            (Self::Scalar(TypeElement::Real(r)), Self::Scalar(TypeElement::Int(i)))
            | (Self::Scalar(TypeElement::Int(i)), Self::Scalar(TypeElement::Real(r))) => {
                r.sub(i.into()).expect("Float overflow").into()
            }
            (Self::Scalar(TypeElement::Real(rl)), Self::Scalar(TypeElement::Real(rr))) => {
                rl.sub(rr.into()).expect("Float overflow").into()
            }
            _ => return Err(VecError::TypeMismatch),
        };
        Ok(sv.try_as_scalar())
    }

    pub fn mult(self, other: Self, context: &InterpContext) -> Result<Self, VecError> {
        let sv = match (self, other) {
            // Int
            (Self::Int(i1), Self::Int(i2)) => i1.mult(i2, context).into(),
            // Int scalar
            (Self::Scalar(TypeElement::Int(s)), Self::Int(i))
            | (Self::Int(i), Self::Scalar(TypeElement::Int(s))) => i.mult_scalar(s).into(),
            // Real
            (Self::Real(r1), Self::Real(r2)) => r1.mult(r2, context).into(),
            // Real Int
            (Self::Real(r), Self::Int(i)) | (Self::Int(i), Self::Real(r)) => {
                r.mult(i.into(), context).into()
            }
            // Real scalar
            (Self::Real(r), Self::Scalar(TypeElement::Real(s_r)))
            | (Self::Scalar(TypeElement::Real(s_r)), Self::Real(r)) => {
                r.mult_scalar(s_r.into()).into()
            }
            // Real Int scalar
            (Self::Real(r), Self::Scalar(TypeElement::Int(s_i)))
            | (Self::Scalar(TypeElement::Int(s_i)), Self::Real(r)) => {
                r.mult_scalar(s_i.into()).into()
            }
            // Int Real scalar
            (Self::Int(i), Self::Scalar(TypeElement::Real(s_r)))
            | (Self::Scalar(TypeElement::Real(s_r)), Self::Int(i)) => {
                LayoutRealFunc::from(i).mult_scalar(s_r.into()).into()
            }
            // Scalars
            (Self::Scalar(TypeElement::Int(i1)), Self::Scalar(TypeElement::Int(i2))) => {
                Self::Scalar((i1 * i2).into())
            }
            (Self::Scalar(TypeElement::Real(r)), Self::Scalar(TypeElement::Int(i)))
            | (Self::Scalar(TypeElement::Int(i)), Self::Scalar(TypeElement::Real(r))) => {
                r.mult(i.into()).expect("Float overflow").into()
            }
            (Self::Scalar(TypeElement::Real(rl)), Self::Scalar(TypeElement::Real(rr))) => {
                rl.mult(rr.into()).expect("Float overflow").into()
            }
            _ => return Err(VecError::TypeMismatch),
        };
        Ok(sv.try_as_scalar())
    }

    pub fn div(self, other: Self, context: &InterpContext) -> Result<Self, VecError> {
        let sv = match (self, other) {
            // Int
            (Self::Int(i1), Self::Int(i2)) => LayoutRealFunc::from(i1)
                .div(LayoutRealFunc::from(i2), context)
                .into(),
            // Int scalar
            (Self::Int(i), Self::Scalar(TypeElement::Int(s))) => {
                LayoutRealFunc::from(i).div_scalar(s.into()).into()
            }
            (Self::Scalar(TypeElement::Int(s)), Self::Int(i)) => {
                LayoutRealFunc::div_scalar_2(s.into(), LayoutRealFunc::from(i)).into()
            }
            // Real
            (Self::Real(r1), Self::Real(r2)) => r1.div(r2, context).into(),
            // Real Int
            (Self::Real(r), Self::Int(i)) => r.div(i.into(), context).into(),
            (Self::Int(i), Self::Real(r)) => LayoutRealFunc::from(i).div(r, context).into(),
            // Real scalar
            (Self::Real(r), Self::Scalar(TypeElement::Real(s_r))) => r.div_scalar(s_r).into(),
            (Self::Scalar(TypeElement::Real(s_r)), Self::Real(r)) => {
                LayoutRealFunc::div_scalar_2(s_r, r).into()
            }
            // Real Int scalar
            (Self::Real(r), Self::Scalar(TypeElement::Int(s_i))) => r.div_scalar(s_i.into()).into(),
            (Self::Scalar(TypeElement::Int(s_i)), Self::Real(r)) => {
                LayoutRealFunc::div_scalar_2(s_i.into(), r).into()
            }
            // Int Real scalar
            (Self::Int(i), Self::Scalar(TypeElement::Real(s_r))) => {
                LayoutRealFunc::from(i).div_scalar(s_r).into()
            }
            (Self::Scalar(TypeElement::Real(s_r)), Self::Int(i)) => {
                LayoutRealFunc::div_scalar_2(s_r, i.into()).into()
            }
            // Scalars
            (Self::Scalar(TypeElement::Int(i1)), Self::Scalar(TypeElement::Int(i2))) => {
                Self::Scalar((Real::from(i1).div_cc(&Real::from(i2))).into())
            }
            (Self::Scalar(TypeElement::Real(r)), Self::Scalar(TypeElement::Int(i))) => {
                Self::Scalar(r.div_cc(&i.into()).into())
            }
            (Self::Scalar(TypeElement::Int(i)), Self::Scalar(TypeElement::Real(r))) => {
                Self::Scalar(Real::from(i).div_cc(&r).into())
            }
            (Self::Scalar(TypeElement::Real(rl)), Self::Scalar(TypeElement::Real(rr))) => {
                Self::Scalar(rl.div_cc(&rr).into())
            }
            _ => return Err(VecError::TypeMismatch),
        };
        Ok(sv.try_as_scalar())
    }

    pub fn rem(self, other: Self, context: &InterpContext) -> Result<Self, VecError> {
        let sv = match (self, other) {
            // Int
            (Self::Int(i1), Self::Int(i2)) => LayoutRealFunc::from(i1)
                .rem(LayoutRealFunc::from(i2), context)
                .into(),
            // Int scalar
            (Self::Int(i), Self::Scalar(TypeElement::Int(s))) => {
                LayoutRealFunc::from(i).rem_scalar(s.into()).into()
            }
            (Self::Scalar(TypeElement::Int(s)), Self::Int(i)) => {
                LayoutRealFunc::rem_scalar_2(s.into(), LayoutRealFunc::from(i)).into()
            }
            // Real
            (Self::Real(r1), Self::Real(r2)) => r1.rem(r2, context).into(),
            // Real Int
            (Self::Real(r), Self::Int(i)) => r.rem(i.into(), context).into(),
            (Self::Int(i), Self::Real(r)) => LayoutRealFunc::from(i).rem(r, context).into(),
            // Real scalar
            (Self::Real(r), Self::Scalar(TypeElement::Real(s_r))) => r.rem_scalar(s_r).into(),
            (Self::Scalar(TypeElement::Real(s_r)), Self::Real(r)) => {
                LayoutRealFunc::rem_scalar_2(s_r, r).into()
            }
            // Real Int scalar
            (Self::Real(r), Self::Scalar(TypeElement::Int(s_i))) => r.rem_scalar(s_i.into()).into(),
            (Self::Scalar(TypeElement::Int(s_i)), Self::Real(r)) => {
                LayoutRealFunc::rem_scalar_2(s_i.into(), r).into()
            }
            // Int Real scalar
            (Self::Int(i), Self::Scalar(TypeElement::Real(s_r))) => {
                LayoutRealFunc::from(i).rem_scalar(s_r).into()
            }
            (Self::Scalar(TypeElement::Real(s_r)), Self::Int(i)) => {
                LayoutRealFunc::rem_scalar_2(s_r, i.into()).into()
            }
            // Scalars
            (Self::Scalar(TypeElement::Int(i1)), Self::Scalar(TypeElement::Int(i2))) => {
                Self::Scalar((Real::from(i1).rem_cc(&Real::from(i2))).into())
            }
            (Self::Scalar(TypeElement::Real(r)), Self::Scalar(TypeElement::Int(i))) => {
                Self::Scalar(r.rem_cc(&i.into()).into())
            }
            (Self::Scalar(TypeElement::Int(i)), Self::Scalar(TypeElement::Real(r))) => {
                Self::Scalar(Real::from(i).rem_cc(&r).into())
            }
            (Self::Scalar(TypeElement::Real(rl)), Self::Scalar(TypeElement::Real(rr))) => {
                Self::Scalar(rl.rem_cc(&rr).into())
            }
            _ => return Err(VecError::TypeMismatch),
        };
        Ok(sv.try_as_scalar())
    }

    pub fn ite(
        self,
        then_term: Self,
        else_term: Self,
        context: &InterpContext,
    ) -> Result<Self, VecError> {
        let sv = match (self, then_term, else_term) {
            // Int - Int
            (Self::Predicate(cond), Self::Int(then_term), Self::Int(else_term)) => {
                Self::Int(cond.int_ite(then_term, else_term, context))
            }
            // Int - Int scalar
            (Self::Predicate(cond), Self::Int(i), Self::Scalar(TypeElement::Int(s))) => {
                Self::Int(cond.int_ite_scalar_else(i, s, context))
            }
            // Int scalar - Int
            (Self::Predicate(cond), Self::Scalar(TypeElement::Int(s)), Self::Int(i)) => {
                Self::Int(cond.int_ite_scalar_then(s, i, context))
            }
            // Int scalar - Int scalar
            (
                Self::Predicate(cond),
                Self::Scalar(TypeElement::Int(s1)),
                Self::Scalar(TypeElement::Int(s2)),
            ) => Self::Int(cond.int_ite_scalar_then_else(s1, s2)),
            // Int - Real
            (Self::Predicate(cond), Self::Int(then_term), Self::Real(else_term)) => {
                Self::Real(cond.real_ite(then_term.into(), else_term, context))
            }
            // Int - Real scalar
            (
                Self::Predicate(cond),
                Self::Int(then_term),
                Self::Scalar(TypeElement::Real(else_s)),
            ) => Self::Real(cond.real_ite_scalar_else(then_term.into(), else_s, context)),
            // Int scalar - Real
            (
                Self::Predicate(cond),
                Self::Scalar(TypeElement::Int(then_term)),
                Self::Real(real),
            ) => Self::Real(cond.real_ite_scalar_then(then_term.into(), real, context)),
            // Int scalar - Real scalar
            (
                Self::Predicate(cond),
                Self::Scalar(TypeElement::Int(then_term)),
                Self::Scalar(TypeElement::Real(else_term)),
            ) => Self::Real(cond.real_ite_scalar_then_else(then_term.into(), else_term)),
            // Real - Int
            (Self::Predicate(cond), Self::Real(then_term), Self::Int(else_term)) => {
                Self::Real(cond.real_ite(then_term, else_term.into(), context))
            }
            // Real - Int scalar
            (
                Self::Predicate(cond),
                Self::Real(then_term),
                Self::Scalar(TypeElement::Int(else_s)),
            ) => Self::Real(cond.real_ite_scalar_else(then_term, else_s.into(), context)),
            // Real scalar - Int
            (
                Self::Predicate(cond),
                Self::Scalar(TypeElement::Real(then_term)),
                Self::Int(else_term),
            ) => Self::Real(cond.real_ite_scalar_then(then_term, else_term.into(), context)),
            // Real scalar - Int scalar
            (
                Self::Predicate(cond),
                Self::Scalar(TypeElement::Real(then_term)),
                Self::Scalar(TypeElement::Int(else_term)),
            ) => Self::Real(cond.real_ite_scalar_then_else(then_term, else_term.into())),
            // Real - Real
            (Self::Predicate(cond), Self::Real(then_term), Self::Real(else_term)) => {
                Self::Real(cond.real_ite(then_term, else_term, context))
            }
            // Real - Real scalar
            (Self::Predicate(cond), Self::Real(i), Self::Scalar(TypeElement::Real(s))) => {
                Self::Real(cond.real_ite_scalar_else(i, s, context))
            }
            // Real scalar - Real
            (Self::Predicate(cond), Self::Scalar(TypeElement::Real(s)), Self::Real(i)) => {
                Self::Real(cond.real_ite_scalar_then(s, i, context))
            }
            // Real scalar - Real scalar
            (
                Self::Predicate(cond),
                Self::Scalar(TypeElement::Real(s1)),
                Self::Scalar(TypeElement::Real(s2)),
            ) => Self::Real(cond.real_ite_scalar_then_else(s1, s2)),
            // Custom - Custom
            (Self::Predicate(cond), Self::TypeEnum(then_term), Self::TypeEnum(else_term)) => {
                Self::TypeEnum(cond.type_enum_ite(then_term, else_term, context)?)
            }
            // Custom - Custom scalar
            (Self::Predicate(cond), Self::TypeEnum(i), Self::Scalar(TypeElement::Custom(s))) => {
                Self::TypeEnum(cond.type_enum_ite_scalar_else(i, s, context)?)
            }
            // Custom scalar - Custom
            (Self::Predicate(cond), Self::Scalar(TypeElement::Custom(s)), Self::TypeEnum(i)) => {
                Self::TypeEnum(cond.type_enum_ite_scalar_then(s, i, context)?)
            }
            // Custom scalar - Custom scalar
            (
                Self::Predicate(cond),
                Self::Scalar(TypeElement::Custom(s1)),
                Self::Scalar(TypeElement::Custom(s2)),
            ) => {
                if s1.0 != s2.0 {
                    return Err(VecError::TypeMismatch);
                }
                Self::TypeEnum(cond.type_enum_ite_scalar_then_else(s1, s2)?)
            }
            (Self::Scalar(TypeElement::Bool(b)), then_term, else_term) => {
                if b {
                    then_term
                } else {
                    else_term
                }
            }
            _ => return Err(VecError::TypeMismatch),
        };
        Ok(sv.try_as_scalar())
    }

    pub fn exists(self, vars: &[BoundVarId], context: &InterpContext) -> Result<Self, VecError> {
        let sv = match self {
            Self::Predicate(p) => p
                .exists(vars, context)
                .map_to_single(Self::Predicate, |f| Self::Scalar(f.into())),
            val @ Self::Scalar(TypeElement::Bool(_)) => val,
            _ => return Err(VecError::TypeMismatch),
        };
        Ok(sv.try_as_scalar())
    }

    pub fn universal(self, vars: &[BoundVarId], context: &InterpContext) -> Result<Self, VecError> {
        let sv = match self {
            Self::Predicate(p) => p
                .universal(vars, context)
                .map_to_single(Self::Predicate, |f| Self::Scalar(f.into())),
            val @ Self::Scalar(TypeElement::Bool(_)) => val,
            _ => return Err(VecError::TypeMismatch),
        };
        Ok(sv.try_as_scalar())
    }

    pub fn is_int(self) -> Result<Self, VecError> {
        match self {
            Self::Real(value) => Ok(Self::Predicate(value.is_int())),
            Self::Scalar(TypeElement::Real(value)) => Ok(value.is_integer().into()),
            _ => return Err(VecError::TypeMismatch),
        }
    }

    pub fn cardinality(
        self,
        vars: &[BoundVarId],
        context: &InterpContext,
    ) -> Result<Self, VecError> {
        let sv: Self = match self {
            Self::Predicate(p) => p
                .card_agg(vars, context)
                .map_to_single(Self::Int, |f| Self::Scalar(f.into())),
            Self::Scalar(TypeElement::Bool(b)) => {
                if b {
                    let domain_len: Int = LayoutVec::domain_len_slice(vars, context)
                        .try_into()
                        .expect("Overflow");
                    domain_len.into()
                } else {
                    0.into()
                }
            }
            _ => return Err(VecError::TypeMismatch),
        };
        Ok(sv.try_as_scalar())
    }

    pub fn sum(self, vars: &[BoundVarId], context: &InterpContext) -> Result<Self, VecError> {
        let sv: Self = match self {
            Self::Int(p) => p
                .sum_agg(vars, context)
                .map_to_single(Self::Int, |f| Self::Scalar(f.into())),
            Self::Real(p) => p
                .sum_agg(vars, context)
                .map_to_single(Self::Real, |f| Self::Scalar(f.into())),
            Self::Scalar(TypeElement::Int(i)) => {
                let domain_len: Int = LayoutVec::domain_len_slice(vars, context)
                    .try_into()
                    .expect("Overflow");
                let res = i.overflowing_mul(domain_len);
                assert!(!res.1);
                res.0.into()
            }
            Self::Scalar(TypeElement::Real(i)) => {
                let domain_len: Int = LayoutVec::domain_len_slice(vars, context)
                    .try_into()
                    .expect("Overflow");
                let res = i.mult(domain_len.into()).expect("Number too big!!");
                res.into()
            }
            _ => return Err(VecError::TypeMismatch),
        };
        Ok(sv.try_as_scalar())
    }

    pub fn try_as_scalar(self) -> Self {
        match self {
            Self::Predicate(vec) => {
                if let Some(b) = vec.try_as_bool() {
                    b.into()
                } else {
                    Self::Predicate(vec)
                }
            }
            Self::Int(vec) => {
                if let Some(val) = vec.try_as_int() {
                    val.into()
                } else {
                    Self::Int(vec)
                }
            }
            Self::Real(vec) => {
                if let Some(val) = vec.try_as_real() {
                    val.into()
                } else {
                    Self::Real(vec)
                }
            }
            Self::TypeEnum(vec) => {
                if let Some(val) = vec.try_as_type_element() {
                    val.into()
                } else {
                    Self::TypeEnum(vec)
                }
            }
            scalar @ Self::Scalar(_) => scalar,
        }
    }

    pub fn is_scalar(&self) -> bool {
        matches!(self, Self::Scalar(_))
    }

    pub fn unwrap_satset(self) -> LayoutSatSet<S> {
        if let Self::Predicate(satset) = self {
            satset
        } else {
            panic!("unwrap_satset on non satset")
        }
    }

    pub fn try_as_bool(&self) -> Option<bool> {
        match self {
            Self::Predicate(p) => p.try_as_bool(),
            Self::Scalar(TypeElement::Bool(b)) => Some(*b),
            _ => None,
        }
    }
}
