use super::{
    AppliedSymbol, BinOp, BinOpFormula, BoolExpr, ChainedCmp, ConjuctiveGuard, ElementExpr, Expr,
    ExprRef, FreeVariables, IfGuard, ImplicativeGuard, InEnumeration, IsEnumerated, Ite, Metadata,
    MetadataIm, Negation, Quantification, Variable, WellDefinedCondition,
};
use crate::fodot::display_as_debug;
use crate::fodot::error::{
    ExprToWellDefFormulaError, NotBoolExpr, NotBoolExprError, NotWellDefinedCause,
    NotWellDefinedExpression, NotWellDefinedExpressionError,
};
use crate::fodot::fmt::{FodotOptions, FodotPrecDisplay};
use crate::fodot::vocabulary::Vocabulary;
use crate::fodot::{
    fmt::{Fmt, FodotDisplay},
    vocabulary::Type,
};
use sli_collections::rc::{Rc, RcA};
use std::fmt::Display;

/// Represents an FO(·) formula.
///
/// A formula is an expression with a boolean codomain.
#[derive(Clone, PartialEq, Eq)]
pub enum Formula {
    AppliedSymbol(Rc<AppliedSymbol>),
    BinOp(BinOpFormula),
    ChainedCmp(Rc<ChainedCmp>),
    Negation(Rc<Negation>),
    Quantification(Rc<Quantification>),
    Ite(Rc<Ite>),
    Bool(Rc<BoolExpr>),
    Variable(Rc<Variable>),
    InEnumeration(Rc<InEnumeration>),
    ConjuctiveGuard(Rc<ConjuctiveGuard>),
    ImplicativeGuard(Rc<ImplicativeGuard>),
    IfGuard(Rc<IfGuard>),
    IsEnumerated(Rc<IsEnumerated>),
}

impl FodotOptions for Formula {
    type Options<'a>
        = <Expr as FodotOptions>::Options<'a>
    where
        Self: 'a;
}

impl FodotDisplay for Formula {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        FodotDisplay::fmt(fmt.with_opts(&ExprRef::from(fmt.value)), f)
    }
}

impl FodotPrecDisplay for Formula {
    fn fmt_with_prec(
        fmt: Fmt<&Self, <Self as FodotOptions>::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
        super_prec: u32,
    ) -> std::fmt::Result {
        ExprRef::fmt_with_prec(fmt.with_opts(&ExprRef::from(fmt.value)), f, super_prec)
    }
}

impl Display for Formula {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

impl PartialEq<ExprRef<'_>> for Formula {
    fn eq(&self, other: &ExprRef<'_>) -> bool {
        use ExprRef as E;
        use Formula as S;
        match (self, other) {
            (S::AppliedSymbol(value1), E::AppliedSymbol(value2)) => value1 == *value2,
            (S::BinOp(value1), E::BinOp(value2)) => value1 == value2,
            (S::ChainedCmp(value1), E::ChainedCmp(value2)) => value1 == *value2,
            (S::Negation(value1), E::Negation(value2)) => value1 == *value2,
            (S::Quantification(value1), E::Quantification(value2)) => value1 == *value2,
            (S::Ite(value1), E::Ite(value2)) => value1 == *value2,
            (S::Bool(value1), E::Bool(value2)) => value1 == *value2,
            (S::Bool(value1), E::Element(value2)) => value1.as_ref() == value2.as_ref(),
            (S::Variable(value1), E::Variable(value2)) => value1 == *value2,
            (S::InEnumeration(value1), E::InEnumeration(value2)) => value1 == *value2,
            (S::ConjuctiveGuard(value1), E::ConjuctiveGuard(value2)) => value1 == *value2,
            (S::ImplicativeGuard(value1), E::ImplicativeGuard(value2)) => value1 == *value2,
            (S::IfGuard(value1), E::IfGuard(value2)) => value1 == *value2,
            _ => false,
        }
    }
}

display_as_debug!(Formula);

impl Formula {
    pub fn as_ref(&self) -> ExprRef {
        self.into()
    }

    pub fn collect_wdcs(&self) -> Vec<WellDefinedCondition> {
        match self {
            Self::AppliedSymbol(value) => value.collect_wdcs(),
            Self::BinOp(value) => BinOpFormula::collect_wdcs(value),
            Self::ChainedCmp(value) => ChainedCmp::collect_wdcs(value),
            Self::Negation(value) => value.collect_wdcs(),
            Self::Quantification(value) => value.collect_wdcs(),
            Self::Ite(value) => value.collect_wdcs(),
            Self::Bool(_) => Vec::new(),
            Self::Variable(_) => Vec::new(),
            Self::InEnumeration(value) => value.collect_wdcs(),
            Self::ConjuctiveGuard(_) => Vec::new(),
            Self::ImplicativeGuard(_) => Vec::new(),
            Self::IfGuard(value) => value.collect_wdcs(),
            Self::IsEnumerated(value) => value.collect_wdcs(),
        }
    }

    pub fn vocab_rc(&self) -> Option<&RcA<Vocabulary>> {
        match self {
            Self::AppliedSymbol(value) => value.vocab_rc(),
            Self::BinOp(value) => value.vocab_rc(),
            Self::ChainedCmp(value) => value.vocab_rc(),
            Self::Negation(value) => value.vocab_rc(),
            Self::Quantification(value) => value.vocab_rc(),
            Self::Ite(value) => value.vocab_rc(),
            Self::Bool(_) => None,
            Self::Variable(value) => value.vocab_rc(),
            Self::InEnumeration(value) => value.vocab_rc(),
            Self::ConjuctiveGuard(value) => value.vocab_rc(),
            Self::ImplicativeGuard(value) => value.vocab_rc(),
            Self::IfGuard(value) => value.vocab_rc(),
            Self::IsEnumerated(value) => value.vocab_rc(),
        }
    }

    pub fn vocab(&self) -> Option<&Vocabulary> {
        self.vocab_rc().map(|f| f.as_ref())
    }
}

impl FreeVariables for Formula {
    fn add_to_free_variable_iter<'a>(&'a self, iter: &mut super::FreeVariableIter<'a>) {
        match self {
            Self::AppliedSymbol(value) => value.add_to_free_variable_iter(iter),
            Self::BinOp(value) => value.add_to_free_variable_iter(iter),
            Self::ChainedCmp(value) => value.add_to_free_variable_iter(iter),
            Self::Negation(value) => value.add_to_free_variable_iter(iter),
            Self::Quantification(value) => value.add_to_free_variable_iter(iter),
            Self::Ite(value) => value.add_to_free_variable_iter(iter),
            Self::Bool(_) => (),
            Self::InEnumeration(value) => value.add_to_free_variable_iter(iter),
            Self::Variable(value) => value.add_to_free_variable_iter(iter),
            Self::ConjuctiveGuard(value) => value.add_to_free_variable_iter(iter),
            Self::ImplicativeGuard(value) => value.add_to_free_variable_iter(iter),
            Self::IfGuard(value) => value.add_to_free_variable_iter(iter),
            Self::IsEnumerated(value) => value.add_to_free_variable_iter(iter),
        }
    }
}

impl TryFrom<Expr> for Formula {
    type Error = NotBoolExprError;

    fn try_from(value: Expr) -> Result<Self, Self::Error> {
        if value.codomain() != Type::Bool {
            return Err(NotBoolExpr {
                found: value.codomain().into(),
            }
            .into());
        }
        match value {
            Expr::AppliedSymbol(value) => Ok(Self::AppliedSymbol(value)),
            Expr::BinOp(BinOp::Logic(value)) => Ok(Self::BinOp(value.into())),
            Expr::BinOp(BinOp::Cmp(value)) => Ok(Self::BinOp(value.into())),
            Expr::BinOp(BinOp::Equality(value)) => Ok(Self::BinOp(value.into())),
            Expr::ChainedCmp(value) => Ok(Self::ChainedCmp(value)),
            Expr::Negation(value) => Ok(Self::Negation(value)),
            Expr::Quantification(value) => Ok(Self::Quantification(value)),
            Expr::Ite(value) => Ok(Self::Ite(value)),
            Expr::Element(value) => Ok(Self::Bool(
                BoolExpr::try_from(ElementExpr::clone(&value))
                    .unwrap()
                    .into(),
            )),
            Expr::InEnumeration(value) => Ok(Self::InEnumeration(value)),
            Expr::Variable(value) => Ok(Self::Variable(value)),
            Expr::ConjuctiveGuard(value) => Ok(Self::ConjuctiveGuard(value)),
            Expr::ImplicativeGuard(value) => Ok(Self::ImplicativeGuard(value)),
            Expr::IfGuard(value) => Ok(Self::IfGuard(value)),
            Expr::IsEnumerated(value) => Ok(Self::IsEnumerated(value)),
            Expr::Aggregate(_) => unreachable!(),
            Expr::CardinalityAggregate(_) => unreachable!(),
            Expr::BinOp(BinOp::Arithmetic(_)) => unreachable!(),
            Expr::NumNegation(_) => unreachable!(),
        }
    }
}

impl TryFrom<AppliedSymbol> for Formula {
    type Error = NotBoolExprError;

    fn try_from(value: AppliedSymbol) -> Result<Self, Self::Error> {
        if value.codomain() != Type::Bool {
            return Err(NotBoolExpr {
                found: value.codomain().into(),
            }
            .into());
        }
        Ok(Self::AppliedSymbol(value.into()))
    }
}

impl TryFrom<BinOp> for Formula {
    type Error = NotBoolExprError;

    fn try_from(value: BinOp) -> Result<Self, Self::Error> {
        match value {
            BinOp::Logic(value) => Ok(Self::BinOp(BinOpFormula::Logic(value))),
            BinOp::Equality(value) => Ok(Self::BinOp(BinOpFormula::Equality(value))),
            BinOp::Cmp(value) => Ok(Self::BinOp(BinOpFormula::Cmp(value))),
            BinOp::Arithmetic(value) => Err(NotBoolExpr {
                found: value.codomain().into(),
            }
            .into()),
        }
    }
}

impl From<Negation> for Formula {
    fn from(value: Negation) -> Self {
        Self::Negation(value.into())
    }
}

impl From<Quantification> for Formula {
    fn from(value: Quantification) -> Self {
        Self::Quantification(value.into())
    }
}

impl TryFrom<Ite> for Formula {
    type Error = NotBoolExprError;

    fn try_from(value: Ite) -> Result<Self, Self::Error> {
        if value.codomain() != Type::Bool {
            return Err(NotBoolExpr {
                found: value.codomain().into(),
            }
            .into());
        }
        Ok(Self::Ite(value.into()))
    }
}

impl From<BoolExpr> for Formula {
    fn from(value: BoolExpr) -> Self {
        Self::Bool(value.into())
    }
}

impl TryFrom<ElementExpr> for Formula {
    type Error = NotBoolExprError;

    fn try_from(value: ElementExpr) -> Result<Self, Self::Error> {
        let element = value.element.clone();
        Ok(Self::Bool(
            BoolExpr::try_from(value)
                .map_err(|_| NotBoolExpr {
                    found: element.codomain().into(),
                })?
                .into(),
        ))
    }
}

impl TryFrom<Variable> for Formula {
    type Error = NotBoolExprError;

    fn try_from(value: Variable) -> Result<Self, Self::Error> {
        if value.codomain() != Type::Bool {
            return Err(NotBoolExpr {
                found: value.codomain().into(),
            }
            .into());
        }
        Ok(Self::Variable(value.into()))
    }
}

impl From<InEnumeration> for Formula {
    fn from(value: InEnumeration) -> Self {
        Self::InEnumeration(value.into())
    }
}

impl<'a> From<&'a Formula> for ExprRef<'a> {
    fn from(value: &'a Formula) -> Self {
        match value {
            Formula::AppliedSymbol(value) => Self::AppliedSymbol(value),
            Formula::BinOp(value) => Self::BinOp(value.into()),
            Formula::ChainedCmp(value) => Self::ChainedCmp(value),
            Formula::Negation(value) => Self::Negation(value),
            Formula::Quantification(value) => Self::Quantification(value),
            Formula::Ite(value) => Self::Ite(value),
            Formula::Bool(value) => Self::Bool(value),
            Formula::Variable(value) => Self::Variable(value),
            Formula::InEnumeration(value) => Self::InEnumeration(value),
            Formula::ConjuctiveGuard(value) => Self::ConjuctiveGuard(value),
            Formula::ImplicativeGuard(value) => Self::ImplicativeGuard(value),
            Formula::IfGuard(value) => Self::IfGuard(value),
            Formula::IsEnumerated(value) => Self::IsEnumerated(value),
        }
    }
}

impl MetadataIm for Formula {
    type Metadata = Metadata;
    fn metadata(&self) -> Option<&Metadata> {
        match self {
            Self::AppliedSymbol(value) => value.metadata(),
            Self::BinOp(value) => value.metadata(),
            Self::ChainedCmp(value) => value.metadata(),
            Self::Negation(value) => value.metadata(),
            Self::Quantification(value) => value.metadata(),
            Self::Ite(value) => value.metadata(),
            Self::Bool(value) => value.metadata(),
            Self::Variable(value) => value.metadata(),
            Self::InEnumeration(value) => value.metadata(),
            Self::ConjuctiveGuard(value) => value.metadata(),
            Self::ImplicativeGuard(value) => value.metadata(),
            Self::IfGuard(value) => value.metadata(),
            Self::IsEnumerated(value) => value.metadata(),
        }
    }
}

/// Represents an well defined [Formula].
///
/// A well defined formula is a formula with no well defined conditions.
#[derive(Clone, PartialEq, Eq)]
pub struct WellDefinedFormula(Formula);

impl FodotOptions for WellDefinedFormula {
    type Options<'a>
        = <Expr as FodotOptions>::Options<'a>
    where
        Self: 'a;
}

impl FodotDisplay for WellDefinedFormula {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        write!(f, "{}", fmt.with_opts(&fmt.value.0))
    }
}

impl Display for WellDefinedFormula {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

display_as_debug!(WellDefinedFormula);

impl WellDefinedFormula {
    pub fn expr(self) -> Formula {
        self.0
    }

    pub fn as_formula(&self) -> &Formula {
        &self.0
    }
}

impl AsRef<Formula> for WellDefinedFormula {
    fn as_ref(&self) -> &Formula {
        &self.0
    }
}

impl TryFrom<Formula> for WellDefinedFormula {
    type Error = NotWellDefinedExpressionError;

    fn try_from(value: Formula) -> Result<Self, Self::Error> {
        let wdcs = value.collect_wdcs();
        if wdcs.len() != 0 {
            Err(NotWellDefinedExpression {
                causes: wdcs
                    .into_iter()
                    .map(|f| NotWellDefinedCause {
                        condition: f.condition,
                        origin: f.origin.to_owned(),
                    })
                    .collect(),
            }
            .into())
        } else {
            Ok(Self(value))
        }
    }
}

impl TryFrom<Expr> for WellDefinedFormula {
    type Error = ExprToWellDefFormulaError;

    fn try_from(value: Expr) -> Result<Self, Self::Error> {
        Ok(WellDefinedFormula::try_from(Formula::try_from(value)?)?)
    }
}

impl<'a> From<&'a WellDefinedFormula> for ExprRef<'a> {
    fn from(value: &'a WellDefinedFormula) -> Self {
        Self::from(&value.0)
    }
}
