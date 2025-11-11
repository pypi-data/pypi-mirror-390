use crate::comp_core::{
    IndexRange,
    constraints::BoundVarId,
    expression::TypeMap,
    structure::{DomainEnumBuilder, DomainEnumIter, TypeInterps},
    vocabulary::{DomainEnum, DomainSlice, TypeEnum},
};
use sli_collections::{hash_map::IdHashMap, hash_set::HashSet};
use std::{
    iter::{self, Copied},
    mem::transmute,
    slice::{Iter, IterMut},
    vec,
};

use super::InterpContext;

pub type LayoutVec = Layout<Vec<BoundVarId>>;

pub type LayoutSlice = Layout<[BoundVarId]>;

impl<T> AsRef<LayoutSlice> for Layout<T>
where
    T: AsRef<[BoundVarId]> + ?Sized,
{
    fn as_ref(&self) -> &LayoutSlice {
        unsafe { transmute(self.0.as_ref()) }
    }
}

/// A layout may never have duplicate bound variables
///
/// (This is weakly enforced unfortunately)
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Layout<T>(pub T)
where
    T: ?Sized;

impl<T> AsRef<[BoundVarId]> for Layout<T>
where
    T: AsRef<[BoundVarId]> + ?Sized,
{
    fn as_ref(&self) -> &[BoundVarId] {
        self.0.as_ref()
    }
}

impl<T> Layout<T>
where
    T: AsRef<[BoundVarId]> + ?Sized,
{
    pub fn len(&self) -> usize {
        self.0.as_ref().len()
    }

    pub fn contains_var(&self, var: BoundVarId) -> bool {
        if let Some(_) = self.0.as_ref().iter().position(|x| *x == var) {
            true
        } else {
            false
        }
    }

    pub fn contains_any_variables<B: AsRef<[BoundVarId]>>(&self, variables: &B) -> bool {
        if let Some(_) = self
            .0
            .as_ref()
            .iter()
            .position(|x| variables.as_ref().contains(x))
        {
            true
        } else {
            false
        }
    }

    pub fn var_loc(&self, var: BoundVarId) -> Option<usize> {
        if let Some(i) = self.0.as_ref().iter().position(|x| *x == var) {
            Some(i)
        } else {
            None
        }
    }

    pub fn domain_len(&self, context: &InterpContext) -> usize {
        Self::domain_len_slice(self.as_slice(), context)
    }

    pub fn iter<'a>(&'a self) -> Copied<Iter<'a, BoundVarId>> {
        self.as_slice().iter().copied()
    }

    pub fn domain_len_slice(vars: &[BoundVarId], context: &InterpContext) -> usize {
        DomainSlice::type_iter_domain_len(
            vars.iter().map(|i| &context.type_map[i]),
            context.type_interps(),
        )
    }

    pub fn get_domain(&self, type_map: &TypeMap) -> Box<DomainSlice> {
        Self::from_iter_get_domain(self.iter(), type_map)
    }

    pub fn from_iter_get_domain<R>(iter: R, type_map: &TypeMap) -> Box<DomainSlice>
    where
        R: IntoIterator<Item = BoundVarId>,
    {
        let types: Box<[_]> = iter.into_iter().map(|var| type_map[&var]).collect();
        types.into()
    }

    /// Returns the length of unused quantification variables.
    /// For example: with `T := {a, b}`, the formula `!x, y in T: f(x).`
    /// would have an "unquantified_len" of 2, as `a` and `b` are both unused for `y`.
    pub fn unquantified_len(&self, vars: &[BoundVarId], context: &InterpContext) -> usize {
        vars.iter()
            .copied()
            .filter(|f| !self.contains_var(*f))
            .map(|f| LayoutVec::domain_len_of_iter(iter::once(f), context))
            .fold(1 as usize, |f, d| f * d)
    }

    pub fn domain_len_of_iter<R: Iterator<Item = BoundVarId>>(
        vars: R,
        context: &InterpContext,
    ) -> usize {
        DomainSlice::type_iter_domain_len(
            vars.map(|i| &context.type_map[&i]),
            context.type_interps(),
        )
    }

    pub fn domains_len<'a>(
        &'a self,
        context: &'a InterpContext,
    ) -> impl Iterator<Item = usize> + ExactSizeIterator + 'a {
        DomainSlice::type_iter_domains_len(
            self.iter().map(|i| &context.get_type_map()[&i]),
            context.type_interps(),
        )
    }

    pub fn iter_indexes<'a>(&'a self, context: &'a InterpContext) -> IndexRange<DomainEnum> {
        IndexRange::new(0..self.domain_len(context))
    }

    pub fn as_slice(&self) -> &[BoundVarId] {
        self.0.as_ref()
    }
}

impl<T> Layout<T>
where
    T: AsRef<[BoundVarId]> + AsMut<[BoundVarId]> + ?Sized,
{
    pub fn replace_var(&mut self, old: BoundVarId, new: BoundVarId) -> bool {
        let pos = if let Some(pos) = self.0.as_ref().iter().position(|x| *x == old) {
            pos
        } else {
            return false;
        };
        let _ = core::mem::replace(&mut self.0.as_mut()[pos], new);
        true
    }
}

impl LayoutVec {
    pub fn new() -> Self {
        Layout(Vec::new())
    }

    pub fn sort_by<F>(&mut self, compare: F)
    where
        F: FnMut(&BoundVarId, &BoundVarId) -> core::cmp::Ordering,
    {
        self.0.sort_by(compare);
    }

    pub(super) unsafe fn from_raw(raw: Vec<BoundVarId>) -> Self {
        debug_assert!(HashSet::<_>::from_iter(raw.iter().copied()).len() == raw.len());
        Layout(raw)
    }

    pub fn add_var(&mut self, var: BoundVarId) {
        if let None = self.0.iter().copied().position(|i| i == var) {
            self.0.push(var)
        }
    }

    pub(super) fn elim<T: IntoIterator<Item = bool>>(&mut self, elim: T)
    where
        T::IntoIter: ExactSizeIterator,
    {
        let mut iter = elim.into_iter();
        debug_assert!(self.len() == iter.len());
        self.0.retain(|_| {
            if let Some(b) = iter.next() {
                !b
            } else {
                unreachable!()
            }
        })
    }

    pub fn iter_mut<'a>(&'a mut self) -> IterMut<'a, BoundVarId> {
        self.0.iter_mut()
    }

    pub fn prepend_var(&mut self, var: BoundVarId) {
        self.0.insert(0, var);
        debug_assert!(HashSet::<_>::from_iter(self.0.iter().copied()).len() == self.0.len());
    }

    pub fn reorder(&mut self, swap1: usize, swap2: usize) {
        self.0.swap(swap1, swap2)
    }

    pub fn eliminate_var(self, var: BoundVarId) -> Self {
        Layout(self.0.into_iter().filter(|i| *i != var).collect())
    }

    pub fn eliminate_var_mut(&mut self, var: BoundVarId) {
        self.0.retain(|f| *f != var);
    }

    pub fn translate_layout(&mut self, var_translation: &IdHashMap<BoundVarId, BoundVarId>) {
        for i in &mut self.0 {
            if let Some(&x) = var_translation.get(&i) {
                *i = x;
            }
        }
        debug_assert!(HashSet::<_>::from_iter(self.0.iter().copied()).len() == self.0.len());
    }

    pub fn type_eq(&self, other: &Self, type_map: &TypeMap) -> bool {
        if self.len() != other.len() {
            return false;
        }
        for (var0, var1) in self.0.iter().zip(&other.0) {
            let type_e_0 = type_map[var0];
            let type_e_1 = type_map[var1];
            if type_e_0 != type_e_1 {
                return false;
            }
        }
        return true;
    }
}

impl FromIterator<BoundVarId> for LayoutVec {
    fn from_iter<T: IntoIterator<Item = BoundVarId>>(iter: T) -> Self {
        let ret = Layout(Vec::from_iter(iter));
        debug_assert!(HashSet::<_>::from_iter(ret.0.iter().copied()).len() == ret.0.len());
        ret
    }
}

impl IntoIterator for LayoutVec {
    type IntoIter = vec::IntoIter<BoundVarId>;
    type Item = BoundVarId;

    fn into_iter(self) -> Self::IntoIter {
        self.0.into_iter()
    }
}

pub struct DomainEnumReorder<'a> {
    dom_cur: Box<DomainSlice>,
    dom_to: Box<DomainSlice>,
    type_interps: &'a TypeInterps,
    order: Box<[Option<usize>]>,
    buffer: Box<[TypeEnum]>,
    same: bool,
}

impl<'a> DomainEnumReorder<'a> {
    pub fn new<C, T>(cur: C, to: T, type_map: &TypeMap, type_interps: &'a TypeInterps) -> Self
    where
        C: AsRef<LayoutSlice>,
        T: AsRef<LayoutSlice>,
    {
        let dom_cur = cur.as_ref().get_domain(type_map);
        let dom_to = to.as_ref().get_domain(type_map);
        let same = cur.as_ref() == to.as_ref();
        if to.as_ref().len() == 0 {
            return Self {
                dom_cur,
                dom_to,
                type_interps,
                order: Default::default(),
                buffer: Default::default(),
                same,
            };
        }

        let order = to
            .as_ref()
            .iter()
            .map(|f| cur.as_ref().var_loc(f))
            .collect();

        let buffer = (0..cur.as_ref().len()).map(|_| 0.into()).collect();

        Self {
            dom_cur: cur.as_ref().get_domain(type_map),
            dom_to: to.as_ref().get_domain(type_map),
            type_interps,
            order,
            buffer,
            same,
        }
    }
    pub fn new_with_context<C, T>(cur: C, to: T, context: &'a InterpContext) -> Self
    where
        C: AsRef<LayoutSlice>,
        T: AsRef<LayoutSlice>,
    {
        Self::new(cur, to, context.get_type_map(), &context.type_interps())
    }

    pub fn dom_to(&self) -> &DomainSlice {
        &self.dom_to
    }

    pub fn dom_from(&self) -> &DomainSlice {
        &self.dom_cur
    }

    pub fn index(&mut self, index: DomainEnum) -> DomainEnumIter {
        if self.same {
            return DomainEnumIter::new(self.type_interps, &self.dom_to, index.into(), &[]);
        }
        let mut builder = DomainEnumBuilder::new(&self.dom_to, self.type_interps);
        for (i, val) in self
            .type_interps
            .type_enum_iter(self.dom_cur.iter(), index)
            .enumerate()
        {
            self.buffer[i] = val;
        }
        let mut cur_var = 0;
        for order in self.order.iter() {
            if let Some(order) = order {
                builder
                    .add_enum_arg(self.buffer[*order])
                    .expect("Internal Error");
            } else {
                builder.add_var(cur_var.into()).expect("Internal Error");
                cur_var += 1;
            }
        }
        builder.iter_indexes()
    }

    pub fn single(&mut self, index: DomainEnum) -> DomainEnum {
        if self.same {
            return index;
        }
        if self.buffer.len() == 0 {
            return 0.into();
        }
        let mut builder = DomainEnumBuilder::new(&self.dom_to, self.type_interps);
        for (i, val) in self
            .type_interps
            .type_enum_iter(self.dom_cur.iter(), index)
            .enumerate()
        {
            self.buffer[i] = val;
        }
        let mut cur_var = 0;
        for order in self.order.iter() {
            if let Some(order) = order {
                builder
                    .add_enum_arg(self.buffer[*order])
                    .expect("Internal Error");
            } else {
                builder.add_var(cur_var.into()).expect("Internal Error");
                cur_var += 1;
            }
        }
        builder.get_index().unwrap()
    }

    pub fn type_interps(&self) -> &'a TypeInterps {
        &self.type_interps
    }
}

#[allow(unused)]
#[cfg(test)]
mod tests {
    #![allow(non_snake_case)]
    use super::{DomainEnumReorder, LayoutVec};
    use crate::comp_core::{
        constraints::BoundVarId,
        structure::UnfinishedStructure,
        structure::{DomainEnumBuilder, DomainEnumErrors, PartialStructure, TypeElement},
        vocabulary::{DomainEnum, Type, Vocabulary},
    };
    use crate::interp_structures::InterpContext;
    use crate::utils::tests::{vocab_add_domain, vocab_add_types};
    use sli_collections::{hash_map::IdHashMap, hash_set::IdHashSet};
    use std::error::Error;

    macro_rules! reorder_tests {
        (
            $($name:ident: {
                    types: {
                        $($types:tt)*
                    },
                    expected: $expected:tt $(,)?
                }
            ,)+
        ) => {
            $(
                #[allow(warnings)]
                #[test]
                fn $name() -> Result<(), Box<dyn Error>> {
                    let mut vocab = Vocabulary::new();
                    let mut u_structure = UnfinishedStructure::new();
                    vocab_add_types!({$($types)*}, &mut vocab, &mut u_structure);
                    let structure = PartialStructure::new(u_structure.finish(vocab.into())?.into());

                    reorder_tests!(test $expected, structure);
                    Ok(())
                }
            )+
        };
        (test
         {
             vars: [$($var_types:expr),*],
             ( [$($layout1:literal),* $(,)?], [$($layout2:literal),+]),
             {$($index:literal => [$($exp:literal),*] $(,)?),*}$(,)?
         }, $struct:ident) => {
            let vars = [
                $($var_types,)*
            ];
            let mut type_map = IdHashMap::default();
            for (i, t) in vars.iter().enumerate() {
                type_map.insert(i.into(), *t);
            }
            let context = InterpContext::new(&type_map, $struct.type_interps());
            let mut layout1 = LayoutVec::new();
            let mut layout2 = LayoutVec::new();
            for var in [$($layout1.into(),)*].iter() {
                layout1.add_var(*var);
            }
            for var in [$($layout2.into(),)*].iter() {
                layout2.add_var(*var);
            }
            let mut reorder = DomainEnumReorder::new_with_context(&layout1, &layout2, &context);
            $(
                println!("index: {}", $index);
                let mut vals = reorder.index($index.into());
                $(
                    assert_eq!(vals.next(), Some($exp.into()));
                )*
                assert_eq!(vals.next(), None);
            )*
        }
    }
    reorder_tests! {
        test_reorder_test_1: {
            types: {
                type 0 := { a, b } isa { BaseType::Str }
            },
            expected: {
                vars: [Type::Str(0.into()), Type::Str(0.into())],
                ([0], [0, 1]),
                {
                    0 => [0, 2],
                    1 => [1, 3]
                },
            },
        },
        test_reorder_test_2: {
            types: {
                type 0 := { a, b } isa { BaseType::Str }
            },
            expected: {
                vars: [Type::Str(0.into()), Type::Str(0.into())],
                ([0], [1, 0]),
                {
                    0 => [0, 1],
                    1 => [2, 3]
                },
            },
        },
        test_reorder_test_3: {
            types: {
                type 0 := { a, b } isa { BaseType::Str }
            },
            expected: {
                vars: [Type::Str(0.into()), Type::Str(0.into())],
                ([0, 1], [0]),
                {
                    0 => [0],
                    1 => [1],
                    2 => [0],
                    3 => [1],
                },
            },
        },
        test_reorder_test_4: {
            types: {
                type 0 := { a, b } isa { BaseType::Str }
            },
            expected: {
                vars: [Type::Str(0.into()), Type::Str(0.into())],
                ([0, 1], [1, 0]),
                {
                    0 => [0],
                    1 => [2],
                    2 => [1],
                    3 => [3],
                },
            },
        },
        test_reorder_test_5: {
            types: {
                type 0 := { a, b } isa { BaseType::Str }
                type 1 := { c, d, e } isa { BaseType::Str }
            },
            expected: {
                vars: [Type::Str(0.into()), Type::Str(1.into())],
                ([0, 1], [1, 0]),
                {
                    0 => [0],
                    1 => [3],
                    2 => [1],
                    3 => [4],
                    4 => [2],
                    5 => [5],
                },
            },
        },
        test_reorder_test_6: {
            types: {
                type 0 := { a, b } isa { BaseType::Str }
            },
            expected: {
                vars: [Type::Str(0.into()), Type::Str(0.into()), Type::Str(0.into())],
                ([0, 1, 2], [0, 2, 1]),
                {
                    0 => [0], 1 => [1],
                    2 => [4], 3 => [5],

                    4 => [2], 5 => [3],
                    6 => [6], 7 => [7],
                },
            },
        },
        test_reorder_test_7: {
            types: {
                type 0 := { a, b } isa { BaseType::Str }
            },
            expected: {
                vars: [Type::Str(0.into()), Type::Str(0.into()), Type::Str(0.into())],
                ([0, 1, 2], [2, 0, 1]),
                {
                    0 => [0], 1 => [2],
                    2 => [4], 3 => [6],

                    4 => [1], 5 => [3],
                    6 => [5], 7 => [7],
                },
            },
        },
    }
}
