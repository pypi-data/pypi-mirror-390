use super::{
    Expr, FreeVariableIter, FreeVariables, Metadata, MetadataIm, MetadataMut, VocabIterCheck,
    WellDefinedCondition,
};
use crate::fodot::display_as_debug;
use crate::fodot::error::{ExprSubMismatchError, SubTypeMismatch, VocabMismatchError};
use crate::fodot::fmt::{FodotOptions, FodotPrecDisplay};
use crate::fodot::{
    fmt::{Fmt, FodotDisplay, FormatOptions},
    vocabulary::{Type, TypeRef, Vocabulary},
};
use itertools::Itertools;
use sli_collections::{iterator::Iterator as SIterator, rc::RcA};
use std::fmt::{Display, Write};

#[derive(Clone)]
pub struct InEnumeration {
    expr: Expr,
    enumeration: Box<[Expr]>,
    metadata: Option<Box<Metadata>>,
    vocab: Option<RcA<Vocabulary>>,
}

impl PartialEq for InEnumeration {
    fn eq(&self, other: &Self) -> bool {
        self.expr == other.expr && self.enumeration == other.enumeration
    }
}

impl Eq for InEnumeration {}

impl FodotOptions for InEnumeration {
    type Options<'a> = FormatOptions;
}

impl FodotDisplay for InEnumeration {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        FodotPrecDisplay::fmt_with_prec(fmt, f, 0)
    }
}

impl FodotPrecDisplay for InEnumeration {
    fn fmt_with_prec(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
        super_prec: u32,
    ) -> std::fmt::Result {
        let this_prec = fmt.value.precedence();
        let needs_bracket = super_prec > this_prec;
        if needs_bracket {
            f.write_char('(')?;
        }
        write!(
            f,
            "{} ",
            fmt.with_opts(&fmt.value.expr).with_prec(this_prec)
        )?;
        if needs_bracket {
            f.write_char(')')?;
        }
        fmt.options.write_in(f)?;
        f.write_char(' ')?;
        write!(
            f,
            "{{{}}}",
            fmt.value
                .enumeration
                .iter()
                .map(|f| fmt.with_opts(f))
                .format(", ")
        )
    }
}

impl Display for InEnumeration {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

display_as_debug!(InEnumeration);

impl MetadataIm for InEnumeration {
    type Metadata = Metadata;
    fn metadata(&self) -> Option<&Metadata> {
        self.metadata.as_deref()
    }
}

impl MetadataMut for InEnumeration {
    fn metadata_mut(&mut self) -> &mut Metadata {
        self.metadata.get_or_insert_default()
    }
}

impl FreeVariables for InEnumeration {
    fn add_to_free_variable_iter<'a>(&'a self, iter: &mut FreeVariableIter<'a>) {
        iter.add_expr(self.expr().into());
        for enume in self.enumeration.iter() {
            iter.add_expr(enume.into());
        }
    }
}

impl InEnumeration {
    pub fn new(expr: Expr, enumeration: Vec<Expr>) -> Result<Self, ExprSubMismatchError> {
        let mut vocab_checker = VocabIterCheck::new(
            enumeration
                .iter()
                .map(|f| f.vocab_rc())
                .chain(core::iter::once(expr.vocab_rc())),
        );
        if !vocab_checker.check_if_consistent() {
            return Err(VocabMismatchError.into());
        }
        let vocab = vocab_checker.take_vocab().cloned();
        let expected_root = expr.codomain().into_root_type();
        for enume in enumeration.iter() {
            let found = enume.codomain().into_root_type();
            if found != expected_root {
                return Err(SubTypeMismatch {
                    found: found.into(),
                    expected: expected_root.into(),
                }
                .into());
            }
        }
        Ok(Self {
            expr,
            enumeration: enumeration.into_boxed_slice(),
            metadata: Default::default(),
            vocab,
        })
    }

    pub fn precedence(&self) -> u32 {
        40
    }

    pub fn expr(&self) -> &Expr {
        &self.expr
    }

    pub fn enumeration(&self) -> impl SIterator<Item = &Expr> + ExactSizeIterator {
        self.enumeration.iter()
    }

    pub fn vocab_rc(&self) -> Option<&RcA<Vocabulary>> {
        self.vocab.as_ref()
    }

    pub fn codomain(&self) -> TypeRef {
        Type::Bool
    }

    pub fn collect_wdcs(&self) -> Vec<WellDefinedCondition> {
        self.expr
            .collect_wdcs()
            .into_iter()
            .chain(self.enumeration.iter().flat_map(|f| f.collect_wdcs()))
            .collect()
    }
}
