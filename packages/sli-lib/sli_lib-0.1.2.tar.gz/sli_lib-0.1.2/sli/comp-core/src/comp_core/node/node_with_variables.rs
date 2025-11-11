use super::variables::Variables;
use super::{
    AggKind, AggregateNode, AggregateNodeBuilder, CardAggNode, ExQuantNode, ExprType,
    FromExpressionUnchecked, NodeEnum, QuantKind, QuantNode, QuantNodeBuilder, Rule, RuleBuilder,
    StandaloneNode, SumAggNode, UniQuantNode, VariablesBuilder,
};
use crate::comp_core::constraints::NodeIndex;
use crate::comp_core::expression::Expressions;
use crate::node::RuleHeadBuilder;
use crate::vocabulary::PfuncIndex;

#[derive(Debug, Clone)]
pub struct NodeWVariables<'a> {
    pub type_of: VariablesKind,
    pub formula: NodeIndex,
    pub variables: Variables<'a>,
}

#[derive(Debug, Clone)]
pub struct NodeWVariablesStandalone {
    pub type_of: VariablesKind,
    pub formula: NodeIndex,
    pub variables: VariablesBuilder,
}

impl NodeWVariablesStandalone {
    pub fn from_ref_without_guard<'a>(value: NodeWVariables<'a>) -> Self {
        Self {
            type_of: value.type_of,
            formula: value.formula,
            variables: VariablesBuilder::from_ref_without_guard(value.variables),
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum VariablesKind {
    ExQuant,
    UniQuant,
    CardAgg,
    SumAgg,
    Rule { definiendum: PfuncIndex },
}

impl<'a, T: AsRef<Expressions>> TryFrom<(NodeIndex, &'a T)> for NodeWVariables<'a> {
    type Error = ();
    fn try_from(value: (NodeIndex, &'a T)) -> Result<Self, Self::Error> {
        let expression = value.1.as_ref();
        let node = expression.nodes(value.0);
        match node.expr {
            ExprType::ExQuant => Ok(ExQuantNode::from_node(value).into()),
            ExprType::UniQuant => Ok(UniQuantNode::from_node(value).into()),
            ExprType::CardAgg => Ok(CardAggNode::from_node(value).into()),
            ExprType::SumAgg => Ok(SumAggNode::from_node(value).into()),
            ExprType::Rule => Ok(Rule::from_node(value).into()),
            _ => Err(()),
        }
    }
}

impl<'a> TryFrom<NodeEnum<'a>> for NodeWVariables<'a> {
    type Error = ();

    fn try_from(value: NodeEnum<'a>) -> Result<Self, Self::Error> {
        use NodeEnum as N;
        match value {
            N::Rule(rule) => Ok(rule.into()),
            N::Agg(agg) => Ok(agg.into()),
            N::Quant(quant) => Ok(quant.into()),
            N::Def(_)
            | N::Neg(_)
            | N::NumNeg(_)
            | N::IsInt(_)
            | N::AppliedAuxSymb(_)
            | N::AppliedSymb(_)
            | N::BinOps(_)
            | N::Element(_)
            | N::Ite(_) => Err(()),
        }
    }
}

impl<'a> From<ExQuantNode<'a>> for NodeWVariables<'a> {
    fn from(value: ExQuantNode<'a>) -> Self {
        Self {
            type_of: VariablesKind::ExQuant,
            formula: value.formula,
            variables: value.variables,
        }
    }
}

impl<'a> From<UniQuantNode<'a>> for NodeWVariables<'a> {
    fn from(value: UniQuantNode<'a>) -> Self {
        Self {
            type_of: VariablesKind::UniQuant,
            formula: value.formula,
            variables: value.variables,
        }
    }
}

impl<'a> From<CardAggNode<'a>> for NodeWVariables<'a> {
    fn from(value: CardAggNode<'a>) -> Self {
        Self {
            type_of: VariablesKind::CardAgg,
            formula: value.formula,
            variables: value.variables,
        }
    }
}

impl<'a> From<SumAggNode<'a>> for NodeWVariables<'a> {
    fn from(value: SumAggNode<'a>) -> Self {
        Self {
            type_of: VariablesKind::SumAgg,
            formula: value.formula,
            variables: value.variables,
        }
    }
}

impl<'a> From<Rule<'a>> for NodeWVariables<'a> {
    fn from(value: Rule<'a>) -> Self {
        Self {
            type_of: VariablesKind::Rule {
                definiendum: value.head.definiendum,
            },
            formula: value.body,
            variables: value.head.variables,
        }
    }
}

impl<'a> NodeWVariables<'a> {
    pub fn get_bound_var(loc: NodeIndex, expr: &Expressions) -> Option<Variables> {
        NodeWVariables::try_from((loc, expr)).ok()?.variables.into()
    }
}

impl From<QuantKind> for VariablesKind {
    fn from(value: QuantKind) -> Self {
        match value {
            QuantKind::ExQuant => Self::ExQuant,
            QuantKind::UniQuant => Self::UniQuant,
        }
    }
}

impl From<AggKind> for VariablesKind {
    fn from(value: AggKind) -> Self {
        match value {
            AggKind::Card => Self::CardAgg,
            AggKind::Sum => Self::SumAgg,
        }
    }
}

impl TryFrom<VariablesKind> for QuantKind {
    type Error = ();
    fn try_from(value: VariablesKind) -> Result<Self, Self::Error> {
        match value {
            VariablesKind::ExQuant => Ok(Self::ExQuant),
            VariablesKind::UniQuant => Ok(Self::UniQuant),
            VariablesKind::CardAgg => Err(()),
            VariablesKind::SumAgg => Err(()),
            VariablesKind::Rule { .. } => Err(()),
        }
    }
}

impl TryFrom<VariablesKind> for AggKind {
    type Error = ();
    fn try_from(value: VariablesKind) -> Result<Self, Self::Error> {
        match value {
            VariablesKind::ExQuant | VariablesKind::UniQuant => Err(()),
            VariablesKind::CardAgg => Ok(Self::Card),
            VariablesKind::SumAgg => Ok(Self::Sum),
            VariablesKind::Rule { .. } => Err(()),
        }
    }
}

impl<'a> From<NodeWVariables<'a>> for NodeWVariablesStandalone {
    fn from(value: NodeWVariables<'a>) -> Self {
        Self {
            type_of: value.type_of,
            formula: value.formula,
            variables: value.variables.into(),
        }
    }
}

impl From<QuantNodeBuilder> for NodeWVariablesStandalone {
    fn from(value: QuantNodeBuilder) -> Self {
        Self {
            formula: value.formula,
            variables: value.variables,
            type_of: value.quant_type.into(),
        }
    }
}

impl From<AggregateNodeBuilder> for NodeWVariablesStandalone {
    fn from(value: AggregateNodeBuilder) -> Self {
        Self {
            formula: value.formula,
            variables: value.variables,
            type_of: value.aggregate_type.into(),
        }
    }
}

impl From<RuleBuilder> for NodeWVariablesStandalone {
    fn from(value: RuleBuilder) -> Self {
        Self {
            formula: value.body,
            variables: value.head.variables,
            type_of: VariablesKind::Rule {
                definiendum: value.head.definiendum,
            },
        }
    }
}

impl TryFrom<StandaloneNode> for NodeWVariablesStandalone {
    type Error = StandaloneNode;

    fn try_from(value: StandaloneNode) -> Result<Self, Self::Error> {
        match value {
            StandaloneNode::Agg(agg) => Ok(agg.into()),
            StandaloneNode::Quant(quant) => Ok(quant.into()),
            StandaloneNode::Rule(value) => Ok(value.into()),
            StandaloneNode::Element(_)
            | StandaloneNode::Vars(_)
            | StandaloneNode::AppliedAuxSymb(_)
            | StandaloneNode::AppliedSymb(_)
            | StandaloneNode::Def(_)
            | StandaloneNode::BinOps(_)
            | StandaloneNode::RuleHead(_)
            | StandaloneNode::Ite(_)
            | StandaloneNode::Neg(_)
            | StandaloneNode::NumNeg(_)
            | StandaloneNode::IsInt(_)
            | StandaloneNode::Rules(_) => Err(value),
        }
    }
}

impl<'a> From<NodeWVariables<'a>> for StandaloneNode {
    fn from(value: NodeWVariables<'a>) -> Self {
        NodeWVariablesStandalone::from(value).into()
    }
}

impl From<NodeWVariablesStandalone> for StandaloneNode {
    fn from(value: NodeWVariablesStandalone) -> Self {
        if let Ok(quant_type) = QuantKind::try_from(value.type_of) {
            QuantNodeBuilder::new(quant_type, value.variables, value.formula).into()
        } else if let Ok(agg_type) = AggKind::try_from(value.type_of) {
            AggregateNodeBuilder::new(agg_type, value.variables, value.formula).into()
        } else if let VariablesKind::Rule { definiendum } = value.type_of {
            RuleBuilder::new(
                RuleHeadBuilder {
                    definiendum,
                    variables: value.variables,
                },
                value.formula,
            )
            .into()
        } else {
            unreachable!()
        }
    }
}

impl<'a> From<QuantNode<'a>> for NodeWVariables<'a> {
    fn from(value: QuantNode<'a>) -> Self {
        Self {
            type_of: value.quant_type.into(),
            variables: value.variables,
            formula: value.formula,
        }
    }
}

impl<'a> From<AggregateNode<'a>> for NodeWVariables<'a> {
    fn from(value: AggregateNode<'a>) -> Self {
        Self {
            type_of: value.aggregate_type.into(),
            variables: value.variables,
            formula: value.formula,
        }
    }
}
