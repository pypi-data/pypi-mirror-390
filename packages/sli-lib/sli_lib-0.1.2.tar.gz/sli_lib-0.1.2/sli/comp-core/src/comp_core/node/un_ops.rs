use super::{ExprType, Node, from_node_impl};
use crate::comp_core::constraints::{NodeIndex, ToConstraint, ToNodeArgs};

macro_rules! create_un_op {
    ($name:ident, $expr:expr) => {
        #[derive(Debug, Clone)]
        pub struct $name {
            pub child: NodeIndex,
        }

        impl $name {
            pub fn new(child: NodeIndex) -> Self {
                Self { child }
            }
        }

        impl From<Node> for $name {
            fn from(value: Node) -> Self {
                debug_assert!(value.expr == $expr);
                Self {
                    child: value.data[0].into(),
                }
            }
        }

        from_node_impl!($name);

        impl ToConstraint for $name {
            fn to_node(self, _: ToNodeArgs) -> Node {
                self.into()
            }
        }

        impl From<$name> for Node {
            fn from(value: $name) -> Self {
                Self {
                    expr: $expr,
                    data: [value.child.into(), 0],
                }
            }
        }
    };
}

create_un_op!(NegNode, ExprType::Neg);
create_un_op!(NumNegNode, ExprType::NumNeg);
create_un_op!(IsIntNode, ExprType::IsInt);
