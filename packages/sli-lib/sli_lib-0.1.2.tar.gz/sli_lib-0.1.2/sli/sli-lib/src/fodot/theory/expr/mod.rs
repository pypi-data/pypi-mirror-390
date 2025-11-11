use crate::ast::Span;
use crate::fodot::display_as_debug;
use crate::fodot::error::{
    IsADefinitionError, NotABoolElementError, NotAnElementError, ParsePrimitiveElementError,
};
use crate::fodot::fmt::{FodotOptions, FodotPrecDisplay};
use crate::fodot::{Metadata, MetadataIm, MetadataMut};
use crate::fodot::{
    fmt::{Fmt, FodotDisplay, FormatOptions},
    vocabulary::{Type, TypeRef, Vocabulary, parse_bool_value, parse_int_value, parse_real_value},
};
use comp_core::{Int, Real, node::ElementNode, structure::TypeElement as CCTypeElement};
use sli_collections::rc::{Rc, RcA};
use std::{
    fmt::{Debug, Display},
    str::FromStr,
};

mod aggregate;
mod applied_symbol;
mod assertion;
mod bin_op;
mod cardinality_aggregate;
mod chained_cmp;
mod definition;
mod formula;
mod guards;
mod in_enumeration;
mod is_enumerated;
mod ite;
mod negation;
mod num_negation;
mod quantification;
mod variables;
mod well_defined_expression;

pub use aggregate::*;
pub use applied_symbol::*;
pub use assertion::*;
pub use bin_op::*;
pub use cardinality_aggregate::*;
pub use chained_cmp::*;
pub use definition::*;
pub use formula::*;
pub use guards::*;
pub use in_enumeration::*;
pub use is_enumerated::*;
pub use ite::*;
pub use negation::*;
pub use num_negation::*;
pub use quantification::*;
pub use variables::*;
pub use well_defined_expression::*;

/// Compares 2 [Option] wrapped vocabulary references for if they point to the same vocabulary.
///
/// If 1 or none of the options are the [Some] variant true is always returned.
pub(crate) fn vocabs_ptr_eq(vocab1: Option<&Vocabulary>, vocab2: Option<&Vocabulary>) -> bool {
    vocab1
        .and_then(|f1| vocab2.map(|f2| f1.exact_eq(f2)))
        .unwrap_or(true)
}

pub(crate) struct VocabIterCheck<'a, T: Iterator<Item = Option<&'a RcA<Vocabulary>>>> {
    iter: T,
    value: Option<&'a RcA<Vocabulary>>,
}

impl<'a, T: Iterator<Item = Option<&'a RcA<Vocabulary>>>> VocabIterCheck<'a, T> {
    pub(crate) fn new(iter: T) -> Self {
        Self { iter, value: None }
    }

    pub(crate) fn take_vocab(self) -> Option<&'a RcA<Vocabulary>> {
        self.value
    }

    pub(crate) fn check_if_consistent(&mut self) -> bool {
        let mut ok = true;
        let mut new_value: Option<&'a RcA<Vocabulary>> = None;
        for pot_vocab in &mut self.iter {
            if let &Some(vocab) = &new_value {
                ok &= vocabs_ptr_eq(Some(vocab.as_ref()), pot_vocab.map(|f| f.as_ref()));
            } else {
                new_value = pot_vocab;
            }
            if !ok {
                break;
            }
        }
        self.value = new_value;
        return ok;
    }
}

impl TryFrom<Expr> for Element {
    type Error = NotAnElementError;

    fn try_from(value: Expr) -> Result<Self, Self::Error> {
        Element::try_from(&value)
    }
}

impl<'a> TryFrom<&'a Expr> for Element {
    type Error = NotAnElementError;

    fn try_from(value: &'a Expr) -> Result<Self, Self::Error> {
        match value {
            Expr::Element(el) => Ok(el.element.clone()),
            _ => Err(NotAnElementError),
        }
    }
}

/// Represents an FO(·) expression.
#[non_exhaustive]
#[derive(Clone, PartialEq, Eq)]
pub enum Expr {
    AppliedSymbol(Rc<AppliedSymbol>),
    BinOp(BinOp),
    ChainedCmp(Rc<ChainedCmp>),
    Negation(Rc<Negation>),
    NumNegation(Rc<NumNegation>),
    Quantification(Rc<Quantification>),
    CardinalityAggregate(Rc<CardinalityAggregate>),
    Aggregate(Rc<Aggregate>),
    Ite(Rc<Ite>),
    Element(Rc<ElementExpr>),
    Variable(Rc<Variable>),
    InEnumeration(Rc<InEnumeration>),
    ConjuctiveGuard(Rc<ConjuctiveGuard>),
    ImplicativeGuard(Rc<ImplicativeGuard>),
    IfGuard(Rc<IfGuard>),
    IsEnumerated(Rc<IsEnumerated>),
}

impl FodotOptions for Expr {
    type Options<'a>
        = FormatOptions
    where
        Self: 'a;
}

impl FodotDisplay for Expr {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        FodotDisplay::fmt(fmt.with_opts(&ExprRef::from(fmt.value)), f)
    }
}

impl FodotPrecDisplay for Expr {
    fn fmt_with_prec(
        fmt: Fmt<&Self, <Self as FodotOptions>::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
        super_prec: u32,
    ) -> std::fmt::Result {
        FodotPrecDisplay::fmt_with_prec(fmt.with_opts(&ExprRef::from(fmt.value)), f, super_prec)
    }
}

impl Display for Expr {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

impl FreeVariables for Expr {
    fn add_to_free_variable_iter<'a>(&'a self, iter: &mut FreeVariableIter<'a>) {
        iter.add_expr(self.into())
    }
}

display_as_debug!(Expr);

impl From<AppliedSymbol> for Expr {
    fn from(value: AppliedSymbol) -> Self {
        Self::AppliedSymbol(value.into())
    }
}

impl From<Rc<AppliedSymbol>> for Expr {
    fn from(value: Rc<AppliedSymbol>) -> Self {
        Self::AppliedSymbol(value)
    }
}

impl From<BinOp> for Expr {
    fn from(value: BinOp) -> Self {
        Self::BinOp(value)
    }
}

impl From<Negation> for Expr {
    fn from(value: Negation) -> Self {
        Self::Negation(value.into())
    }
}

impl From<Rc<Negation>> for Expr {
    fn from(value: Rc<Negation>) -> Self {
        Self::Negation(value)
    }
}

impl From<NumNegation> for Expr {
    fn from(value: NumNegation) -> Self {
        Self::NumNegation(value.into())
    }
}

impl From<Rc<NumNegation>> for Expr {
    fn from(value: Rc<NumNegation>) -> Self {
        Self::NumNegation(value)
    }
}

impl From<Quantification> for Expr {
    fn from(value: Quantification) -> Self {
        Self::Quantification(value.into())
    }
}

impl From<Rc<Quantification>> for Expr {
    fn from(value: Rc<Quantification>) -> Self {
        Self::Quantification(value)
    }
}

impl From<Aggregate> for Expr {
    fn from(value: Aggregate) -> Self {
        Self::Aggregate(value.into())
    }
}

impl From<Rc<Aggregate>> for Expr {
    fn from(value: Rc<Aggregate>) -> Self {
        Self::Aggregate(value)
    }
}

impl From<CardinalityAggregate> for Expr {
    fn from(value: CardinalityAggregate) -> Self {
        Self::CardinalityAggregate(value.into())
    }
}

impl From<Rc<CardinalityAggregate>> for Expr {
    fn from(value: Rc<CardinalityAggregate>) -> Self {
        Self::CardinalityAggregate(value)
    }
}

impl From<Ite> for Expr {
    fn from(value: Ite) -> Self {
        Self::Ite(value.into())
    }
}

impl From<Rc<Ite>> for Expr {
    fn from(value: Rc<Ite>) -> Self {
        Self::Ite(value)
    }
}

impl From<ElementExpr> for Expr {
    fn from(value: ElementExpr) -> Self {
        Self::Element(value.into())
    }
}

impl From<Rc<ElementExpr>> for Expr {
    fn from(value: Rc<ElementExpr>) -> Self {
        Self::Element(value)
    }
}

impl From<Rc<InEnumeration>> for Expr {
    fn from(value: Rc<InEnumeration>) -> Self {
        Self::InEnumeration(value)
    }
}

impl From<ConjuctiveGuard> for Expr {
    fn from(value: ConjuctiveGuard) -> Self {
        Self::ConjuctiveGuard(value.into())
    }
}

impl From<Rc<ConjuctiveGuard>> for Expr {
    fn from(value: Rc<ConjuctiveGuard>) -> Self {
        Self::ConjuctiveGuard(value)
    }
}

impl From<ImplicativeGuard> for Expr {
    fn from(value: ImplicativeGuard) -> Self {
        Self::ImplicativeGuard(value.into())
    }
}

impl From<Rc<ImplicativeGuard>> for Expr {
    fn from(value: Rc<ImplicativeGuard>) -> Self {
        Self::ImplicativeGuard(value)
    }
}

impl From<IfGuard> for Expr {
    fn from(value: IfGuard) -> Self {
        Self::IfGuard(value.into())
    }
}

impl From<Rc<IfGuard>> for Expr {
    fn from(value: Rc<IfGuard>) -> Self {
        Self::IfGuard(value)
    }
}

impl From<IsEnumerated> for Expr {
    fn from(value: IsEnumerated) -> Self {
        Self::IsEnumerated(value.into())
    }
}

impl From<Rc<IsEnumerated>> for Expr {
    fn from(value: Rc<IsEnumerated>) -> Self {
        Self::IsEnumerated(value)
    }
}

impl From<Element> for Expr {
    fn from(value: Element) -> Self {
        Self::Element(ElementExpr::from(value).into())
    }
}

impl From<Variable> for Expr {
    fn from(value: Variable) -> Self {
        Self::Variable(value.into())
    }
}

impl From<Rc<Variable>> for Expr {
    fn from(value: Rc<Variable>) -> Self {
        Self::Variable(value)
    }
}

impl From<Rc<BoolExpr>> for Expr {
    fn from(value: Rc<BoolExpr>) -> Self {
        Element::Bool(value.value).into()
    }
}

impl From<bool> for Expr {
    fn from(value: bool) -> Self {
        Element::Bool(value).into()
    }
}

impl From<Int> for Expr {
    fn from(value: Int) -> Self {
        Element::Int(value).into()
    }
}

impl From<Real> for Expr {
    fn from(value: Real) -> Self {
        Element::Real(value).into()
    }
}

impl From<InEnumeration> for Expr {
    fn from(value: InEnumeration) -> Self {
        Expr::InEnumeration(value.into())
    }
}

impl TryFrom<Assertion> for Expr {
    type Error = IsADefinitionError;

    fn try_from(value: Assertion) -> Result<Self, Self::Error> {
        match value {
            Assertion::Bool(value) => Ok(value.into()),
            Assertion::AppliedSymbol(value) => Ok(value.into()),
            Assertion::Quantification(value) => Ok(value.into()),
            Assertion::Negation(value) => Ok(value.into()),
            Assertion::BinOp(value) => Ok(value.into()),
            Assertion::ChainedCmp(value) => Ok(value.into()),
            Assertion::Ite(value) => Ok(value.into()),
            Assertion::Definition(_) => Err(IsADefinitionError),
            Assertion::ConjuctiveGuard(value) => Ok(value.into()),
            Assertion::ImplicativeGuard(value) => Ok(value.into()),
            Assertion::IfGuard(value) => Ok(value.into()),
            Assertion::IsEnumerated(value) => Ok(value.into()),
            Assertion::InEnumeration(value) => Ok(value.into()),
        }
    }
}

impl PartialEq<VariableDeclRef> for Expr {
    fn eq(&self, other: &VariableDeclRef) -> bool {
        match self {
            Self::Variable(var) => var.as_ref() == other,
            _ => false,
        }
    }
}

impl<'a> From<&'a Expr> for ExprRef<'a> {
    fn from(value: &'a Expr) -> Self {
        match value {
            Expr::AppliedSymbol(value) => Self::AppliedSymbol(value),
            Expr::BinOp(value) => Self::BinOp(value.into()),
            Expr::ChainedCmp(value) => Self::ChainedCmp(value),
            Expr::Negation(value) => Self::Negation(value),
            Expr::NumNegation(value) => Self::NumNegation(value),
            Expr::Quantification(value) => Self::Quantification(value),
            Expr::CardinalityAggregate(value) => Self::CardinalityAggregate(value),
            Expr::Aggregate(value) => Self::Aggregate(value),
            Expr::Ite(value) => Self::Ite(value),
            Expr::Element(value) => Self::Element(value),
            Expr::Variable(value) => Self::Variable(value),
            Expr::InEnumeration(value) => Self::InEnumeration(value),
            Expr::ConjuctiveGuard(value) => Self::ConjuctiveGuard(value),
            Expr::ImplicativeGuard(value) => Self::ImplicativeGuard(value),
            Expr::IfGuard(value) => Self::IfGuard(value),
            Expr::IsEnumerated(value) => Self::IsEnumerated(value),
        }
    }
}

impl PartialEq<ExprRef<'_>> for Expr {
    fn eq(&self, other: &ExprRef<'_>) -> bool {
        use Expr as E;
        use ExprRef as ER;
        match (self, other) {
            (E::AppliedSymbol(value1), ER::AppliedSymbol(value2)) => value1 == *value2,
            (E::BinOp(value1), ER::BinOp(value2)) => value1 == value2,
            (E::ChainedCmp(value1), ER::ChainedCmp(value2)) => value1 == *value2,
            (E::Quantification(value1), ER::Quantification(value2)) => value1 == *value2,
            (E::CardinalityAggregate(value1), ER::CardinalityAggregate(value2)) => {
                value1 == *value2
            }
            (E::Aggregate(value1), ER::Aggregate(value2)) => value1 == *value2,
            (E::Ite(value1), ER::Ite(value2)) => value1 == *value2,
            (E::Element(value1), ER::Element(value2)) => value1 == *value2,
            (E::Element(value1), ER::Bool(value2)) => value1.as_ref() == value2.as_ref(),
            (E::Variable(value1), ER::Variable(value2)) => value1 == *value2,
            (E::InEnumeration(value1), ER::InEnumeration(value2)) => value1 == *value2,
            (E::ConjuctiveGuard(value1), ER::ConjuctiveGuard(value2)) => value1 == *value2,
            (E::ImplicativeGuard(value1), ER::ImplicativeGuard(value2)) => value1 == *value2,
            (E::IfGuard(value1), ER::IfGuard(value2)) => value1 == *value2,
            (E::IsEnumerated(value1), ER::IsEnumerated(value2)) => value1 == *value2,
            _ => false,
        }
    }
}

impl Expr {
    pub fn vocab(&self) -> Option<&Vocabulary> {
        self.vocab_rc().map(|f| f.as_ref())
    }

    pub fn vocab_rc(&self) -> Option<&RcA<Vocabulary>> {
        match self {
            Self::AppliedSymbol(value) => value.vocab_rc(),
            Self::BinOp(value) => value.vocab_rc(),
            Self::ChainedCmp(value) => value.vocab_rc(),
            Self::Quantification(value) => value.vocab_rc(),
            Self::CardinalityAggregate(value) => value.vocab_rc(),
            Self::Aggregate(value) => value.vocab_rc(),
            Self::Ite(value) => value.vocab_rc(),
            Self::Negation(value) => value.vocab_rc(),
            Self::NumNegation(value) => value.vocab_rc(),
            Self::Element(_) => None,
            Self::Variable(value) => value.vocab_rc(),
            Self::InEnumeration(value) => value.vocab_rc(),
            Self::ConjuctiveGuard(value) => value.vocab_rc(),
            Self::ImplicativeGuard(value) => value.vocab_rc(),
            Self::IfGuard(value) => value.vocab_rc(),
            Self::IsEnumerated(value) => value.vocab_rc(),
        }
    }

    /// Returns the codomain of this expression.
    pub fn codomain(&self) -> TypeRef {
        match self {
            Self::AppliedSymbol(value) => value.codomain(),
            Self::BinOp(value) => value.codomain(),
            Self::ChainedCmp(value) => value.codomain(),
            Self::Quantification(value) => value.codomain(),
            Self::CardinalityAggregate(value) => value.codomain(),
            Self::Aggregate(value) => value.codomain(),
            Self::Ite(value) => value.codomain(),
            Self::Negation(value) => value.codomain(),
            Self::NumNegation(value) => value.codomain(),
            Self::Element(value) => value.codomain(),
            Self::Variable(value) => value.codomain(),
            Self::InEnumeration(value) => value.codomain(),
            Self::ConjuctiveGuard(value) => value.codomain(),
            Self::ImplicativeGuard(value) => value.codomain(),
            Self::IfGuard(value) => value.codomain(),
            Self::IsEnumerated(value) => value.codomain(),
        }
    }

    pub fn collect_wdcs(&self) -> Vec<WellDefinedCondition> {
        match self {
            Self::AppliedSymbol(value) => value.collect_wdcs(),
            Self::BinOp(value) => BinOp::collect_wdcs(value),
            Self::ChainedCmp(value) => ChainedCmp::collect_wdcs(value),
            Self::Negation(value) => value.collect_wdcs(),
            Self::NumNegation(value) => value.collect_wdcs(),
            Self::Quantification(value) => value.collect_wdcs(),
            Self::CardinalityAggregate(value) => value.collect_wdcs(),
            Self::Aggregate(value) => value.collect_wdcs(),
            Self::Ite(value) => value.collect_wdcs(),
            Self::Element(_) => Vec::new(),
            Self::Variable(_) => Vec::new(),
            Self::InEnumeration(value) => value.collect_wdcs(),
            Self::ConjuctiveGuard(_) => Vec::new(),
            Self::ImplicativeGuard(_) => Vec::new(),
            Self::IfGuard(value) => value.collect_wdcs(),
            Self::IsEnumerated(value) => value.collect_wdcs(),
        }
    }

    pub fn as_ref(&self) -> ExprRef {
        self.into()
    }
}

#[derive(Clone, Copy, PartialEq, Eq)]
pub enum ExprRef<'a> {
    AppliedSymbol(&'a Rc<AppliedSymbol>),
    BinOp(BinOpRef<'a>),
    ChainedCmp(&'a Rc<ChainedCmp>),
    Negation(&'a Rc<Negation>),
    NumNegation(&'a Rc<NumNegation>),
    Quantification(&'a Rc<Quantification>),
    CardinalityAggregate(&'a Rc<CardinalityAggregate>),
    Aggregate(&'a Rc<Aggregate>),
    Ite(&'a Rc<Ite>),
    Element(&'a Rc<ElementExpr>),
    Variable(&'a Rc<Variable>),
    InEnumeration(&'a Rc<InEnumeration>),
    Bool(&'a Rc<BoolExpr>),
    ConjuctiveGuard(&'a Rc<ConjuctiveGuard>),
    ImplicativeGuard(&'a Rc<ImplicativeGuard>),
    IfGuard(&'a Rc<IfGuard>),
    IsEnumerated(&'a Rc<IsEnumerated>),
}

impl<'a> From<&'a Rc<AppliedSymbol>> for ExprRef<'a> {
    fn from(value: &'a Rc<AppliedSymbol>) -> Self {
        Self::AppliedSymbol(value)
    }
}

impl<'a> From<BinOpRef<'a>> for ExprRef<'a> {
    fn from(value: BinOpRef<'a>) -> Self {
        Self::BinOp(value)
    }
}

impl<'a> From<&'a Rc<Negation>> for ExprRef<'a> {
    fn from(value: &'a Rc<Negation>) -> Self {
        Self::Negation(value)
    }
}

impl<'a> From<&'a Rc<NumNegation>> for ExprRef<'a> {
    fn from(value: &'a Rc<NumNegation>) -> Self {
        Self::NumNegation(value)
    }
}

impl<'a> From<&'a Rc<ChainedCmp>> for ExprRef<'a> {
    fn from(value: &'a Rc<ChainedCmp>) -> Self {
        Self::ChainedCmp(value)
    }
}

impl<'a> From<&'a Rc<Quantification>> for ExprRef<'a> {
    fn from(value: &'a Rc<Quantification>) -> Self {
        Self::Quantification(value)
    }
}

impl<'a> From<&'a Rc<CardinalityAggregate>> for ExprRef<'a> {
    fn from(value: &'a Rc<CardinalityAggregate>) -> Self {
        Self::CardinalityAggregate(value)
    }
}

impl<'a> From<&'a Rc<Aggregate>> for ExprRef<'a> {
    fn from(value: &'a Rc<Aggregate>) -> Self {
        Self::Aggregate(value)
    }
}

impl<'a> From<&'a Rc<Ite>> for ExprRef<'a> {
    fn from(value: &'a Rc<Ite>) -> Self {
        Self::Ite(value)
    }
}

impl<'a> From<&'a Rc<ElementExpr>> for ExprRef<'a> {
    fn from(value: &'a Rc<ElementExpr>) -> Self {
        Self::Element(value)
    }
}

impl<'a> From<&'a Rc<InEnumeration>> for ExprRef<'a> {
    fn from(value: &'a Rc<InEnumeration>) -> Self {
        Self::InEnumeration(value)
    }
}

impl<'a> From<&'a Rc<BoolExpr>> for ExprRef<'a> {
    fn from(value: &'a Rc<BoolExpr>) -> Self {
        Self::Bool(value)
    }
}

impl<'a> From<&'a Rc<ConjuctiveGuard>> for ExprRef<'a> {
    fn from(value: &'a Rc<ConjuctiveGuard>) -> Self {
        Self::ConjuctiveGuard(value)
    }
}

impl<'a> From<&'a Rc<ImplicativeGuard>> for ExprRef<'a> {
    fn from(value: &'a Rc<ImplicativeGuard>) -> Self {
        Self::ImplicativeGuard(value)
    }
}

impl<'a> From<&'a Rc<IfGuard>> for ExprRef<'a> {
    fn from(value: &'a Rc<IfGuard>) -> Self {
        Self::IfGuard(value)
    }
}

impl<'a> From<&'a Rc<IsEnumerated>> for ExprRef<'a> {
    fn from(value: &'a Rc<IsEnumerated>) -> Self {
        Self::IsEnumerated(value)
    }
}

impl FodotOptions for ExprRef<'_> {
    type Options<'a> = FormatOptions;
}

impl FodotDisplay for ExprRef<'_> {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        Self::fmt_with_prec(fmt, f, 0)
    }
}

impl FodotPrecDisplay for ExprRef<'_> {
    fn fmt_with_prec(
        fmt: Fmt<&Self, <Self as FodotOptions>::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
        super_prec: u32,
    ) -> std::fmt::Result {
        match fmt.value {
            Self::AppliedSymbol(value) => write!(f, "{}", fmt.with_format_opts(value.as_ref())),
            Self::BinOp(value) => {
                BinOpRef::fmt_with_prec(fmt.with_format_opts(value), f, super_prec)
            }
            Self::ChainedCmp(value) => write!(f, "{}", fmt.with_format_opts(value.as_ref())),
            Self::Negation(value) => {
                Negation::fmt_with_prec(fmt.with_format_opts(value.as_ref()), f, super_prec)
            }
            Self::NumNegation(value) => {
                NumNegation::fmt_with_prec(fmt.with_format_opts(value.as_ref()), f, super_prec)
            }
            Self::Quantification(value) => write!(f, "{}", fmt.with_format_opts(value.as_ref())),
            Self::CardinalityAggregate(value) => {
                write!(f, "{}", fmt.with_format_opts(value.as_ref()))
            }
            Self::Aggregate(value) => write!(f, "{}", fmt.with_format_opts(value.as_ref())),
            Self::Ite(value) => {
                Ite::fmt_with_prec(fmt.with_format_opts(value.as_ref()), f, super_prec)
            }
            Self::Element(value) => write!(f, "{}", fmt.with_format_opts(value.as_ref())),
            Self::Bool(value) => write!(f, "{}", fmt.with_format_opts(value.as_ref())),
            Self::Variable(value) => write!(f, "{}", fmt.with_format_opts(value.as_ref())),
            Self::InEnumeration(value) => {
                InEnumeration::fmt_with_prec(fmt.with_format_opts(value.as_ref()), f, super_prec)
            }
            Self::ConjuctiveGuard(value) => write!(f, "{}", fmt.with_format_opts(value.as_ref())),
            Self::ImplicativeGuard(value) => write!(f, "{}", fmt.with_format_opts(value.as_ref())),
            Self::IfGuard(value) => {
                IfGuard::fmt_with_prec(fmt.with_format_opts(value.as_ref()), f, super_prec)
            }
            Self::IsEnumerated(value) => FodotDisplay::fmt(fmt.with_format_opts(value.as_ref()), f),
        }
    }
}

impl Display for ExprRef<'_> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

display_as_debug!(ExprRef<'_>);

impl<'a> ExprRef<'a> {
    pub fn for_each<F: FnMut(ExprRef<'a>)>(&self, f: &mut F) {
        f(*self);
        match self {
            Self::AppliedSymbol(value) => value
                .args()
                .iter()
                .for_each(|expr| ExprRef::from(expr).for_each(f)),
            Self::IsEnumerated(value) => value
                .applied_symbol
                .args()
                .iter()
                .for_each(|expr| ExprRef::from(expr).for_each(f)),
            Self::BinOp(bin_op) => {
                ExprRef::from(bin_op.lhs()).for_each(f);
                ExprRef::from(bin_op.rhs()).for_each(f);
            }
            Self::ChainedCmp(chained_cmp) => {
                chained_cmp
                    .iter_exprs()
                    .for_each(|expr| ExprRef::from(expr).for_each(f));
            }
            Self::Negation(neg) => ExprRef::from(neg.subformula()).for_each(f),
            Self::NumNegation(neg) => ExprRef::from(neg.subexpr()).for_each(f),
            Self::Quantification(quant) => ExprRef::from(quant.subformula()).for_each(f),
            Self::CardinalityAggregate(card) => ExprRef::from(card.subformula()).for_each(f),
            Self::Aggregate(agg) => {
                ExprRef::from(agg.term()).for_each(f);
                ExprRef::from(agg.formula()).for_each(f);
            }
            Self::Ite(ite) => {
                ExprRef::from(ite.if_formula()).for_each(f);
                ExprRef::from(ite.then_expr()).for_each(f);
                ExprRef::from(ite.else_expr()).for_each(f);
            }
            Self::Element(_) => (),
            Self::Bool(_) => (),
            Self::Variable(_) => (),
            Self::InEnumeration(in_enum) => {
                ExprRef::from(in_enum.expr()).for_each(f);
                in_enum
                    .enumeration()
                    .for_each(|expr| ExprRef::from(expr).for_each(f));
            }
            Self::ConjuctiveGuard(guard) => ExprRef::from(guard.subformula()).for_each(f),
            Self::ImplicativeGuard(guard) => ExprRef::from(guard.subformula()).for_each(f),
            Self::IfGuard(guard) => {
                ExprRef::from(guard.term()).for_each(f);
                ExprRef::from(guard.else_term()).for_each(f);
            }
        }
    }

    pub fn any<F: Fn(ExprRef<'a>) -> bool>(&self, f: &F) -> bool {
        if f(*self) {
            return true;
        }
        match self {
            Self::AppliedSymbol(value) => {
                value.args().iter().any(|expr| ExprRef::from(expr).any(f))
            }
            Self::IsEnumerated(value) => value
                .applied_symbol
                .args()
                .iter()
                .any(|expr| ExprRef::from(expr).any(f)),
            Self::BinOp(bin_op) => {
                ExprRef::from(bin_op.lhs()).any(f) || ExprRef::from(bin_op.rhs()).any(f)
            }
            Self::ChainedCmp(chained_cmp) => chained_cmp
                .iter_exprs()
                .any(|expr| ExprRef::from(expr).any(f)),
            Self::Negation(neg) => ExprRef::from(neg.subformula()).any(f),
            Self::NumNegation(neg) => ExprRef::from(neg.subexpr()).any(f),
            Self::Quantification(quant) => ExprRef::from(quant.subformula()).any(f),
            Self::CardinalityAggregate(card) => ExprRef::from(card.subformula()).any(f),
            Self::Aggregate(agg) => {
                ExprRef::from(agg.term()).any(f) || ExprRef::from(agg.formula()).any(f)
            }
            Self::Ite(ite) => {
                ExprRef::from(ite.if_formula()).any(f)
                    || ExprRef::from(ite.then_expr()).any(f)
                    || ExprRef::from(ite.else_expr()).any(f)
            }
            Self::Element(_) => false,
            Self::Bool(_) => false,
            Self::Variable(_) => false,
            Self::InEnumeration(in_enum) => {
                ExprRef::from(in_enum.expr()).any(f)
                    || in_enum.enumeration().any(|expr| ExprRef::from(expr).any(f))
            }
            Self::ConjuctiveGuard(guard) => ExprRef::from(guard.subformula()).any(f),
            Self::ImplicativeGuard(guard) => ExprRef::from(guard.subformula()).any(f),
            Self::IfGuard(guard) => {
                ExprRef::from(guard.term()).any(f) || ExprRef::from(guard.else_term()).any(f)
            }
        }
    }

    fn any_conjunction<F: Fn(ExprRef) -> bool>(&self, f: F) -> bool {
        match self {
            ExprRef::BinOp(BinOpRef::Logic(logic)) => logic.any_conjunction(&f),
            _ => false,
        }
    }

    pub fn syntax_eq(&self, other: &Self) -> bool {
        match (self, other) {
            (Self::BinOp(value1), Self::BinOp(value2)) => value1.syntax_eq(value2),
            _ => self == other,
        }
    }

    pub fn for_each_quantees<F: FnMut(&'a Quantees)>(&self, f: &mut F) {
        self.for_each(&mut |expr| match expr {
            ExprRef::Quantification(quant) => f(quant.quantees()),
            ExprRef::CardinalityAggregate(card) => f(card.quantees()),
            ExprRef::Aggregate(agg) => f(agg.quantees()),
            _ => {}
        });
    }

    pub fn to_owned(&self) -> Expr {
        match self {
            Self::AppliedSymbol(value) => (*value).clone().into(),
            Self::BinOp(value) => value.to_owned().into(),
            Self::ChainedCmp(value) => (*value).clone().into(),
            Self::Negation(value) => (*value).clone().into(),
            Self::NumNegation(value) => (*value).clone().into(),
            Self::Quantification(value) => (*value).clone().into(),
            Self::CardinalityAggregate(value) => (*value).clone().into(),
            Self::Aggregate(value) => (*value).clone().into(),
            Self::Ite(value) => (*value).clone().into(),
            Self::Element(value) => (*value).clone().into(),
            Self::Bool(value) => ElementExpr::from(value.as_ref().clone()).into(),
            Self::Variable(value) => (*value).clone().into(),
            Self::InEnumeration(value) => (*value).clone().into(),
            Self::ConjuctiveGuard(value) => (*value).clone().into(),
            Self::ImplicativeGuard(value) => (*value).clone().into(),
            Self::IfGuard(value) => (*value).clone().into(),
            Self::IsEnumerated(value) => (*value).clone().into(),
        }
    }

    pub fn codomain(&self) -> TypeRef {
        match self {
            Self::AppliedSymbol(value) => value.codomain(),
            Self::BinOp(value) => value.codomain(),
            Self::ChainedCmp(value) => value.codomain(),
            Self::Negation(value) => value.codomain(),
            Self::NumNegation(value) => value.codomain(),
            Self::Quantification(value) => value.codomain(),
            Self::CardinalityAggregate(value) => value.codomain(),
            Self::Aggregate(value) => value.codomain(),
            Self::Ite(value) => value.codomain(),
            Self::Element(value) => value.codomain(),
            Self::Bool(_) => Type::Bool,
            Self::Variable(value) => value.codomain(),
            Self::InEnumeration(value) => value.codomain(),
            Self::ConjuctiveGuard(value) => value.codomain(),
            Self::ImplicativeGuard(value) => value.codomain(),
            Self::IfGuard(value) => value.codomain(),
            Self::IsEnumerated(value) => value.codomain(),
        }
    }

    pub fn span(&self) -> Option<Span> {
        match self {
            Self::AppliedSymbol(value) => value.span(),
            Self::BinOp(value) => value.span(),
            Self::ChainedCmp(value) => value.span(),
            Self::Negation(value) => value.span(),
            Self::NumNegation(value) => value.span(),
            Self::Quantification(value) => value.span(),
            Self::CardinalityAggregate(value) => value.span(),
            Self::Aggregate(value) => value.span(),
            Self::Ite(value) => value.span(),
            Self::Element(value) => value.span(),
            Self::Bool(value) => value.span(),
            Self::Variable(value) => value.span(),
            Self::InEnumeration(value) => value.span(),
            Self::ConjuctiveGuard(value) => value.span(),
            Self::ImplicativeGuard(value) => value.span(),
            Self::IfGuard(value) => value.span(),
            Self::IsEnumerated(value) => value.span(),
        }
    }
}

/// A builtin type element.
#[non_exhaustive]
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Element {
    Bool(bool),
    Int(Int),
    Real(Real),
}

impl FromStr for Element {
    type Err = ParsePrimitiveElementError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        if let Ok(value) = parse_bool_value(s) {
            Ok(value.into())
        } else if let Ok(value) = parse_int_value(s) {
            Ok(value.into())
        } else if let Ok(value) = parse_real_value(s) {
            Ok(value.into())
        } else {
            Err(ParsePrimitiveElementError)
        }
    }
}

impl FodotOptions for Element {
    type Options<'a>
        = FormatOptions
    where
        Self: 'a;
}

impl FodotDisplay for Element {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        match fmt.value {
            Element::Bool(value) => write!(f, "{}", value),
            Element::Int(value) => write!(f, "{}", value),
            Element::Real(value) => write!(f, "{}", value),
        }
    }
}

impl Display for Element {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", Fmt::with_defaults(self))
    }
}

impl Element {
    pub fn codomain(&self) -> TypeRef {
        match self {
            Element::Bool(_) => Type::Bool,
            Element::Int(_) => Type::Int,
            Element::Real(_) => Type::Real,
        }
    }
}

impl From<bool> for Element {
    fn from(value: bool) -> Self {
        Self::Bool(value)
    }
}

impl From<Int> for Element {
    fn from(value: Int) -> Self {
        Self::Int(value)
    }
}

impl From<Real> for Element {
    fn from(value: Real) -> Self {
        Self::Real(value)
    }
}

impl From<Element> for ElementExpr {
    fn from(value: Element) -> Self {
        Self {
            element: value,
            metadata: Default::default(),
        }
    }
}

impl From<Element> for CCTypeElement {
    fn from(value: Element) -> Self {
        match value {
            Element::Bool(value) => value.into(),
            Element::Int(value) => value.into(),
            Element::Real(value) => value.into(),
        }
    }
}

impl From<Element> for ElementNode {
    fn from(value: Element) -> Self {
        match value {
            Element::Bool(value) => ElementNode::Bool(value.into()),
            Element::Int(value) => ElementNode::Int(value.into()),
            Element::Real(value) => ElementNode::Real(value.into()),
        }
    }
}

/// An element expression.
///
/// Difference between [Element] is that this struct implements [MetadataMut].
#[derive(Clone)]
pub struct ElementExpr {
    pub element: Element,
    metadata: Option<Box<Metadata>>,
}

impl FodotOptions for ElementExpr {
    type Options<'a>
        = FormatOptions
    where
        Self: 'a;
}

impl FodotDisplay for ElementExpr {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        write!(f, "{}", fmt.with_format_opts(&fmt.value.element))
    }
}

impl Display for ElementExpr {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

display_as_debug!(ElementExpr);

impl PartialEq for ElementExpr {
    fn eq(&self, other: &Self) -> bool {
        self.element == other.element
    }
}

impl Eq for ElementExpr {}

impl PartialEq<BoolExpr> for ElementExpr {
    fn eq(&self, other: &BoolExpr) -> bool {
        match self.element {
            Element::Bool(value) => value == other.value,
            _ => false,
        }
    }
}

impl PartialEq<ElementExpr> for BoolExpr {
    fn eq(&self, other: &ElementExpr) -> bool {
        ElementExpr::eq(other, self)
    }
}

impl From<BoolExpr> for ElementExpr {
    fn from(value: BoolExpr) -> Self {
        Self {
            element: value.value.into(),
            metadata: value.metadata,
        }
    }
}

impl ElementExpr {
    pub fn codomain(&self) -> TypeRef {
        self.element.codomain()
    }
}

impl MetadataIm for ElementExpr {
    type Metadata = Metadata;
    fn metadata(&self) -> Option<&Metadata> {
        self.metadata.as_deref()
    }
}

impl MetadataMut for ElementExpr {
    fn metadata_mut(&mut self) -> &mut Metadata {
        self.metadata.get_or_insert_default()
    }
}

/// An [Element] that is boolean value.
#[derive(Clone)]
pub struct BoolExpr {
    pub value: bool,
    metadata: Option<Box<Metadata>>,
}

impl FodotOptions for BoolExpr {
    type Options<'a>
        = FormatOptions
    where
        Self: 'a;
}

impl FodotDisplay for BoolExpr {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        write!(f, "{}", &fmt.value.value)
    }
}

impl Display for BoolExpr {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

display_as_debug!(BoolExpr);

impl PartialEq for BoolExpr {
    fn eq(&self, other: &Self) -> bool {
        self.value == other.value
    }
}

impl Eq for BoolExpr {}

impl TryFrom<ElementExpr> for BoolExpr {
    type Error = NotABoolElementError;

    fn try_from(value: ElementExpr) -> Result<Self, Self::Error> {
        match value.element {
            Element::Bool(val) => Ok(Self {
                value: val,
                metadata: value.metadata,
            }),
            _ => Err(NotABoolElementError),
        }
    }
}

impl MetadataIm for BoolExpr {
    type Metadata = Metadata;
    fn metadata(&self) -> Option<&Metadata> {
        self.metadata.as_deref()
    }
}

impl MetadataMut for BoolExpr {
    fn metadata_mut(&mut self) -> &mut Metadata {
        self.metadata.get_or_insert_default()
    }
}

#[cfg(test)]
mod test {
    use super::*;

    #[test]
    fn contains_free_variables() {
        let vocab = Vocabulary::new("V");
        let (vocab, _) = vocab.complete_vocab();
        let var =
            VariableDecl::new("x", Vocabulary::parse_type_rc(&vocab, "Bool").unwrap()).finish();
        let bin_op = BinOp::new(
            var.create_var_ref().into(),
            BinOps::Equivalence,
            true.into(),
        )
        .unwrap();
        let vars: Vec<_> = bin_op
            .iter_free_variables()
            .map(|f| Variable::clone(&f))
            .collect();
        assert_eq! {
            vars,
            vec![var.create_var_ref()]
        }
        assert!(bin_op.contains_free_variables());
    }

    #[test]
    fn does_not_contain_free_variables() {
        let bin_op = BinOp::new(false.into(), BinOps::Equivalence, true.into()).unwrap();
        let vars: Vec<_> = bin_op
            .iter_free_variables()
            .map(|f| Variable::clone(&f))
            .collect();
        assert_eq! {
            vars,
            Vec::<Variable>::new()
        }
        assert!(!bin_op.contains_free_variables());
    }
}
