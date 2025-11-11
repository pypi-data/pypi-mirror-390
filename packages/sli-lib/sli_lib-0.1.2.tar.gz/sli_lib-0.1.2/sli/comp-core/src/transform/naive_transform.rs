use super::{Transformer, tranform_assistor::ExpressionTransformer};
use crate::comp_core::{
    constraints::{BoundVarId, NodeIndex},
    expression::{ExpressionRef, VariableValue},
    node::{
        AppliedAuxSymbBuilder, AppliedSymbBuilder, BinOpNode, BinOps, ElementNode, IntElementNode,
        IteNode, NodeEnum, NodeWVariables, StandaloneNode, VariablesKind,
    },
    structure::{PartialStructure, TypeElement},
    vocabulary::TypeEnum,
};
use std::{collections::HashMap, ops::ControlFlow};

pub struct NaiveTransform<'a> {
    var_map: HashMap<BoundVarId, TypeEnum>,
    structure: &'a PartialStructure,
}

impl<'a> NaiveTransform<'a> {
    pub fn new(structure: &'a PartialStructure) -> Self {
        Self {
            var_map: HashMap::new(),
            structure,
        }
    }
}

impl VariableValue for NaiveTransform<'_> {
    fn set_type_enum(&mut self, var: BoundVarId, val: TypeEnum) {
        self.var_map.insert(var, val);
    }

    fn get_type_enum(&self, var: BoundVarId) -> Option<TypeEnum> {
        self.var_map.get(&var).copied()
    }

    fn remove_var(&mut self, var: BoundVarId) {
        self.var_map.remove(&var);
    }
}

impl NaiveTransform<'_> {
    fn next_transform<'a>(
        &mut self,
        from: ExpressionRef<'a>,
        expr_transformer: &mut ExpressionTransformer,
    ) -> NodeIndex {
        let transform = |from, t_expr: &mut _| self.transform(from, t_expr);
        let a = expr_transformer.transform(from, transform);
        a
    }

    fn transform<'a>(
        &mut self,
        from_expr: ExpressionRef<'a>,
        expr_transformer: &mut ExpressionTransformer,
    ) -> NodeIndex {
        match from_expr.first_node_enum() {
            NodeEnum::Ite(ite) => {
                let cond = self.next_transform(from_expr.new_at(ite.cond), expr_transformer);
                let cond_value = expr_transformer.get_expr_ref().as_bool(cond);
                if let Some(cond_value) = cond_value {
                    if cond_value {
                        self.next_transform(from_expr.new_at(ite.then_term), expr_transformer)
                    } else {
                        self.next_transform(from_expr.new_at(ite.else_term), expr_transformer)
                    }
                } else {
                    let then_term =
                        self.next_transform(from_expr.new_at(ite.then_term), expr_transformer);
                    let else_term =
                        self.next_transform(from_expr.new_at(ite.else_term), expr_transformer);
                    expr_transformer.push_node(
                        IteNode {
                            cond,
                            then_term,
                            else_term,
                        },
                        from_expr,
                    )
                }
            }
            var_node @ (NodeEnum::Agg(_) | NodeEnum::Quant(_)) => {
                let node_with_var = match var_node {
                    NodeEnum::Agg(agg) => NodeWVariables::from(agg),
                    NodeEnum::Quant(quant) => NodeWVariables::from(quant),
                    _ => unreachable!(),
                };
                let op = match node_with_var.type_of {
                    VariablesKind::CardAgg | VariablesKind::SumAgg => BinOps::Add,
                    VariablesKind::ExQuant => BinOps::Or,
                    VariablesKind::UniQuant => BinOps::And,
                    VariablesKind::Rule { .. } => unreachable!(),
                };
                let int_1 = expr_transformer.push_node(IntElementNode::new(1), from_expr);
                let int_0 = expr_transformer.push_node(IntElementNode::new(0), from_expr);
                let preamble =
                    |f: NodeIndex, expr_transformer: &mut ExpressionTransformer| -> NodeIndex {
                        match node_with_var.type_of {
                            VariablesKind::CardAgg => {
                                let new = expr_transformer.get_expr_ref().to_expression(f);
                                let b = new.try_into_bool();
                                if let Some(b) = b {
                                    if b { int_1 } else { int_0 }
                                } else {
                                    expr_transformer.push_node(
                                        IteNode {
                                            cond: f,
                                            then_term: int_1,
                                            else_term: int_0,
                                        },
                                        from_expr,
                                    )
                                }
                            }
                            VariablesKind::SumAgg
                            | VariablesKind::ExQuant
                            | VariablesKind::UniQuant => f,
                            VariablesKind::Rule { .. } => unreachable!(),
                        }
                    };
                let mut form = None;
                from_expr.expressions().iter_variables_with_end(
                    &node_with_var.variables,
                    self.structure.type_interps(),
                    self,
                    |f| {
                        let new_form = preamble(
                            f.transform_expression(
                                from_expr.new_at(node_with_var.formula),
                                expr_transformer,
                            ),
                            expr_transformer,
                        );
                        let bool_value = expr_transformer
                            .get_expr_ref()
                            .to_expression(new_form)
                            .try_into_bool();
                        if let Some(form_val) = form {
                            form = expr_transformer
                                .push_node(BinOpNode::new(op, form_val, new_form), from_expr)
                                .into();
                        } else {
                            form = Some(new_form);
                        }
                        match (node_with_var.type_of, bool_value) {
                            (VariablesKind::ExQuant, Some(true)) => ControlFlow::Break(()),
                            (VariablesKind::UniQuant, Some(false)) => ControlFlow::Break(()),
                            _ => ControlFlow::Continue(()),
                        }
                    },
                );
                if let Some(form) = form {
                    form
                } else {
                    match node_with_var.type_of {
                        VariablesKind::CardAgg | VariablesKind::SumAgg => {
                            expr_transformer.push_node(IntElementNode { num: 0 }, from_expr)
                        }
                        VariablesKind::ExQuant => expr_transformer.push_node(false, from_expr),
                        VariablesKind::UniQuant => expr_transformer.push_node(true, from_expr),
                        VariablesKind::Rule { .. } => unreachable!(),
                    }
                }
            }
            NodeEnum::Neg(_) => {
                // simplify transform simplifies this if possible
                expr_transformer.apply(from_expr, |tr, expr| self.next_transform(expr, tr))
            }
            NodeEnum::NumNeg(_) => {
                // simplify transform simplifies this if possible
                expr_transformer.apply(from_expr, |tr, expr| self.next_transform(expr, tr))
            }
            NodeEnum::IsInt(_) => {
                // simplify transform simplifies this if possible
                expr_transformer.apply(from_expr, |tr, expr| self.next_transform(expr, tr))
            }
            NodeEnum::BinOps(bin_op) => {
                // simplify transform simplifies this if possible
                let lhs = self.next_transform(from_expr.new_at(bin_op.lhs), expr_transformer);
                let rhs = self.next_transform(from_expr.new_at(bin_op.rhs), expr_transformer);
                expr_transformer.push_node(BinOpNode::new(bin_op.bin_op, lhs, rhs), from_expr)
            }
            NodeEnum::Element(el) => match el {
                el @ (ElementNode::Int(_)
                | ElementNode::Real(_)
                | ElementNode::Bool(_)
                | ElementNode::Type(_)) => expr_transformer.push_node(el, from_expr),
                ElementNode::Quant(q) => {
                    let var_type =
                        from_expr.get_type_map()[&q.bound_var_id].with_interps(self.structure);
                    let type_enum = self.var_map[&q.bound_var_id];
                    let element =
                        TypeElement::from_type(type_enum, &var_type).expect("Internal error");
                    expr_transformer.push_node(element, from_expr)
                }
            },
            applsymb @ (NodeEnum::AppliedSymb(_) | NodeEnum::AppliedAuxSymb(_)) => {
                let el = match &applsymb {
                    NodeEnum::AppliedSymb(aps) => aps.get_value(self.structure, &*self),
                    NodeEnum::AppliedAuxSymb(aux_aps) => {
                        aux_aps.get_value(from_expr.expressions, &*self)
                    }
                    _ => unreachable!(),
                };
                if let Some(el) = el {
                    expr_transformer.push_node(el, from_expr)
                } else {
                    let map_children = |arg: ElementNode| match arg {
                        ElementNode::Quant(e) => {
                            let var_type = from_expr.get_type_map()[&e.bound_var_id]
                                .with_interps(self.structure);
                            let type_enum = self.var_map[&e.bound_var_id];
                            let element = TypeElement::from_type(type_enum, &var_type)
                                .expect("Internal error");
                            element.into()
                        }
                        el => el,
                    };
                    let new_aps: StandaloneNode = match applsymb {
                        NodeEnum::AppliedSymb(aps) => AppliedSymbBuilder::from(aps)
                            .map_children(map_children)
                            .into(),
                        NodeEnum::AppliedAuxSymb(aps) => AppliedAuxSymbBuilder::from(aps)
                            .map_children(map_children)
                            .into(),
                        _ => unreachable!(),
                    };
                    expr_transformer.push_node(new_aps, from_expr)
                }
            }
            NodeEnum::Def(_) => expr_transformer.rec_copy(from_expr),
            NodeEnum::Rule(_) => expr_transformer.rec_copy(from_expr),
        }
    }
}

impl<'a, 'b> Transformer<'b> for NaiveTransform<'a> {
    fn transform_expression(
        &mut self,
        from_expr: ExpressionRef<'b>,
        expr_transformer: &mut ExpressionTransformer,
    ) -> NodeIndex {
        self.next_transform(from_expr, expr_transformer)
    }
}
