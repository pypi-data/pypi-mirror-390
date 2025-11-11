use crate::{
    comp_core::{
        Int, Real,
        constraints::{BoundVarId, NodeIndex},
        expression::{ExpressionRef, Expressions},
        node::{
            AggKind, BinOps, ElementNode, IntElementNode, NegNode, NodeEnum, QuantKind,
            QuantNodeBuilder, RealElementNode, StandaloneNode, Variables,
        },
        structure::TypeElement,
    },
    node::{BoolElement, NodeWVariablesStandalone},
};

pub fn vars_contains_vars<'a>(variables: &Variables<'a>, bound_var: BoundVarId) -> bool {
    variables.iter_vars().any(|&f| {
        if f == bound_var {
            true
        } else if let Some(idompred) = variables.get_i_dom_pred() {
            idompred.layout().contains_var(bound_var)
        } else {
            false
        }
    })
}

pub fn contains_bound_var<'a>(cur_expr: ExpressionRef<'a>, bound_var: BoundVarId) -> bool {
    cur_expr.any(|node_enum| match node_enum {
        NodeEnum::Agg(agg) => vars_contains_vars(&agg.variables, bound_var),
        NodeEnum::Quant(quant) => vars_contains_vars(&quant.variables, bound_var),
        NodeEnum::Element(ElementNode::Quant(n)) => n.bound_var_id == bound_var,
        NodeEnum::AppliedSymb(n) => n.contains_var(bound_var),
        NodeEnum::AppliedAuxSymb(n) => n.contains_var(bound_var),
        NodeEnum::Rule(rule) => vars_contains_vars(&rule.head.variables, bound_var),
        _ => false,
    })
}

#[derive(Debug)]
pub enum SimplifyResult {
    Node(StandaloneNode),
    Existing(NodeIndex),
}

fn simplify_agg_bin_op_lit(_agg_vars: Variables, bin_op: BinOps, el: ElementNode) -> Option<bool> {
    let type_el = if let Ok(el) = TypeElement::try_from(el) {
        el
    } else {
        return None;
    };
    if !matches!(
        bin_op,
        BinOps::Eq | BinOps::Neq | BinOps::Lt | BinOps::Le | BinOps::Gt | BinOps::Ge
    ) {
        return None;
    }
    match bin_op {
        BinOps::Eq => {
            match type_el {
                TypeElement::Int(el) => {
                    // TODO: further simplify if el is larger than domain size
                    if el < 0 { false.into() } else { None }
                }
                TypeElement::Real(el) => {
                    if el < 0 {
                        false.into()
                    } else if let Err(_) = Int::try_from(el) {
                        false.into()
                    } else {
                        None
                    }
                }
                _ => None,
            }
        }
        BinOps::Neq => {
            // for consistency
            None
        }
        BinOps::Lt => {
            match type_el {
                TypeElement::Int(el) => {
                    // TODO: further simplify if el is larger than domain size
                    if el <= 0 { false.into() } else { None }
                }
                TypeElement::Real(el) => {
                    if el <= 0 {
                        false.into()
                    } else {
                        None
                    }
                }
                _ => None,
            }
        }
        BinOps::Le => {
            match type_el {
                TypeElement::Int(el) => {
                    // TODO: further simplify if el is larger than domain size
                    if el < 0 { false.into() } else { None }
                }
                TypeElement::Real(el) => {
                    if el < 0 {
                        false.into()
                    } else {
                        None
                    }
                }
                _ => None,
            }
        }
        BinOps::Gt => match type_el {
            TypeElement::Int(el) => {
                if el < 0 {
                    true.into()
                } else {
                    None
                }
            }
            TypeElement::Real(el) => {
                if el < 0 {
                    true.into()
                } else {
                    None
                }
            }
            _ => None,
        },
        BinOps::Ge => match type_el {
            TypeElement::Int(el) => {
                if el <= 0 {
                    true.into()
                } else {
                    None
                }
            }
            TypeElement::Real(el) => {
                if el <= 0 {
                    true.into()
                } else {
                    None
                }
            }
            _ => None,
        },
        _ => unreachable!(),
    }
}

pub fn simplify_node<'a>(node: StandaloneNode, from_expr: &Expressions) -> SimplifyResult {
    use SimplifyResult as S;
    match node {
        StandaloneNode::BinOps(b) => {
            let left = from_expr.to_expression(b.lhs).try_into_bool();
            let right = from_expr.to_expression(b.rhs).try_into_bool();
            match b.bin_op {
                BinOps::And => match (left, right) {
                    (Some(l), Some(r)) => S::Node((l && r).into()),
                    (Some(l), None) => {
                        if l {
                            S::Existing(b.rhs)
                        } else {
                            S::Node(false.into())
                        }
                    }
                    (None, Some(r)) => {
                        if r {
                            S::Existing(b.lhs)
                        } else {
                            S::Node(false.into())
                        }
                    }
                    (None, None) => S::Node(b.into()),
                },
                BinOps::Or => match (left, right) {
                    (Some(l), Some(r)) => S::Node((l || r).into()),
                    (Some(l), None) => {
                        if !l {
                            S::Existing(b.rhs)
                        } else {
                            S::Node(true.into())
                        }
                    }
                    (None, Some(r)) => {
                        if !r {
                            S::Existing(b.lhs)
                        } else {
                            S::Node(true.into())
                        }
                    }
                    (None, None) => S::Node(b.into()),
                },
                BinOps::Impl => match (left, right) {
                    (Some(l), Some(r)) => S::Node((!l || r).into()),
                    (Some(l), None) => {
                        if l {
                            S::Existing(b.rhs)
                        } else {
                            S::Node(true.into())
                        }
                    }
                    (None, Some(r)) => {
                        if !r {
                            S::Node(NegNode::new(b.lhs).into())
                        } else {
                            S::Node(true.into())
                        }
                    }
                    (None, None) => S::Node(b.into()),
                },
                BinOps::Eqv => match (left, right) {
                    (Some(l), Some(r)) => S::Node((l == r).into()),
                    (Some(l), None) => {
                        if l {
                            S::Existing(b.rhs)
                        } else {
                            S::Node(NegNode::new(b.rhs).into())
                        }
                    }
                    (None, Some(r)) => {
                        if r {
                            S::Existing(b.lhs)
                        } else {
                            S::Node(NegNode::new(b.lhs).into())
                        }
                    }
                    (None, None) => S::Node(b.into()),
                },
                BinOps::Eq => {
                    let expr_left = from_expr.to_expression(b.lhs);
                    let expr_right = from_expr.to_expression(b.rhs);
                    let left_node = expr_left.first_node_enum();
                    let right_node = expr_right.first_node_enum();
                    match (left_node, right_node) {
                        (
                            NodeEnum::Element(ElementNode::Bool(b_l)),
                            NodeEnum::Element(ElementNode::Bool(b_r)),
                        ) => S::Node((b_l.value == b_r.value).into()),
                        (
                            NodeEnum::Element(ElementNode::Int(i_l)),
                            NodeEnum::Element(ElementNode::Int(i_r)),
                        ) => S::Node((i_l.num == i_r.num).into()),
                        (
                            NodeEnum::Element(ElementNode::Real(r_l)),
                            NodeEnum::Element(ElementNode::Real(r_r)),
                        ) => S::Node((r_l.real == r_r.real).into()),
                        (
                            NodeEnum::Element(ElementNode::Int(i_l)),
                            NodeEnum::Element(ElementNode::Real(i_r)),
                        ) => S::Node((i_l.num == i_r.real).into()),
                        (
                            NodeEnum::Element(ElementNode::Real(r_l)),
                            NodeEnum::Element(ElementNode::Int(r_r)),
                        ) => S::Node((r_l.real == r_r.num).into()),
                        (
                            NodeEnum::Element(ElementNode::Type(t_l)),
                            NodeEnum::Element(ElementNode::Type(t_r)),
                        ) => S::Node((t_l.element == t_r.element).into()),
                        (
                            NodeEnum::Element(
                                ElementNode::Bool(_)
                                | ElementNode::Real(_)
                                | ElementNode::Type(_)
                                | ElementNode::Int(_),
                            ),
                            NodeEnum::Element(
                                ElementNode::Bool(_)
                                | ElementNode::Real(_)
                                | ElementNode::Type(_)
                                | ElementNode::Int(_),
                            ),
                        ) => {
                            panic!("Type mismatch!")
                        }
                        (NodeEnum::Agg(agg), NodeEnum::Element(el))
                        | (NodeEnum::Element(el), NodeEnum::Agg(agg))
                            if agg.aggregate_type == AggKind::Card =>
                        {
                            simplify_agg_bin_op_lit(agg.variables, b.bin_op, el)
                                .map(|f| S::Node(f.into()))
                                .unwrap_or(S::Node(b.into()))
                        }
                        // Eq between same variable is always true
                        (
                            NodeEnum::Element(ElementNode::Quant(q1)),
                            NodeEnum::Element(ElementNode::Quant(q2)),
                        ) => {
                            if q1.bound_var_id == q2.bound_var_id {
                                S::Node(true.into())
                            } else {
                                S::Node(b.into())
                            }
                        }
                        _ => S::Node(b.into()),
                    }
                }
                BinOps::Neq => {
                    let expr_left = from_expr.to_expression(b.lhs);
                    let expr_right = from_expr.to_expression(b.rhs);
                    let left_node = expr_left.first_node_enum();
                    let right_node = expr_right.first_node_enum();
                    match (left_node, right_node) {
                        (
                            NodeEnum::Element(ElementNode::Bool(b_l)),
                            NodeEnum::Element(ElementNode::Bool(b_r)),
                        ) => S::Node((b_l.value != b_r.value).into()),
                        (
                            NodeEnum::Element(ElementNode::Int(i_l)),
                            NodeEnum::Element(ElementNode::Int(i_r)),
                        ) => S::Node((i_l.num != i_r.num).into()),
                        (
                            NodeEnum::Element(ElementNode::Real(r_l)),
                            NodeEnum::Element(ElementNode::Real(r_r)),
                        ) => S::Node((r_l.real != r_r.real).into()),
                        (
                            NodeEnum::Element(ElementNode::Int(i_l)),
                            NodeEnum::Element(ElementNode::Real(i_r)),
                        ) => S::Node((i_l.num != i_r.real).into()),
                        (
                            NodeEnum::Element(ElementNode::Real(r_l)),
                            NodeEnum::Element(ElementNode::Int(r_r)),
                        ) => S::Node((r_l.real != r_r.num).into()),
                        (
                            NodeEnum::Element(ElementNode::Type(t_l)),
                            NodeEnum::Element(ElementNode::Type(t_r)),
                        ) => S::Node((t_l.element != t_r.element).into()),
                        (
                            NodeEnum::Element(
                                ElementNode::Bool(_)
                                | ElementNode::Real(_)
                                | ElementNode::Type(_)
                                | ElementNode::Int(_),
                            ),
                            NodeEnum::Element(
                                ElementNode::Bool(_)
                                | ElementNode::Real(_)
                                | ElementNode::Type(_)
                                | ElementNode::Int(_),
                            ),
                        ) => {
                            panic!("Type mismatch!")
                        }
                        _ => S::Node(b.into()),
                    }
                }
                BinOps::Lt => {
                    let expr_left = from_expr.to_expression(b.lhs);
                    let expr_right = from_expr.to_expression(b.rhs);
                    let left_node = expr_left.first_node_enum();
                    let right_node = expr_right.first_node_enum();
                    match (left_node, right_node) {
                        (
                            NodeEnum::Element(ElementNode::Int(i_l)),
                            NodeEnum::Element(ElementNode::Int(i_r)),
                        ) => S::Node((i_l.num < i_r.num).into()),
                        (
                            NodeEnum::Element(ElementNode::Real(r_l)),
                            NodeEnum::Element(ElementNode::Real(r_r)),
                        ) => S::Node((r_l.real < r_r.real).into()),
                        (
                            NodeEnum::Element(ElementNode::Int(i_l)),
                            NodeEnum::Element(ElementNode::Real(r_r)),
                        ) => S::Node((i_l.num < r_r.real).into()),
                        (
                            NodeEnum::Element(ElementNode::Real(r_l)),
                            NodeEnum::Element(ElementNode::Int(i_i)),
                        ) => S::Node((r_l.real < i_i.num).into()),
                        (NodeEnum::Agg(agg), NodeEnum::Element(el))
                            if agg.aggregate_type == AggKind::Card =>
                        {
                            simplify_agg_bin_op_lit(agg.variables, b.bin_op, el)
                                .map(|f| S::Node(f.into()))
                                .unwrap_or(S::Node(b.into()))
                        }
                        (NodeEnum::Element(el), NodeEnum::Agg(agg))
                            if agg.aggregate_type == AggKind::Card =>
                        {
                            simplify_agg_bin_op_lit(agg.variables, BinOps::Gt, el)
                                .map(|f| S::Node(f.into()))
                                .unwrap_or(S::Node(b.into()))
                        }
                        _ => S::Node(b.into()),
                    }
                }
                BinOps::Le => {
                    let expr_left = from_expr.to_expression(b.lhs);
                    let expr_right = from_expr.to_expression(b.rhs);
                    let left_node = expr_left.first_node_enum();
                    let right_node = expr_right.first_node_enum();
                    match (left_node, right_node) {
                        (
                            NodeEnum::Element(ElementNode::Int(i_l)),
                            NodeEnum::Element(ElementNode::Int(i_r)),
                        ) => S::Node((i_l.num <= i_r.num).into()),
                        (
                            NodeEnum::Element(ElementNode::Real(r_l)),
                            NodeEnum::Element(ElementNode::Real(r_r)),
                        ) => S::Node((r_l.real <= r_r.real).into()),
                        (
                            NodeEnum::Element(ElementNode::Int(i_l)),
                            NodeEnum::Element(ElementNode::Real(r_r)),
                        ) => S::Node((i_l.num <= r_r.real).into()),
                        (
                            NodeEnum::Element(ElementNode::Real(r_l)),
                            NodeEnum::Element(ElementNode::Int(i_i)),
                        ) => S::Node((r_l.real <= i_i.num).into()),
                        (NodeEnum::Agg(agg), NodeEnum::Element(el))
                            if agg.aggregate_type == AggKind::Card =>
                        {
                            simplify_agg_bin_op_lit(agg.variables, b.bin_op, el)
                                .map(|f| S::Node(f.into()))
                                .unwrap_or(S::Node(b.into()))
                        }
                        (NodeEnum::Element(el), NodeEnum::Agg(agg))
                            if agg.aggregate_type == AggKind::Card =>
                        {
                            simplify_agg_bin_op_lit(agg.variables, BinOps::Ge, el)
                                .map(|f| S::Node(f.into()))
                                .unwrap_or(S::Node(b.into()))
                        }
                        _ => S::Node(b.into()),
                    }
                }
                BinOps::Gt => {
                    let expr_left = from_expr.to_expression(b.lhs);
                    let expr_right = from_expr.to_expression(b.rhs);
                    let left_node = expr_left.first_node_enum();
                    let right_node = expr_right.first_node_enum();
                    match (left_node, right_node) {
                        (
                            NodeEnum::Element(ElementNode::Int(i_l)),
                            NodeEnum::Element(ElementNode::Int(i_r)),
                        ) => S::Node((i_l.num > i_r.num).into()),
                        (
                            NodeEnum::Element(ElementNode::Real(r_l)),
                            NodeEnum::Element(ElementNode::Real(r_r)),
                        ) => S::Node((r_l.real > r_r.real).into()),
                        (
                            NodeEnum::Element(ElementNode::Int(i_l)),
                            NodeEnum::Element(ElementNode::Real(r_r)),
                        ) => S::Node((i_l.num > r_r.real).into()),
                        (
                            NodeEnum::Element(ElementNode::Real(r_l)),
                            NodeEnum::Element(ElementNode::Int(i_i)),
                        ) => S::Node((r_l.real > i_i.num).into()),
                        (NodeEnum::Agg(agg), NodeEnum::Element(el))
                            if agg.aggregate_type == AggKind::Card =>
                        {
                            simplify_agg_bin_op_lit(agg.variables, b.bin_op, el)
                                .map(|f| S::Node(f.into()))
                                .unwrap_or(S::Node(b.into()))
                        }
                        (NodeEnum::Element(el), NodeEnum::Agg(agg))
                            if agg.aggregate_type == AggKind::Card =>
                        {
                            simplify_agg_bin_op_lit(agg.variables, BinOps::Lt, el)
                                .map(|f| S::Node(f.into()))
                                .unwrap_or(S::Node(b.into()))
                        }
                        _ => S::Node(b.into()),
                    }
                }
                BinOps::Ge => {
                    let expr_left = from_expr.to_expression(b.lhs);
                    let expr_right = from_expr.to_expression(b.rhs);
                    let left_node = expr_left.first_node_enum();
                    let right_node = expr_right.first_node_enum();
                    match (left_node, right_node) {
                        (
                            NodeEnum::Element(ElementNode::Int(i_l)),
                            NodeEnum::Element(ElementNode::Int(i_r)),
                        ) => S::Node((i_l.num >= i_r.num).into()),
                        (
                            NodeEnum::Element(ElementNode::Real(r_l)),
                            NodeEnum::Element(ElementNode::Real(r_r)),
                        ) => S::Node((r_l.real >= r_r.real).into()),
                        (
                            NodeEnum::Element(ElementNode::Int(i_l)),
                            NodeEnum::Element(ElementNode::Real(r_r)),
                        ) => S::Node((i_l.num >= r_r.real).into()),
                        (
                            NodeEnum::Element(ElementNode::Real(r_l)),
                            NodeEnum::Element(ElementNode::Int(i_i)),
                        ) => S::Node((r_l.real >= i_i.num).into()),
                        (NodeEnum::Agg(agg), NodeEnum::Element(el))
                            if agg.aggregate_type == AggKind::Card =>
                        {
                            simplify_agg_bin_op_lit(agg.variables, b.bin_op, el)
                                .map(|f| S::Node(f.into()))
                                .unwrap_or(S::Node(b.into()))
                        }
                        (NodeEnum::Element(el), NodeEnum::Agg(agg))
                            if agg.aggregate_type == AggKind::Card =>
                        {
                            simplify_agg_bin_op_lit(agg.variables, BinOps::Le, el)
                                .map(|f| S::Node(f.into()))
                                .unwrap_or(S::Node(b.into()))
                        }
                        _ => S::Node(b.into()),
                    }
                }
                BinOps::Add => {
                    let expr_left = from_expr.to_expression(b.lhs);
                    let expr_right = from_expr.to_expression(b.rhs);
                    let left_node = expr_left.first_node_enum();
                    let right_node = expr_right.first_node_enum();
                    match (left_node, right_node) {
                        (
                            NodeEnum::Element(ElementNode::Int(i_l)),
                            NodeEnum::Element(ElementNode::Int(i_r)),
                        ) => S::Node(
                            IntElementNode {
                                num: i_l.num + i_r.num,
                            }
                            .into(),
                        ),
                        (
                            NodeEnum::Element(ElementNode::Real(r_l)),
                            NodeEnum::Element(ElementNode::Real(r_r)),
                        ) => {
                            let real_res = r_l.real.add(r_r.real).expect("Float overflow");
                            S::Node(RealElementNode::new(real_res).into())
                        }
                        (
                            NodeEnum::Element(ElementNode::Int(i_l)),
                            NodeEnum::Element(ElementNode::Real(r_r)),
                        ) => {
                            let real_res =
                                Real::from(i_l.num).add(r_r.real).expect("Float overflow");
                            S::Node(RealElementNode::new(real_res).into())
                        }
                        (
                            NodeEnum::Element(ElementNode::Real(r_l)),
                            NodeEnum::Element(ElementNode::Int(i_r)),
                        ) => {
                            let real_res = r_l.real.add(i_r.num.into()).expect("Float overflow");
                            S::Node(RealElementNode::new(real_res).into())
                        }
                        (NodeEnum::Element(ElementNode::Real(real)), _) if real.real == 0 => {
                            S::Existing(b.rhs)
                        }
                        (_, NodeEnum::Element(ElementNode::Real(real))) if real.real == 0 => {
                            S::Existing(b.lhs)
                        }
                        (NodeEnum::Element(ElementNode::Int(int)), _) if int.num == 0 => {
                            S::Existing(b.rhs)
                        }
                        (_, NodeEnum::Element(ElementNode::Int(int))) if int.num == 0 => {
                            S::Existing(b.lhs)
                        }
                        _ => S::Node(b.into()),
                    }
                }
                BinOps::Sub => {
                    let expr_left = from_expr.to_expression(b.lhs);
                    let expr_right = from_expr.to_expression(b.rhs);
                    let left_node = expr_left.first_node_enum();
                    let right_node = expr_right.first_node_enum();
                    match (left_node, right_node) {
                        (
                            NodeEnum::Element(ElementNode::Int(i_l)),
                            NodeEnum::Element(ElementNode::Int(i_r)),
                        ) => S::Node(
                            IntElementNode {
                                num: i_l.num - i_r.num,
                            }
                            .into(),
                        ),
                        (
                            NodeEnum::Element(ElementNode::Real(r_l)),
                            NodeEnum::Element(ElementNode::Real(r_r)),
                        ) => {
                            let real_res = r_l.real.sub(r_r.real).expect("Float overflow");
                            S::Node(RealElementNode::new(real_res).into())
                        }
                        (
                            NodeEnum::Element(ElementNode::Int(i_l)),
                            NodeEnum::Element(ElementNode::Real(r_r)),
                        ) => {
                            let real_res =
                                Real::from(i_l.num).sub(r_r.real).expect("Float overflow");
                            S::Node(RealElementNode::new(real_res).into())
                        }
                        (
                            NodeEnum::Element(ElementNode::Real(r_l)),
                            NodeEnum::Element(ElementNode::Int(i_r)),
                        ) => {
                            let real_res = r_l.real.sub(i_r.num.into()).expect("Float overflow");
                            S::Node(RealElementNode::new(real_res).into())
                        }
                        _ => S::Node(b.into()),
                    }
                }
                BinOps::Mult => {
                    let expr_left = from_expr.to_expression(b.lhs);
                    let expr_right = from_expr.to_expression(b.rhs);
                    let left_node = expr_left.first_node_enum();
                    let right_node = expr_right.first_node_enum();
                    match (left_node, right_node) {
                        (
                            NodeEnum::Element(ElementNode::Int(i_l)),
                            NodeEnum::Element(ElementNode::Int(i_r)),
                        ) => S::Node(
                            IntElementNode {
                                num: i_l.num * i_r.num,
                            }
                            .into(),
                        ),
                        (
                            NodeEnum::Element(ElementNode::Real(r_l)),
                            NodeEnum::Element(ElementNode::Real(r_r)),
                        ) => {
                            let real_res = r_l.real.mult(r_r.real).expect("Float overflow");
                            S::Node(RealElementNode::new(real_res).into())
                        }
                        (
                            NodeEnum::Element(ElementNode::Int(i_l)),
                            NodeEnum::Element(ElementNode::Real(r_r)),
                        ) => {
                            let real_res =
                                Real::from(i_l.num).mult(r_r.real).expect("Float overflow");
                            S::Node(RealElementNode::new(real_res).into())
                        }
                        (
                            NodeEnum::Element(ElementNode::Real(r_l)),
                            NodeEnum::Element(ElementNode::Int(i_r)),
                        ) => {
                            let real_res = r_l.real.mult(i_r.num.into()).expect("Float overflow");
                            S::Node(RealElementNode::new(real_res).into())
                        }
                        (NodeEnum::Element(ElementNode::Real(real)), _) if real.real == 1 => {
                            S::Existing(b.rhs)
                        }
                        (_, NodeEnum::Element(ElementNode::Real(real))) if real.real == 1 => {
                            S::Existing(b.lhs)
                        }
                        (NodeEnum::Element(ElementNode::Int(int)), _) if int.num == 1 => {
                            S::Existing(b.rhs)
                        }
                        (_, NodeEnum::Element(ElementNode::Int(int))) if int.num == 1 => {
                            S::Existing(b.lhs)
                        }
                        _ => S::Node(b.into()),
                    }
                }
                BinOps::Divide => {
                    let expr_left = from_expr.to_expression(b.lhs);
                    let expr_right = from_expr.to_expression(b.rhs);
                    let left_node = expr_left.first_node_enum();
                    let right_node = expr_right.first_node_enum();
                    match (left_node, right_node) {
                        (
                            NodeEnum::Element(ElementNode::Int(i_l)),
                            NodeEnum::Element(ElementNode::Int(i_r)),
                        ) => S::Node(
                            RealElementNode {
                                real: Real::from(i_l.num).div_cc(&Real::from(i_r.num)),
                            }
                            .into(),
                        ),
                        (
                            NodeEnum::Element(ElementNode::Real(r_l)),
                            NodeEnum::Element(ElementNode::Real(r_r)),
                        ) => {
                            let real_res = r_l.real.div_cc(&r_r.real);
                            S::Node(RealElementNode::new(real_res).into())
                        }
                        (
                            NodeEnum::Element(ElementNode::Int(i_l)),
                            NodeEnum::Element(ElementNode::Real(r_r)),
                        ) => {
                            let real_res = Real::from(i_l.num).div_cc(&r_r.real);
                            S::Node(RealElementNode::new(real_res).into())
                        }
                        (
                            NodeEnum::Element(ElementNode::Real(r_l)),
                            NodeEnum::Element(ElementNode::Int(i_r)),
                        ) => {
                            let real_res = r_l.real.div_cc(&i_r.num.into());
                            S::Node(RealElementNode::new(real_res).into())
                        }
                        (_, NodeEnum::Element(ElementNode::Real(real))) if real.real == 1 => {
                            S::Existing(b.lhs)
                        }
                        (_, NodeEnum::Element(ElementNode::Int(int))) if int.num == 1 => {
                            S::Existing(b.lhs)
                        }
                        _ => S::Node(b.into()),
                    }
                }
                BinOps::Rem => {
                    let expr_left = from_expr.to_expression(b.lhs);
                    let expr_right = from_expr.to_expression(b.rhs);
                    let left_node = expr_left.first_node_enum();
                    let right_node = expr_right.first_node_enum();
                    match (left_node, right_node) {
                        (
                            NodeEnum::Element(ElementNode::Int(i_l)),
                            NodeEnum::Element(ElementNode::Int(i_r)),
                        ) => S::Node(
                            IntElementNode {
                                num: i_l.num.checked_rem(i_r.num).unwrap_or_default(),
                            }
                            .into(),
                        ),
                        (
                            NodeEnum::Element(ElementNode::Real(r_l)),
                            NodeEnum::Element(ElementNode::Real(r_r)),
                        ) => {
                            let real_res = r_l.real.rem_cc(&r_r.real);
                            S::Node(RealElementNode::new(real_res).into())
                        }
                        (
                            NodeEnum::Element(ElementNode::Int(i_l)),
                            NodeEnum::Element(ElementNode::Real(r_r)),
                        ) => {
                            let real_res = Real::from(i_l.num).rem_cc(&r_r.real);
                            S::Node(RealElementNode::new(real_res).into())
                        }
                        (
                            NodeEnum::Element(ElementNode::Real(r_l)),
                            NodeEnum::Element(ElementNode::Int(i_r)),
                        ) => {
                            let real_res = r_l.real.rem_cc(&i_r.num.into());
                            S::Node(RealElementNode::new(real_res).into())
                        }
                        (_, NodeEnum::Element(ElementNode::Real(real))) if real.real == 1 => {
                            S::Node(IntElementNode::new(0).into())
                        }
                        (_, NodeEnum::Element(ElementNode::Int(int))) if int.num == 1 => {
                            S::Node(IntElementNode::new(0).into())
                        }
                        _ => S::Node(b.into()),
                    }
                }
            }
        }
        StandaloneNode::Neg(n) => {
            let child = from_expr.to_expression(n.child).try_into_bool();
            match child {
                Some(t) => S::Node((!t).into()),
                None => S::Node(n.into()),
            }
        }
        StandaloneNode::NumNeg(n) => {
            let child = from_expr.to_expression(n.child);
            let child_node = child.first_node_enum();
            match child_node {
                NodeEnum::Element(ElementNode::Int(value)) => {
                    SimplifyResult::Node(IntElementNode::new(-value.num).into())
                }
                NodeEnum::Element(ElementNode::Real(value)) => {
                    SimplifyResult::Node(RealElementNode::new(-value.real).into())
                }
                _ => S::Node(n.into()),
            }
        }
        StandaloneNode::IsInt(n) => {
            let child = from_expr.to_expression(n.child);
            let child_node = child.first_node_enum();
            match child_node {
                NodeEnum::Element(ElementNode::Real(value)) => {
                    SimplifyResult::Node(BoolElement::new(value.real.is_integer()).into())
                }
                _ => S::Node(n.into()),
            }
        }
        StandaloneNode::Ite(ite) => {
            let cond = from_expr.new_at(ite.cond).try_into_bool();
            if let Some(cond) = cond {
                if cond {
                    S::Existing(ite.then_term)
                } else {
                    S::Existing(ite.else_term)
                }
            } else {
                S::Node(ite.into())
            }
        }
        StandaloneNode::Quant(q) => simplify_quantification(q, from_expr),
        StandaloneNode::Agg(agg) => {
            let value = from_expr.new_at(agg.formula).try_into_type_element();
            match (value, agg.aggregate_type) {
                (Some(TypeElement::Bool(value)), AggKind::Card) => {
                    if !value {
                        S::Node(IntElementNode::from(0).into())
                    } else {
                        S::Node(agg.into())
                    }
                }
                (Some(TypeElement::Int(0)), AggKind::Sum) => {
                    S::Node(IntElementNode::from(0).into())
                }
                (Some(TypeElement::Real(real)), AggKind::Sum) if real == 0 => {
                    S::Node(IntElementNode::from(0).into())
                }
                _ => S::Node(agg.into()),
            }
        }
        StandaloneNode::AppliedSymb(_)
        | StandaloneNode::AppliedAuxSymb(_)
        | StandaloneNode::Element(_)
        | StandaloneNode::Rule(_)
        | StandaloneNode::Def(_)
        | StandaloneNode::Vars(_)
        | StandaloneNode::RuleHead(_)
        | StandaloneNode::Rules(_) => S::Node(node),
    }
}

pub fn simplify_quantification(q: QuantNodeBuilder, from_expr: &Expressions) -> SimplifyResult {
    simplify_quantification_with_extra_vars(q, from_expr, |_| false, false)
}

pub fn simplify_quantification_with_extra_vars(
    mut q: QuantNodeBuilder,
    from_expr: &Expressions,
    mut vars: impl FnMut(&BoundVarId) -> bool,
    assume_guard: bool,
) -> SimplifyResult {
    use SimplifyResult as S;
    let form = from_expr.to_expression(q.formula).try_into_bool();
    if q.variables.len() == 0 {
        return S::Existing(q.formula);
    }
    match (
        form,
        q.quant_type,
        assume_guard,
        q.variables.take_i_dom_pred(),
    ) {
        (Some(true), QuantKind::UniQuant, _, _) => S::Node(true.into()),
        (Some(false), QuantKind::UniQuant, false, None) => S::Node(false.into()),
        (Some(false), QuantKind::UniQuant, true, i_dom_pred) => {
            if let Some(i_dom_pred) = i_dom_pred {
                q.variables.set_i_dom_pred(i_dom_pred);
            }
            S::Node(q.into())
        }
        (Some(false), QuantKind::UniQuant, false, Some(i_dom_pred)) => {
            if i_dom_pred.bit_vec.cardinality() == 0 {
                S::Node(true.into())
            } else {
                S::Node(false.into())
            }
        }
        (Some(false), QuantKind::ExQuant, _, _) => S::Node(false.into()),
        (Some(true), QuantKind::ExQuant, false, None) => S::Node(true.into()),
        (Some(true), QuantKind::ExQuant, true, i_dom_pred) => {
            if let Some(i_dom_pred) = i_dom_pred {
                q.variables.set_i_dom_pred(i_dom_pred);
            }
            S::Node(q.into())
        }
        (Some(true), QuantKind::ExQuant, false, Some(i_dom_pred)) => {
            if i_dom_pred.bit_vec.cardinality() == 0 {
                S::Node(false.into())
            } else {
                S::Node(true.into())
            }
        }
        (_, _, _, i_dom_pred) => {
            q.variables.retain(|var| {
                (vars)(var)
                    || i_dom_pred
                        .as_ref()
                        .map(|f| f.layout().contains_var(*var))
                        .unwrap_or(false)
                    || contains_bound_var(from_expr.to_expression(q.formula), *var)
            });
            if let Some(i_dom_pred) = i_dom_pred {
                q.variables.set_i_dom_pred(i_dom_pred);
            }
            if q.variables.len() == 0 {
                S::Existing(q.formula)
            } else {
                S::Node(q.into())
            }
        }
    }
}

pub fn simplify_node_with_var_with_extra_vars(
    node_with_var: NodeWVariablesStandalone,
    from_expr: &Expressions,
    vars: impl FnMut(&BoundVarId) -> bool,
    assume_guard: bool,
) -> SimplifyResult {
    use SimplifyResult as S;
    match StandaloneNode::from(node_with_var) {
        StandaloneNode::Quant(q) => {
            simplify_quantification_with_extra_vars(q, from_expr, vars, assume_guard)
        }
        StandaloneNode::Agg(agg) => S::Node(agg.into()),
        StandaloneNode::Rule(rule) => S::Node(rule.into()),
        StandaloneNode::RuleHead(_)
        | StandaloneNode::BinOps(_)
        | StandaloneNode::Neg(_)
        | StandaloneNode::NumNeg(_)
        | StandaloneNode::IsInt(_)
        | StandaloneNode::Ite(_)
        | StandaloneNode::Def(_)
        | StandaloneNode::AppliedSymb(_)
        | StandaloneNode::AppliedAuxSymb(_)
        | StandaloneNode::Vars(_)
        | StandaloneNode::Element(_)
        | StandaloneNode::Rules(_) => unreachable!(),
    }
}

#[derive(Debug)]
pub enum HalfSimplifyResult {
    None,
    Node(StandaloneNode),
}

pub fn simplify_half_bin(
    bin_op: BinOps,
    child: NodeIndex,
    lhs: bool,
    expr: &Expressions,
) -> HalfSimplifyResult {
    use HalfSimplifyResult as S;
    match bin_op {
        BinOps::And => {
            let child_as_bool = expr.to_expression(child).try_into_bool();
            match child_as_bool {
                Some(l) => {
                    if l {
                        S::None
                    } else {
                        S::Node(false.into())
                    }
                }
                None => S::None,
            }
        }
        BinOps::Or => {
            let child_as_bool = expr.to_expression(child).try_into_bool();
            match child_as_bool {
                Some(l) => {
                    if !l {
                        S::None
                    } else {
                        S::Node(true.into())
                    }
                }
                None => S::None,
            }
        }
        BinOps::Impl => {
            let child_as_bool = expr.to_expression(child).try_into_bool();
            match (child_as_bool, lhs) {
                (Some(l), true) => {
                    if l {
                        S::None
                    } else {
                        S::Node(true.into())
                    }
                }
                (Some(r), false) => {
                    if !r {
                        S::None
                    } else {
                        S::Node(true.into())
                    }
                }
                (None, _) => S::None,
            }
        }
        _ => S::None,
    }
}
