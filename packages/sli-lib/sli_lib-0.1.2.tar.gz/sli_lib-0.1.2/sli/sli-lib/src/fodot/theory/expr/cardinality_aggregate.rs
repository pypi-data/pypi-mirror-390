use super::{
    Formula, FreeVariableIter, FreeVariables, Metadata, MetadataIm, MetadataMut, Quantees,
    VariableBinder, VocabIterCheck, WellDefinedCondition, vocabs_ptr_eq,
};
use crate::fodot::display_as_debug;
use crate::fodot::error::VocabMismatchError;
use crate::fodot::fmt::FodotOptions;
use crate::fodot::{
    fmt::{Fmt, FodotDisplay, FormatOptions},
    vocabulary::{Type, TypeRef, Vocabulary},
};
use sli_collections::{iterator::Iterator as SIterator, rc::RcA};
use std::fmt::Display;

/// A cardinality aggregate.
pub struct CardinalityAggregate {
    quantees: Quantees,
    formula: Formula,
    vocab: Option<RcA<Vocabulary>>,
    metadata: Option<Box<Metadata>>,
}

impl Clone for CardinalityAggregate {
    fn clone(&self) -> Self {
        Self {
            quantees: self.quantees.duplicate(),
            formula: self.formula.clone(),
            vocab: self.vocab.clone(),
            metadata: self.metadata.clone(),
        }
    }
}

impl FodotOptions for CardinalityAggregate {
    type Options<'a>
        = FormatOptions
    where
        Self: 'a;
}

impl FodotDisplay for CardinalityAggregate {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        write!(
            f,
            "#{{ {}: {} }}",
            fmt.with_format_opts(&fmt.value.quantees),
            fmt.with_format_opts(&fmt.value.formula),
        )
    }
}

impl Display for CardinalityAggregate {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", Fmt::with_defaults(self))
    }
}

display_as_debug!(CardinalityAggregate);

impl PartialEq for CardinalityAggregate {
    fn eq(&self, other: &Self) -> bool {
        self.quantees == other.quantees && self.formula == other.formula
    }
}

impl Eq for CardinalityAggregate {}

impl CardinalityAggregate {
    pub fn new(quantees: Quantees, formula: Formula) -> Result<Self, VocabMismatchError> {
        let mut vocab_checker = VocabIterCheck::new(quantees.iter_decls().map(|f| f.vocab_rc()));
        if !vocab_checker.check_if_consistent() {
            return Err(VocabMismatchError);
        }
        let vocab = vocab_checker.take_vocab();
        if !vocabs_ptr_eq(vocab.map(|f| f.as_ref()), formula.vocab()) {
            return Err(VocabMismatchError);
        }
        let vocab = vocab.or(formula.vocab_rc()).cloned();

        Ok(Self {
            quantees,
            formula,
            vocab,
            metadata: Default::default(),
        })
    }

    pub fn vocab_rc(&self) -> Option<&RcA<Vocabulary>> {
        self.vocab.as_ref()
    }

    pub fn codomain(&self) -> TypeRef {
        Type::Int
    }

    pub fn quantees(&self) -> &Quantees {
        &self.quantees
    }

    pub fn iter_variables(&self) -> impl SIterator<Item = &VariableBinder> {
        self.quantees.iter()
    }

    pub fn subformula(&self) -> &Formula {
        &self.formula
    }

    pub fn collect_wdcs(&self) -> Vec<WellDefinedCondition> {
        self.formula.collect_wdcs()
    }
}

impl FreeVariables for CardinalityAggregate {
    fn add_to_free_variable_iter<'a>(&'a self, iter: &mut FreeVariableIter<'a>) {
        iter.add_quantees(self.quantees());
        iter.add_expr(self.subformula().into());
    }
}

impl MetadataIm for CardinalityAggregate {
    type Metadata = Metadata;
    fn metadata(&self) -> Option<&Metadata> {
        self.metadata.as_deref()
    }
}

impl MetadataMut for CardinalityAggregate {
    fn metadata_mut(&mut self) -> &mut Metadata {
        self.metadata.get_or_insert_default()
    }
}
