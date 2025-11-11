use super::{
    Formula, FreeVariableIter, FreeVariables, Metadata, MetadataIm, MetadataMut,
    WellDefinedCondition,
};
use crate::fodot::display_as_debug;
use crate::fodot::fmt::{FodotOptions, FodotPrecDisplay};
use crate::fodot::{
    fmt::{Fmt, FodotDisplay, FormatOptions},
    vocabulary::{Type, TypeRef, Vocabulary},
};
use sli_collections::rc::RcA;
use std::fmt::{Display, Write};

/// Represents a negation.
#[derive(Clone)]
pub struct Negation {
    subformula: Formula,
    metadata: Option<Box<Metadata>>,
}

impl FodotOptions for Negation {
    type Options<'a>
        = FormatOptions
    where
        Self: 'a;
}

impl FodotDisplay for Negation {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        FodotPrecDisplay::fmt_with_prec(fmt, f, 0)
    }
}

impl FodotPrecDisplay for Negation {
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
        fmt.options.write_neg(f)?;
        write!(
            f,
            "{}",
            fmt.with_format_opts(&fmt.value.subformula)
                .with_prec(this_prec)
        )?;
        if needs_bracket {
            f.write_char(')')?;
        }
        Ok(())
    }
}

impl Display for Negation {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", Fmt::with_defaults(self))
    }
}

display_as_debug!(Negation);

impl PartialEq for Negation {
    fn eq(&self, other: &Self) -> bool {
        self.subformula == other.subformula
    }
}

impl Eq for Negation {}

impl Negation {
    /// Try to negate the given subformula.
    pub fn new(subformula: Formula) -> Self {
        Self {
            subformula,
            metadata: Default::default(),
        }
    }

    pub fn precedence(&self) -> u32 {
        80
    }

    pub fn codomain(&self) -> TypeRef {
        Type::Bool
    }

    pub fn vocab_rc(&self) -> Option<&RcA<Vocabulary>> {
        self.subformula.vocab_rc()
    }

    /// Returns the given subformula.
    pub fn subformula(&self) -> &Formula {
        &self.subformula
    }

    pub fn collect_wdcs(&self) -> Vec<WellDefinedCondition> {
        self.subformula.collect_wdcs()
    }
}

impl FreeVariables for Negation {
    fn add_to_free_variable_iter<'a>(&'a self, iter: &mut FreeVariableIter<'a>) {
        iter.add_expr(self.subformula().into());
    }
}

impl MetadataIm for Negation {
    type Metadata = Metadata;
    fn metadata(&self) -> Option<&Metadata> {
        self.metadata.as_deref()
    }
}

impl MetadataMut for Negation {
    fn metadata_mut(&mut self) -> &mut Metadata {
        self.metadata.get_or_insert_default()
    }
}
