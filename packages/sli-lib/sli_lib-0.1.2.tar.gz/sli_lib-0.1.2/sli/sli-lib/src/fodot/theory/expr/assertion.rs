use super::{
    AppliedSymbol, BinOp, BinOpFormula, BoolExpr, ChainedCmp, ConjuctiveGuard, Definition,
    ElementExpr, Expr, ExprRef, Formula, IfGuard, ImplicativeGuard, InEnumeration, IsEnumerated,
    Ite, IterFreeVariables, Metadata, MetadataIm, Negation, Quantification, WellDefinedCondition,
};
use crate::fodot::display_as_debug;
use crate::fodot::error::{
    ExprToAssertFreeVarError, ExprToAssertionError, FormulaToAssertionError, NotBoolExpr,
    NotBoolExprError, NotWellDefinedCause, NotWellDefinedExpression, NotWellDefinedExpressionError,
};
use crate::fodot::fmt::{FodotOptions, FodotPrecDisplay};
use crate::fodot::{
    fmt::{Fmt, FodotDisplay, FormatOptions},
    vocabulary::{Type, Vocabulary},
};
use sli_collections::rc::{Rc, RcA};
use std::fmt::Display;

/// Represents an FO(·) assertion.
#[non_exhaustive]
#[derive(Clone, PartialEq, Eq)]
pub enum Assertion {
    AppliedSymbol(Rc<AppliedSymbol>),
    BinOp(BinOpFormula),
    ChainedCmp(Rc<ChainedCmp>),
    Negation(Rc<Negation>),
    Quantification(Rc<Quantification>),
    Ite(Rc<Ite>),
    Bool(Rc<BoolExpr>),
    Definition(Rc<Definition>),
    InEnumeration(Rc<InEnumeration>),
    ConjuctiveGuard(Rc<ConjuctiveGuard>),
    ImplicativeGuard(Rc<ImplicativeGuard>),
    IfGuard(Rc<IfGuard>),
    IsEnumerated(Rc<IsEnumerated>),
}

impl TryFrom<Vec<WellDefinedCondition<'_>>> for NotWellDefinedExpression {
    type Error = ();
    fn try_from(value: Vec<WellDefinedCondition>) -> Result<Self, Self::Error> {
        if value.len() == 0 {
            Err(())
        } else {
            Ok(NotWellDefinedExpression {
                causes: value
                    .into_iter()
                    .map(|f| NotWellDefinedCause {
                        condition: f.condition,
                        origin: f.origin.to_owned(),
                    })
                    .collect(),
            })
        }
    }
}

impl TryFrom<Vec<WellDefinedCondition<'_>>> for NotWellDefinedExpressionError {
    type Error = ();
    fn try_from(value: Vec<WellDefinedCondition>) -> Result<Self, Self::Error> {
        NotWellDefinedExpression::try_from(value).map(|f| f.into())
    }
}

impl FodotOptions for Assertion {
    type Options<'a>
        = FormatOptions
    where
        Self: 'a;
}

impl FodotDisplay for Assertion {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        Self::fmt_with_prec(fmt, f, 0)
    }
}

impl FodotPrecDisplay for Assertion {
    fn fmt_with_prec(
        fmt: Fmt<&Self, <Self as FodotOptions>::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
        super_prec: u32,
    ) -> std::fmt::Result {
        match fmt.value {
            Assertion::AppliedSymbol(value) => {
                write!(f, "{}", fmt.with_format_opts(value.as_ref()))
            }
            Assertion::BinOp(value) => {
                BinOpFormula::fmt_with_prec(fmt.with_format_opts(value), f, super_prec)
            }
            Assertion::ChainedCmp(value) => write!(f, "{}", fmt.with_format_opts(value.as_ref())),
            Assertion::Negation(value) => {
                Negation::fmt_with_prec(fmt.with_format_opts(value), f, super_prec)
            }
            Assertion::Quantification(value) => {
                write!(f, "{}", fmt.with_format_opts(value.as_ref()))
            }
            Assertion::Ite(value) => {
                Ite::fmt_with_prec(fmt.with_format_opts(value.as_ref()), f, super_prec)
            }
            Assertion::Bool(value) => write!(f, "{}", fmt.with_format_opts(value.as_ref())),
            Assertion::Definition(value) => write!(f, "{}", fmt.with_format_opts(value.as_ref())),
            Assertion::InEnumeration(value) => {
                InEnumeration::fmt_with_prec(fmt.with_format_opts(value.as_ref()), f, super_prec)
            }
            Assertion::ConjuctiveGuard(value) => {
                write!(f, "{}", fmt.with_format_opts(value.as_ref()))
            }
            Assertion::ImplicativeGuard(value) => {
                write!(f, "{}", fmt.with_format_opts(value.as_ref()))
            }
            Assertion::IfGuard(value) => {
                IfGuard::fmt_with_prec(fmt.with_format_opts(value.as_ref()), f, super_prec)
            }
            Assertion::IsEnumerated(value) => {
                FodotDisplay::fmt(fmt.with_format_opts(value.as_ref()), f)
            }
        }
    }
}

impl Display for Assertion {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

display_as_debug!(Assertion);

impl TryFrom<AppliedSymbol> for Assertion {
    type Error = ExprToAssertionError;

    fn try_from(value: AppliedSymbol) -> Result<Self, Self::Error> {
        if value.codomain() != Type::Bool {
            return Err(NotBoolExpr {
                found: value.codomain().into(),
            }
            .into());
        }
        if value.contains_free_variables() {
            return Err(ExprToAssertFreeVarError.into());
        }
        NotWellDefinedExpression::try_from(value.collect_wdcs())
            .ok()
            .map_or(Ok(()), Err)?;
        Ok(Self::AppliedSymbol(value.into()))
    }
}

impl TryFrom<Rc<AppliedSymbol>> for Assertion {
    type Error = ExprToAssertionError;

    fn try_from(value: Rc<AppliedSymbol>) -> Result<Self, Self::Error> {
        if value.codomain() != Type::Bool {
            return Err(NotBoolExpr {
                found: value.codomain().into(),
            }
            .into());
        }
        if value.contains_free_variables() {
            return Err(ExprToAssertFreeVarError.into());
        }
        NotWellDefinedExpression::try_from(value.collect_wdcs())
            .ok()
            .map_or(Ok(()), Err)?;
        Ok(Self::AppliedSymbol(value))
    }
}

impl TryFrom<BinOp> for Assertion {
    type Error = ExprToAssertionError;

    fn try_from(value: BinOp) -> Result<Self, Self::Error> {
        let value = BinOpFormula::try_from(value)?;
        if value.contains_free_variables() {
            return Err(ExprToAssertFreeVarError.into());
        }
        NotWellDefinedExpression::try_from(BinOpFormula::collect_wdcs(&value))
            .ok()
            .map_or(Ok(()), Err)?;
        Ok(Self::BinOp(value))
    }
}

impl TryFrom<ChainedCmp> for Assertion {
    type Error = ExprToAssertionError;

    fn try_from(value: ChainedCmp) -> Result<Self, Self::Error> {
        Rc::new(value).try_into()
    }
}

impl TryFrom<Rc<ChainedCmp>> for Assertion {
    type Error = ExprToAssertionError;

    fn try_from(value: Rc<ChainedCmp>) -> Result<Self, Self::Error> {
        if value.contains_free_variables() {
            return Err(ExprToAssertFreeVarError.into());
        }
        NotWellDefinedExpression::try_from(value.collect_wdcs())
            .ok()
            .map_or(Ok(()), Err)?;
        Ok(Self::ChainedCmp(value.into()))
    }
}

impl TryFrom<Negation> for Assertion {
    type Error = FormulaToAssertionError;

    fn try_from(value: Negation) -> Result<Self, Self::Error> {
        if value.contains_free_variables() {
            return Err(ExprToAssertFreeVarError.into());
        }
        NotWellDefinedExpression::try_from(value.collect_wdcs())
            .ok()
            .map_or(Ok(()), Err)?;
        Ok(Self::Negation(value.into()))
    }
}

impl TryFrom<Rc<Negation>> for Assertion {
    type Error = FormulaToAssertionError;

    fn try_from(value: Rc<Negation>) -> Result<Self, Self::Error> {
        if value.contains_free_variables() {
            return Err(ExprToAssertFreeVarError.into());
        }
        NotWellDefinedExpression::try_from(value.collect_wdcs())
            .ok()
            .map_or(Ok(()), Err)?;
        Ok(Self::Negation(value.into()))
    }
}

impl TryFrom<Quantification> for Assertion {
    type Error = FormulaToAssertionError;

    fn try_from(value: Quantification) -> Result<Self, Self::Error> {
        if value.contains_free_variables() {
            return Err(ExprToAssertFreeVarError.into());
        }
        NotWellDefinedExpression::try_from(value.collect_wdcs())
            .ok()
            .map_or(Ok(()), Err)?;
        Ok(Self::Quantification(value.into()))
    }
}

impl TryFrom<Rc<Quantification>> for Assertion {
    type Error = FormulaToAssertionError;

    fn try_from(value: Rc<Quantification>) -> Result<Self, Self::Error> {
        if value.contains_free_variables() {
            return Err(ExprToAssertFreeVarError.into());
        }
        NotWellDefinedExpression::try_from(value.collect_wdcs())
            .ok()
            .map_or(Ok(()), Err)?;
        Ok(Self::Quantification(value))
    }
}

impl TryFrom<Ite> for Assertion {
    type Error = ExprToAssertionError;

    fn try_from(value: Ite) -> Result<Self, Self::Error> {
        if value.codomain() != Type::Bool {
            return Err(NotBoolExpr {
                found: value.codomain().into(),
            }
            .into());
        }

        if value.contains_free_variables() {
            return Err(ExprToAssertFreeVarError.into());
        }
        NotWellDefinedExpression::try_from(value.collect_wdcs())
            .ok()
            .map_or(Ok(()), Err)?;

        Ok(Assertion::Ite(value.into()))
    }
}

impl TryFrom<Rc<Ite>> for Assertion {
    type Error = ExprToAssertionError;

    fn try_from(value: Rc<Ite>) -> Result<Self, Self::Error> {
        if value.codomain() != Type::Bool {
            return Err(NotBoolExpr {
                found: value.codomain().into(),
            }
            .into());
        }

        if value.as_ref().contains_free_variables() {
            return Err(ExprToAssertFreeVarError.into());
        }
        NotWellDefinedExpression::try_from(value.collect_wdcs())
            .ok()
            .map_or(Ok(()), Err)?;

        Ok(Assertion::Ite(value))
    }
}

impl TryFrom<Rc<InEnumeration>> for Assertion {
    type Error = FormulaToAssertionError;

    fn try_from(value: Rc<InEnumeration>) -> Result<Self, Self::Error> {
        if value.as_ref().contains_free_variables() {
            return Err(ExprToAssertFreeVarError.into());
        }
        NotWellDefinedExpression::try_from(value.collect_wdcs())
            .ok()
            .map_or(Ok(()), Err)?;
        Ok(Assertion::InEnumeration(value))
    }
}

impl TryFrom<ElementExpr> for Assertion {
    type Error = NotBoolExprError;

    fn try_from(value: ElementExpr) -> Result<Self, Self::Error> {
        let element = value.element.clone();
        Ok(Self::Bool(Rc::new(BoolExpr::try_from(value).map_err(
            |_| NotBoolExpr {
                found: element.codomain().into(),
            },
        )?)))
    }
}

impl TryFrom<ConjuctiveGuard> for Assertion {
    type Error = ExprToAssertFreeVarError;

    fn try_from(value: ConjuctiveGuard) -> Result<Self, Self::Error> {
        Rc::new(value).try_into()
    }
}

impl TryFrom<Rc<ConjuctiveGuard>> for Assertion {
    type Error = ExprToAssertFreeVarError;

    fn try_from(value: Rc<ConjuctiveGuard>) -> Result<Self, Self::Error> {
        if value.contains_free_variables() {
            return Err(ExprToAssertFreeVarError);
        }
        Ok(Self::ConjuctiveGuard(value))
    }
}

impl TryFrom<ImplicativeGuard> for Assertion {
    type Error = ExprToAssertFreeVarError;

    fn try_from(value: ImplicativeGuard) -> Result<Self, Self::Error> {
        Rc::new(value).try_into()
    }
}

impl TryFrom<Rc<ImplicativeGuard>> for Assertion {
    type Error = ExprToAssertFreeVarError;

    fn try_from(value: Rc<ImplicativeGuard>) -> Result<Self, Self::Error> {
        if value.contains_free_variables() {
            return Err(ExprToAssertFreeVarError);
        }
        Ok(Self::ImplicativeGuard(value))
    }
}

impl TryFrom<IfGuard> for Assertion {
    type Error = ExprToAssertionError;

    fn try_from(value: IfGuard) -> Result<Self, Self::Error> {
        Rc::new(value).try_into()
    }
}

impl TryFrom<Rc<IfGuard>> for Assertion {
    type Error = ExprToAssertionError;

    fn try_from(value: Rc<IfGuard>) -> Result<Self, Self::Error> {
        if value.contains_free_variables() {
            return Err(ExprToAssertFreeVarError.into());
        }
        NotWellDefinedExpression::try_from(value.collect_wdcs())
            .ok()
            .map_or(Ok(()), Err)?;
        Ok(Self::IfGuard(value))
    }
}

impl TryFrom<IsEnumerated> for Assertion {
    type Error = ExprToAssertionError;

    fn try_from(value: IsEnumerated) -> Result<Self, Self::Error> {
        Rc::new(value).try_into()
    }
}

impl TryFrom<Rc<IsEnumerated>> for Assertion {
    type Error = ExprToAssertionError;

    fn try_from(value: Rc<IsEnumerated>) -> Result<Self, Self::Error> {
        if value.contains_free_variables() {
            return Err(ExprToAssertFreeVarError.into());
        }
        NotWellDefinedExpression::try_from(value.collect_wdcs())
            .ok()
            .map_or(Ok(()), Err)?;
        Ok(Self::IsEnumerated(value))
    }
}

impl From<Definition> for Assertion {
    fn from(value: Definition) -> Self {
        Self::Definition(value.into())
    }
}

impl From<Rc<Definition>> for Assertion {
    fn from(value: Rc<Definition>) -> Self {
        Self::Definition(value)
    }
}

impl From<BoolExpr> for Assertion {
    fn from(value: BoolExpr) -> Self {
        Self::Bool(value.into())
    }
}

impl TryFrom<Expr> for Assertion {
    type Error = ExprToAssertionError;

    fn try_from(value: Expr) -> Result<Self, Self::Error> {
        match value {
            Expr::Ite(value) => Ok(value.try_into()?),
            Expr::BinOp(value) => Ok(value.try_into()?),
            Expr::ChainedCmp(value) => Ok(value.try_into()?),
            Expr::Negation(value) => Ok(value.try_into()?),
            Expr::Quantification(value) => Ok(value.try_into()?),
            Expr::Element(value) => Ok(ElementExpr::clone(&value).try_into()?),
            Expr::AppliedSymbol(value) => Ok(value.try_into()?),
            Expr::InEnumeration(value) => Ok(value.try_into()?),
            Expr::ConjuctiveGuard(value) => Ok(value.try_into()?),
            Expr::ImplicativeGuard(value) => Ok(value.try_into()?),
            Expr::IfGuard(value) => Ok(value.try_into()?),
            Expr::IsEnumerated(value) => Ok(value.try_into()?),
            Expr::Variable(_) => Err(ExprToAssertFreeVarError.into()),
            Expr::NumNegation(value) => Err(NotBoolExpr {
                found: value.codomain().into(),
            }
            .into()),
            Expr::CardinalityAggregate(value) => Err(NotBoolExpr {
                found: value.codomain().into(),
            }
            .into()),
            Expr::Aggregate(value) => Err(NotBoolExpr {
                found: value.codomain().into(),
            }
            .into()),
        }
    }
}

impl TryFrom<Formula> for Assertion {
    type Error = FormulaToAssertionError;

    fn try_from(value: Formula) -> Result<Self, Self::Error> {
        if value.contains_free_variables() {
            return Err(ExprToAssertFreeVarError.into());
        }
        let wdcs = value.collect_wdcs();
        NotWellDefinedExpression::try_from(wdcs)
            .ok()
            .map_or(Ok(()), Err)?;
        match value {
            Formula::AppliedSymbol(value) => Ok(Self::AppliedSymbol(value)),
            Formula::BinOp(value) => Ok(Self::BinOp(value)),
            Formula::ChainedCmp(value) => Ok(Self::ChainedCmp(value)),
            Formula::Negation(value) => Ok(Self::Negation(value)),
            Formula::InEnumeration(value) => Ok(Self::InEnumeration(value)),
            Formula::Quantification(value) => Ok(Self::Quantification(value)),
            Formula::Bool(value) => Ok(Self::Bool(value)),
            Formula::Ite(value) => Ok(Self::Ite(value)),
            Formula::ImplicativeGuard(value) => Ok(Self::ImplicativeGuard(value)),
            Formula::ConjuctiveGuard(value) => Ok(Self::ConjuctiveGuard(value)),
            Formula::IfGuard(value) => Ok(Self::IfGuard(value)),
            Formula::IsEnumerated(value) => Ok(Self::IsEnumerated(value)),
            Formula::Variable(_) => unreachable!(),
        }
    }
}

impl<'a> TryFrom<&'a Assertion> for ExprRef<'a> {
    type Error = &'a Definition;

    fn try_from(value: &'a Assertion) -> Result<Self, Self::Error> {
        use Assertion as A;
        match value {
            A::AppliedSymbol(value) => Ok(ExprRef::from(value)),
            A::BinOp(value) => Ok(ExprRef::from(value)),
            A::ChainedCmp(value) => Ok(ExprRef::from(value)),
            A::Negation(value) => Ok(ExprRef::from(value)),
            A::Quantification(value) => Ok(ExprRef::from(value)),
            A::Ite(value) => Ok(ExprRef::from(value)),
            A::Bool(value) => Ok(ExprRef::from(value)),
            A::InEnumeration(value) => Ok(ExprRef::from(value)),
            A::ConjuctiveGuard(value) => Ok(ExprRef::from(value)),
            A::ImplicativeGuard(value) => Ok(ExprRef::from(value)),
            A::IfGuard(value) => Ok(ExprRef::from(value)),
            A::IsEnumerated(value) => Ok(ExprRef::from(value)),
            A::Definition(value) => Err(value),
        }
    }
}

impl MetadataIm for Assertion {
    type Metadata = Metadata;
    fn metadata(&self) -> Option<&Metadata> {
        match self {
            Self::AppliedSymbol(value) => value.metadata(),
            Self::BinOp(value) => value.metadata(),
            Self::ChainedCmp(value) => value.metadata(),
            Self::Quantification(value) => value.metadata(),
            Self::Ite(value) => value.metadata(),
            Self::Negation(value) => value.metadata(),
            Self::Definition(value) => value.metadata(),
            Self::InEnumeration(value) => value.metadata(),
            Self::ConjuctiveGuard(value) => value.metadata(),
            Self::ImplicativeGuard(value) => value.metadata(),
            Self::IfGuard(value) => value.metadata(),
            Self::IsEnumerated(value) => value.metadata(),
            Self::Bool(value) => value.metadata(),
        }
    }
}

impl Assertion {
    pub fn vocab(&self) -> Option<&Vocabulary> {
        self.vocab_rc().map(|f| f.as_ref())
    }

    pub fn vocab_rc(&self) -> Option<&RcA<Vocabulary>> {
        match self {
            Self::AppliedSymbol(value) => value.vocab_rc(),
            Self::BinOp(value) => value.vocab_rc().into(),
            Self::ChainedCmp(value) => value.vocab_rc().into(),
            Self::Quantification(value) => value.vocab_rc().into(),
            Self::Ite(value) => value.vocab_rc().into(),
            Self::Negation(value) => value.vocab_rc().into(),
            Self::Definition(value) => value.vocab_rc().into(),
            Self::InEnumeration(value) => value.vocab_rc().into(),
            Self::ConjuctiveGuard(value) => value.vocab_rc().into(),
            Self::ImplicativeGuard(value) => value.vocab_rc().into(),
            Self::IfGuard(value) => value.vocab_rc().into(),
            Self::IsEnumerated(value) => value.vocab_rc().into(),
            Self::Bool(_) => None,
        }
    }
}
