use super::{Formulas, NodeIndex};
use crate::comp_core::{
    expression::{ExpressionIter, ExpressionTree, TransformedExpressions},
    structure::TypeInterps,
};
use sli_collections::rc::Rc;
use std::fmt::Debug;

/// These constraints keep track of their origin
/// (TODO: this is currently broken and also doesn't work because IR1 does not exist yet).
#[derive(Clone)]
pub struct TransformedConstraints {
    pub expressions: TransformedExpressions,
    pub formulas: Formulas,
}

impl Debug for TransformedConstraints {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{{\n")?;
        for form in self.formulas_iter() {
            write!(
                f,
                "  {:?}\n",
                ExpressionTree::<2> {
                    exp_ref: form,
                    depth: 2,
                }
            )?;
        }
        write!(f, "}}\n")
    }
}

impl TransformedConstraints {
    pub fn new(type_interps: Rc<TypeInterps>) -> Self {
        Self {
            expressions: TransformedExpressions::new(type_interps),
            formulas: Formulas::new(),
        }
    }

    pub fn get_origin(&self, index: NodeIndex) -> NodeIndex {
        self.expressions.get_origin(index)
    }

    pub fn formulas_iter<'a>(&'a self) -> ExpressionIter<'a> {
        ExpressionIter::new(&self.expressions, self.formulas.iter())
    }

    pub fn add_constraint(&mut self, node_id: NodeIndex) {
        self.formulas.push(node_id)
    }
}
