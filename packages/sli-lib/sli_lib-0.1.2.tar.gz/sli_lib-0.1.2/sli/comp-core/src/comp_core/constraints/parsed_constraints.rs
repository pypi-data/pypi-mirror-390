use super::{BoundVarId, Formulas, NodeIndex, ToConstraint};
use crate::comp_core::{
    expression::{ExpressionIter, ExpressionTree, Expressions},
    structure::TypeInterps,
};
use sli_collections::rc::Rc;
use std::fmt::Debug;
use typed_index_collections::TiVec;
pub type SourceMap = TiVec<NodeIndex, (usize, usize)>;

/// The formulas parsed as they are. These are not supposed to change.
#[derive(Clone)]
pub struct ParsedConstraints {
    expressions: Expressions,
    pub formulas: Formulas,
    pub source_map: SourceMap,
}

impl Debug for ParsedConstraints {
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

impl ParsedConstraints {
    // TODO type_interps should not be needed here.
    // Fix this when mythical IR1 appears.
    pub fn new(type_interps: Rc<TypeInterps>) -> Self {
        Self {
            expressions: Expressions::new(type_interps),
            formulas: Formulas::new(),
            source_map: SourceMap::new(),
        }
    }

    pub fn get_expressions(&self) -> &Expressions {
        &self.expressions
    }

    pub fn get_mut_expressions(&mut self) -> &mut Expressions {
        &mut self.expressions
    }

    pub fn new_bound_var(&mut self) -> BoundVarId {
        self.expressions.new_bound_var()
    }

    pub fn push_node<T>(&mut self, node: T, start: usize, end: usize) -> NodeIndex
    where
        T: ToConstraint,
    {
        let index = self.expressions.push_node(node);
        // TODO fix this
        for index in self.source_map.len()..usize::from(index) {
            self.source_map.insert(index.into(), (0, 0))
        }
        self.source_map.insert(index, (start, end));
        index
    }

    pub fn formulas_iter<'a>(&'a self) -> ExpressionIter<'a> {
        ExpressionIter::new(&self.expressions, self.formulas.iter())
    }

    pub fn add_constraint(&mut self, node_id: NodeIndex) {
        self.formulas.push(node_id)
    }
}
