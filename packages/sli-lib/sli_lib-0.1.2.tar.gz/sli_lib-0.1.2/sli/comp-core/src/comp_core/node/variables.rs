use super::{ExprType, FromExpressionUnchecked, Node};
use crate::comp_core::{
    IndexRepr,
    constraints::{BoundVarId, ExtraIndex, NodeIndex, ToConstraint, ToNodeArgs},
    expression::{Expressions, IDomainPredicate, TypeMap},
    vocabulary::Type,
};
use itertools::Itertools;
use sli_collections::hash_map::IdHashMap;
use std::{borrow::Cow, fmt::Debug, iter::Zip, mem::transmute, slice::Iter};

#[derive(Clone)]
pub struct Variables<'a> {
    dom_pred_id: NodeIndex,
    variable_ids: &'a [BoundVarId],
    /// A guard for the domain of the variables.
    /// e.g. for a universal quantification this is equivalent to:
    /// ```idp
    /// !x, y, ...: i_dom_pred(x, y, ...) => ...
    /// ```
    i_dom_pred: Option<&'a IDomainPredicate>,
    type_map: &'a TypeMap,
}

impl<'a> AsRef<[BoundVarId]> for Variables<'a> {
    fn as_ref(&self) -> &[BoundVarId] {
        self.variable_ids
    }
}

impl<'a> Debug for Variables<'a> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self.get_i_dom_pred() {
            None => write!(f, "[{:?}]", self.iter().format(", ")),
            Some(i) => write!(
                f,
                "[{:?}] over [{:?}] in {{{:?}}}",
                self.iter().format(", "),
                i.layout().iter().format(", "),
                i.iter_new().format(", ")
            ),
        }
    }
}

impl<'a> Variables<'a> {
    /// The [NodeIndex] used for storing the [IDomainPredicate].
    pub fn dom_pred_id(&self) -> NodeIndex {
        self.dom_pred_id
    }

    pub fn contains(&self, var: BoundVarId) -> bool {
        if let Some(_) = self.iter_vars().position(|x| *x == var) {
            true
        } else {
            false
        }
    }

    pub fn slice_vars(&self) -> &'a [BoundVarId] {
        self.variable_ids
    }

    pub fn iter(&self) -> impl Iterator<Item = (BoundVarId, Type)> + '_ {
        self.variable_ids
            .iter()
            .copied()
            .map(|f| (f, self.type_map[&f]))
    }

    pub fn iter_vars(&self) -> Iter<'a, BoundVarId> {
        self.variable_ids.iter()
    }

    pub fn last(&self) -> BoundVarId {
        self.variable_ids[self.variable_ids.len() - 1]
    }

    pub fn first(&self) -> BoundVarId {
        self.variable_ids[0]
    }

    pub fn iter_types(&self) -> impl Iterator<Item = Type> + 'a {
        self.variable_ids.iter().map(|f| self.type_map[f])
    }

    pub fn len(&self) -> usize {
        self.variable_ids.len()
    }

    pub fn get(&self, index: usize) -> Option<(BoundVarId, Type)> {
        if index < self.len() {
            let var = self.variable_ids[index];
            Some((var, self.type_map[&var]))
        } else {
            None
        }
    }

    pub fn get_i_dom_pred(&self) -> Option<&'a IDomainPredicate> {
        self.i_dom_pred
    }
}

#[derive(Debug, Clone)]
pub struct VariablesBuilder {
    variables: Vec<BoundVarId>,
    i_dom_pred: Option<IDomainPredicate>,
    types: Vec<Type>,
}

impl AsRef<[BoundVarId]> for VariablesBuilder {
    fn as_ref(&self) -> &[BoundVarId] {
        self.variables.as_ref()
    }
}

impl VariablesBuilder {
    pub fn new() -> VariablesBuilder {
        Self {
            variables: Vec::new(),
            i_dom_pred: None,
            types: Vec::new(),
        }
    }

    pub fn last(&self) -> BoundVarId {
        *self.variables.last().unwrap()
    }

    pub fn get_i_dom_pred(&self) -> Option<&IDomainPredicate> {
        (&self.i_dom_pred).into()
    }

    pub fn take_i_dom_pred(&mut self) -> Option<IDomainPredicate> {
        self.i_dom_pred.take()
    }

    pub fn set_i_dom_pred(&mut self, new: IDomainPredicate) {
        self.i_dom_pred = new.into();
    }

    pub fn slice_vars(&self) -> &[BoundVarId] {
        self.variables.as_slice()
    }

    pub fn add_var(&mut self, bound_var_id: BoundVarId, type_enum: Type) {
        self.variables.push(bound_var_id);
        self.types.push(type_enum);
    }

    pub fn map_vars<F: FnMut(BoundVarId) -> BoundVarId>(&mut self, mut map: F) {
        for var in self.variables.iter_mut() {
            let new_var = map(*var);
            *var = new_var;
        }
    }

    pub fn translate_i_dom_pred_layout(
        &mut self,
        var_translation: &IdHashMap<BoundVarId, BoundVarId>,
    ) {
        if let Some(ref mut i_dom_pred) = self.i_dom_pred {
            i_dom_pred.translate_layout(var_translation)
        }
    }

    pub fn retain<F: FnMut(&BoundVarId) -> bool>(&mut self, map: F) {
        let to_retain = self.variables.iter().map(map).collect::<Box<[_]>>();
        let mut retain_iter = to_retain.iter();
        self.variables.retain(|_| *retain_iter.next().unwrap());
        let mut retain_iter = to_retain.iter();
        self.types.retain(|_| *retain_iter.next().unwrap());
    }

    pub fn iter_vars(&self) -> Iter<'_, BoundVarId> {
        self.variables.iter()
    }

    pub fn iter_types(&self) -> Iter<'_, Type> {
        self.types.iter()
    }

    pub fn iter(&self) -> impl Iterator<Item = (BoundVarId, Type)> + '_ {
        self.iter_vars().copied().zip(self.iter_types().cloned())
    }

    pub fn remove_at_index(&mut self, index: usize) {
        self.variables.remove(index);
        self.types.remove(index);
    }

    pub fn len(&self) -> usize {
        self.variables.len()
    }

    pub fn get(&self, index: usize) -> Option<(BoundVarId, Type)> {
        if index < self.len() {
            Some((self.variables[index], self.types[index]))
        } else {
            None
        }
    }

    pub fn from_ref_without_guard<'a>(value: Variables<'a>) -> Self {
        let mut variables = Vec::new();
        variables.reserve_exact(value.variable_ids.len());
        variables.extend(value.iter_vars());
        let mut types = Vec::new();
        variables.reserve_exact(value.variable_ids.len());
        types.extend(value.iter_types());
        Self {
            variables,
            i_dom_pred: None,
            types,
        }
    }
}

impl FromIterator<(BoundVarId, Type)> for VariablesBuilder {
    fn from_iter<T: IntoIterator<Item = (BoundVarId, Type)>>(iter: T) -> Self {
        let (variables, types) = iter.into_iter().unzip();
        Self {
            variables,
            types,
            i_dom_pred: None,
        }
    }
}

impl<'a> From<Variables<'a>> for VariablesBuilder {
    fn from(value: Variables<'a>) -> Self {
        let mut ret = Self::from_ref_without_guard(value.clone());
        if let Some(guard) = value.get_i_dom_pred() {
            ret.set_i_dom_pred(guard.clone());
        }
        ret
    }
}

impl<'a> FromExpressionUnchecked<'a> for Variables<'a> {
    fn from_node<T: AsRef<Expressions>>(value: (NodeIndex, &'a T)) -> Self {
        let expression = value.1.as_ref();
        let node = expression.nodes(value.0);
        debug_assert_eq!(node.expr, ExprType::Variables);
        let start_extra: ExtraIndex = node.data[0].into();
        let extra_len: ExtraIndex = (node.data[1] + IndexRepr::from(start_extra)).into();
        let variable_ids = expression.extra_slice(start_extra..(extra_len));
        let i_dom_pred = expression.quant_elements_get(value.0);
        Self {
            dom_pred_id: value.0,
            i_dom_pred,
            variable_ids: unsafe { transmute::<&[IndexRepr], &[BoundVarId]>(variable_ids) },
            type_map: expression.get_type_map(),
        }
    }
}

impl ToConstraint for VariablesBuilder {
    fn extra_children(&self) -> Cow<'_, [IndexRepr]> {
        Cow::Borrowed(unsafe { transmute::<&[BoundVarId], &[IndexRepr]>(self.variables.as_ref()) })
    }

    fn to_type_map(&self) -> Zip<Iter<'_, BoundVarId>, Iter<'_, Type>> {
        self.variables.iter().zip(self.types.iter())
    }

    fn quant_elements(&mut self) -> Option<IDomainPredicate> {
        self.i_dom_pred.take()
    }

    fn to_node(self, ToNodeArgs { extra_len, .. }: ToNodeArgs) -> Node {
        debug_assert!(self.variables.len() == self.types.len());
        Node {
            expr: ExprType::Variables,
            data: [
                extra_len.try_into().unwrap(),
                self.variables.len().try_into().unwrap(),
            ],
        }
    }
}
