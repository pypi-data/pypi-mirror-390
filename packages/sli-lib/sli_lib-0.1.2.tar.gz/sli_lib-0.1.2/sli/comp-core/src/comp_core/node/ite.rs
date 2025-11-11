use super::{ExprType, FromExpressionUnchecked};
use crate::comp_core::IndexRepr;
use crate::comp_core::constraints::{NodeIndex, ToConstraint, ToNodeArgs};
use crate::comp_core::expression::Expressions;
use crate::comp_core::node::Node;
use std::borrow::Cow;
use std::mem::transmute;
use std::slice::from_raw_parts;

#[repr(C)]
#[derive(Debug, Clone)]
pub struct IteNode {
    pub cond: NodeIndex,
    // Don't change the order of these
    pub then_term: NodeIndex,
    pub else_term: NodeIndex,
}

impl<'a> FromExpressionUnchecked<'a> for IteNode {
    fn from_node<T: AsRef<Expressions>>(value: (NodeIndex, &'a T)) -> Self {
        let expr = value.1.as_ref();
        let node = expr.nodes(value.0);
        debug_assert_eq!(node.expr, ExprType::Ite);
        let cond = node.data[0].into();
        let start_extra = node.data[1];
        let then_term = expr.extra(start_extra.into()).into();
        let else_term = expr.extra((start_extra + 1).into()).into();
        Self {
            cond,
            then_term,
            else_term,
        }
    }
}

impl ToConstraint for IteNode {
    fn extra_children(&self) -> Cow<'_, [IndexRepr]> {
        Cow::Borrowed(unsafe { transmute(from_raw_parts(&(self.then_term), 2)) })
    }

    fn to_node(self, ToNodeArgs { extra_len, .. }: ToNodeArgs) -> Node {
        Node {
            expr: ExprType::Ite,
            data: [self.cond.into(), extra_len.try_into().unwrap()],
        }
    }
}
