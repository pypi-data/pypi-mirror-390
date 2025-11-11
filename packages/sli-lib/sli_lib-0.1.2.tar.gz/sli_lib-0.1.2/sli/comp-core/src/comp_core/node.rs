//! Nodes in the comp core AST. These are serialized in [Expressions]
//! to hopefully increase preformance by reducing memory footprint and keeping data somewhat close
//! to eachother.

mod bin_ops;
pub use bin_ops::*;
mod un_ops;
pub use un_ops::*;
mod elements;
pub use elements::*;
mod applied_symb;
pub use applied_symb::*;
mod quant;
pub use quant::*;
mod ite;
pub use ite::*;
mod variables;
pub use variables::*;
mod aggregate;
pub use aggregate::*;
mod node_with_variables;
pub use node_with_variables::*;
mod definition;
pub use definition::*;

use super::{
    IndexRepr,
    constraints::{BoundVarId, NodeIndex, ToConstraint, ToNodeArgs},
    expression::{AuxIndex, ExpressionRef, Expressions, IDomainPredicate},
    vocabulary::{PfuncIndex, Type},
};
use std::{borrow::Cow, iter::Zip, slice::Iter};

/// Deserialization trait for nodes in an [Expressions].
trait FromExpressionUnchecked<'a> {
    fn from_node<T: AsRef<Expressions>>(value: (NodeIndex, &'a T)) -> Self;
}

/// Serialized expression type.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ExprType {
    Add,
    And,

    Divide,
    Element,
    QuantElement,
    IntElement,
    RealElement,
    Eq,
    Eqv,
    ExQuant,
    UniQuant,

    AppliedSymb,
    AppliedAuxSymb,
    // Splitted variants are used in satisfying set transform,
    // These variants behave exactly the same for everything else.
    SplittedAppliedSymb,
    SplittedAppliedAuxSymb,

    Impl,
    Rem,
    Mult,
    Neg,
    NumNeg,
    Neq,
    Or,
    Symb,
    Sub,
    Interpreted,
    // numeric comp ops
    Lt,
    Le,
    Gt,
    Ge,
    // if then else
    Ite,
    Variables,
    // Aggregates
    CardAgg,
    SumAgg,
    // Definitions
    RuleHead,
    Rule,
    Definition,
    // is int operation for reals
    IsInt,

    True,
    False,

    // Helper nodes
    Rules,
}

impl ExprType {
    /// This function tells which expression type should be evaluated first.
    /// The expressions that evaluate to true are expression that have no or a limited (by
    /// vocabulary or others) amount of descendants (That is why AppliedSymb is in eval first list).
    ///
    /// This is used when walking over the tree to decide which expression to choose first, as a
    /// form of optimization. For example:
    /// When we encounter an implication, we peek into the left and right child of the
    /// implication and first check if one of the expression types returns True/False.
    /// If that is the case, we evaluate that side of the expression first. This can potentially
    /// remove an entire branch, e.g., when we find that the left side of the implication returns
    /// False.
    /// Note: this does _not_ perform interpretations.
    pub fn eval_first(&self) -> bool {
        use ExprType as E;
        match self {
            E::Add
            | E::And
            | E::Divide
            | E::Eq
            | E::ExQuant
            | E::UniQuant
            | E::Impl
            | E::Rem
            | E::Mult
            | E::Neg
            | E::IsInt
            | E::NumNeg
            | E::Neq
            | E::Or
            | E::Sub
            | E::Eqv
            | E::Lt
            | E::Le
            | E::Gt
            | E::Ge
            | E::Ite
            | E::Variables
            | E::CardAgg
            | E::SumAgg
            | E::RuleHead
            | E::Rule
            | E::Definition
            | E::Rules => false,
            E::Element
            | E::QuantElement
            | E::IntElement
            | E::RealElement
            | E::Symb
            | E::Interpreted
            | E::True
            | E::False
            | E::AppliedSymb
            | E::SplittedAppliedSymb
            | E::AppliedAuxSymb
            | E::SplittedAppliedAuxSymb => true,
        }
    }
}

#[derive(Debug, Clone)]
pub struct Node {
    pub expr: ExprType,
    data: [IndexRepr; 2],
}

impl Node {
    pub fn try_into_bool(&self) -> Option<bool> {
        match self.expr {
            ExprType::True => Some(true),
            ExprType::False => Some(false),
            _ => None,
        }
    }
}

impl From<bool> for Node {
    fn from(value: bool) -> Self {
        match value {
            true => Self {
                expr: ExprType::True,
                data: [0, 0],
            },
            false => Self {
                expr: ExprType::False,
                data: [0, 0],
            },
        }
    }
}

impl ToConstraint for Node {
    fn to_node(self, _: ToNodeArgs) -> Node {
        self
    }
}

macro_rules! create_node_enum {
    ({
        $(($name:ty, $builder:ty, $pat:pat, $enum_name:ident)),+ $(,)?
    }$(,)?
        $(($standalone_only:ty, $enum_standalone:ident)),* $(,)?
    ) => {
        /// A view for a node in an comp core expression.
        #[derive(Debug, Clone)]
        pub enum NodeEnum<'a> {
            $(
                $enum_name($name),
            )+
        }

        impl<'a> NodeEnum<'a> {
            pub fn from<T: AsRef<Expressions>>(id: NodeIndex, expr: &'a T) -> Self {
                NodeEnum::try_from((id, expr))
                    .expect("Cannot create NodeEnum from helper expr type")
            }
        }

        impl<'a, T: AsRef<Expressions>> TryFrom<(NodeIndex, &'a T)> for NodeEnum<'a> {
            type Error = ExprType;
            fn try_from(value: (NodeIndex, &'a T)) -> Result<Self, Self::Error> {
                let expression = value.1.as_ref();
                let node = expression.nodes(value.0);
                match node.expr {
                    $(
                        $pat => {
                            Ok(NodeEnum::$enum_name(<$name>::from_node(value)))
                        }
                    )+
                    e => Err(e)
                }
            }
        }

        $(
            impl<'a> From<$name> for NodeEnum<'a> {
                fn from(value: $name) -> Self {
                    NodeEnum::$enum_name(value)
                }
            }
        )+

        $(
            impl<'a, T: AsRef<Expressions>> TryFrom<(NodeIndex, &'a T)> for $name {
                type Error = ();
                fn try_from(value: (NodeIndex, &'a T)) -> Result<Self, Self::Error> {
                    let expression = value.1.as_ref();
                    let node = expression.nodes(value.0);
                    match node.expr {
                        $pat => Ok(<$name>::from_node(value)),
                        _ => Err(()),
                    }
                }
            }

            impl<'a> TryFrom<ExpressionRef<'a>> for $name {
                type Error = ();
                fn try_from(value: ExpressionRef<'a>) -> Result<Self, Self::Error> {
                    Self::try_from((value.start, value.expressions))
                }
            }
        )+

        impl<'a> From<NodeEnum<'a>> for StandaloneNode {
            fn from(value: NodeEnum) -> StandaloneNode {
                match value {
                    $(
                        NodeEnum::$enum_name(val) =>
                            StandaloneNode::$enum_name(val.into()),
                    )+
                }
            }
        }

        /// A 'standalone` node for a comp core expression.
        /// The data stored might contain 'pointers' (indices) to an expression stored somewhere
        /// So it is not completely standalone.
        /// Needed to add dynamically sized nodes to expressions, e.g. applied symbols.
        #[derive(Debug, Clone)]
        pub enum StandaloneNode {
            $(
                $enum_name($builder),
            )+
            $(
                $enum_standalone($standalone_only),
            )*
        }

        $(
            impl From<$builder> for StandaloneNode {
                fn from(value: $builder) -> Self {
                    Self::$enum_name(value)
                }
            }
         )+

        $(
            impl From<$standalone_only> for StandaloneNode {
                fn from(value: $standalone_only) -> Self {
                    Self::$enum_standalone(value)
                }
            }
         )+

        impl ToConstraint for StandaloneNode {
            fn sub_node(&mut self) -> Option<Self> {
                match self {
                    $(
                        Self::$enum_name(value) => value.sub_node(),
                    )+
                    $(
                        Self::$enum_standalone(value) => value.sub_node(),
                    )*
                }
            }

            fn to_pfunc_map(&self) -> Option<PfuncIndex> {
                match self {
                    $(
                        Self::$enum_name(value) => value.to_pfunc_map(),
                    )+
                    $(
                        Self::$enum_standalone(value) => value.to_pfunc_map(),
                    )*
                }
            }

            fn to_aux_map(&self) -> Option<AuxIndex> {
                match self {
                    $(
                        Self::$enum_name(value) => value.to_aux_map(),
                    )+
                    $(
                        Self::$enum_standalone(value) => value.to_aux_map(),
                    )*
                }
            }

            fn to_type_map(&self) -> Zip<Iter<'_, BoundVarId>, Iter<'_, Type>> {
                match self {
                    $(
                        Self::$enum_name(value) => value.to_type_map(),
                    )+
                    $(
                        Self::$enum_standalone(value) => value.to_type_map(),
                    )*
                }
            }

            fn extra_children(&self) -> Cow<'_, [IndexRepr]> {
                match self {
                    $(
                        Self::$enum_name(value) => value.extra_children(),
                    )+
                    $(
                        Self::$enum_standalone(value) => value.extra_children(),
                    )*
                }
            }

            fn children(&self) -> Box<[StandaloneNode]> {
                match self {
                    $(
                        Self::$enum_name(value) => value.children(),
                    )+
                    $(
                        Self::$enum_standalone(value) => value.children(),
                    )*
                }
            }

            fn quant_elements(&mut self) -> Option<IDomainPredicate> {
                match self {
                    $(
                        Self::$enum_name(value) => value.quant_elements(),
                    )+
                    $(
                        Self::$enum_standalone(value) => value.quant_elements(),
                    )+
                }
            }

            fn to_node(self, to_node_args: ToNodeArgs) -> Node {
                match self {
                    $(
                        Self::$enum_name(value) => value.to_node(to_node_args),
                    )+
                    $(
                        Self::$enum_standalone(value) => value.to_node(to_node_args),
                    )+
                }
            }
        }
    };
}

create_node_enum!(
    {
    (QuantNode<'a>, QuantNodeBuilder, ExprType::ExQuant | ExprType::UniQuant, Quant),
    (AggregateNode<'a>, AggregateNodeBuilder, ExprType::CardAgg | ExprType::SumAgg, Agg),
    (AppliedSymbNode<'a>, AppliedSymbBuilder, ExprType::AppliedSymb | ExprType::SplittedAppliedSymb, AppliedSymb),
    (AppliedAuxSymbNode<'a>, AppliedAuxSymbBuilder,
     ExprType::AppliedAuxSymb | ExprType::SplittedAppliedAuxSymb, AppliedAuxSymb),
    (BinOpNode, BinOpNode, ExprType::And | ExprType::Or | ExprType::Impl | ExprType::Add |
     ExprType::Sub | ExprType::Rem | ExprType::Mult | ExprType::Divide | ExprType::Eq |
     ExprType::Neq | ExprType::Eqv | ExprType::Lt | ExprType::Le | ExprType::Gt |
     ExprType::Ge
     , BinOps),
    (NegNode, NegNode, ExprType::Neg, Neg),
    (NumNegNode, NumNegNode, ExprType::NumNeg, NumNeg),
    (IsIntNode, IsIntNode, ExprType::IsInt, IsInt),
    (ElementNode, ElementNode, ExprType::QuantElement | ExprType::Element |
     ExprType::IntElement | ExprType::RealElement | ExprType::True |
     ExprType::False, Element),
    (IteNode, IteNode, ExprType::Ite, Ite),
    (Rule<'a>, RuleBuilder, ExprType::Rule, Rule),
    (Definition<'a>, DefinitionBuilder, ExprType::Definition, Def),
    },
    (VariablesBuilder, Vars),
    (RuleHeadBuilder, RuleHead),
    (RulesComplete, Rules),
);

impl<'a> NodeEnum<'a> {
    pub fn has_variable<T>(loc: NodeIndex, expr: T) -> bool
    where
        T: Into<&'a Expressions>,
    {
        QuantNode::try_from((loc, expr.into())).is_ok()
    }
}

impl<'a> From<bool> for NodeEnum<'a> {
    fn from(value: bool) -> Self {
        NodeEnum::Element(BoolElement::from(value).into())
    }
}

impl From<bool> for StandaloneNode {
    fn from(value: bool) -> Self {
        StandaloneNode::Element(BoolElement::from(value).into())
    }
}

impl StandaloneNode {
    pub fn quant_node_var(&self) -> Option<Iter<BoundVarId>> {
        match self {
            StandaloneNode::Quant(q) => Some(q.variables.iter_vars()),
            _ => None,
        }
    }
}

/// Convenience macro for helper structures to
macro_rules! from_node_impl {
    ($t:ty) => {
        impl<'a> crate::comp_core::node::FromExpressionUnchecked<'a> for $t {
            fn from_node<T: AsRef<crate::comp_core::expression::Expressions>>(
                value: (crate::comp_core::constraints::NodeIndex, &'a T),
            ) -> Self {
                let expression = value.1.as_ref();
                let node = expression.nodes(value.0);
                node.clone().into()
            }
        }
    };
}

pub(self) use from_node_impl;

/// Helper trait for auto implementing [ToConstraint] for nodes with no children.
pub(crate) trait Childless {}

impl<S> ToConstraint for S
where
    S: Childless + Into<Node>,
{
    fn to_node(self, _: ToNodeArgs) -> Node {
        self.into()
    }
}
