use super::{
    Expr, Formula, FreeVariableIter, FreeVariables, Metadata, MetadataIm, MetadataMut, Quantees,
    VariableBinder, VocabIterCheck, WellDefinedCondition, vocabs_ptr_eq,
};
use crate::fodot::display_as_debug;
use crate::fodot::error::{ExprSubMismatchError, SubTypeMismatch, VocabMismatchError};
use crate::fodot::fmt::FodotOptions;
use crate::fodot::{
    fmt::{Fmt, FodotDisplay, FormatOptions},
    vocabulary::{Type, TypeRef, Vocabulary},
};
use sli_collections::{iterator::Iterator as SIterator, rc::RcA};
use std::fmt::Display;

/// Types of aggregates.
///
/// A cardinality aggregate is not in this list, See
/// [CardinalityAggregate](super::CardinalityAggregate).
#[non_exhaustive]
#[derive(Clone, Copy, PartialEq, Eq)]
pub enum AggType {
    Sum,
    // TODO:
    // Maximum,
    // Minimum,
}

/// An aggregate, the type of aggregate is decided by [AggType].
pub struct Aggregate {
    agg_type: AggType,
    quantees: Quantees,
    term: Expr,
    formula: Formula,
    vocab: Option<RcA<Vocabulary>>,
    metadata: Option<Box<Metadata>>,
}

impl Clone for Aggregate {
    fn clone(&self) -> Self {
        Self {
            agg_type: self.agg_type,
            quantees: self.quantees.duplicate(),
            term: self.term.clone(),
            formula: self.formula.clone(),
            vocab: self.vocab.clone(),
            metadata: self.metadata.clone(),
        }
    }
}

impl FodotOptions for Aggregate {
    type Options<'a>
        = FormatOptions
    where
        Self: 'a;
}

impl FodotDisplay for Aggregate {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        match fmt.value.agg_type {
            AggType::Sum => f.write_str("sum{{ "),
        }?;
        write!(
            f,
            "{} | {}: {}",
            fmt.with_format_opts(&fmt.value.term),
            fmt.with_format_opts(&fmt.value.quantees),
            fmt.with_format_opts(&fmt.value.formula),
        )?;
        match fmt.value.agg_type {
            AggType::Sum => f.write_str(" }}"),
        }
    }
}

impl Display for Aggregate {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

display_as_debug!(Aggregate);

impl PartialEq for Aggregate {
    fn eq(&self, other: &Self) -> bool {
        self.agg_type == other.agg_type
            && self.quantees == other.quantees
            && self.term == other.term
            && self.formula == other.formula
    }
}

impl Eq for Aggregate {}

impl Aggregate {
    pub fn new(
        agg_type: AggType,
        quantees: Quantees,
        term: Expr,
        formula: Formula,
    ) -> Result<Self, ExprSubMismatchError> {
        let mut vocab_checker = VocabIterCheck::new(quantees.iter().map(|f| f.vocab_rc()));
        if !vocab_checker.check_if_consistent() {
            return Err(VocabMismatchError.into());
        }
        let vocab = vocab_checker.take_vocab();
        if !vocabs_ptr_eq(vocab.map(|f| f.as_ref()), term.vocab())
            || !vocabs_ptr_eq(vocab.map(|f| f.as_ref()), formula.vocab())
        {
            return Err(VocabMismatchError.into());
        }
        let vocab = vocab.or(term.vocab_rc()).or(formula.vocab_rc()).cloned();

        match (agg_type, term.codomain()) {
            (AggType::Sum, codomain) if codomain.is_subtype(&TypeRef::Real) => {}
            (AggType::Sum, codomain) => {
                return Err(SubTypeMismatch {
                    found: codomain.into(),
                    expected: TypeRef::Real.into(),
                }
                .into());
            }
        }

        Ok(Self {
            agg_type,
            quantees,
            term,
            formula,
            vocab,
            metadata: Default::default(),
        })
    }

    pub fn vocab_rc(&self) -> Option<&RcA<Vocabulary>> {
        self.vocab.as_ref()
    }

    pub fn quantees(&self) -> &Quantees {
        &self.quantees
    }

    pub fn codomain(&self) -> TypeRef {
        match self.agg_type {
            AggType::Sum => match self.term.codomain() {
                Type::Int => Type::Int,
                Type::Real => Type::Real,
                Type::IntType(_) => Type::Int,
                Type::RealType(_) => Type::Real,
                _ => unreachable!(),
            },
        }
    }

    /// Returns the term of the aggregate.
    ///
    /// i.e. the expression to the left of the '|'.
    pub fn term(&self) -> &Expr {
        &self.term
    }

    /// Returns the formula of the aggregate.
    ///
    /// i.e. the expression to the right of the quantification.
    pub fn formula(&self) -> &Formula {
        &self.formula
    }

    pub fn agg_type(&self) -> AggType {
        self.agg_type
    }

    pub fn iter_variables(&self) -> impl SIterator<Item = &VariableBinder> {
        self.quantees.iter()
    }

    pub fn collect_wdcs(&self) -> Vec<WellDefinedCondition> {
        self.formula
            .collect_wdcs()
            .into_iter()
            .chain(self.term.collect_wdcs().into_iter())
            .collect()
    }
}

impl FreeVariables for Aggregate {
    fn add_to_free_variable_iter<'a>(&'a self, iter: &mut FreeVariableIter<'a>) {
        iter.add_quantees(self.quantees());
        iter.add_expr(self.term().into());
        iter.add_expr(self.formula().into());
    }
}

impl MetadataIm for Aggregate {
    type Metadata = Metadata;
    fn metadata(&self) -> Option<&Metadata> {
        self.metadata.as_deref()
    }
}

impl MetadataMut for Aggregate {
    fn metadata_mut(&mut self) -> &mut Metadata {
        self.metadata.get_or_insert_default()
    }
}
