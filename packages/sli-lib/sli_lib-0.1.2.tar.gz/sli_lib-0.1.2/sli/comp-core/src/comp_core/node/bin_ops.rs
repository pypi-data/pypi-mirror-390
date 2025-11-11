use super::{ExprType, from_node_impl};
use crate::comp_core::constraints::{NodeIndex, ToConstraint, ToNodeArgs};
use crate::comp_core::node::Node;
use crate::comp_core::theory::Theory;

macro_rules! create_bin_op {
    ($(($name:ident, $expr:expr, $pat:pat, $type:ident)),+$(,)?) => {
        $(
            #[derive(Debug, Clone)]
            pub struct $name {
                pub lhs: NodeIndex,
                pub rhs: NodeIndex,
            }

            #[allow(dead_code)]
            impl $name {
                pub fn new(lhs: NodeIndex, rhs: NodeIndex) -> Self {
                    Self {
                        lhs,
                        rhs,
                    }
                }
            }

            impl From<Node> for $name {
                fn from(value: Node) -> Self {
                    debug_assert!(value.expr == $expr);
                    Self {
                        lhs: value.data[0].into(),
                        rhs: value.data[1].into(),
                    }
                }
            }

            impl<
                'a,
            > From<(Node, NodeIndex, &Theory<'a>)> for $name {
                fn from(value: (Node, NodeIndex, &Theory)) -> Self {
                    value.0.into()
                }
            }

            from_node_impl!($name);

            impl From<$name> for Node {
                fn from(value: $name) -> Self {
                    Self {
                        expr: $expr,
                        data: [value.lhs.into(), value.rhs.into()]
                    }
                }
            }
        )+

        #[derive(Debug, Clone, Copy, PartialEq, Eq)]
        pub enum BinOps {
            $(
                $type,
            )+
        }

        #[repr(C)]
        #[derive(Debug, Clone)]
        pub struct BinOpNode {
            pub lhs: NodeIndex,
            pub rhs: NodeIndex,
            pub bin_op: BinOps,
        }

        $(
            impl From<$name> for BinOpNode {
                fn from(value: $name) -> Self {
                    Self {
                        bin_op: BinOps::$type,
                        lhs: value.lhs,
                        rhs: value.rhs,
                    }
                }
            }
        )+

        impl From<BinOpNode> for Node {
            fn from(value: BinOpNode) -> Self {
                let expr = match value.bin_op {
                    $(
                        BinOps::$type => $expr,
                    )+
                };
                Self {
                    expr,
                    data: [value.lhs.into(), value.rhs.into()],
                }
            }
        }

        impl From<Node> for BinOpNode {
            fn from(value: Node) -> Self {
                match value.expr {
                    $(
                        $pat => Self::new(
                            BinOps::$type,
                            value.data[0].into(),
                            value.data[1].into(),
                        ),
                    )+
                    _ => unreachable!(),
                }
            }
        }

        from_node_impl!(BinOpNode);
   };
}

impl BinOpNode {
    pub fn new(bin_op: BinOps, lhs: NodeIndex, rhs: NodeIndex) -> Self {
        Self { bin_op, lhs, rhs }
    }
}

create_bin_op!(
    (AndNode, ExprType::And, ExprType::And, And),
    (OrNode, ExprType::Or, ExprType::Or, Or),
    (ImplNode, ExprType::Impl, ExprType::Impl, Impl),
    (EqvNode, ExprType::Eqv, ExprType::Eqv, Eqv),
    (AddNode, ExprType::Add, ExprType::Add, Add),
    (SubNode, ExprType::Sub, ExprType::Sub, Sub),
    (RemNode, ExprType::Rem, ExprType::Rem, Rem),
    (MultNode, ExprType::Mult, ExprType::Mult, Mult),
    (DivideNode, ExprType::Divide, ExprType::Divide, Divide),
    (EqNode, ExprType::Eq, ExprType::Eq, Eq),
    (NeqNode, ExprType::Neq, ExprType::Neq, Neq),
    (LtNode, ExprType::Lt, ExprType::Lt, Lt),
    (LeNode, ExprType::Le, ExprType::Le, Le),
    (GtNode, ExprType::Gt, ExprType::Gt, Gt),
    (GeNode, ExprType::Ge, ExprType::Ge, Ge),
);

impl ToConstraint for BinOpNode {
    fn to_node(self, _: ToNodeArgs) -> Node {
        self.into()
    }
}
