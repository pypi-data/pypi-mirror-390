use std::mem::swap;

use super::variables::{Variables, VariablesBuilder};
use super::{ExprType, FromExpressionUnchecked};
use crate::comp_core::constraints::{NodeIndex, ToConstraint, ToNodeArgs};
use crate::comp_core::expression::Expressions;
use crate::comp_core::node::Node;

macro_rules! create_quant_nodes {
    ($(($name:ident, $expr:expr, $pat:pat, $type:ident)),+$(,)?) => {
        $(
            #[derive(Debug, Clone)]
            pub struct $name<'a> {
                pub formula: NodeIndex,
                pub variables: Variables<'a>,
            }

            impl<'a> FromExpressionUnchecked<'a> for $name<'a> {
                fn from_node<T: AsRef<Expressions>>(value: (NodeIndex, &'a T)) -> Self {
                    let quant_node = QuantNode::from_node(value);
                    debug_assert_eq!(quant_node.quant_type, QuantKind::$type);
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
                        $pat => {
                            Ok($name::from_node(value))
                        },
                        _ => Err(()),
                    }
                }
            }
        )+

        #[derive(Debug, Clone, Copy, PartialEq, Eq)]
        pub enum QuantKind {
            $(
                $type,
            )+
        }

        $(
            impl<'a> From<$name<'a>> for QuantNode<'a> {
                fn from(value: $name<'a>) -> Self {
                    Self {
                        quant_type: QuantKind::$type,
                        formula: value.formula,
                        variables: value.variables,
                    }
                }
            }
        )+
    }
}

create_quant_nodes!(
    (ExQuantNode, ExprType::ExQuant, ExprType::ExQuant, ExQuant),
    (
        UniQuantNode,
        ExprType::UniQuant,
        ExprType::UniQuant,
        UniQuant
    ),
);

impl From<QuantKind> for ExprType {
    fn from(value: QuantKind) -> Self {
        match value {
            QuantKind::UniQuant => Self::UniQuant,
            QuantKind::ExQuant => Self::ExQuant,
        }
    }
}

impl TryFrom<ExprType> for QuantKind {
    type Error = ();

    fn try_from(value: ExprType) -> Result<Self, Self::Error> {
        match value {
            ExprType::ExQuant => Ok(Self::ExQuant),
            ExprType::UniQuant => Ok(Self::UniQuant),
            _ => Err(()),
        }
    }
}

#[derive(Debug, Clone)]
pub struct QuantNode<'a> {
    pub quant_type: QuantKind,
    pub formula: NodeIndex,
    pub variables: Variables<'a>,
}

impl<'a> QuantNode<'a> {
    pub fn new(quant_type: QuantKind, variables: Variables<'a>, formula: NodeIndex) -> Self {
        Self {
            quant_type,
            formula,
            variables,
        }
    }

    pub fn standalone(self) -> QuantNodeBuilder {
        self.into()
    }
}

#[derive(Debug, Clone)]
pub struct QuantNodeBuilder {
    pub quant_type: QuantKind,
    pub formula: NodeIndex,
    pub variables: VariablesBuilder,
}

impl<'a> From<QuantNode<'a>> for QuantNodeBuilder {
    fn from(value: QuantNode<'a>) -> Self {
        Self {
            quant_type: value.quant_type,
            formula: value.formula,
            variables: value.variables.into(),
        }
    }
}

impl QuantNodeBuilder {
    pub fn new(quant_type: QuantKind, variables: VariablesBuilder, formula: NodeIndex) -> Self {
        Self {
            quant_type,
            formula,
            variables,
        }
    }
}

impl<'a> FromExpressionUnchecked<'a> for QuantNode<'a> {
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
            quant_type: expr,
            formula: node.data[0].into(),
            variables,
        }
    }
}

impl ToConstraint for QuantNodeBuilder {
    fn sub_node(&mut self) -> Option<super::StandaloneNode> {
        let mut dummy = VariablesBuilder::new();
        swap(&mut self.variables, &mut dummy);
        Some(dummy.into())
    }

    fn to_node(self, ToNodeArgs { sub, .. }: ToNodeArgs) -> Node {
        Node {
            expr: self.quant_type.into(),
            data: [self.formula.into(), sub.unwrap().into()],
        }
    }
}
