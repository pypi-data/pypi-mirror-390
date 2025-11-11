use crate::comp_core::expression::{AuxIndex, ExpressionIter};
use crate::comp_core::node::{
    AppliedAuxSymbBuilder, AppliedSymbBuilder, BinOpNode, BinOps, Definition, NegNode, QuantKind,
    QuantNodeBuilder, Rule,
};
use crate::comp_core::vocabulary::{PfuncIndex, Symbol, Type};
use crate::transform::Transformer;
use crate::{
    comp_core::{
        constraints::NodeIndex,
        expression::ExpressionRef,
        node::{NodeEnum, QuantElementNode},
    },
    transform::ExpressionTransformer,
};
use sli_collections::{hash_map::IdHashMap, hash_set::IdHashSet};

/// Replaces definitions with their Clark's completion or level mapping
/// e.g.
/// ```text
/// {
///     !x: P(x) <- x = a.
///     !x: P(x) <- ~o(x).
///     !x: P(x) <- r(x).
/// }
/// ```
///
/// would become:
/// ```text
/// !x: P(x) <=> (x = a | ~o(x) | r(x)).
/// ```
///
/// ```text
/// {
///     p(x) <- r(x).
///     r(x) <- p(x).
/// }
/// ```
///
/// would become:
/// ```text
/// (!x:
///   (p(x) => r(x) & aux_p(x) > aux_r(x)) &
///   (p(x) <= r(x) | aux_p(x) < aux_r(x))
/// ) &
/// (!x:
///   (r(x) => p(x) & aux_r(x) > aux_p(x)) &
///   (r(x) <= p(x) | aux_r(x) < aux_p(x))
/// ).
/// ```
///
/// Do note that each rule becomes its own quantification because rules may not overlap and for a
/// single definiendum all rules must describe its entire domain.
#[derive(Clone)]
pub struct DefTransform {
    completion_vec: Vec<NodeIndex>,
}

impl DefTransform {
    pub fn new() -> Self {
        Self {
            completion_vec: Vec::new(),
        }
    }

    fn create_clarks_completion<'a>(
        &mut self,
        def_symbol: Symbol,
        rules: impl Iterator<Item = Rule<'a>>,
        from_expr: ExpressionRef<'a>,
        expr_transformer: &mut ExpressionTransformer,
    ) {
        for rule in rules {
            expr_transformer.preamble_variables(&rule.head.variables);
            let body = expr_transformer.rec_copy(from_expr.new_at(rule.body));
            let mut applied_symb = AppliedSymbBuilder::new(def_symbol.index);
            let vars = expr_transformer.translate_variables(rule.head.variables.clone().into());
            let lhs = {
                for (var, type_e) in vars.iter().take(def_symbol.domain.len()) {
                    applied_symb.add_arg(QuantElementNode::new(var, type_e).into())
                }
                if def_symbol.codomain != Type::Bool {
                    let last_var = QuantElementNode::new(
                        *vars.slice_vars().last().unwrap(),
                        def_symbol.codomain,
                    );
                    let var_id = expr_transformer.push_translated_node(last_var, from_expr);
                    let applied_symb_id =
                        expr_transformer.push_translated_node(applied_symb, from_expr);
                    expr_transformer.push_translated_node(
                        BinOpNode::new(BinOps::Eq, applied_symb_id, var_id),
                        from_expr,
                    )
                } else {
                    expr_transformer.push_translated_node(applied_symb, from_expr)
                }
            };
            let eqv = expr_transformer
                .push_translated_node(BinOpNode::new(BinOps::Eqv, lhs, body), from_expr);
            // Since rules must not overlap and the union of all quantifications in the head of
            // rules for a single definiendum must be over the entire domain of the definiendum,
            // this is ok (or we explicitly allow the definition completion to be partial).
            let uni = QuantNodeBuilder::new(QuantKind::UniQuant, vars, eqv);
            self.completion_vec
                .push(expr_transformer.push_translated_node(uni, from_expr));
            expr_transformer.postamble_variables(&rule.head.variables);
        }
    }

    fn create_level_mapping<'a>(
        &mut self,
        def_symbol: Symbol,
        level_symbols: &IdHashMap<PfuncIndex, AuxIndex>,
        rules: impl Iterator<Item = Rule<'a>>,
        from_expr: ExpressionRef<'a>,
        expr_transformer: &mut ExpressionTransformer,
    ) {
        for rule in rules {
            expr_transformer.preamble_variables(&rule.head.variables);
            let vars = expr_transformer.translate_variables(rule.head.variables.clone().into());
            // reusable applied level map symbol of definiendum
            let head_level = {
                let args = vars
                    .iter()
                    .take(def_symbol.domain.len())
                    .map(|(var, type_e)| QuantElementNode::new(var, type_e).into())
                    .collect();
                expr_transformer.push_translated_node(
                    AppliedAuxSymbBuilder::apply(level_symbols[&def_symbol.index], args),
                    from_expr,
                )
            };
            let level_mapping_symbs = LevelMappingSymbs {
                level_symbols: &level_symbols,
                head_level,
            };
            // implication
            let body_impl = LevelMapping {
                symbs: &level_mapping_symbs,
                pos_justification: true,
                polarity: true,
            }
            .transform_expression(from_expr.new_at(rule.body), expr_transformer);

            // reverse implication
            let body_rimpl = LevelMapping {
                symbs: &level_mapping_symbs,
                pos_justification: false,
                polarity: false,
            }
            .transform_expression(from_expr.new_at(rule.body), expr_transformer);
            let mut applied_symb = AppliedSymbBuilder::new(def_symbol.index);
            let lhs = {
                for (var, type_e) in vars.iter().take(def_symbol.domain.len()) {
                    applied_symb.add_arg(QuantElementNode::new(var, type_e).into())
                }
                // no nested symbols supported
                assert!(def_symbol.codomain == Type::Bool);
                expr_transformer.push_translated_node(applied_symb, from_expr)
            };
            let impl_index = expr_transformer
                .push_translated_node(BinOpNode::new(BinOps::Impl, lhs, body_impl), from_expr);
            let rimpl_index = expr_transformer
                .push_translated_node(BinOpNode::new(BinOps::Impl, body_rimpl, lhs), from_expr);
            let both = expr_transformer.push_translated_node(
                BinOpNode {
                    bin_op: BinOps::And,
                    lhs: impl_index,
                    rhs: rimpl_index,
                },
                from_expr,
            );
            // Since rules must not overlap and the union of all quantifications in the head of
            // rules for a single definiendum must be over the entire domain of the definiendum,
            // this is ok (or we explicitly allow the definition completion to be partial).
            let uni = QuantNodeBuilder::new(QuantKind::UniQuant, vars, both);
            self.completion_vec
                .push(expr_transformer.push_translated_node(uni, from_expr));
            expr_transformer.postamble_variables(&rule.head.variables);
        }
    }
}

impl<'a> Transformer<'a> for DefTransform {
    fn transform_expression(
        &mut self,
        from_expr: ExpressionRef<'a>,
        expr_transformer: &mut ExpressionTransformer,
    ) -> NodeIndex {
        let def = if let Ok(def) = Definition::try_from(from_expr) {
            def
        } else {
            return expr_transformer.rec_copy(from_expr);
        };

        if def.len() == 0 {
            return expr_transformer.rec_copy(from_expr);
        }
        // create auxiliary symbols for inductively defined symbols
        let level_symbols: IdHashMap<_, _> = def
            .iter_inductive()
            .filter_map(|(f, inductive)| {
                if !inductive {
                    return None;
                }
                Some((
                    f,
                    expr_transformer
                        .get_mut_expr_ref()
                        .new_aux_from(f)
                        .with_codomain(Type::Real)
                        .finish(),
                ))
            })
            .collect();
        // rules is an iterator over all rules of definiendum
        for (definiendum, inductive, rules) in def.iter_rules_nested_full() {
            let def_symbol = from_expr.expressions().vocab().pfuncs(definiendum);
            // NOTE: this could be simplified, there is no need to iterate over all rules of a
            // single definiendum at once anymore.
            if !inductive {
                self.create_clarks_completion(def_symbol, rules, from_expr, expr_transformer);
            } else {
                self.create_level_mapping(
                    def_symbol,
                    &level_symbols,
                    rules,
                    from_expr,
                    expr_transformer,
                );
            }
        }
        let ret = expr_transformer
            .create_op_chain(
                BinOps::And,
                &mut self.completion_vec.iter().copied(),
                from_expr,
            )
            .unwrap();
        self.completion_vec.clear();
        ret
    }
}

#[derive(Debug, Clone)]
pub struct LevelMappingSymbs<'a> {
    level_symbols: &'a IdHashMap<PfuncIndex, AuxIndex>,
    head_level: NodeIndex,
}

#[derive(Debug, Clone, Copy)]
pub struct LevelMapping<'a> {
    symbs: &'a LevelMappingSymbs<'a>,
    /// Keeps track of the current polarity.
    polarity: bool,
    /// Keeps track of what type of justification we are in.
    pos_justification: bool,
}

impl<'a> LevelMapping<'a> {
    fn flip_polarity(self) -> Self {
        Self {
            polarity: !self.polarity,
            ..self
        }
    }

    fn transform_expression<'b>(
        self,
        from_expr: ExpressionRef<'b>,
        expr_transformer: &mut ExpressionTransformer,
    ) -> NodeIndex {
        expr_transformer.structless_opt_transform(from_expr, |cur_expr, expr_transformer| {
            match cur_expr.first_node_enum() {
                NodeEnum::BinOps(bin_op) => {
                    let bin_op_new = match bin_op.bin_op {
                        BinOps::Impl => {
                            let lhs = self.flip_polarity().transform_expression(
                                cur_expr.new_at(bin_op.lhs),
                                expr_transformer,
                            );
                            let rhs = self.transform_expression(
                                cur_expr.new_at(bin_op.rhs),
                                expr_transformer,
                            );
                            BinOpNode {
                                bin_op: bin_op.bin_op,
                                lhs,
                                rhs,
                            }
                        }
                        // split equivalence, needed for polarity
                        BinOps::Eqv => {
                            let lhs_1 = self.flip_polarity().transform_expression(
                                cur_expr.new_at(bin_op.lhs),
                                expr_transformer,
                            );
                            let rhs_1 = self.transform_expression(
                                cur_expr.new_at(bin_op.rhs),
                                expr_transformer,
                            );
                            let impl_1 = expr_transformer.push_node(
                                BinOpNode {
                                    bin_op: BinOps::Impl,
                                    lhs: lhs_1,
                                    rhs: rhs_1,
                                },
                                cur_expr,
                            );
                            let lhs_2 = self.flip_polarity().transform_expression(
                                cur_expr.new_at(bin_op.rhs),
                                expr_transformer,
                            );
                            let rhs_2 = self.transform_expression(
                                cur_expr.new_at(bin_op.lhs),
                                expr_transformer,
                            );
                            let impl_2 = expr_transformer.push_node(
                                BinOpNode {
                                    bin_op: BinOps::Impl,
                                    lhs: lhs_2,
                                    rhs: rhs_2,
                                },
                                cur_expr,
                            );
                            BinOpNode {
                                bin_op: BinOps::And,
                                lhs: impl_1,
                                rhs: impl_2,
                            }
                        }
                        _ => return None,
                    };
                    expr_transformer.push_node(bin_op_new, from_expr).into()
                }
                NodeEnum::Neg(negation) => {
                    let child = self
                        .flip_polarity()
                        .transform_expression(cur_expr.new_at(negation.child), expr_transformer);
                    expr_transformer
                        .push_node(NegNode { child }, from_expr)
                        .into()
                }
                NodeEnum::AppliedSymb(symb) => {
                    if !self.symbs.level_symbols.contains_key(&symb.index) {
                        // Copy expression without change
                        return None;
                    }
                    let symb_new = expr_transformer.rec_copy(cur_expr);
                    let head_level = self.symbs.head_level;
                    let symb_aux = self.symbs.level_symbols[&symb.index];
                    let args = expr_transformer
                        .translate_args(symb.to_builder().take_args(), cur_expr.expressions());
                    let symb_level = expr_transformer.push_translated_node(
                        AppliedAuxSymbBuilder::apply(symb_aux, args),
                        cur_expr,
                    );

                    let bin_op = match (self.pos_justification, self.polarity) {
                        (true, true) => BinOps::Gt,
                        (false, true) => BinOps::Ge,
                        (true, false) => BinOps::Le,
                        (false, false) => BinOps::Lt,
                    };
                    let comp = expr_transformer.push_node(
                        BinOpNode {
                            bin_op,
                            lhs: head_level,
                            rhs: symb_level,
                        },
                        from_expr,
                    );
                    let end_op = if self.polarity {
                        BinOps::And
                    } else {
                        BinOps::Or
                    };
                    expr_transformer
                        .push_node(
                            BinOpNode {
                                bin_op: end_op,
                                lhs: comp,
                                rhs: symb_new,
                            },
                            from_expr,
                        )
                        .into()
                }
                _ => None,
            }
        })
    }
}

pub struct NestedSymbols;

pub fn validate_expr(mut expressions: ExpressionIter) -> Result<(), NestedSymbols> {
    let mut nested = false;
    if !expressions.any(|f| {
        let def = if let Ok(def) = Definition::try_from(f) {
            def
        } else {
            return false;
        };
        let definiendums: IdHashSet<_> = def.iter_definiendums().collect();
        let def_ref = &definiendums;
        f.any(move |node| {
            let definiendums = def_ref;
            match node {
                NodeEnum::BinOps(BinOpNode {
                    bin_op: BinOps::And | BinOps::Or | BinOps::Impl | BinOps::Eqv,
                    ..
                }) => false,
                NodeEnum::BinOps(_) => {
                    nested = true;
                    false
                }
                NodeEnum::Ite(_) => {
                    nested = true;
                    false
                }
                NodeEnum::Agg(_) => {
                    nested = true;
                    false
                }
                NodeEnum::AppliedSymb(symb) => {
                    if nested && definiendums.contains(&symb.index) {
                        true
                    } else {
                        false
                    }
                }
                _ => false,
            }
        })
    }) {
        Ok(())
    } else {
        Err(NestedSymbols)
    }
}
