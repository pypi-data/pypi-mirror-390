use super::expression::AuxIndex;
use super::expression::IDomainPredicate;
use super::node::{Node, StandaloneNode};
use super::vocabulary::{PfuncIndex, Type};
use super::{IndexRepr, create_index};
use std::borrow::Cow;
use std::fmt::Debug;
use std::iter::Zip;
use std::slice::Iter;

mod parsed_constraints;
mod transformed_constraints;

pub use parsed_constraints::*;
pub use transformed_constraints::*;

pub type Formulas = Vec<NodeIndex>;

create_index!(NodeIndex);
create_index!(ExtraIndex);
create_index!(BoundVarId);

pub struct ToNodeArgs {
    pub extra_len: usize,
    pub sub: Option<NodeIndex>,
}

/// Serialization trait for any node.
/// See [node](super::node) for info about deserialization.
pub trait ToConstraint {
    fn sub_node(&mut self) -> Option<StandaloneNode> {
        None
    }

    fn to_pfunc_map(&self) -> Option<PfuncIndex> {
        None
    }

    fn to_type_map(&self) -> Zip<Iter<'_, BoundVarId>, Iter<'_, Type>> {
        Iter::default().zip(Iter::default())
    }

    fn children(&self) -> Box<[StandaloneNode]> {
        Box::default()
    }

    fn extra_children(&self) -> Cow<'_, [IndexRepr]> {
        Cow::Owned(Vec::new())
    }

    fn to_aux_map(&self) -> Option<AuxIndex> {
        None
    }

    fn quant_elements(&mut self) -> Option<IDomainPredicate> {
        None
    }

    fn to_node(self, args: ToNodeArgs) -> Node;
}
