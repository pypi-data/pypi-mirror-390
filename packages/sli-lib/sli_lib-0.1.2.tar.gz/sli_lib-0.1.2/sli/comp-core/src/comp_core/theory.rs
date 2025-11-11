use super::{
    constraints::ParsedConstraints,
    expression::{ExpressionIter, Expressions},
    structure::PartialStructure,
    vocabulary::Vocabulary,
};
use sli_collections::rc::Rc;

/// Represents an FO(.) Theory. Created based on the vocabulary block, theory block, and optionally
/// a structure block. This combination is also known as a **knowledge base** or **specification**.
/// **Caution**: Not to be confused with a _theory block_, which only contains formulas.
#[derive(Debug, Clone)]
pub struct Theory<'a> {
    pub source: &'a str,
    /// Parsed constraints are never modified.
    pub parsed_constraints: Rc<ParsedConstraints>,
    pub structure: PartialStructure,
    pub vocabulary: Rc<Vocabulary>,
}

impl<'b> Theory<'b> {
    pub fn new(vocabulary: Rc<Vocabulary>, structure: PartialStructure, source: &'b str) -> Self {
        Self {
            parsed_constraints: Rc::new(ParsedConstraints::new(
                structure.rc_type_interps().clone(),
            )),
            structure,
            vocabulary,
            source,
        }
    }

    pub fn expressions(&self) -> &Expressions {
        self.parsed_constraints.get_expressions()
    }

    pub fn formula_iter<'a>(&'a self) -> ExpressionIter<'a> {
        self.parsed_constraints.formulas_iter()
    }

    pub fn set_structure(
        &mut self,
        new_structure: PartialStructure,
    ) -> Result<PartialStructure, ()> {
        if !Rc::ptr_eq(&self.vocabulary, new_structure.rc_vocab()) {
            return Err(());
        }
        if !Rc::ptr_eq(
            self.structure.rc_type_interps(),
            new_structure.rc_type_interps(),
        ) {
            unimplemented!("Changing type interps is currently not implemented");
        }
        let old = self.structure.clone();
        self.structure = new_structure.into();
        Ok(old)
    }
}
