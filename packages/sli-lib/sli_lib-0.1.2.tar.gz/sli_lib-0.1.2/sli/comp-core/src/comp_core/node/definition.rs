use super::{ExprType, FromExpressionUnchecked, Node, NodeEnum, Variables, VariablesBuilder};
use crate::{
    comp_core::{
        IndexRepr,
        constraints::{BoundVarId, ExtraIndex, NodeIndex, ToConstraint, ToNodeArgs},
        expression::Expressions,
        vocabulary::{PfuncIndex, Symbol, Type},
    },
    interp_structures::InterpContext,
};
use indexmap::IndexSet;
use itertools::Either;
use std::{borrow::Cow, collections::HashSet, mem::swap};

#[derive(Debug, Clone)]
pub struct DefinitionBuilder {
    defined_symbs: IndexSet<PfuncIndex>,
    /// keeps track of dependencies of each definiendum
    symb_deps: Vec<HashSet<PfuncIndex>>,
    /// These NodeIndexes must be rules!
    /// And inner Vecs must be non empty
    rules: Vec<Vec<NodeIndex>>,
    inductive: bool,
}

impl DefinitionBuilder {
    pub fn new() -> Self {
        Self {
            defined_symbs: IndexSet::new(),
            symb_deps: Vec::new(),
            rules: Vec::new(),
            inductive: false,
        }
    }

    /// Creates symbol dependencies, used when converting a [Definition] to a
    /// [DefinitionBuilder].
    fn create_symb_deps(
        defined_symbs: &IndexSet<PfuncIndex>,
        rules: &Vec<Vec<NodeIndex>>,
        expr: &Expressions,
    ) -> Vec<HashSet<PfuncIndex>> {
        let mut symb_deps = Vec::new();
        for rules in rules.iter() {
            let mut cur_deps = HashSet::new();
            for &rule in rules {
                expr.to_expression(rule)
                    .for_each(&mut |node_enum| match node_enum {
                        NodeEnum::AppliedSymb(val) => {
                            cur_deps.insert(val.index);
                        }
                        _ => {}
                    })
            }
            symb_deps.push(cur_deps);
        }
        Self::fill_inductive_deps(defined_symbs, &mut symb_deps);
        symb_deps
    }

    /// Finds and fills dependencies of symbols caused by induction.
    fn fill_inductive_deps(
        defined_symbs: &IndexSet<PfuncIndex>,
        symb_deps: &mut Vec<HashSet<PfuncIndex>>,
    ) {
        let mut has_changed = true;
        while has_changed {
            has_changed = false;
            for i in 0..symb_deps.len() {
                for (j, other) in defined_symbs.iter().enumerate() {
                    if i == j {
                        continue;
                    }
                    if symb_deps[i].contains(other) {
                        let len_before = symb_deps[i].len();
                        // split_at_mut splits with provided index always in right slice.
                        // We have to make sure the other index is not in the same slice
                        let (deps_i, deps_j) = if i > j {
                            let (left, right) = symb_deps.split_at_mut(i);
                            (&mut right[0], &left[j])
                        } else {
                            let (left, right) = symb_deps.split_at_mut(j);
                            (&mut left[i], &right[0])
                        };
                        deps_i.extend(deps_j);
                        has_changed |= len_before != symb_deps[i].len();
                    }
                }
            }
        }
    }

    /// Extends symbol dependencies, for a previously existing or non-existing definiendum.
    /// If `def_pos` is [None] this means the definiendum did not previously exist so we must add
    /// it to all the relevant fields.
    fn extend_symb_deps(&mut self, def_pos: Option<usize>, body_id: NodeIndex, expr: &Expressions) {
        let (symb_deps, defined_symbs) = (&mut self.symb_deps, &self.defined_symbs);
        let symb_dep = match def_pos {
            Some(val) => &mut symb_deps[val],
            None => {
                symb_deps.push(HashSet::new());
                symb_deps.last_mut().unwrap()
            }
        };
        expr.to_expression(body_id).for_each(&mut |f| match f {
            NodeEnum::AppliedSymb(f) => {
                symb_dep.insert(f.index);
            }
            _ => {}
        });
        Self::fill_inductive_deps(defined_symbs, symb_deps);
    }

    fn is_inductive(&self) -> bool {
        self.defined_symbs
            .iter()
            .enumerate()
            .any(|(i, f)| self.symb_deps[i].contains(f))
    }

    pub fn add_rule_index(&mut self, rule_id: NodeIndex, expr: &Expressions) {
        let rule = Rule::try_from((rule_id, expr)).expect("Must be a Rule!!");
        self._add_rule_index(rule_id, rule.head.definiendum, rule.body, expr);
    }

    fn check_overlap(
        &self,
        new_rule: NodeIndex,
        definiendum_id: usize,
        expr: &Expressions,
    ) -> bool {
        let new_rule = Rule::try_from((new_rule, expr)).unwrap();
        let context = InterpContext::new(expr.get_type_map(), expr.type_interps());
        for &rule_id in &self.rules[definiendum_id] {
            let rule = Rule::try_from((rule_id, expr)).unwrap();
            match (
                new_rule.head.variables.get_i_dom_pred(),
                rule.head.variables.get_i_dom_pred(),
            ) {
                (Some(guard_new), Some(guard_old)) => {
                    let mut normalized_new = guard_new.bit_vec.clone();
                    for cur in normalized_new.mut_layout().iter_mut() {
                        let pos = new_rule
                            .head
                            .variables
                            .iter_vars()
                            .enumerate()
                            .find(|f| *f.1 == *cur)
                            .expect("definitions are not allowed free variables");
                        *cur = pos.0.into();
                    }
                    let mut normalized_old = guard_old.bit_vec.clone();
                    for cur in normalized_old.mut_layout().iter_mut() {
                        let pos = rule
                            .head
                            .variables
                            .iter_vars()
                            .enumerate()
                            .find(|f| *f.1 == *cur)
                            .expect("definitions are not allowed free variables");
                        *cur = pos.0.into();
                    }
                    if normalized_new.and(normalized_old, &context).cardinality() != 0 {
                        return true;
                    }
                }
                _ => return true,
            }
        }
        return false;
    }

    fn _add_rule_index(
        &mut self,
        rule_id: NodeIndex,
        definiendum: PfuncIndex,
        body_id: NodeIndex,
        expr: &Expressions,
    ) {
        let prev_id = self.defined_symbs.get_index_of(&definiendum);
        self.defined_symbs.insert(definiendum);
        Self::extend_symb_deps(self, prev_id, body_id, expr);
        self.inductive |= self.is_inductive();
        if let Some(prev_id) = prev_id {
            debug_assert!(!self.check_overlap(rule_id, prev_id, expr));
            self.rules[prev_id].push(rule_id);
        } else {
            self.rules.push(Vec::new());
            self.rules.last_mut().unwrap().push(rule_id);
        }
    }

    pub fn add_rule(&mut self, rule: RuleBuilder, expr: &mut Expressions) {
        let body_id = rule.body;
        let definiendum = rule.head.definiendum;
        let rule_id = expr.push_node(rule);
        self._add_rule_index(rule_id, definiendum, body_id, &expr)
    }
}

impl<'a> From<Definition<'a>> for DefinitionBuilder {
    fn from(value: Definition<'a>) -> Self {
        let rules = value.iter_indexes_nested().map(|f| f.collect()).collect();
        let defined_symbs = value.iter_definiendums().collect();
        let symb_deps = Self::create_symb_deps(&defined_symbs, &rules, value.expr);
        Self {
            defined_symbs,
            symb_deps,
            rules,
            inductive: value.inductive,
        }
    }
}

#[derive(Debug, Clone)]
pub struct Definition<'a> {
    extra_start: IndexRepr,
    // Inner array: first index is start, second is len
    // first index is boolean value denoting if definiendum is inductively defined
    // second index till end are indexes of rules of definiendum
    rule_slices: &'a [[ExtraIndex; 2]],
    inductive: bool,
    expr: &'a Expressions,
}

const START_RULES: usize = 1;
const INDUCTIVE_POS: usize = 0;

impl<'a> Definition<'a> {
    pub fn is_inductive(&self) -> bool {
        self.inductive
    }

    fn slice_definiendum_rules(&self, index: usize) -> &[NodeIndex] {
        let start = IndexRepr::from(self.rule_slices[index][0])
            + self.extra_start
            + IndexRepr::try_from(START_RULES).unwrap();
        let len = self.rule_slices[index][1];
        unsafe {
            core::mem::transmute(
                self.expr.extra_slice(
                    start.into()..(IndexRepr::from(start) + IndexRepr::from(len)).into(),
                ),
            )
        }
    }

    fn slice_definiendum_info(&self, index: usize) -> &[IndexRepr] {
        let start = IndexRepr::from(self.rule_slices[index][0]) + self.extra_start;
        unsafe {
            core::mem::transmute(self.expr.extra_slice(
                start.into()
                    ..(IndexRepr::from(start) + IndexRepr::try_from(START_RULES).unwrap()).into(),
            ))
        }
    }

    fn is_def_inductive_pos(&self, index: usize) -> bool {
        let value = self.slice_definiendum_info(index)[INDUCTIVE_POS];
        value != 0
    }

    /// Returns true is symbol is inductively defined.
    /// Returns false is given symbol is not defined in this definition or if the symbol
    /// is not inductively defined.
    pub fn is_def_inductive(&self, symbol: PfuncIndex) -> bool {
        self.iter_inductive().any(|f| f.0 == symbol && f.1)
    }

    pub fn iter_rules(&self) -> impl Iterator<Item = Rule> {
        self.iter_indexes()
            .map(|rule_id| Rule::from_node((rule_id, self.expr)))
    }

    pub fn iter_rules_and_indexes(&self) -> impl Iterator<Item = (Rule, NodeIndex)> {
        self.iter_indexes()
            .map(|rule_id| (Rule::from_node((rule_id, self.expr)), rule_id))
    }

    pub fn iter_definiendums(&self) -> impl Iterator<Item = PfuncIndex> + '_ {
        self.rule_slices.iter().enumerate().map(|(i, _)| {
            let rule_id = self.slice_definiendum_rules(i)[0];
            Rule::from_node((rule_id, self.expr)).head.definiendum
        })
    }

    /// Returns an iterator that iterates over tuples of [PfuncIndexes](PfuncIndex) and another
    /// iterator.
    /// The nested iterator iterates over all the rules of the definiendum denoted by the
    /// [PfuncIndex] in the tuple.
    pub fn iter_rules_nested(
        &self,
    ) -> impl Iterator<Item = (PfuncIndex, impl Iterator<Item = Rule> + '_)> + '_ {
        self.iter_rules_nested_full().map(|f| (f.0, f.2))
    }

    /// Returns an iterator that iterates over tuples of [PfuncIndexes](PfuncIndex), bool,
    /// and another iterator.
    /// The bool value represents if the definendum given by the [PfuncIndex] is inductively
    /// defined.
    /// The nested iterator iterates over all the rules of the definiendum denoted by the
    /// [PfuncIndex] in the tuple.
    pub fn iter_rules_nested_full(
        &self,
    ) -> impl Iterator<Item = (PfuncIndex, bool, impl Iterator<Item = Rule> + '_)> + '_ {
        self.rule_slices.iter().enumerate().map(move |(i, _)| {
            let slice = self.slice_definiendum_rules(i);
            let is_inductive = self.is_def_inductive_pos(i);
            let lookahead = Rule::from_node((slice[0], self.expr)).head.definiendum;
            (
                lookahead,
                is_inductive,
                slice.iter().copied().map(move |f| {
                    let ret = Rule::from_node((f, self.expr));
                    debug_assert!(lookahead == ret.head.definiendum);
                    ret
                }),
            )
        })
    }

    /// An iterator over all definiendums in definition and a boolean denoting if the defniendum is
    /// inductively defined.
    pub fn iter_inductive(&self) -> impl Iterator<Item = (PfuncIndex, bool)> + '_ {
        self.rule_slices.iter().enumerate().map(|(i, _)| {
            let slice = self.slice_definiendum_rules(i);
            let lookahead = Rule::from_node((slice[0], self.expr)).head.definiendum;
            let is_inductive = self.is_def_inductive_pos(i);
            (lookahead, is_inductive)
        })
    }

    pub fn len(&self) -> usize {
        self.rule_slices
            .iter()
            .map(|[_, len]| usize::from(*len))
            .sum()
    }

    pub fn iter_indexes(&self) -> impl Iterator<Item = NodeIndex> + '_ {
        self.iter_indexes_nested().flatten()
    }

    pub fn iter_indexes_nested(
        &self,
    ) -> impl Iterator<Item = impl Iterator<Item = NodeIndex> + '_> + '_ {
        self.rule_slices
            .iter()
            .enumerate()
            .map(|(i, _)| self.slice_definiendum_rules(i).iter().copied())
    }
}

impl<'a> FromExpressionUnchecked<'a> for Definition<'a> {
    fn from_node<T: AsRef<Expressions>>(value: (NodeIndex, &'a T)) -> Self {
        let expression = value.1.as_ref();
        let index = value.0;
        let node = expression.nodes(index);
        debug_assert_eq!(node.expr, ExprType::Definition);
        let child_start = node.data[0];
        let definiendum_amount = node.data[1];
        let inductive = expression.extra(child_start.into()) != 0;
        let definiendum_slices_start = child_start + 1;
        // * 2 since for each definiendum we have start and len
        let definiendun_slices_end = definiendum_slices_start + definiendum_amount * 2;
        let rule_slices: &'a [ExtraIndex] = unsafe {
            core::mem::transmute::<&[IndexRepr], &[ExtraIndex]>(
                expression
                    .extra_slice(definiendum_slices_start.into()..definiendun_slices_end.into()),
            )
        };
        let rule_slices = unsafe {
            core::slice::from_raw_parts(
                rule_slices.as_ptr() as *const [ExtraIndex; 2],
                // divide length by two since type is [[ExtraIndex; 2]]
                // this division will always be perfect since we did a definiendum_amount * 2
                // above
                rule_slices.len() / 2,
            )
        };
        let extra_start = definiendun_slices_end;
        Self {
            extra_start,
            rule_slices,
            inductive,
            expr: expression,
        }
    }
}

// pairs of begin and len
// begin starts at 0 and is offset by previous rules arrays
// len is len
// [ [Begin Len] ... | [ inductive?, NodeIndex ..], ... ]
impl ToConstraint for DefinitionBuilder {
    fn extra_children(&self) -> Cow<'_, [IndexRepr]> {
        let mut accum_len = 0;
        Cow::Owned(
            // first add if inductive
            std::iter::once(self.inductive as IndexRepr)
                .chain(
                    // add info about rules
                    // pairs of numbers each,
                    // first denotes offset of rules
                    // second amount of rules for definiendum
                    self.rules
                        .iter()
                        .map(|f| {
                            let ret = [
                                IndexRepr::try_from(accum_len).unwrap(),
                                f.len().try_into().unwrap(),
                            ];
                            // account for individual inductive bool
                            accum_len += f.len() + START_RULES;
                            ret
                        })
                        .flatten(),
                )
                .chain(
                    self.rules
                        .iter()
                        .zip(self.defined_symbs.iter())
                        .enumerate()
                        .map(|(i, (f, definiendum))| {
                            core::iter::once(
                                // Add if definiendum of next rules is inductive
                                self.symb_deps[i].contains(definiendum) as IndexRepr,
                            )
                            .chain(
                                // Add indexes of actual rules
                                f.iter().copied().map(|f| IndexRepr::from(f)),
                            )
                        })
                        .flatten(),
                )
                .collect(),
        )
    }

    fn to_node(self, ToNodeArgs { extra_len, .. }: ToNodeArgs) -> super::Node {
        Node {
            expr: ExprType::Definition,
            data: [
                extra_len.try_into().unwrap(),
                self.rules.len().try_into().unwrap(),
            ],
        }
    }
}

#[derive(Debug, Clone)]
pub struct RuleHeadBuilder {
    pub variables: VariablesBuilder,
    pub definiendum: PfuncIndex,
}

impl RuleHeadBuilder {
    pub fn with_vars(definiendum: Symbol, variables: VariablesBuilder) -> Result<Self, ()> {
        let func_arity = definiendum.domain.len();
        let eq_var = match definiendum.codomain {
            Type::Bool => 0,
            _ => 1,
        };
        if variables.len() != func_arity + eq_var {
            return Err(());
        }
        Ok(Self {
            variables,
            definiendum: definiendum.index,
        })
    }

    pub fn new(definiendum: Symbol, expr: &mut Expressions) -> Self {
        Self {
            variables: Self::create_canonical_vars(definiendum.clone(), || expr.new_bound_var()),
            definiendum: definiendum.index,
        }
    }

    /// Canonical vars are guaranteed to have the following format
    /// `[vars of args in order] + extra var if codomain is not boolean`
    pub fn create_canonical_vars<F: FnMut() -> BoundVarId>(
        definiendum: Symbol,
        mut new_bound_var: F,
    ) -> VariablesBuilder {
        let mut variables = VariablesBuilder::new();
        for type_enum in definiendum.domain.iter() {
            variables.add_var(new_bound_var(), *type_enum);
        }
        match definiendum.codomain {
            Type::Bool => {}
            other => variables.add_var(new_bound_var(), other),
        }
        variables
    }

    fn empty() -> Self {
        Self {
            variables: VariablesBuilder::new(),
            definiendum: 0.into(),
        }
    }
}

impl<'a> From<RuleHead<'a>> for RuleHeadBuilder {
    fn from(value: RuleHead<'a>) -> Self {
        Self {
            variables: value.variables.into(),
            definiendum: value.definiendum.into(),
        }
    }
}

#[derive(Debug, Clone)]
pub struct RuleHead<'a> {
    pub variables: Variables<'a>,
    pub definiendum: PfuncIndex,
}

impl<'a> FromExpressionUnchecked<'a> for RuleHead<'a> {
    fn from_node<T: AsRef<Expressions>>(value: (NodeIndex, &'a T)) -> Self {
        let expression = value.1.as_ref();
        let index = value.0;
        let node = expression.nodes(index);
        debug_assert_eq!(node.expr, ExprType::RuleHead);
        let definiendum = node.data[0].into();
        let variables_id: NodeIndex = node.data[1].into();
        let variables = Variables::from_node((variables_id, expression));
        Self {
            variables,
            definiendum,
        }
    }
}

impl ToConstraint for RuleHeadBuilder {
    fn sub_node(&mut self) -> Option<super::StandaloneNode> {
        let mut dummy = VariablesBuilder::new();
        swap(&mut self.variables, &mut dummy);
        Some(dummy.into())
    }

    fn to_node(self, ToNodeArgs { sub, .. }: ToNodeArgs) -> super::Node {
        Node {
            expr: ExprType::RuleHead,
            data: [self.definiendum.into(), sub.unwrap().into()],
        }
    }
}

#[derive(Debug, Clone)]
pub struct RuleBuilder {
    pub head: RuleHeadBuilder,
    pub body: NodeIndex,
}

impl RuleBuilder {
    pub fn new(head: RuleHeadBuilder, body: NodeIndex) -> Self {
        RuleBuilder { head, body }
    }
}

impl<'a> From<Rule<'a>> for RuleBuilder {
    fn from(value: Rule<'a>) -> Self {
        Self {
            head: value.head.into(),
            body: value.body,
        }
    }
}

#[derive(Debug, Clone)]
pub struct Rule<'a> {
    pub head: RuleHead<'a>,
    pub body: NodeIndex,
}

impl<'a> FromExpressionUnchecked<'a> for Rule<'a> {
    fn from_node<T: AsRef<Expressions>>(value: (NodeIndex, &'a T)) -> Self {
        let expression = value.1.as_ref();
        let node = expression.nodes(value.0);
        debug_assert_eq!(node.expr, ExprType::Rule);
        let rule_id: NodeIndex = node.data[0].into();
        let head = RuleHead::from_node((rule_id, expression));
        let body = node.data[1].into();
        Self { head, body }
    }
}

impl ToConstraint for RuleBuilder {
    fn sub_node(&mut self) -> Option<super::StandaloneNode> {
        let mut dummy = RuleHeadBuilder::empty();
        swap(&mut self.head, &mut dummy);
        Some(dummy.into())
    }

    fn to_node(self, ToNodeArgs { sub, .. }: ToNodeArgs) -> super::Node {
        Node {
            expr: ExprType::Rule,
            data: [sub.unwrap().into(), self.body.into()],
        }
    }
}

// Helper node for transformations that want to map a singular rule to many rules.
// Besides from existing when transforming in such transformations this node must not be reachable
// otherwise.
#[derive(Clone, Debug)]
pub struct Rules<'a> {
    pub rules: &'a [NodeIndex],
}

impl<'a> Rules<'a> {
    pub fn iter_rules(&self, expr: &'a Expressions) -> impl Iterator<Item = Rule<'a>> {
        self.rules
            .iter()
            .map(move |f| Rule::try_from((*f, expr)).unwrap())
    }

    pub fn iter_rules_and_indexes(
        &self,
        expr: &'a Expressions,
    ) -> impl Iterator<Item = (Rule<'a>, NodeIndex)> {
        self.rules
            .iter()
            .map(move |f| (Rule::try_from((*f, expr)).unwrap(), *f))
    }
}

impl<'a, T: AsRef<Expressions>> TryFrom<(NodeIndex, &'a T)> for Rules<'a> {
    type Error = ();
    fn try_from(value: (NodeIndex, &'a T)) -> Result<Self, Self::Error> {
        let expression = value.1.as_ref();
        let node = expression.nodes(value.0);
        match node.expr {
            ExprType::Rules => Ok(<Rules>::from_node(value)),
            _ => Err(()),
        }
    }
}

/// Builder for [Rules].
#[derive(Clone, Debug)]
pub struct RulesBuilder {
    rules: Vec<NodeIndex>,
}

impl RulesBuilder {
    pub fn new() -> Self {
        Self {
            rules: Default::default(),
        }
    }

    pub fn add_rule_index(&mut self, rule_id: NodeIndex, expr: &Expressions) {
        let _ = Rule::try_from((rule_id, expr)).expect("Must be a Rule!!");
        self.add_rule_index_unchecked(rule_id);
    }

    pub fn add_rule_index_unchecked(&mut self, rule_id: NodeIndex) {
        self.rules.push(rule_id);
    }

    pub fn complete(self) -> Result<RulesComplete, Either<NodeIndex, ()>> {
        match self.rules.as_slice() {
            [] => Err(Either::Right(())),
            [rule] => Err(Either::Left(*rule)),
            [_, _, ..] => Ok(RulesComplete { rules: self.rules }),
        }
    }
}

#[derive(Clone, Debug)]
pub struct RulesComplete {
    // these rules contain either zero or more than 2 rules
    rules: Vec<NodeIndex>,
}

impl RulesComplete {
    pub fn empty() -> RulesComplete {
        RulesComplete {
            rules: Default::default(),
        }
    }
}

impl ToConstraint for RulesComplete {
    fn extra_children(&self) -> Cow<'_, [IndexRepr]> {
        let rules_as_index_repr =
            unsafe { core::mem::transmute::<&[NodeIndex], &[IndexRepr]>(self.rules.as_slice()) };
        Cow::Borrowed(rules_as_index_repr)
    }

    fn to_node(self, args: ToNodeArgs) -> Node {
        Node {
            expr: ExprType::Rules,
            data: [
                args.extra_len.try_into().unwrap(),
                self.rules.len().try_into().unwrap(),
            ],
        }
    }
}

impl<'a> FromExpressionUnchecked<'a> for Rules<'a> {
    fn from_node<T: AsRef<Expressions>>(value: (NodeIndex, &'a T)) -> Self {
        let expression = value.1.as_ref();
        let node = expression.nodes(value.0);
        debug_assert_eq!(node.expr, ExprType::Rules);
        let rules_slice =
            expression.extra_slice(node.data[0].into()..(node.data[0] + node.data[1]).into());
        Self {
            rules: unsafe { core::mem::transmute::<&[IndexRepr], &[NodeIndex]>(rules_slice) },
        }
    }
}
