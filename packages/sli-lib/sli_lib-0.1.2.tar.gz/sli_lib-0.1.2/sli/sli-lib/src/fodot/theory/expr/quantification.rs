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
use std::fmt::{Debug, Display};

/// Type of quantifier.
#[non_exhaustive]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum QuantType {
    Universal,
    Existential,
}

/// A quantification over some variables.
pub struct Quantification {
    quant_type: QuantType,
    quantees: Quantees,
    sub_formula: Formula,
    vocab: Option<RcA<Vocabulary>>,
    metadata: Option<Box<Metadata>>,
}

impl Clone for Quantification {
    fn clone(&self) -> Self {
        Self {
            quant_type: self.quant_type,
            quantees: self.quantees.duplicate(),
            sub_formula: self.sub_formula.clone(),
            vocab: self.vocab.clone(),
            metadata: self.metadata.clone(),
        }
    }
}

impl FodotOptions for Quantification {
    type Options<'a>
        = FormatOptions
    where
        Self: 'a;
}

impl FodotDisplay for Quantification {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        match fmt.value.quant_type {
            QuantType::Existential => fmt.options.write_ex_quant(f),
            QuantType::Universal => fmt.options.write_uni_quant(f),
        }?;
        write!(
            f,
            "{}: {}",
            fmt.with_format_opts(&fmt.value.quantees),
            fmt.with_format_opts(&fmt.value.sub_formula),
        )
    }
}

impl Display for Quantification {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", Fmt::with_defaults(self))
    }
}

display_as_debug!(Quantification);

impl PartialEq for Quantification {
    fn eq(&self, other: &Self) -> bool {
        self.quant_type == other.quant_type
            && self.quantees == other.quantees
            && self.sub_formula == other.sub_formula
    }
}

impl Eq for Quantification {}

impl Quantification {
    pub fn new(
        quant_type: QuantType,
        quantees: Quantees,
        sub_formula: Formula,
    ) -> Result<Self, VocabMismatchError> {
        let mut vocab_checker = VocabIterCheck::new(quantees.iter_decls().map(|f| f.vocab_rc()));
        if !vocab_checker.check_if_consistent() {
            return Err(VocabMismatchError);
        }
        let vocab = vocab_checker.take_vocab();
        if !vocabs_ptr_eq(vocab.map(|f| f.as_ref()), sub_formula.vocab()) {
            return Err(VocabMismatchError);
        }
        let vocab = vocab.or(sub_formula.vocab_rc()).cloned();

        Ok(Self {
            quant_type,
            quantees,
            sub_formula,
            vocab,
            metadata: Default::default(),
        })
    }

    pub fn vocab_rc(&self) -> Option<&RcA<Vocabulary>> {
        self.vocab.as_ref()
    }

    pub fn codomain(&self) -> TypeRef {
        Type::Bool
    }

    pub fn iter_variables(&self) -> impl SIterator<Item = &VariableBinder> {
        self.quantees.iter()
    }

    pub fn quant_type(&self) -> QuantType {
        self.quant_type
    }

    pub fn quantees(&self) -> &Quantees {
        &self.quantees
    }

    pub fn subformula(&self) -> &Formula {
        &self.sub_formula
    }

    pub fn collect_wdcs(&self) -> Vec<WellDefinedCondition> {
        self.sub_formula.collect_wdcs()
    }
}

impl FreeVariables for Quantification {
    fn add_to_free_variable_iter<'a>(&'a self, iter: &mut FreeVariableIter<'a>) {
        iter.add_quantees(self.quantees());
        iter.add_expr(self.subformula().into());
    }
}

impl MetadataIm for Quantification {
    type Metadata = Metadata;
    fn metadata(&self) -> Option<&Metadata> {
        self.metadata.as_deref()
    }
}

impl MetadataMut for Quantification {
    fn metadata_mut(&mut self) -> &mut Metadata {
        self.metadata.get_or_insert_default()
    }
}
