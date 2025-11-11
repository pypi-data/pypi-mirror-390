use super::{Expr, ExprRef};
use crate::fodot::display_as_debug;
use crate::fodot::error::{
    NotWellDefinedCause, NotWellDefinedExpression, NotWellDefinedExpressionError,
};
use crate::fodot::fmt::FodotOptions;
use crate::fodot::fmt::{Fmt, FodotDisplay};
use std::fmt::{Debug, Display};

/// Condition for an expression to be well defined.
#[derive(Debug, Clone)]
pub struct WellDefinedCondition<'a> {
    pub(super) condition: Expr,
    pub(super) origin: ExprRef<'a>,
}

impl<'a> WellDefinedCondition<'a> {
    pub fn condition(&self) -> &Expr {
        &self.condition
    }

    pub fn origin(&self) -> ExprRef<'a> {
        self.origin
    }
}

/// An [Expr] that is well defined.
///
/// An expression is well defined if it has no well defined conditions.
#[derive(Clone, PartialEq, Eq)]
pub struct WellDefinedExpr(Expr);

impl FodotOptions for WellDefinedExpr {
    type Options<'a>
        = <Expr as FodotOptions>::Options<'a>
    where
        Self: 'a;
}

impl FodotDisplay for WellDefinedExpr {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        write!(f, "{}", fmt.with_opts(&fmt.value.0))
    }
}

impl Display for WellDefinedExpr {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

display_as_debug!(WellDefinedExpr);

impl WellDefinedExpr {
    pub fn expr(self) -> Expr {
        self.0
    }

    pub fn as_expr(&self) -> &Expr {
        &self.0
    }
}

impl AsRef<Expr> for WellDefinedExpr {
    fn as_ref(&self) -> &Expr {
        &self.0
    }
}

impl TryFrom<Expr> for WellDefinedExpr {
    type Error = NotWellDefinedExpressionError;

    fn try_from(value: Expr) -> Result<Self, Self::Error> {
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

impl<'a> From<&'a WellDefinedExpr> for ExprRef<'a> {
    fn from(value: &'a WellDefinedExpr) -> Self {
        ExprRef::from(&value.0)
    }
}
