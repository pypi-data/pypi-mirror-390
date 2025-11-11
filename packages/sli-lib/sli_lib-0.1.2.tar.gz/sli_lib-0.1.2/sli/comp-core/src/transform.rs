//! A module for easing the process of transforming comp core expressions.
//! For transforming expressions with a certain transformer use [ConstraintTransformer].
pub mod copy_transform;
pub mod naive_transform;
pub mod satisfying_set_transform;
pub mod simplify_transform;
use std::marker::PhantomData;

use crate::{
    comp_core::{
        constraints::{Formulas, NodeIndex, TransformedConstraints},
        expression::{ExpressionIter, ExpressionRef},
        theory::Theory,
    },
    expression::free_variables,
};

pub trait Transformer<'a> {
    fn transform_expression(
        &mut self,
        from_expr: ExpressionRef<'a>,
        expr_transformer: &mut ExpressionTransformer,
    ) -> NodeIndex;
}

pub struct ConstraintTransformer<'a, T: Transformer<'a>> {
    transformer: T,
    phantom: PhantomData<&'a ()>,
}

impl<'a, T: Transformer<'a>> ConstraintTransformer<'a, T> {
    pub fn new(transformer: T) -> Self {
        Self {
            transformer,
            phantom: PhantomData,
        }
    }

    pub fn transform_theory(self, theory: &'a Theory) -> TransformedConstraints {
        self.transform_formulas(theory.formula_iter())
    }

    pub fn transform_formulas(self, formulas_iter: ExpressionIter<'a>) -> TransformedConstraints {
        self.transform_formulas_with_transformer(formulas_iter).0
    }

    pub fn transform_formulas_with_transformer(
        mut self,
        formulas_iter: ExpressionIter<'a>,
    ) -> (TransformedConstraints, T) {
        let mut expression_transformer =
            ExpressionTransformer::new(formulas_iter.expressions().rc_type_interps().clone());
        let mut formulas = Formulas::new();
        for from_expr in formulas_iter {
            let new_assertion = self
                .transformer
                .transform_expression(from_expr, &mut expression_transformer);
            debug_assert!(
                free_variables(
                    expression_transformer
                        .get_expressions()
                        .new_at(new_assertion)
                )
                .len()
                    == 0,
                "transformed into assertion with free variables, {:#?}",
                expression_transformer
                    .get_expressions()
                    .new_at(new_assertion),
            );
            formulas.push(new_assertion);
        }
        (
            TransformedConstraints {
                expressions: expression_transformer.take_expressions(),
                formulas,
            },
            self.transformer,
        )
    }
}

pub(crate) use tranform_assistor::ExpressionTransformer;

mod tranform_assistor {
    use sli_collections::{hash_map::IdHashMap, hash_set::IdHashSet};

    use super::simplify_transform::{
        HalfSimplifyResult, SimplifyResult, simplify_half_bin, simplify_node,
    };
    use crate::comp_core::{
        constraints::{BoundVarId, NodeIndex},
        expression::{
            AuxIndex, ExpressionRef, Expressions, IDomainPredicate, TransformedExpressions,
        },
        node::{
            AppliedAuxSymbBuilder, AppliedSymbBuilder, BinOpNode, BinOps, DefinitionBuilder,
            ElementNode, NodeEnum, NodeWVariables, QuantElementNode, QuantNodeBuilder, RuleBuilder,
            StandaloneNode, Variables, VariablesBuilder,
        },
        structure::TypeInterps,
    };
    use sli_collections::rc::Rc;
    use std::{collections::hash_map::Entry, mem::swap};

    impl From<&NodeIndex> for NodeIndex {
        fn from(value: &NodeIndex) -> Self {
            *value
        }
    }

    #[derive(Debug, Clone)]
    pub struct ExpressionTransformer {
        ctx: TransformContext,
        transformed_expressions: TransformedExpressions,
    }

    #[derive(Default, Clone, Debug)]
    pub struct TransformContext {
        quant_ids: IdHashMap<BoundVarId, BoundVarId>,
        aux_ids: IdHashMap<AuxIndex, AuxIndex>,
    }

    impl TransformContext {
        pub fn clear(&mut self) {
            self.quant_ids.clear();
            self.aux_ids.clear();
        }
    }

    impl ExpressionTransformer {
        pub fn new(type_interps: Rc<TypeInterps>) -> Self {
            Self {
                ctx: Default::default(),
                transformed_expressions: TransformedExpressions::new(type_interps),
            }
        }

        /// Clears all fields, reuses allocations.
        pub fn clear(&mut self) {
            self.transformed_expressions.clear();
            self.ctx.clear();
        }

        pub fn add_custom_var_translation(&mut self, from: BoundVarId, to: BoundVarId) {
            self.ctx.quant_ids.insert(from, to);
        }

        pub fn remove_custom_var_translation(&mut self, from: BoundVarId) {
            self.ctx.quant_ids.remove(&from);
        }

        pub fn new_var(&mut self) -> BoundVarId {
            self.transformed_expressions.new_bound_var()
        }

        pub fn get_quant_translation(&self) -> &IdHashMap<BoundVarId, BoundVarId> {
            &self.ctx.quant_ids
        }

        pub fn get_expr_ref(&self) -> &TransformedExpressions {
            &self.transformed_expressions
        }

        pub fn get_mut_expr_ref(&mut self) -> &mut TransformedExpressions {
            &mut self.transformed_expressions
        }

        pub fn get_expressions(&self) -> &Expressions {
            self.transformed_expressions.as_ref()
        }

        pub fn take_expressions(self) -> TransformedExpressions {
            self.transformed_expressions
        }

        /// Maps the given [BoundVarId] to a **new** id.
        ///
        /// For translating [ElementNode] and [QuantElementNode] you probably want
        /// [Self::translate_element] and [Self::translate_quant_element] respectively.
        pub fn translate_var(&mut self, var: BoundVarId) -> BoundVarId {
            match self.ctx.quant_ids.entry(var) {
                Entry::Occupied(o) => *o.get(),
                Entry::Vacant(v) => {
                    let new_var = self.transformed_expressions.new_bound_var();
                    v.insert(new_var);
                    new_var
                }
            }
        }

        pub fn translate_node(
            &mut self,
            node: StandaloneNode,
            from: &Expressions,
        ) -> StandaloneNode {
            match node {
                StandaloneNode::Quant(mut q) => {
                    q.variables = self.translate_variables(q.variables);
                    q.into()
                }
                StandaloneNode::Agg(mut agg) => {
                    agg.variables = self.translate_variables(agg.variables);
                    agg.into()
                }
                StandaloneNode::Element(el) => self.translate_element(el, from).into(),
                StandaloneNode::Rule(mut rule) => {
                    rule.head.variables = self.translate_variables(rule.head.variables);
                    rule.into()
                }
                StandaloneNode::AppliedAuxSymb(aux) => self.translate_aux_symbs(aux, from).into(),
                a => a,
            }
        }

        pub fn translate_element(
            &mut self,
            element: ElementNode,
            from: &Expressions,
        ) -> ElementNode {
            match element {
                ElementNode::Quant(q) => self.translate_quant_element(q, from).into(),
                a => a.into(),
            }
        }

        pub fn translate_args(
            &mut self,
            mut args: Vec<ElementNode>,
            from: &Expressions,
        ) -> Vec<ElementNode> {
            for i in 0..args.len() {
                args[i] = self.translate_element(args[i].clone(), from);
            }
            args
        }

        pub fn add_i_dom_pred(&mut self, id: NodeIndex, mut i_dom_pred: IDomainPredicate) {
            i_dom_pred.translate_layout(&self.ctx.quant_ids);
            self.transformed_expressions
                .quant_elements_insert(id, i_dom_pred);
        }

        pub fn translate_i_dom_pred(&self, mut i_dom_pred: IDomainPredicate) -> IDomainPredicate {
            i_dom_pred.translate_layout(&self.ctx.quant_ids);
            i_dom_pred
        }

        pub fn translate_variables(&mut self, mut q: VariablesBuilder) -> VariablesBuilder {
            q.map_vars(|f| self.translate_var(f));
            q.translate_i_dom_pred_layout(&self.ctx.quant_ids);
            q
        }

        pub fn translate_quant_element(
            &mut self,
            q: QuantElementNode,
            from: &Expressions,
        ) -> QuantElementNode {
            let mut new = q.clone();
            if let Some(new_var) = self.ctx.quant_ids.get(&q.bound_var_id) {
                new.bound_var_id = *new_var;
            } else {
                match self
                    .transformed_expressions
                    .get_type_map_mut()
                    .entry(q.bound_var_id)
                {
                    Entry::Vacant(v) => {
                        v.insert(from.type_map(q.bound_var_id));
                    }
                    Entry::Occupied(_) => {}
                };
            }
            new
        }

        pub fn translate_aux_symb_id(&mut self, old_aux: AuxIndex, from: &Expressions) -> AuxIndex {
            let new_aux = match self.ctx.aux_ids.entry(old_aux) {
                Entry::Vacant(v) => {
                    let aux_decl = from.aux_decl(old_aux);
                    let new_aux = self.transformed_expressions.add_aux_decl(aux_decl);
                    let symb = from.get(old_aux).to_owned();
                    self.transformed_expressions
                        .set_aux_with_index(symb, new_aux);
                    v.insert(new_aux);
                    new_aux
                }
                Entry::Occupied(v) => *v.get(),
            };
            new_aux
        }

        pub fn translate_aux_symbs(
            &mut self,
            mut symb: AppliedAuxSymbBuilder,
            from: &Expressions,
        ) -> AppliedAuxSymbBuilder {
            let old_aux = symb.index();
            let new_aux = self.translate_aux_symb_id(old_aux, from);
            symb.set_index(new_aux);
            symb
        }

        /// Push the node to the expression.
        ///
        /// Return the [NodeIndex] and a [bool] signifying if the node was not added due to a
        /// simplification.
        pub fn push_node_checked<'a, T>(
            &mut self,
            node: T,
            from_expr: ExpressionRef<'a>,
        ) -> (NodeIndex, bool)
        where
            T: Into<StandaloneNode>,
        {
            let node = node.into();
            let corrected_node = self.translate_node(node, from_expr.expressions());
            self.push_translated_node_checked(corrected_node, from_expr)
        }

        pub fn push_node<'a, T>(&mut self, node: T, from_expr: ExpressionRef<'a>) -> NodeIndex
        where
            T: Into<StandaloneNode>,
        {
            let node = node.into();
            let corrected_node = self.translate_node(node, from_expr.expressions());
            self.push_translated_node(corrected_node, from_expr)
        }

        pub fn push_translated_node<'a, T>(
            &mut self,
            corrected_node: T,
            from_expr: ExpressionRef<'a>,
        ) -> NodeIndex
        where
            T: Into<StandaloneNode>,
        {
            self.push_translated_node_checked(corrected_node, from_expr)
                .0
        }

        pub fn push_translated_simplified_node<'a, T>(
            &mut self,
            simplified_corrected_node: T,
            from_expr: ExpressionRef<'a>,
        ) -> NodeIndex
        where
            T: Into<StandaloneNode>,
        {
            self.transformed_expressions
                .push_node(simplified_corrected_node.into(), from_expr.start())
        }

        /// Push an already translated node to the expression.
        ///
        /// Returns the [NodeIndex] and a [bool] signifying if the node was not added due to a
        /// simplification.
        ///
        /// Pushing a node that has not been translated is unspecified behaviour.
        pub fn push_translated_node_checked<'a, T>(
            &mut self,
            corrected_node: T,
            from_expr: ExpressionRef<'a>,
        ) -> (NodeIndex, bool)
        where
            T: Into<StandaloneNode>,
        {
            let simplify_result =
                simplify_node(corrected_node.into(), self.transformed_expressions.as_ref());
            match simplify_result {
                SimplifyResult::Node(n) => (
                    self.transformed_expressions.push_node(n, from_expr.start()),
                    false,
                ),
                SimplifyResult::Existing(e) => (e, true),
            }
        }

        #[inline(always)]
        pub fn transform<'a, F, T>(&mut self, from_expr: ExpressionRef<'a>, transform: F) -> T
        where
            F: FnOnce(ExpressionRef<'a>, &mut ExpressionTransformer) -> T,
        {
            match NodeWVariables::get_bound_var(from_expr.start(), from_expr.expressions()) {
                Some(q) => {
                    self.preamble_variables(&q);
                    let ret = transform(from_expr, self);
                    self.postamble_variables(&q);
                    ret
                }
                _ => transform(from_expr, self),
            }
        }

        fn wrap_opt_transform<'a, F>(
            &mut self,
            from_expr: ExpressionRef<'a>,
            transform: F,
        ) -> NodeIndex
        where
            F: Fn(ExpressionRef<'a>, &mut ExpressionTransformer) -> Option<NodeIndex> + Clone,
        {
            if let Some(ret) = transform(from_expr, self) {
                ret
            } else {
                self.apply(from_expr, |expr_transformer, cur_expr| {
                    expr_transformer.wrap_opt_transform(cur_expr, transform.clone())
                })
            }
        }

        /// Applies given closure to node whilst auto translating variables.
        /// The closure must return `Option<T>`.
        /// `None` Signifies no transformation has been done.
        /// If no transformation has been done the node will be copied
        /// and then the optional transformation will be applied to the children.
        #[inline(always)]
        pub fn structless_opt_transform<'a, F>(
            &mut self,
            from_expr: ExpressionRef<'a>,
            transform: F,
        ) -> NodeIndex
        where
            F: Fn(ExpressionRef<'a>, &mut ExpressionTransformer) -> Option<NodeIndex> + Clone,
        {
            match NodeWVariables::get_bound_var(from_expr.start(), from_expr.expressions()) {
                Some(q) => {
                    self.preamble_variables(&q);
                    let ret = self.wrap_opt_transform(from_expr, transform);
                    self.postamble_variables(&q);
                    ret
                }
                _ => self.wrap_opt_transform(from_expr, transform),
            }
        }

        // TODO make adding an interpreted_node not copy everything maybe
        pub fn interpreted_node<'a>(&mut self, from_expr: ExpressionRef<'a>) -> NodeIndex {
            self.rec_copy(from_expr)
        }

        pub fn preamble_variables(&mut self, variables: &Variables) {
            for &var in variables.iter_vars() {
                self.translate_var(var);
            }
        }

        pub fn postamble_variables(&mut self, variables: &Variables) {
            for var in variables.iter_vars() {
                self.ctx.quant_ids.remove(var);
            }
        }

        /// Call provided closure for each child of first node of the given expression.
        /// For binary operators evaluates according to ExprType::eval\_first. If both should or
        /// should not be evaluated first the order is lhs and then rhs.
        pub fn apply<'a, T>(&mut self, cur_expr: ExpressionRef<'a>, mut apply: T) -> NodeIndex
        where
            T: FnMut(&mut Self, ExpressionRef<'a>) -> NodeIndex,
        {
            let node_enum = cur_expr.first_node_enum();
            let standalone_node: StandaloneNode;
            let from = cur_expr.expressions();
            match node_enum {
                NodeEnum::BinOps(bin_op) => {
                    let mut new_bin_op = bin_op.clone();
                    let which_first = (
                        cur_expr.new_at(bin_op.lhs).eval_first(),
                        cur_expr.new_at(bin_op.rhs).eval_first(),
                    );
                    let lhs = match which_first {
                        // lhs has children rhs does not, evaluate rhs first
                        (false, true) => false,
                        _ => true,
                    };

                    let child = if lhs {
                        new_bin_op.lhs = apply(self, cur_expr.new_at(bin_op.lhs));
                        new_bin_op.lhs
                    } else {
                        new_bin_op.rhs = apply(self, cur_expr.new_at(bin_op.rhs));
                        new_bin_op.rhs
                    };
                    // See if we can simplify with only one known side of binary op
                    match simplify_half_bin(bin_op.bin_op, child, lhs, self.get_expr_ref().as_ref())
                    {
                        HalfSimplifyResult::None => {}
                        HalfSimplifyResult::Node(b) => {
                            return self.push_node(b, cur_expr);
                        }
                    }
                    if lhs {
                        new_bin_op.rhs = apply(self, cur_expr.new_at(bin_op.rhs));
                    } else {
                        new_bin_op.lhs = apply(self, cur_expr.new_at(bin_op.lhs));
                    }
                    standalone_node = self.translate_node(new_bin_op.into(), from);
                }
                NodeEnum::Neg(n) => {
                    let mut neg_op = n.clone();
                    neg_op.child = apply(self, cur_expr.new_at(neg_op.child));
                    standalone_node = self.translate_node(neg_op.into(), from);
                }
                NodeEnum::NumNeg(n) => {
                    let mut neg_op = n.clone();
                    neg_op.child = apply(self, cur_expr.new_at(neg_op.child));
                    standalone_node = self.translate_node(neg_op.into(), from);
                }
                NodeEnum::IsInt(n) => {
                    let mut neg_op = n.clone();
                    neg_op.child = apply(self, cur_expr.new_at(neg_op.child));
                    standalone_node = self.translate_node(neg_op.into(), from);
                }
                NodeEnum::Quant(quant) => {
                    let mut new_quant = quant.clone();
                    self.preamble_variables(&quant.variables);
                    new_quant.formula = apply(self, cur_expr.new_at(quant.formula));
                    standalone_node =
                        self.translate_node(QuantNodeBuilder::from(new_quant).into(), from);
                    self.postamble_variables(&quant.variables);
                }
                NodeEnum::Element(e) => {
                    standalone_node = self.translate_node(e.into(), from);
                }
                NodeEnum::AppliedSymb(n) => {
                    let mut as_builder = AppliedSymbBuilder::new(n.index);
                    as_builder.kind = n.get_kind();
                    for child in n.child_iter() {
                        as_builder.add_arg(self.translate_element(child, from));
                    }
                    standalone_node = self.translate_node(as_builder.into(), from);
                }
                NodeEnum::AppliedAuxSymb(n) => {
                    let mut as_builder = AppliedAuxSymbBuilder::new(n.index);
                    for child in n.child_iter() {
                        as_builder.add_arg(self.translate_element(child, from));
                    }
                    standalone_node = self.translate_node(as_builder.into(), from);
                }
                NodeEnum::Ite(ite) => {
                    let mut new_ite = ite.clone();
                    new_ite.cond = apply(self, cur_expr.new_at(new_ite.cond));
                    new_ite.then_term = apply(self, cur_expr.new_at(new_ite.then_term));
                    new_ite.else_term = apply(self, cur_expr.new_at(new_ite.else_term));
                    standalone_node = self.translate_node(new_ite.into(), from);
                }
                NodeEnum::Agg(agg) => {
                    let mut new_agg = agg.clone();
                    self.preamble_variables(&agg.variables);
                    new_agg.formula = apply(self, cur_expr.new_at(new_agg.formula));
                    standalone_node = self.translate_node(new_agg.standalone().into(), from);
                    self.postamble_variables(&agg.variables);
                }
                NodeEnum::Rule(rule) => {
                    let rule_head = rule.head.clone().into();
                    let vars = rule.head.variables.clone();
                    self.preamble_variables(&vars);
                    let new_body = apply(self, cur_expr.new_at(rule.body));
                    let new_rule = RuleBuilder::new(rule_head, new_body);
                    standalone_node = self.translate_node(new_rule.into(), from);
                    self.postamble_variables(&vars);
                }
                NodeEnum::Def(def) => {
                    let mut new_def = DefinitionBuilder::new();
                    for rule in def.iter_indexes() {
                        let new_rule = apply(self, cur_expr.new_at(rule));
                        new_def.add_rule_index(new_rule, self.get_expr_ref().as_ref());
                    }
                    standalone_node = self.translate_node(new_def.into(), from);
                }
            }
            // TODO
            let _origin = if let Some(_m) = 1.into() {
                0.into()
                // m[&cur_expr.start()]
            } else {
                cur_expr.start()
            };
            self.push_translated_node(standalone_node, cur_expr)
        }

        pub fn rec_copy<'a>(&mut self, cur_expr: ExpressionRef<'a>) -> NodeIndex {
            self.apply(cur_expr, |s, c| s.rec_copy(c))
        }

        /// Creates chain op operators, returns None if iterator is empty
        pub fn create_op_chain(
            &mut self,
            op: BinOps,
            iter: impl Iterator<Item = NodeIndex>,
            from: ExpressionRef<'_>,
        ) -> Option<NodeIndex> {
            let mut op_chained = None;
            for value in iter {
                if let Some(op_chainedd) = op_chained {
                    op_chained = Some(self.push_node(BinOpNode::new(op, op_chainedd, value), from));
                } else {
                    op_chained = Some(value)
                }
            }
            op_chained
        }

        fn translate_aux_index_to_existing(
            &mut self,
            index: AuxIndex,
            to: AuxIndex,
            from: &Expressions,
        ) {
            match self.ctx.aux_ids.entry(index) {
                Entry::Vacant(v) => {
                    let symb = from.get(index).to_owned();
                    self.transformed_expressions.set_aux_with_index(symb, to);
                    v.insert(to);
                }
                Entry::Occupied(v) => {
                    v.get();
                }
            };
        }

        pub fn inner_transform_iter<'a, T>(
            &'a mut self,
            loc: NodeIndex,
            transform: T,
        ) -> InnerIterTransform<'a, T>
        where
            T: FnMut(ExpressionRef<'_>, &mut Self) -> Option<NodeIndex>,
        {
            let mut inner = Self::new(self.transformed_expressions.rc_type_interps().clone());
            let cur_bvar = self.transformed_expressions.cur_bound_var();
            inner.transformed_expressions.set_bound_var_start(cur_bvar);
            let empty_context: TransformContext = Default::default();
            InnerIterTransform {
                transform,
                from_loc: loc,
                empty_context,
                inner,
                outer: self,
            }
        }

        pub fn inner_transform_many<T>(&mut self, loc: NodeIndex, transform: T) -> Vec<NodeIndex>
        where
            T: FnOnce(ExpressionRef<'_>, &mut Self) -> Vec<NodeIndex>,
        {
            let expr = self.transformed_expressions.to_expression(loc).into();
            let mut inner = Self::new(self.transformed_expressions.rc_type_interps().clone());
            let cur_bvar = self.transformed_expressions.cur_bound_var();
            inner.transformed_expressions.set_bound_var_start(cur_bvar);
            let mut locs = transform(expr, &mut inner);
            let mut empty_context: TransformContext = Default::default();
            locs.iter_mut().for_each(|f| {
                empty_context.clear();
                *f = self.copy_from_inner_transform_with_context(&inner, *f, &mut empty_context);
            });
            locs
        }

        pub fn inner_transform<T>(&mut self, loc: NodeIndex, transform: T) -> NodeIndex
        where
            T: FnOnce(ExpressionRef<'_>, &mut Self) -> NodeIndex,
        {
            let expr = self.transformed_expressions.to_expression(loc).into();
            let mut inner = Self::new(self.transformed_expressions.rc_type_interps().clone());
            let cur_bvar = self.transformed_expressions.cur_bound_var();
            inner.transformed_expressions.set_bound_var_start(cur_bvar);
            let loc = transform(expr, &mut inner);
            self.copy_from_inner_transform(&inner, loc)
        }

        /// Does the first part of an inner transformation.
        ///
        /// See [Self::copy_from_inner_transform], [Self::copy_from_inner_transform_with_context_mapped] and
        /// [Self::copy_from_inner_transform_with_context] for the second part of an inner transformation.
        pub fn cinner_transform_with_other<T, R>(
            &mut self,
            loc: NodeIndex,
            transform: T,
            inner: &mut Self,
        ) -> R
        where
            T: FnOnce(ExpressionRef<'_>, &mut Self) -> R,
        {
            let expr = self.transformed_expressions.to_expression(loc).into();
            let cur_bvar = self.transformed_expressions.cur_bound_var();
            inner.clear();
            inner.transformed_expressions.set_bound_var_start(cur_bvar);
            transform(expr, inner)
        }

        pub fn inner_transform_maybe<T>(
            &mut self,
            loc: NodeIndex,
            transform: T,
        ) -> Option<NodeIndex>
        where
            T: FnOnce(ExpressionRef<'_>, &mut Self) -> Option<NodeIndex>,
        {
            let expr = self.transformed_expressions.to_expression(loc).into();
            let mut inner = Self::new(self.transformed_expressions.rc_type_interps().clone());
            let cur_bvar = self.transformed_expressions.cur_bound_var();
            inner.transformed_expressions.set_bound_var_start(cur_bvar);
            let loc =
                transform(expr, &mut inner).map(|f| self.copy_from_inner_transform(&inner, f));
            loc
        }

        pub fn copy_from_inner_transform(&mut self, inner: &Self, loc: NodeIndex) -> NodeIndex {
            let mut empty_context = Default::default();
            self.copy_from_inner_transform_with_context(inner, loc, &mut empty_context)
        }

        /// The given context must be empty.
        pub fn copy_from_inner_transform_with_context(
            &mut self,
            inner: &Self,
            loc: NodeIndex,
            empty_context: &mut TransformContext,
        ) -> NodeIndex {
            swap(&mut self.ctx, empty_context);
            // map aux index back to our index
            inner.ctx.aux_ids.iter().for_each(|(&ours, &their)| {
                self.translate_aux_index_to_existing(their, ours, inner.get_expressions());
            });
            self.ctx
                .aux_ids
                .extend(inner.ctx.aux_ids.iter().map(|f| (*f.1, *f.0)));
            let ret = self.rec_copy(inner.get_expr_ref().to_expression(loc).into());
            swap(&mut self.ctx, empty_context);
            ret
        }

        /// The given context must be empty.
        pub fn copy_from_inner_transform_with_context_mapped(
            &mut self,
            inner: &Self,
            loc: NodeIndex,
            empty_context: &mut TransformContext,
            to_map: &IdHashSet<NodeIndex>,
        ) -> (NodeIndex, IdHashMap<NodeIndex, NodeIndex>) {
            swap(&mut self.ctx, empty_context);
            // map aux index back to our index
            inner.ctx.aux_ids.iter().for_each(|(&ours, &their)| {
                self.translate_aux_index_to_existing(their, ours, inner.get_expressions());
            });
            self.ctx
                .aux_ids
                .extend(inner.ctx.aux_ids.iter().map(|f| (*f.1, *f.0)));
            let ret = self.mapped_rec_copy(inner.get_expr_ref().to_expression(loc).into(), to_map);
            swap(&mut self.ctx, empty_context);
            ret
        }

        /// Recursively copies while keeping track of where a [NodeIndex] got copied to
        ///
        /// Only keeps track of [NodeIndex] that are in the `to_map` argument.
        pub fn mapped_rec_copy<'a>(
            &mut self,
            cur_expr: ExpressionRef<'a>,
            to_map: &IdHashSet<NodeIndex>,
        ) -> (NodeIndex, IdHashMap<NodeIndex, NodeIndex>) {
            let mut mapped: IdHashMap<_, _> = Default::default();
            let mapped_ref = &mut mapped;
            let value = self.apply(cur_expr, move |s, c| {
                let new = s._mapped_rec_copy(c, to_map, mapped_ref);
                if to_map.contains(&c.start) {
                    mapped_ref.insert(c.start, new);
                }
                new
            });
            if to_map.contains(&cur_expr.start) {
                mapped.insert(cur_expr.start, value);
            }
            (value, mapped)
        }

        fn _mapped_rec_copy<'a>(
            &mut self,
            cur_expr: ExpressionRef<'a>,
            to_map: &IdHashSet<NodeIndex>,
            mapped: &mut IdHashMap<NodeIndex, NodeIndex>,
        ) -> NodeIndex {
            let value = self.apply(cur_expr, move |s, c| {
                let new = s._mapped_rec_copy(c, to_map, mapped);
                if to_map.contains(&c.start) {
                    mapped.insert(c.start, new);
                }
                new
            });
            value
        }
    }

    pub struct InnerIterTransform<'a, F>
    where
        F: FnMut(ExpressionRef<'_>, &mut ExpressionTransformer) -> Option<NodeIndex>,
    {
        transform: F,
        from_loc: NodeIndex,
        pub empty_context: TransformContext,
        pub inner: ExpressionTransformer,
        pub outer: &'a mut ExpressionTransformer,
    }

    impl<'a, F> InnerIterTransform<'a, F>
    where
        F: FnMut(ExpressionRef<'_>, &mut ExpressionTransformer) -> Option<NodeIndex>,
    {
        pub fn expr_transformer(&self) -> &ExpressionTransformer {
            &self.outer
        }

        pub fn expr_transformer_mut(&mut self) -> &mut ExpressionTransformer {
            self.outer
        }

        pub fn inner_mut(&mut self) -> &mut ExpressionTransformer {
            &mut self.inner
        }
    }

    impl<'a, F> Iterator for InnerIterTransform<'a, F>
    where
        F: FnMut(ExpressionRef<'_>, &mut ExpressionTransformer) -> Option<NodeIndex>,
    {
        type Item = NodeIndex;

        fn next(&mut self) -> Option<Self::Item> {
            let expr = self
                .outer
                .transformed_expressions
                .to_expression(self.from_loc)
                .into();
            self.inner.clear();
            let cur_var = self.outer.transformed_expressions.cur_bound_var();
            self.inner
                .transformed_expressions
                .set_bound_var_start(cur_var);
            let new = (self.transform)(expr, &mut self.inner);
            new.map(|f| {
                // make sure we empty new context
                self.empty_context.clear();
                self.outer.copy_from_inner_transform_with_context(
                    &self.inner,
                    f,
                    &mut self.empty_context,
                )
            })
        }
    }
}
