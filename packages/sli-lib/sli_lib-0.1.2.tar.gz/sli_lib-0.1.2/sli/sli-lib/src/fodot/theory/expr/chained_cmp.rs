use super::{
    BinOps, CmpBinOps, EqualityBinOps, Expr, FreeVariableIter, FreeVariables, Metadata, MetadataIm,
    MetadataMut, WellDefinedCondition, vocabs_ptr_eq,
};
use crate::fodot::display_as_debug;
use crate::fodot::error::{
    ExprSubMismatchError, SubTypeMismatch, TypeMismatch, VocabMismatchError,
};
use crate::fodot::fmt::{Fmt, FodotDisplay, FormatOptions};
use crate::fodot::fmt::{FodotOptions, display_fn};
use crate::fodot::vocabulary::{TypeRef, TypeStr, Vocabulary};
use itertools::Itertools;
use sli_collections::{
    iterator::Iterator as SIterator,
    rc::{Rc, RcA},
};
use std::fmt::{Debug, Display, Write};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum OrdOps {
    Equal,
    NotEqual,
    LessThan,
    LessOrEqual,
    GreaterThan,
    GreaterOrEqual,
}

impl FodotOptions for OrdOps {
    type Options<'a>
        = FormatOptions
    where
        Self: 'a;
}

impl FodotDisplay for OrdOps {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        match fmt.value {
            Self::Equal => write!(f, "="),
            Self::NotEqual => fmt.options.write_neq(f),
            Self::LessThan => f.write_char('<'),
            Self::LessOrEqual => fmt.options.write_le(f),
            Self::GreaterThan => f.write_char('>'),
            Self::GreaterOrEqual => fmt.options.write_ge(f),
        }
    }
}

impl Display for OrdOps {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", Fmt::with_defaults(self))
    }
}

impl TryFrom<BinOps> for OrdOps {
    type Error = ();

    fn try_from(value: BinOps) -> Result<Self, Self::Error> {
        match value {
            BinOps::Equal => Ok(Self::Equal),
            BinOps::NotEqual => Ok(Self::NotEqual),
            BinOps::LessThan => Ok(Self::LessThan),
            BinOps::LessOrEqual => Ok(Self::LessOrEqual),
            BinOps::GreaterThan => Ok(Self::GreaterThan),
            BinOps::GreaterOrEqual => Ok(Self::GreaterOrEqual),
            _ => Err(()),
        }
    }
}

impl From<EqualityBinOps> for OrdOps {
    fn from(value: EqualityBinOps) -> Self {
        match value {
            EqualityBinOps::Equal => Self::Equal,
            EqualityBinOps::NotEqual => Self::NotEqual,
        }
    }
}

impl From<CmpBinOps> for OrdOps {
    fn from(value: CmpBinOps) -> Self {
        match value {
            CmpBinOps::LessThan => Self::LessThan,
            CmpBinOps::LessOrEqual => Self::LessOrEqual,
            CmpBinOps::GreaterThan => Self::GreaterThan,
            CmpBinOps::GreaterOrEqual => Self::GreaterOrEqual,
        }
    }
}

/// A chaining comparison operator.
pub struct ChainedCmp {
    first_value: Expr,
    rest: Vec<(OrdOps, Expr)>,
    vocab: Option<RcA<Vocabulary>>,
    metadata: Option<Box<Metadata>>,
}

impl FodotOptions for ChainedCmp {
    type Options<'a>
        = FormatOptions
    where
        Self: 'a;
}

impl FodotDisplay for ChainedCmp {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        write!(f, "{} ", fmt.with_opts(&fmt.value.first_value))?;
        write!(
            f,
            "{}",
            fmt.value
                .rest
                .iter()
                .map(|value| display_fn(|f| write!(
                    f,
                    "{} {}",
                    fmt.with_opts(&value.0),
                    fmt.with_opts(&value.1)
                )))
                .format(" ")
        )
    }
}

impl Display for ChainedCmp {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", Fmt::with_defaults(self))
    }
}

display_as_debug!(ChainedCmp);

impl PartialEq for ChainedCmp {
    fn eq(&self, other: &Self) -> bool {
        self.first_value == other.first_value && self.rest == other.rest
    }
}

impl Eq for ChainedCmp {}

impl From<ChainedCmp> for Expr {
    fn from(value: ChainedCmp) -> Self {
        Self::ChainedCmp(value.into())
    }
}

impl From<Rc<ChainedCmp>> for Expr {
    fn from(value: Rc<ChainedCmp>) -> Self {
        Self::ChainedCmp(value)
    }
}

impl ChainedCmp {
    pub fn new(lhs: Expr, op: OrdOps, rhs: Expr) -> Result<Self, ExprSubMismatchError> {
        Self::check_expr(&lhs, op, &rhs)?;
        let vocab = lhs.vocab_rc().or_else(|| rhs.vocab_rc()).cloned();
        Ok(Self {
            first_value: lhs,
            rest: vec![(op, rhs)],
            vocab,
            metadata: None,
        })
    }

    pub(super) fn check_expr(
        lhs: &Expr,
        op: OrdOps,
        rhs: &Expr,
    ) -> Result<(), ExprSubMismatchError> {
        if !vocabs_ptr_eq(lhs.vocab(), rhs.vocab()) {
            return Err(VocabMismatchError.into());
        }
        match op {
            OrdOps::LessThan
            | OrdOps::LessOrEqual
            | OrdOps::GreaterThan
            | OrdOps::GreaterOrEqual => {
                if !lhs.codomain().is_subtype(&TypeRef::Real) {
                    return Err(SubTypeMismatch {
                        found: lhs.codomain().into_root_type().into(),
                        expected: TypeStr::Real,
                    }
                    .into());
                } else if !rhs.codomain().is_subtype(&TypeRef::Real) {
                    return Err(SubTypeMismatch {
                        found: rhs.codomain().into_root_type().into(),
                        expected: TypeStr::Real,
                    }
                    .into());
                }
            }
            OrdOps::Equal | OrdOps::NotEqual => {
                if lhs.codomain().into_root_type() != rhs.codomain().into_root_type() {
                    return Err(TypeMismatch {
                        found: lhs.codomain().into_root_type().into(),
                        expected: rhs.codomain().into_root_type().into(),
                    }
                    .into());
                }
            }
        }
        Ok(())
    }

    pub fn first(&self) -> (&Expr, OrdOps, &Expr) {
        let first = self.rest.first().unwrap();
        (&self.first_value, first.0, &first.1)
    }

    pub fn cur_value(&self) -> &Expr {
        self.rest.last().map(|f| &f.1).unwrap_or(&self.first_value)
    }

    pub fn add_op(&mut self, op: OrdOps, rhs: Expr) -> Result<(), ExprSubMismatchError> {
        Self::check_expr(self.cur_value(), op, &rhs)?;
        self.vocab = self.vocab.take().or(rhs.vocab_rc().cloned());
        self.rest.push((op, rhs));
        Ok(())
    }

    pub fn iter(&self) -> Iter {
        Iter::new(self)
    }

    pub fn iter_exprs(&self) -> impl SIterator<Item = &Expr> {
        core::iter::once(&self.first_value).chain(self.rest.iter().map(|f| &f.1))
    }

    pub fn codomain(&self) -> TypeRef {
        TypeRef::Bool
    }

    pub fn collect_wdcs(&self) -> Vec<WellDefinedCondition> {
        self.iter_exprs().flat_map(|f| f.collect_wdcs()).collect()
    }

    /// Returns the corresponding [Vocabulary] as `&RcA<Vocabulary>`.
    pub fn vocab_rc(&self) -> Option<&RcA<Vocabulary>> {
        self.vocab.as_ref()
    }

    pub fn vocab(&self) -> Option<&Vocabulary> {
        self.vocab.as_deref()
    }
}

impl FreeVariables for ChainedCmp {
    fn add_to_free_variable_iter<'a>(&'a self, iter: &mut FreeVariableIter<'a>) {
        for value in self.iter_exprs() {
            iter.add_expr(value.into());
        }
    }
}

impl MetadataIm for ChainedCmp {
    type Metadata = Metadata;
    fn metadata(&self) -> Option<&Metadata> {
        self.metadata.as_deref()
    }
}

impl MetadataMut for ChainedCmp {
    fn metadata_mut(&mut self) -> &mut Metadata {
        self.metadata.get_or_insert_default()
    }
}

pub struct Iter<'a> {
    cur: &'a Expr,
    rest: core::slice::Iter<'a, (OrdOps, Expr)>,
}

impl<'a> Iter<'a> {
    fn new(chained_cmp: &'a ChainedCmp) -> Self {
        Self {
            cur: &chained_cmp.first_value,
            rest: chained_cmp.rest.iter(),
        }
    }
}

impl<'a> Iterator for Iter<'a> {
    type Item = (&'a Expr, OrdOps, &'a Expr);

    fn next(&mut self) -> Option<Self::Item> {
        let cur_rest = self.rest.next()?;
        let ret = (self.cur, cur_rest.0, &cur_rest.1);
        self.cur = &cur_rest.1;
        Some(ret)
    }
}
