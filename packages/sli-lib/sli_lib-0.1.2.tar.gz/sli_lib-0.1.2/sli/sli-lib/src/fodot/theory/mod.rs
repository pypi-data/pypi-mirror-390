//! Theory datatructures and methods.
//!
//! A [Theory] represents an FO(·) Theory. It contains some [Assertion]s and a [PartialStructure].

use super::{
    display_as_debug,
    error::{
        VocabMismatchError, WithPartialInterpsError,
        parse::{Diagnostics, IDPError},
    },
    fmt::{Fmt, FodotDisplay, FodotOptions, FormatOptions},
    lower::translate_assertions,
    structure::{PartialStructure, StructureBlock, TypeInterps},
    vocabulary::{SymbolError, Vocabulary},
};
use crate::{
    ast::{self, TheoryAst, tree_sitter::TsParser},
    sli_entrance::parse_theory_decls,
};
use comp_core::constraints::ParsedConstraints;
use sli_collections::{iterator::Iterator as SIterator, rc::Rc};
use std::fmt::Display;

mod expr;
pub use expr::*;

/// A list of [Assertion]s.
#[derive(Clone)]
pub struct Assertions {
    vocab: Rc<Vocabulary>,
    assertions: Vec<Assertion>,
}

impl PartialEq for Assertions {
    fn eq(&self, other: &Self) -> bool {
        Rc::ptr_eq(&self.vocab, &other.vocab) && self.assertions == other.assertions
    }
}

impl Eq for Assertions {}

impl FodotOptions for Assertions {
    type Options<'a> = FormatOptions;
}

impl FodotDisplay for Assertions {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        for assertion in fmt.value {
            fmt.write_indent(f)?;
            writeln!(f, "{}.", fmt.with_opts(assertion))?;
        }
        Ok(())
    }
}

impl<'a> Display for Assertions {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

display_as_debug!(Assertions);

impl Assertions {
    /// Create an empty list of [Assertion]s.
    pub fn new(vocab: Rc<Vocabulary>) -> Self {
        Self {
            vocab,
            assertions: Default::default(),
        }
    }

    pub fn parse(&mut self, decls: &str) -> Result<&mut Self, Diagnostics> {
        let mut parser = TsParser::new();
        let theory_ast = ast::Parser::parse_theory(&mut parser, decls);
        let mut diagnostics = Diagnostics::new();
        for (err, span) in theory_ast.parse_errors() {
            diagnostics.add_error(IDPError::new(err.into(), span));
        }
        let vocabulary = self.vocab.clone();
        let count_before = self.assertions.len();
        parse_theory_decls(
            &vocabulary,
            self,
            theory_ast.decls(),
            &decls,
            &mut diagnostics,
        );
        if diagnostics.errors().len() == 0 {
            Ok(self)
        } else {
            self.assertions.truncate(count_before);
            Err(diagnostics)
        }
    }

    pub fn vocab(&self) -> &Vocabulary {
        &self.vocab
    }

    pub fn vocab_rc(&self) -> &Rc<Vocabulary> {
        &self.vocab
    }

    /// Add an [Assertion], fails if the [Assertion]'s corresponding [Vocabulary] is different.
    pub fn add_assertion(&mut self, assertion: Assertion) -> Result<(), VocabMismatchError> {
        if !vocabs_ptr_eq(Some(self.vocab.as_ref()), assertion.vocab()) {
            return Err(VocabMismatchError.into());
        }
        self.assertions.push(assertion);
        Ok(())
    }

    /// Returns an [Iterator] over all [Assertion]s.
    pub fn iter<'a>(&'a self) -> impl SIterator<Item = &'a Assertion> {
        self.into_iter()
    }

    pub(crate) fn lower(
        &self,
        structure: &PartialStructure,
    ) -> Result<ParsedConstraints, SymbolError> {
        let mut parsed_constraints =
            ParsedConstraints::new(Rc::clone(structure.type_interps().cc()));
        translate_assertions(self, structure, &mut parsed_constraints)?;
        Ok(parsed_constraints)
    }
}

impl<'a> IntoIterator for &'a Assertions {
    type IntoIter = core::slice::Iter<'a, Assertion>;
    type Item = &'a Assertion;

    fn into_iter(self) -> Self::IntoIter {
        self.assertions.iter()
    }
}

/// [Assertions] with a name.
#[derive(Clone)]
pub struct TheoryBlock {
    name: Box<str>,
    assertions: Assertions,
}

impl FodotOptions for TheoryBlock {
    type Options<'a> = FormatOptions;
}

impl FodotDisplay for TheoryBlock {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        writeln!(
            f,
            "theory {}: {} {{",
            fmt.value.name,
            fmt.value.vocab().name
        )?;
        write!(f, "{}", fmt.with_opts(&fmt.value.assertions).with_indent())?;
        writeln!(f, "}}")
    }
}

impl Display for TheoryBlock {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

display_as_debug!(TheoryBlock);

impl TheoryBlock {
    pub fn new(name: &str, assertions: Assertions) -> Self {
        Self {
            name: name.into(),
            assertions,
        }
    }

    pub fn vocab(&self) -> &Vocabulary {
        self.assertions.vocab()
    }
}

/// Represents an FO(·) Theory which is represented here by [Assertions] and a [PartialStructure].
#[derive(Clone)]
pub struct Theory {
    assertions: Rc<Assertions>,
    structure: PartialStructure,
}

impl FodotOptions for Theory {
    type Options<'a> = FormatOptions;
}

impl FodotDisplay for Theory {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        let vocab_name = &fmt.value.vocab().name;
        write!(
            f,
            "\
                {}\n\n\
                theory T:{} {{\n\
                    {}\
                }}\n\n\
                structure S:{} {{\n\
                    {}\
                }}\n\n\
            ",
            fmt.with_format_opts(fmt.value.vocab()),
            vocab_name,
            fmt.with_format_opts(fmt.value.assertions()).with_indent(),
            vocab_name,
            fmt.with_format_opts(fmt.value.structure()).with_indent(),
        )
    }
}

impl Display for Theory {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

display_as_debug!(Theory);

impl Theory {
    pub fn empty() -> Self {
        let (_, part_type_interps) = Vocabulary::new("").complete_vocab();
        let type_interps = Rc::new(part_type_interps.try_err_complete().unwrap());
        Self {
            assertions: Assertions::new(type_interps.vocab_rc().clone()).into(),
            structure: PartialStructure::new(type_interps),
        }
    }

    /// Creates an new [Theory].
    pub fn new(
        assertions: Rc<Assertions>,
        structure: PartialStructure,
    ) -> Result<Self, VocabMismatchError> {
        if !assertions.vocab.exact_eq(structure.vocab()) {
            return Err(VocabMismatchError);
        }
        Ok(Self {
            assertions,
            structure,
        })
    }

    /// Creates a [Theory] from the [TheoryBlock] and [StructureBlock].
    pub fn from_blocks(
        theory_block: TheoryBlock,
        structure: StructureBlock,
    ) -> Result<Self, WithPartialInterpsError> {
        if !vocabs_ptr_eq(Some(theory_block.vocab()), Some(structure.vocab())) {
            return Err(VocabMismatchError.into());
        }

        Ok(Self {
            assertions: theory_block.assertions.into(),
            structure: structure
                .structure
                .try_into_partial()
                .map_err(|f| f.type_interps().missing_type_error())?,
        })
    }

    pub fn vocab(&self) -> &Vocabulary {
        self.structure.vocab()
    }

    pub fn vocab_rc(&self) -> &Rc<Vocabulary> {
        &self.structure.vocab_rc()
    }

    pub fn type_interps(&self) -> &TypeInterps {
        self.structure.type_interps()
    }

    pub fn type_interps_rc(&self) -> &Rc<TypeInterps> {
        &self.structure.type_interps_rc()
    }

    pub fn assertions(&self) -> &Assertions {
        &self.assertions
    }

    pub fn assertions_rc(&self) -> &Rc<Assertions> {
        &self.assertions
    }

    pub fn structure(&self) -> &PartialStructure {
        &self.structure
    }

    pub fn set_structure(&mut self, structure: PartialStructure) -> Result<(), VocabMismatchError> {
        if !vocabs_ptr_eq(Some(self.vocab()), Some(structure.vocab())) {
            return Err(VocabMismatchError.into());
        }
        self.structure = structure;
        Ok(())
    }

    pub(crate) fn lower(&self) -> Result<ParsedConstraints, SymbolError> {
        self.assertions.lower(self.structure())
    }
}

#[cfg(test)]
mod tests {
    use super::Assertions;
    use crate::fodot::vocabulary::{BaseType, Vocabulary};

    #[test]
    fn parse_assertions() {
        let mut vocab = Vocabulary::new("T");
        vocab.add_type_decl("D", BaseType::Int).unwrap();
        vocab.parse("type T p: T -> Bool r: T -> D").unwrap();
        let (vocab, _) = vocab.complete_vocab();
        let mut assertions = Assertions::new(vocab);
        assertions
            .parse("!x in T: p(x). ?x in T, y in D: r(x) = y & y > 2.")
            .unwrap();
    }

    #[test]
    fn failed_parse_assertions() {
        let mut vocab = Vocabulary::new("T");
        vocab.add_type_decl("D", BaseType::Int).unwrap();
        vocab.parse("type T p: T -> Bool r: T -> D").unwrap();
        let (vocab, _) = vocab.complete_vocab();
        let mut assertions = Assertions::new(vocab);
        let prev_assertions = assertions.clone();
        assertions
            .parse("!x in T: p(x). ?x in T, y in D: r(x) = y & y > 2")
            .unwrap_err();
        assert!(prev_assertions == assertions);
    }

    #[test]
    fn escaped_theory() {
        let mut vocab = Vocabulary::new("T");
        vocab.add_type_decl("D", BaseType::Int).unwrap();
        vocab.parse("type T p: T -> Bool r: T -> D").unwrap();
        let (vocab, _) = vocab.complete_vocab();
        let mut assertions = Assertions::new(vocab);
        let decls = "!x in T: p(x). } vocabulary V {";
        let diag = assertions.parse(decls).unwrap_err();
        assert!(diag.errors().len() == 1);
        let a = diag.errors().first().unwrap();
        assert_eq!(a.span().end, decls.len());
    }
}
