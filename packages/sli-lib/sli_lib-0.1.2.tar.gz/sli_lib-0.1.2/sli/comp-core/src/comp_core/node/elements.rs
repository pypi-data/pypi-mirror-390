use super::{
    Childless, ExprType, FromExpressionUnchecked, NodeEnum, StandaloneNode, from_node_impl,
};
use crate::comp_core::RealRepr;
use crate::comp_core::constraints::{BoundVarId, NodeIndex, ToConstraint, ToNodeArgs};
use crate::comp_core::expression::Expressions;
use crate::comp_core::node::Node;
use crate::comp_core::structure::TypeElement;
use crate::comp_core::{
    Int, Real,
    vocabulary::{PfuncIndex, Type, TypeElementIndex, TypeEnum, TypeIndex},
};
use crate::{DiscreteInt, IndexRepr};
use std::iter::Zip;
use std::slice::Iter;
use std::{debug_assert, unreachable};

macro_rules! create_element_node {
    ($(($name:ident, $pat:pat, $e_type:ident)),+$(,)?) => {
        #[derive(Debug, Clone, PartialEq, Eq)]
        pub enum ElementNode {
            $(
                $e_type($name),
            )+
        }

        $(
            impl From<$name> for ElementNode {
                fn from(value: $name) -> Self {
                    Self::$e_type(value)
                }
            }

            impl<'a> From<$name> for NodeEnum<'a> {
                fn from(value: $name) -> Self {
                    Self::Element(value.into())
                }
            }

            impl From<$name> for StandaloneNode {
                fn from(value: $name) -> Self {
                    Self::Element(value.into())
                }
            }
        )+

        impl From<ElementNode> for Node {
            fn from(value: ElementNode) -> Self {
                match value {
                    $(
                        ElementNode::$e_type(val) => val.into(),
                    )+
                }
            }
        }

        impl<'a> FromExpressionUnchecked<'a> for ElementNode {
            fn from_node<T: AsRef<Expressions>>(value: (NodeIndex, &'a T)) -> Self {
                let node = value.1.as_ref().nodes(value.0);
                match node.expr {
                    $(
                        $pat => Self::$e_type($name::from_node(value.into())),
                    )+
                    _ => unreachable!(),
                }
            }
        }

        impl<'a> ToConstraint for ElementNode {
            fn to_type_map(&self) -> Zip<Iter<'_, BoundVarId>, Iter<'_, Type>> {
                match self {
                    $(
                        Self::$e_type(val) => val.to_type_map(),
                     )+
                }
            }

            fn to_pfunc_map(&self) -> Option<PfuncIndex> {
                match self {
                    $(
                        Self::$e_type(val) => val.to_pfunc_map(),
                     )+
                }
            }

            fn extra_children(&self) -> std::borrow::Cow<'_, [crate::comp_core::IndexRepr]> {
                match self {
                    $(
                        Self::$e_type(val) => val.extra_children(),
                     )+
                }
            }

            fn to_node(self, to_node_args: ToNodeArgs) -> Node {
                match self {
                    $(
                        Self::$e_type(val) => val.to_node(to_node_args),
                     )+
                }
            }
        }
   };
}

create_element_node!(
    (TypeElementNode, ExprType::Element, Type),
    (IntElementNode, ExprType::IntElement, Int),
    (RealElementNode, ExprType::RealElement, Real),
    (QuantElementNode, ExprType::QuantElement, Quant),
    (BoolElement, ExprType::True | ExprType::False, Bool),
);

impl From<TypeElement> for ElementNode {
    fn from(value: TypeElement) -> Self {
        match value {
            TypeElement::Bool(b) => Self::Bool(b.into()),
            TypeElement::Int(b) => Self::Int(b.into()),
            TypeElement::Real(b) => Self::Real(b.into()),
            TypeElement::Custom(b) => Self::Type(b.into()),
        }
    }
}

impl TryFrom<ElementNode> for TypeElement {
    type Error = ();
    fn try_from(value: ElementNode) -> Result<Self, Self::Error> {
        match value {
            ElementNode::Bool(e) => Ok(e.value.into()),
            ElementNode::Int(e) => Ok(e.num.into()),
            ElementNode::Real(e) => Ok(e.real.into()),
            ElementNode::Type(e) => Ok(e.element.into()),
            ElementNode::Quant(_) => Err(()),
        }
    }
}

impl From<TypeElement> for StandaloneNode {
    fn from(value: TypeElement) -> Self {
        ElementNode::from(value).into()
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct QuantElementNode {
    pub bound_var_id: BoundVarId,
    pub type_enum: Type,
}

impl ToConstraint for QuantElementNode {
    fn to_type_map(&self) -> Zip<Iter<'_, BoundVarId>, Iter<'_, Type>> {
        core::slice::from_ref(&self.bound_var_id)
            .iter()
            .zip(core::slice::from_ref(&self.type_enum).iter())
    }

    fn to_node(self, _: ToNodeArgs) -> Node {
        self.into()
    }
}

impl QuantElementNode {
    pub fn new(bound_var_id: BoundVarId, type_enum: Type) -> Self {
        Self {
            bound_var_id,
            type_enum,
        }
    }
}

impl<'a> FromExpressionUnchecked<'a> for QuantElementNode {
    fn from_node<T: AsRef<Expressions>>(value: (NodeIndex, &'a T)) -> Self {
        let expression = value.1.as_ref();
        let index = value.0;
        let node = expression.nodes(index);
        debug_assert_eq!(node.expr, ExprType::QuantElement);
        let bound_var_id = node.data[0].into();
        let type_id = expression.type_map(bound_var_id);
        Self {
            type_enum: type_id,
            bound_var_id,
        }
    }
}

impl From<QuantElementNode> for Node {
    fn from(value: QuantElementNode) -> Self {
        Self {
            expr: ExprType::QuantElement,
            data: [value.bound_var_id.into(), 0],
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct TypeElementNode {
    pub element: TypeElementIndex,
}

impl Childless for TypeElementNode {}

impl TypeElementNode {
    pub fn new(type_index: TypeIndex, type_enum: TypeEnum) -> Self {
        Self {
            element: TypeElementIndex(type_index, type_enum),
        }
    }
}

impl From<Node> for TypeElementNode {
    fn from(value: Node) -> Self {
        debug_assert!(value.expr == ExprType::Element);
        Self {
            element: TypeElementIndex(value.data[0].into(), value.data[1].into()),
        }
    }
}

impl From<TypeElementIndex> for TypeElementNode {
    fn from(value: TypeElementIndex) -> Self {
        TypeElementNode::new(value.0, value.1)
    }
}

from_node_impl!(TypeElementNode);

impl From<TypeElementNode> for Node {
    fn from(value: TypeElementNode) -> Self {
        Self {
            expr: ExprType::Element,
            data: [value.element.0.into(), value.element.1.into()],
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct IntElementNode {
    pub num: Int,
}

impl Childless for IntElementNode {}

impl IntElementNode {
    pub fn new(num: Int) -> Self {
        Self { num }
    }
}

impl From<Node> for IntElementNode {
    fn from(value: Node) -> Self {
        debug_assert!(value.expr == ExprType::IntElement);
        Self {
            num: unsafe { std::mem::transmute(value.data[0]) },
        }
    }
}

impl From<Int> for IntElementNode {
    fn from(value: Int) -> Self {
        IntElementNode::new(value)
    }
}

impl From<IntElementNode> for Node {
    fn from(value: IntElementNode) -> Self {
        Self {
            expr: ExprType::IntElement,
            data: [
                unsafe { std::mem::transmute::<Int, IndexRepr>(value.num) },
                0,
            ],
        }
    }
}

from_node_impl!(IntElementNode);

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct RealElementNode {
    pub real: Real,
}

impl Childless for RealElementNode {}

impl RealElementNode {
    pub fn new(real: Real) -> Self {
        Self { real }
    }
}

impl From<Real> for RealElementNode {
    fn from(value: Real) -> Self {
        RealElementNode::new(value)
    }
}

from_node_impl!(RealElementNode);

impl From<Node> for RealElementNode {
    fn from(value: Node) -> Self {
        let numer = value.data[0];
        let denom = value.data[1];
        Self {
            real: Real::new(RealRepr::new(numer as DiscreteInt, denom as DiscreteInt)),
        }
    }
}

impl From<RealElementNode> for Node {
    fn from(value: RealElementNode) -> Self {
        Self {
            expr: ExprType::RealElement,
            data: [
                *value.real.inner_ref().numer() as IndexRepr,
                *value.real.inner_ref().denom() as IndexRepr,
            ],
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct BoolElement {
    pub value: bool,
}

impl Childless for BoolElement {}

impl BoolElement {
    pub fn new(value: bool) -> Self {
        Self { value }
    }
}

impl From<Node> for BoolElement {
    fn from(value: Node) -> Self {
        let value = match value.expr {
            ExprType::True => true,
            ExprType::False => false,
            _ => unreachable!(),
        };
        Self { value }
    }
}

from_node_impl!(BoolElement);

impl From<BoolElement> for Node {
    fn from(value: BoolElement) -> Self {
        let expr = match value.value {
            true => ExprType::True,
            false => ExprType::False,
        };
        Self { expr, data: [0, 0] }
    }
}

impl From<bool> for BoolElement {
    fn from(value: bool) -> Self {
        BoolElement::new(value)
    }
}

impl Into<bool> for BoolElement {
    fn into(self) -> bool {
        self.value
    }
}
