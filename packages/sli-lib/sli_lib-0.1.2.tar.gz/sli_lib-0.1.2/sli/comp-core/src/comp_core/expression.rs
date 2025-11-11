pub mod expressions;
pub mod transformed_expressions;
use super::{
    constraints::{BoundVarId, NodeIndex},
    node::{ElementNode, NodeEnum, NodeWVariables, Variables},
    vocabulary::TypeEnum,
};
pub use expressions::*;
use sli_collections::hash_set::IdHashSet;
use std::{cell::RefCell, collections::HashMap, hash::BuildHasher, slice::Iter};
pub use transformed_expressions::*;

#[derive(Debug, Clone)]
pub struct ExpressionIter<'a> {
    expressions: &'a Expressions,
    formulas: Iter<'a, NodeIndex>,
}

impl<'a> ExpressionIter<'a> {
    pub fn expressions(&self) -> &'a Expressions {
        self.expressions
    }
}

impl<'a> ExpressionIter<'a> {
    pub fn new<R: AsRef<Expressions>>(expressions: &'a R, formulas: Iter<'a, NodeIndex>) -> Self {
        Self {
            expressions: expressions.as_ref(),
            formulas,
        }
    }
}

impl<'a> Iterator for ExpressionIter<'a> {
    type Item = ExpressionRef<'a>;
    fn next(&mut self) -> Option<Self::Item> {
        if let Some(&i) = self.formulas.next() {
            Some(self.expressions.to_expression(i))
        } else {
            None
        }
    }
}

impl<'a> DoubleEndedIterator for ExpressionIter<'a> {
    fn next_back(&mut self) -> Option<Self::Item> {
        if let Some(&i) = self.formulas.next_back() {
            Some(self.expressions.to_expression(i))
        } else {
            None
        }
    }
}

/// Collects the free variables of the given expression.
pub fn free_variables(expr_ref: ExpressionRef) -> Vec<BoundVarId> {
    let mut free_vars = Vec::new();
    let seen_vars: RefCell<IdHashSet<BoundVarId>> = Default::default();
    let add_vars = |vars: &Variables, seen_vars: &RefCell<IdHashSet<BoundVarId>>| {
        let mut seen_vars = seen_vars.borrow_mut();
        vars.iter_vars().for_each(|f| {
            let _prev = seen_vars.insert(*f);
            debug_assert!(_prev, "same variable bound twice!");
        })
    };
    let remove_vars = |vars: &Variables, seen_vars: &RefCell<IdHashSet<BoundVarId>>| {
        let mut seen_vars = seen_vars.borrow_mut();
        vars.iter_vars().for_each(|f| {
            let _prev = seen_vars.remove(f);
            debug_assert!(_prev, "unseen variable should never happen");
        })
    };
    expr_ref.bi_for_each(
        &mut |pre| {
            if let Ok(variables) = NodeWVariables::try_from(pre.clone()) {
                add_vars(&variables.variables, &seen_vars);
            }
            use NodeEnum as N;
            match pre {
                N::Element(ElementNode::Quant(var)) => {
                    if !seen_vars.borrow().contains(&var.bound_var_id) {
                        free_vars.push(var.bound_var_id);
                    }
                }
                N::AppliedSymb(ap) => ap.child_iter().for_each(|f| {
                    if let ElementNode::Quant(var) = f {
                        if !seen_vars.borrow().contains(&var.bound_var_id) {
                            free_vars.push(var.bound_var_id);
                        }
                    }
                }),
                N::AppliedAuxSymb(ap) => ap.child_iter().for_each(|f| {
                    if let ElementNode::Quant(var) = f {
                        if !seen_vars.borrow().contains(&var.bound_var_id) {
                            free_vars.push(var.bound_var_id);
                        }
                    }
                }),
                N::Def(_)
                | N::Agg(_)
                | N::BinOps(_)
                | N::IsInt(_)
                | N::NumNeg(_)
                | N::Neg(_)
                | N::Ite(_)
                | N::Element(_)
                | N::Quant(_)
                | N::Rule(_) => {}
            }
        },
        &mut |post| {
            if let Ok(variables) = NodeWVariables::try_from(post.clone()) {
                remove_vars(&variables.variables, &seen_vars);
            }
        },
    );
    free_vars
}

/// Trait for linking FO quantified variables to a domain element.
pub trait VariableValue {
    /// Panicking version of [get_type_enum](Self::get_type_enum).
    fn get(&self, var: BoundVarId) -> TypeEnum {
        self.get_type_enum(var)
            .expect("Variable should have a value!")
    }
    fn get_type_enum(&self, var: BoundVarId) -> Option<TypeEnum>;
    fn set_type_enum(&mut self, var: BoundVarId, val: TypeEnum);
    fn remove_var(&mut self, var: BoundVarId);
}

impl<S: BuildHasher> VariableValue for HashMap<BoundVarId, TypeEnum, S> {
    fn get_type_enum(&self, var: BoundVarId) -> Option<TypeEnum> {
        self.get(&var).copied()
    }

    fn set_type_enum(&mut self, var: BoundVarId, val: TypeEnum) {
        self.insert(var, val);
    }

    fn remove_var(&mut self, var: BoundVarId) {
        self.remove(&var);
    }
}
