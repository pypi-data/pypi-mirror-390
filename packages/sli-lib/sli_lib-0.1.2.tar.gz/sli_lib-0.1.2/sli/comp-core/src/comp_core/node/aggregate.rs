use super::{ExprType, FromExpressionUnchecked, Variables, VariablesBuilder};
use crate::comp_core::constraints::{NodeIndex, ToConstraint, ToNodeArgs};
use crate::comp_core::expression::Expressions;
use crate::comp_core::node::Node;
use std::mem::swap;

macro_rules! create_aggregate_nodes {
    ($(($name:ident, $expr:expr, $pat:pat, $type:ident)),+$(,)?) => {
        $(
            #[derive(Debug, Clone)]
            pub struct $name<'a> {
                pub formula: NodeIndex,
                pub variables: Variables<'a>,
            }

            impl<'a> FromExpressionUnchecked<'a> for $name<'a> {
                fn from_node<T: AsRef<Expressions>>(value: (NodeIndex, &'a T)) -> Self {
                    let quant_node = AggregateNode::from_node(value);
                    debug_assert_eq!(quant_node.aggregate_type, AggKind::$type);
                    Self {
                        formula: quant_node.formula,
                        variables: quant_node.variables,
                    }
                }
            }

            impl<'a, T: AsRef<Expressions>> TryFrom<(NodeIndex, &'a T)> for $name<'a> {
                type Error = ();

                fn try_from(value: (NodeIndex, &'a T)) -> Result<Self, Self::Error> {
                    let expression = value.1.as_ref();
                    let index = value.0;
                    let node = expression.nodes(index);
                    match node.expr {
                        $pat => Ok($name::from_node(value)),
                        _ => Err(()),
                    }
                }
            }
        )+

        #[derive(Debug, Clone, Copy, PartialEq, Eq)]
        pub enum AggKind {
            $(
                $type,
            )+
        }

        $(
            impl<'a> From<$name<'a>> for AggregateNode<'a> {
                fn from(value: $name<'a>) -> Self {
                    Self {
                        aggregate_type: AggKind::$type,
                        formula: value.formula,
                        variables: value.variables,
                    }
                }
            }
        )+
    }
}

create_aggregate_nodes!(
    (CardAggNode, ExprType::CardAgg, ExprType::CardAgg, Card),
    (SumAggNode, ExprType::SumAgg, ExprType::SumAgg, Sum),
);

/// Represents an aggregate.
#[derive(Debug, Clone)]
pub struct AggregateNode<'a> {
    pub aggregate_type: AggKind,
    pub formula: NodeIndex,
    pub variables: Variables<'a>,
}

impl<'a> AggregateNode<'a> {
    pub fn new(quant_type: AggKind, formula: NodeIndex, variables: Variables<'a>) -> Self {
        Self {
            aggregate_type: quant_type,
            formula,
            variables,
        }
    }

    pub fn standalone(self) -> AggregateNodeBuilder {
        self.into()
    }
}

impl From<AggKind> for ExprType {
    fn from(value: AggKind) -> Self {
        match value {
            AggKind::Card => Self::CardAgg,
            AggKind::Sum => Self::SumAgg,
        }
    }
}

impl TryFrom<ExprType> for AggKind {
    type Error = ();

    fn try_from(value: ExprType) -> Result<Self, Self::Error> {
        match value {
            ExprType::CardAgg => Ok(Self::Card),
            ExprType::SumAgg => Ok(Self::Sum),
            _ => Err(()),
        }
    }
}

impl<'a> From<AggregateNode<'a>> for AggregateNodeBuilder {
    fn from(value: AggregateNode<'a>) -> Self {
        Self {
            aggregate_type: value.aggregate_type,
            formula: value.formula,
            variables: value.variables.into(),
        }
    }
}

/// Standalone version of [AggregateNode].
#[derive(Debug, Clone)]
pub struct AggregateNodeBuilder {
    pub aggregate_type: AggKind,
    pub formula: NodeIndex,
    pub variables: VariablesBuilder,
}

impl AggregateNodeBuilder {
    pub fn new(aggregate_type: AggKind, variables: VariablesBuilder, formula: NodeIndex) -> Self {
        Self {
            aggregate_type,
            formula,
            variables,
        }
    }
}

impl<'a> FromExpressionUnchecked<'a> for AggregateNode<'a> {
    fn from_node<T: AsRef<Expressions>>(value: (NodeIndex, &'a T)) -> Self {
        let expression = value.1.as_ref();
        let index = value.0;
        let node = expression.nodes(index);
        let variables_id: NodeIndex = node.data[1].into();
        let expr = match node.expr.try_into() {
            Ok(kind) => kind,
            _ => unreachable!(),
        };
        let variables = Variables::from_node((variables_id, expression));
        Self {
            aggregate_type: expr,
            formula: node.data[0].into(),
            variables,
        }
    }
}

impl ToConstraint for AggregateNodeBuilder {
    fn sub_node(&mut self) -> Option<super::StandaloneNode> {
        let mut dummy = VariablesBuilder::new();
        swap(&mut self.variables, &mut dummy);
        Some(dummy.into())
    }

    fn to_node(self, ToNodeArgs { sub, .. }: ToNodeArgs) -> Node {
        Node {
            expr: self.aggregate_type.into(),
            data: [self.formula.into(), sub.unwrap().into()],
        }
    }
}
