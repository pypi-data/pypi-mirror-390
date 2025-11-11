use super::{
    ChainedCmp, Element, ElementExpr, Expr, ExprRef, Formula, FreeVariableIter, FreeVariables,
    Metadata, MetadataIm, MetadataMut, OrdOps, WellDefinedCondition, vocabs_ptr_eq,
};
use crate::fodot::display_as_debug;
use crate::fodot::error::{
    DivByZeroError, ExprBinOpError, ExprMismatchError, ExprSubMismatchError, NotBoolExpr,
    NotBoolExprError, SubTypeMismatch, TypeMismatch, VocabMismatchError,
};
use crate::fodot::fmt::{FodotOptions, FodotPrecDisplay};
use crate::fodot::{
    fmt::{Fmt, FodotDisplay, FormatOptions},
    structure::TypeInterpRef,
    vocabulary::{CustomTypeRef, Type, TypeRef, Vocabulary},
};
use sli_collections::rc::{Rc, RcA};
use std::fmt::{Debug, Display, Write};

/// All possible logical binary operations.
#[non_exhaustive]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum LogicBinOps {
    And,
    Or,
    Implication,
    Equivalence,
}

impl FodotOptions for LogicBinOps {
    type Options<'a>
        = FormatOptions
    where
        Self: 'a;
}

impl FodotDisplay for LogicBinOps {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        match fmt.value {
            LogicBinOps::And => fmt.options.write_and(f),
            LogicBinOps::Or => fmt.options.write_or(f),
            LogicBinOps::Implication => fmt.options.write_rimpl(f),
            LogicBinOps::Equivalence => fmt.options.write_eqv(f),
        }
    }
}

impl Display for LogicBinOps {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", Fmt::with_defaults(self))
    }
}

impl LogicBinOps {
    pub fn precedence(&self) -> u32 {
        match self {
            Self::And => 30,
            Self::Or => 20,
            Self::Implication | Self::Equivalence => 10,
        }
    }
}

#[derive(Clone)]
pub struct LogicBinOp {
    op: LogicBinOps,
    lhs: Formula,
    rhs: Formula,
    metadata: Option<Box<Metadata>>,
}

impl FodotOptions for LogicBinOp {
    type Options<'a>
        = FormatOptions
    where
        Self: 'a;
}

impl FodotDisplay for LogicBinOp {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        Self::fmt_with_prec(fmt, f, 0)
    }
}

impl FodotPrecDisplay for LogicBinOp {
    fn fmt_with_prec(
        fmt: Fmt<&Self, <Self as FodotOptions>::Options<'_>>,
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
            "{} {} {}",
            fmt.with_format_opts(&fmt.value.lhs).with_prec(this_prec),
            fmt.with_format_opts(&fmt.value.op),
            fmt.with_format_opts(&fmt.value.rhs).with_prec(this_prec),
        )?;
        if needs_bracket {
            f.write_char(')')?;
        }
        Ok(())
    }
}

impl Display for LogicBinOp {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", Fmt::with_defaults(self))
    }
}

impl PartialEq<BinOpRef<'_>> for LogicBinOp {
    fn eq(&self, other: &BinOpRef<'_>) -> bool {
        BinOps::from(self.op()) == other.op()
            && self.lhs() == &other.lhs()
            && self.rhs() == &other.rhs()
    }
}

impl PartialEq<LogicBinOp> for BinOpRef<'_> {
    fn eq(&self, other: &LogicBinOp) -> bool {
        LogicBinOp::eq(other, self)
    }
}

display_as_debug!(LogicBinOp);

impl PartialEq for LogicBinOp {
    fn eq(&self, other: &Self) -> bool {
        self.op == other.op && self.lhs == other.lhs && self.rhs == other.rhs
    }
}

impl Eq for LogicBinOp {}

impl From<LogicBinOp> for Formula {
    fn from(value: LogicBinOp) -> Self {
        Self::BinOp(value.into())
    }
}

impl LogicBinOp {
    /// Try to create a binary operation between the two given expression using the given binary
    /// operator.
    pub fn new(lhs: Formula, op: LogicBinOps, rhs: Formula) -> Result<Self, VocabMismatchError> {
        if !vocabs_ptr_eq(rhs.vocab(), lhs.vocab()) {
            return Err(VocabMismatchError);
        }
        Ok(Self {
            lhs,
            op,
            rhs,
            metadata: Default::default(),
        })
    }

    pub fn precedence(&self) -> u32 {
        self.op().precedence()
    }

    pub fn vocab_rc(&self) -> Option<&RcA<Vocabulary>> {
        self.lhs.vocab_rc().or_else(|| self.rhs.vocab_rc())
    }

    pub fn vocab(&self) -> Option<&Vocabulary> {
        self.vocab_rc().map(|f| f.as_ref())
    }

    pub fn codomain(&self) -> TypeRef {
        Type::Bool
    }

    /// Returns the operator.
    pub fn op(&self) -> LogicBinOps {
        self.op
    }

    /// Returns the left hand side of the binary operation.
    pub fn lhs(&self) -> &Formula {
        &self.lhs
    }

    /// Returns the right hand side of the binary operation.
    pub fn rhs(&self) -> &Formula {
        &self.rhs
    }

    pub fn syntax_eq(&self, other: &Self) -> bool {
        let op = if self.op() == other.op() {
            self.op()
        } else {
            return false;
        };
        match op {
            LogicBinOps::And | LogicBinOps::Or | LogicBinOps::Equivalence => {
                (self.lhs() == other.lhs() && self.rhs() == other.rhs())
                    || (self.lhs() == other.rhs() && other.lhs() == self.rhs())
            }
            _ => self == other,
        }
    }

    pub(super) fn any_conjunction<F: Fn(ExprRef) -> bool>(&self, f: &F) -> bool {
        if self.op() != LogicBinOps::And {
            return false;
        }
        let left = match self.lhs() {
            Formula::BinOp(BinOpFormula::Logic(bin_op)) if bin_op.op() == LogicBinOps::And => {
                bin_op.any_conjunction(f)
            }
            value => f(value.as_ref()),
        };
        if left {
            return true;
        }
        match self.rhs() {
            Formula::BinOp(BinOpFormula::Logic(bin_op)) if bin_op.op() == LogicBinOps::And => {
                bin_op.any_conjunction(f)
            }
            value => f(value.as_ref()),
        }
    }

    pub fn collect_wdcs<'a>(this: &'a Rc<Self>) -> Vec<WellDefinedCondition<'a>> {
        let mut rhs_wdcs = this.rhs.collect_wdcs();
        if matches!(this.op(), LogicBinOps::And | LogicBinOps::Implication) {
            rhs_wdcs.retain(|f| {
                !(this.lhs.as_ref().syntax_eq(&f.condition().as_ref())
                    || this.lhs().as_ref().any_conjunction(|conj_subform| {
                        conj_subform.syntax_eq(&f.condition.as_ref())
                    }))
            });
        }
        let mut lhs_wdcs = this.lhs.collect_wdcs();
        lhs_wdcs.append(&mut rhs_wdcs);
        lhs_wdcs
    }
}

impl FreeVariables for LogicBinOp {
    fn add_to_free_variable_iter<'a>(&'a self, iter: &mut FreeVariableIter<'a>) {
        iter.add_expr(self.lhs().into());
        iter.add_expr(self.rhs().into());
    }
}

impl MetadataIm for LogicBinOp {
    type Metadata = Metadata;
    fn metadata(&self) -> Option<&Metadata> {
        self.metadata.as_deref()
    }
}

impl MetadataMut for LogicBinOp {
    fn metadata_mut(&mut self) -> &mut Metadata {
        self.metadata.get_or_insert_default()
    }
}

/// All possible logical binary operations.
#[non_exhaustive]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ArithBinOps {
    Add,
    Subtract,
    Mult,
    Rem,
    Division,
}

impl FodotOptions for ArithBinOps {
    type Options<'a>
        = FormatOptions
    where
        Self: 'a;
}

impl FodotDisplay for ArithBinOps {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        match fmt.value {
            ArithBinOps::Add => f.write_char('+'),
            ArithBinOps::Subtract => f.write_char('-'),
            ArithBinOps::Rem => f.write_char('%'),
            ArithBinOps::Mult => fmt.options.write_product(f),
            ArithBinOps::Division => f.write_char('/'),
        }
    }
}

impl Display for ArithBinOps {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", Fmt::with_defaults(self))
    }
}

impl PartialEq<BinOpRef<'_>> for ArithBinOp {
    fn eq(&self, other: &BinOpRef<'_>) -> bool {
        BinOps::from(self.op()) == other.op()
            && self.lhs() == &other.lhs()
            && self.rhs() == &other.rhs()
    }
}

impl PartialEq<ArithBinOp> for BinOpRef<'_> {
    fn eq(&self, other: &ArithBinOp) -> bool {
        ArithBinOp::eq(other, self)
    }
}

impl ArithBinOps {
    pub fn precedence(&self) -> u32 {
        match self {
            Self::Add | Self::Subtract => 60,
            Self::Mult | Self::Division | Self::Rem => 70,
        }
    }
}

#[derive(Clone)]
pub struct ArithBinOp {
    op: ArithBinOps,
    lhs: Expr,
    rhs: Expr,
    metadata: Option<Box<Metadata>>,
}

impl FodotOptions for ArithBinOp {
    type Options<'a>
        = FormatOptions
    where
        Self: 'a;
}

impl FodotDisplay for ArithBinOp {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        Self::fmt_with_prec(fmt, f, 0)
    }
}

impl FodotPrecDisplay for ArithBinOp {
    fn fmt_with_prec(
        fmt: Fmt<&Self, <Self as FodotOptions>::Options<'_>>,
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
            "{} {} {}",
            fmt.with_format_opts(&fmt.value.lhs).with_prec(this_prec),
            fmt.with_format_opts(&fmt.value.op),
            fmt.with_format_opts(&fmt.value.rhs).with_prec(this_prec),
        )?;
        if needs_bracket {
            f.write_char(')')?;
        }
        Ok(())
    }
}

impl Display for ArithBinOp {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", Fmt::with_defaults(self))
    }
}

display_as_debug!(ArithBinOp);

impl PartialEq for ArithBinOp {
    fn eq(&self, other: &Self) -> bool {
        self.op == other.op && self.lhs == other.lhs && self.rhs == other.rhs
    }
}

impl Eq for ArithBinOp {}

impl ArithBinOp {
    /// Try to create a binary operation between the two given expression using the given binary
    /// operator.
    pub fn new(lhs: Expr, op: ArithBinOps, rhs: Expr) -> Result<Self, ExprBinOpError> {
        if !vocabs_ptr_eq(rhs.vocab(), lhs.vocab()) {
            return Err(VocabMismatchError.into());
        }
        match (op, &rhs) {
            (ArithBinOps::Division | ArithBinOps::Rem, Expr::Element(el)) => match el.as_ref() {
                ElementExpr {
                    element: Element::Int(value),
                    ..
                } if *value == 0 => return Err(DivByZeroError.into()),
                ElementExpr {
                    element: Element::Real(value),
                    ..
                } if *value == 0 => return Err(DivByZeroError.into()),
                _ => {}
            },
            _ => {}
        }
        let codomain_left = lhs.codomain();
        let codomain_right = rhs.codomain();

        if !codomain_left.is_subtype(&TypeRef::Real) {
            return Err(SubTypeMismatch {
                expected: TypeRef::Real.into(),
                found: codomain_left.into(),
            }
            .into());
        } else if !codomain_right.is_subtype(&TypeRef::Real) {
            return Err(SubTypeMismatch {
                expected: TypeRef::Real.into(),
                found: codomain_right.into(),
            }
            .into());
        }

        Ok(Self {
            lhs,
            op,
            rhs,
            metadata: Default::default(),
        })
    }

    pub fn precedence(&self) -> u32 {
        self.op().precedence()
    }

    pub fn vocab_rc(&self) -> Option<&RcA<Vocabulary>> {
        self.lhs.vocab_rc().or_else(|| self.rhs.vocab_rc())
    }

    pub fn vocab(&self) -> Option<&Vocabulary> {
        self.vocab_rc().map(|f| f.as_ref())
    }

    pub fn codomain(&self) -> TypeRef {
        match self.op {
            ArithBinOps::Division => Type::Real,
            ArithBinOps::Add | ArithBinOps::Subtract | ArithBinOps::Mult | ArithBinOps::Rem => {
                let codomain_left = self.lhs.codomain();
                let codomain_right = self.rhs.codomain();
                match (codomain_left, codomain_right) {
                    (Type::Int | Type::IntType(_), Type::Int | Type::IntType(_)) => Type::Int,
                    (Type::Int | Type::IntType(_), Type::Real | Type::RealType(_))
                    | (Type::Real | Type::RealType(_), Type::Int | Type::IntType(_))
                    | (Type::Real | Type::RealType(_), Type::Real | Type::RealType(_)) => {
                        Type::Real
                    }
                    _ => unreachable!(),
                }
            }
        }
    }

    /// Returns the operator.
    pub fn op(&self) -> ArithBinOps {
        self.op
    }

    /// Returns the left hand side of the binary operation.
    pub fn lhs(&self) -> &Expr {
        &self.lhs
    }

    /// Returns the right hand side of the binary operation.
    pub fn rhs(&self) -> &Expr {
        &self.rhs
    }

    pub fn syntax_eq(&self, other: &Self) -> bool {
        let op = if self.op() == other.op() {
            self.op()
        } else {
            return false;
        };
        match op {
            ArithBinOps::Add | ArithBinOps::Mult => {
                (self.lhs() == other.lhs() && self.rhs() == other.rhs())
                    || (self.lhs() == other.rhs() && other.lhs() == self.rhs())
            }
            _ => self == other,
        }
    }

    pub fn collect_wdcs<'a>(this: &'a Rc<Self>) -> Vec<WellDefinedCondition<'a>> {
        let mut extras = match this.op {
            ArithBinOps::Division | ArithBinOps::Rem => match &this.rhs {
                Expr::Element(_) => Vec::new(),
                _ => {
                    // If 0 is (potentially) contained in codomain of rhs, create wdc
                    if CustomTypeRef::try_from(this.rhs().codomain())
                        .map(|f| {
                            f.vocab()
                                .get_interp(f)
                                .unwrap() // Cannot be a vocabulary mismatch
                                .map(|custom_codomain| match custom_codomain {
                                    TypeInterpRef::Real(value) => value.contains(0.into()),
                                    TypeInterpRef::Int(value) => value.contains(0),
                                    _ => unreachable!(),
                                })
                                .unwrap_or(true)
                        })
                        .unwrap_or(true)
                    {
                        vec![WellDefinedCondition {
                            condition: BinOp::new(this.rhs.clone(), BinOps::NotEqual, 0.into())
                                .unwrap()
                                .into(),
                            origin: ExprRef::BinOp(this.into()),
                        }]
                    } else {
                        Vec::new()
                    }
                }
            },
            _ => Vec::new(),
        };
        extras.append(
            &mut core::iter::once(&this.lhs)
                .chain(core::iter::once(&this.rhs))
                .flat_map(|f| f.collect_wdcs())
                .collect(),
        );
        extras
    }
}

impl FreeVariables for ArithBinOp {
    fn add_to_free_variable_iter<'a>(&'a self, iter: &mut FreeVariableIter<'a>) {
        iter.add_expr(self.lhs().into());
        iter.add_expr(self.rhs().into());
    }
}

impl MetadataIm for ArithBinOp {
    type Metadata = Metadata;
    fn metadata(&self) -> Option<&Metadata> {
        self.metadata.as_deref()
    }
}

impl MetadataMut for ArithBinOp {
    fn metadata_mut(&mut self) -> &mut Metadata {
        self.metadata.get_or_insert_default()
    }
}

#[non_exhaustive]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum EqualityBinOps {
    Equal,
    NotEqual,
}

impl FodotOptions for EqualityBinOps {
    type Options<'a>
        = FormatOptions
    where
        Self: 'a;
}

impl FodotDisplay for EqualityBinOps {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        match fmt.value {
            Self::Equal => write!(f, "="),
            Self::NotEqual => fmt.options.write_neq(f),
        }
    }
}

impl Display for EqualityBinOps {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", Fmt::with_defaults(self))
    }
}

impl EqualityBinOps {
    pub fn precedence(&self) -> u32 {
        30
    }
}

#[derive(Clone)]
pub struct EqualityBinOp {
    op: EqualityBinOps,
    lhs: Expr,
    rhs: Expr,
    metadata: Option<Box<Metadata>>,
}

impl FodotOptions for EqualityBinOp {
    type Options<'a>
        = FormatOptions
    where
        Self: 'a;
}

impl FodotDisplay for EqualityBinOp {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        Self::fmt_with_prec(fmt, f, 0)
    }
}

impl FodotPrecDisplay for EqualityBinOp {
    fn fmt_with_prec(
        fmt: Fmt<&Self, <Self as FodotOptions>::Options<'_>>,
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
            "{} {} {}",
            fmt.with_format_opts(&fmt.value.lhs).with_prec(this_prec),
            fmt.with_format_opts(&fmt.value.op),
            fmt.with_format_opts(&fmt.value.rhs).with_prec(this_prec),
        )?;
        if needs_bracket {
            f.write_char(')')?;
        }
        Ok(())
    }
}

impl Display for EqualityBinOp {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", Fmt::with_defaults(self))
    }
}

display_as_debug!(EqualityBinOp);

impl PartialEq for EqualityBinOp {
    fn eq(&self, other: &Self) -> bool {
        self.lhs == other.lhs && self.rhs == other.rhs
    }
}

impl Eq for EqualityBinOp {}

impl From<EqualityBinOp> for Formula {
    fn from(value: EqualityBinOp) -> Self {
        Self::BinOp(value.into())
    }
}

impl PartialEq<BinOpRef<'_>> for EqualityBinOp {
    fn eq(&self, other: &BinOpRef<'_>) -> bool {
        BinOps::from(self.op()) == other.op()
            && self.lhs() == &other.lhs()
            && self.rhs() == &other.rhs()
    }
}

impl PartialEq<EqualityBinOp> for BinOpRef<'_> {
    fn eq(&self, other: &EqualityBinOp) -> bool {
        EqualityBinOp::eq(other, self)
    }
}

impl EqualityBinOp {
    /// Try to create a binary operation between the two given expression using the given binary
    /// operator.
    pub fn new(lhs: Expr, op: EqualityBinOps, rhs: Expr) -> Result<Self, ExprMismatchError> {
        if !vocabs_ptr_eq(rhs.vocab(), lhs.vocab()) {
            return Err(VocabMismatchError.into());
        }
        if lhs.codomain().into_root_type() != rhs.codomain().into_root_type() {
            return Err(TypeMismatch {
                found: rhs.codomain().into(),
                expected: lhs.codomain().into(),
            }
            .into());
        }
        Ok(Self {
            op,
            lhs,
            rhs,
            metadata: Default::default(),
        })
    }

    pub fn precedence(&self) -> u32 {
        self.op().precedence()
    }

    pub fn vocab_rc(&self) -> Option<&RcA<Vocabulary>> {
        self.lhs.vocab_rc().or_else(|| self.rhs.vocab_rc())
    }

    pub fn vocab(&self) -> Option<&Vocabulary> {
        self.vocab_rc().map(|f| f.as_ref())
    }

    pub fn codomain(&self) -> TypeRef {
        Type::Bool
    }

    pub fn op(&self) -> EqualityBinOps {
        self.op
    }

    /// Returns the left hand side of the binary operation.
    pub fn lhs(&self) -> &Expr {
        &self.lhs
    }

    /// Returns the right hand side of the binary operation.
    pub fn rhs(&self) -> &Expr {
        &self.rhs
    }

    pub fn syntax_eq(&self, other: &Self) -> bool {
        if self.op() != other.op() {
            return false;
        };
        (self.lhs() == other.lhs() && self.rhs() == other.rhs())
            || (self.lhs() == other.rhs() && other.lhs() == self.rhs())
    }

    pub fn collect_wdcs<'a>(this: &'a Rc<Self>) -> Vec<WellDefinedCondition<'a>> {
        core::iter::once(&this.lhs)
            .chain(core::iter::once(&this.rhs))
            .flat_map(|f| f.collect_wdcs())
            .collect()
    }
}

impl FreeVariables for EqualityBinOp {
    fn add_to_free_variable_iter<'a>(&'a self, iter: &mut FreeVariableIter<'a>) {
        iter.add_expr(self.lhs().into());
        iter.add_expr(self.rhs().into());
    }
}

impl MetadataIm for EqualityBinOp {
    type Metadata = Metadata;
    fn metadata(&self) -> Option<&Metadata> {
        self.metadata.as_deref()
    }
}

impl MetadataMut for EqualityBinOp {
    fn metadata_mut(&mut self) -> &mut Metadata {
        self.metadata.get_or_insert_default()
    }
}

/// All possible binary ordering operations.
#[non_exhaustive]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CmpBinOps {
    LessThan,
    LessOrEqual,
    GreaterThan,
    GreaterOrEqual,
}

impl FodotOptions for CmpBinOps {
    type Options<'a>
        = FormatOptions
    where
        Self: 'a;
}

impl FodotDisplay for CmpBinOps {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        match fmt.value {
            CmpBinOps::LessThan => f.write_char('<'),
            CmpBinOps::LessOrEqual => fmt.options.write_le(f),
            CmpBinOps::GreaterThan => f.write_char('>'),
            CmpBinOps::GreaterOrEqual => fmt.options.write_ge(f),
        }
    }
}

impl Display for CmpBinOps {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", Fmt::with_defaults(self))
    }
}

impl CmpBinOps {
    pub fn precedence(&self) -> u32 {
        30
    }

    pub fn reversed(self) -> Self {
        match self {
            Self::LessThan => Self::GreaterThan,
            Self::GreaterThan => Self::LessThan,
            Self::LessOrEqual => Self::GreaterOrEqual,
            Self::GreaterOrEqual => Self::LessOrEqual,
        }
    }
}

#[derive(Clone)]
pub struct CmpBinOp {
    op: CmpBinOps,
    lhs: Expr,
    rhs: Expr,
    metadata: Option<Box<Metadata>>,
}

impl FodotOptions for CmpBinOp {
    type Options<'a>
        = FormatOptions
    where
        Self: 'a;
}

impl FodotDisplay for CmpBinOp {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        // TODO add precedence info to remove brackets if possible
        write!(
            f,
            "({} {} {})",
            fmt.with_format_opts(&fmt.value.lhs),
            fmt.with_format_opts(&fmt.value.op),
            fmt.with_format_opts(&fmt.value.rhs),
        )
    }
}

impl FodotPrecDisplay for CmpBinOp {
    fn fmt_with_prec(
        fmt: Fmt<&Self, <Self as FodotOptions>::Options<'_>>,
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
            "{} {} {}",
            fmt.with_format_opts(&fmt.value.lhs).with_prec(this_prec),
            fmt.with_format_opts(&fmt.value.op),
            fmt.with_format_opts(&fmt.value.rhs).with_prec(this_prec),
        )?;
        if needs_bracket {
            f.write_char(')')?;
        }
        Ok(())
    }
}

impl Display for CmpBinOp {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", Fmt::with_defaults(self))
    }
}

display_as_debug!(CmpBinOp);

impl PartialEq for CmpBinOp {
    fn eq(&self, other: &Self) -> bool {
        self.op == other.op && self.lhs == other.lhs && self.rhs == other.rhs
    }
}

impl Eq for CmpBinOp {}

impl PartialEq<BinOpRef<'_>> for CmpBinOp {
    fn eq(&self, other: &BinOpRef<'_>) -> bool {
        BinOps::from(self.op()) == other.op()
            && self.lhs() == &other.lhs()
            && self.rhs() == &other.rhs()
    }
}

impl PartialEq<CmpBinOp> for BinOpRef<'_> {
    fn eq(&self, other: &CmpBinOp) -> bool {
        CmpBinOp::eq(other, self)
    }
}

impl CmpBinOp {
    /// Try to create a binary operation between the two given expression using the given binary
    /// operator.
    pub fn new(lhs: Expr, op: CmpBinOps, rhs: Expr) -> Result<Self, ExprSubMismatchError> {
        ChainedCmp::check_expr(&lhs, op.into(), &rhs)?;
        Ok(Self {
            lhs,
            op,
            rhs,
            metadata: Default::default(),
        })
    }

    pub fn precedence(&self) -> u32 {
        self.op().precedence()
    }

    pub fn vocab_rc(&self) -> Option<&RcA<Vocabulary>> {
        self.lhs.vocab_rc().or_else(|| self.rhs.vocab_rc())
    }

    pub fn vocab(&self) -> Option<&Vocabulary> {
        self.vocab_rc().map(|f| f.as_ref())
    }

    pub fn codomain(&self) -> TypeRef {
        Type::Bool
    }

    /// Returns the operator.
    pub fn op(&self) -> CmpBinOps {
        self.op
    }

    /// Returns the left hand side of the binary operation.
    pub fn lhs(&self) -> &Expr {
        &self.lhs
    }

    /// Returns the right hand side of the binary operation.
    pub fn rhs(&self) -> &Expr {
        &self.rhs
    }

    pub fn syntax_eq(&self, other: &Self) -> bool {
        match (self.op(), other.op()) {
            (left, right) if left == right => {
                self.lhs() == other.lhs() && other.rhs() == self.rhs()
            }
            (left, right) if left == right.reversed() => {
                self.lhs() == other.rhs() && other.lhs() == self.rhs()
            }
            _ => self == other,
        }
    }

    pub fn collect_wdcs<'a>(this: &'a Rc<Self>) -> Vec<WellDefinedCondition<'a>> {
        core::iter::once(&this.lhs)
            .chain(core::iter::once(&this.rhs))
            .flat_map(|f| f.collect_wdcs())
            .collect()
    }
}

impl FreeVariables for CmpBinOp {
    fn add_to_free_variable_iter<'a>(&'a self, iter: &mut FreeVariableIter<'a>) {
        iter.add_expr(self.lhs().into());
        iter.add_expr(self.rhs().into());
    }
}

impl MetadataIm for CmpBinOp {
    type Metadata = Metadata;
    fn metadata(&self) -> Option<&Metadata> {
        self.metadata.as_deref()
    }
}

impl MetadataMut for CmpBinOp {
    fn metadata_mut(&mut self) -> &mut Metadata {
        self.metadata.get_or_insert_default()
    }
}

#[derive(PartialEq, Eq, Clone)]
pub enum BinOp {
    Logic(Rc<LogicBinOp>),
    Arithmetic(Rc<ArithBinOp>),
    Equality(Rc<EqualityBinOp>),
    Cmp(Rc<CmpBinOp>),
}

impl FodotOptions for BinOp {
    type Options<'a>
        = FormatOptions
    where
        Self: 'a;
}

impl FodotDisplay for BinOp {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        FodotDisplay::fmt(fmt.with_opts(&BinOpRef::from(fmt.value)), f)
    }
}

impl Display for BinOp {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", Fmt::with_defaults(self))
    }
}

display_as_debug!(BinOp);

impl From<LogicBinOp> for BinOp {
    fn from(value: LogicBinOp) -> Self {
        Self::Logic(value.into())
    }
}

impl From<ArithBinOp> for BinOp {
    fn from(value: ArithBinOp) -> Self {
        Self::Arithmetic(value.into())
    }
}

impl From<EqualityBinOp> for BinOp {
    fn from(value: EqualityBinOp) -> Self {
        Self::Equality(value.into())
    }
}

impl From<CmpBinOp> for BinOp {
    fn from(value: CmpBinOp) -> Self {
        Self::Cmp(value.into())
    }
}

impl<'a> From<&'a BinOp> for BinOpRef<'a> {
    fn from(value: &'a BinOp) -> Self {
        match value {
            BinOp::Logic(value) => Self::Logic(value),
            BinOp::Arithmetic(value) => Self::Arithmetic(value),
            BinOp::Equality(value) => Self::Equality(value),
            BinOp::Cmp(value) => Self::Cmp(value),
        }
    }
}

impl PartialEq<BinOpRef<'_>> for BinOp {
    fn eq(&self, other: &BinOpRef<'_>) -> bool {
        self.op() == other.op() && self.lhs() == other.lhs() && self.rhs() == other.rhs()
    }
}

impl PartialEq<BinOp> for BinOpRef<'_> {
    fn eq(&self, other: &BinOp) -> bool {
        BinOp::eq(other, self)
    }
}

impl BinOp {
    /// Try to create a binary operation between the two given expressions using the given binary
    /// operator.
    pub fn new(lhs: Expr, op: BinOps, rhs: Expr) -> Result<Self, ExprBinOpError> {
        match SplitBinOps::from(op) {
            SplitBinOps::Logic(op) => {
                Ok(LogicBinOp::new(lhs.try_into()?, op, rhs.try_into()?)?.into())
            }
            SplitBinOps::Arithmetic(op) => Ok(ArithBinOp::new(lhs, op, rhs)?.into()),
            SplitBinOps::Equality(op) => Ok(EqualityBinOp::new(lhs, op, rhs)?.into()),
            SplitBinOps::Cmp(op) => Ok(CmpBinOp::new(lhs, op, rhs)?.into()),
        }
    }

    pub fn precedence(&self) -> u32 {
        self.op().precedence()
    }

    pub fn vocab_rc(&self) -> Option<&RcA<Vocabulary>> {
        BinOpRef::from(self).vocab_rc()
    }

    pub fn vocab(&self) -> Option<&Vocabulary> {
        self.vocab_rc().map(|f| f.as_ref())
    }

    pub fn codomain(&self) -> TypeRef {
        BinOpRef::from(self).codomain()
    }

    /// Returns the operator.
    pub fn op(&self) -> BinOps {
        BinOpRef::from(self).op()
    }

    /// Returns the left hand side of the binary operation.
    pub fn lhs(&self) -> ExprRef {
        BinOpRef::from(self).lhs()
    }

    /// Returns the right hand side of the binary operation.
    pub fn rhs(&self) -> ExprRef {
        BinOpRef::from(self).rhs()
    }

    pub fn syntax_eq(&self, other: &Self) -> bool {
        match (self, other) {
            (Self::Logic(value1), Self::Logic(value2)) => value1.syntax_eq(value2),
            (Self::Arithmetic(value1), Self::Arithmetic(value2)) => value1.syntax_eq(value2),
            (Self::Equality(value1), Self::Equality(value2)) => value1.syntax_eq(value2),
            (Self::Cmp(value1), Self::Cmp(value2)) => value1.syntax_eq(value2),
            _ => false,
        }
    }

    pub fn collect_wdcs<'a>(&'a self) -> Vec<WellDefinedCondition<'a>> {
        BinOpRef::from(self).collect_wdcs()
    }
}

impl FreeVariables for BinOp {
    fn add_to_free_variable_iter<'a>(&'a self, iter: &mut FreeVariableIter<'a>) {
        match self {
            Self::Logic(value) => FreeVariables::add_to_free_variable_iter(value.as_ref(), iter),
            Self::Arithmetic(value) => {
                FreeVariables::add_to_free_variable_iter(value.as_ref(), iter)
            }
            Self::Equality(value) => FreeVariables::add_to_free_variable_iter(value.as_ref(), iter),
            Self::Cmp(value) => FreeVariables::add_to_free_variable_iter(value.as_ref(), iter),
        }
    }
}

impl MetadataIm for BinOp {
    type Metadata = Metadata;
    fn metadata(&self) -> Option<&Metadata> {
        match self {
            Self::Logic(value) => MetadataIm::metadata(value.as_ref()),
            Self::Arithmetic(value) => MetadataIm::metadata(value.as_ref()),
            Self::Equality(value) => MetadataIm::metadata(value.as_ref()),
            Self::Cmp(value) => MetadataIm::metadata(value.as_ref()),
        }
    }
}

impl MetadataMut for BinOp {
    fn metadata_mut(&mut self) -> &mut Metadata {
        match self {
            Self::Logic(value) => MetadataMut::metadata_mut(Rc::make_mut(value)),
            Self::Arithmetic(value) => MetadataMut::metadata_mut(Rc::make_mut(value)),
            Self::Equality(value) => MetadataMut::metadata_mut(Rc::make_mut(value)),
            Self::Cmp(value) => MetadataMut::metadata_mut(Rc::make_mut(value)),
        }
    }
}

#[derive(PartialEq, Eq, Clone)]
pub enum BinOpFormula {
    Logic(Rc<LogicBinOp>),
    Equality(Rc<EqualityBinOp>),
    Cmp(Rc<CmpBinOp>),
}

impl FodotOptions for BinOpFormula {
    type Options<'a>
        = FormatOptions
    where
        Self: 'a;
}

impl FodotDisplay for BinOpFormula {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        Self::fmt_with_prec(fmt, f, 0)
    }
}

impl FodotPrecDisplay for BinOpFormula {
    fn fmt_with_prec(
        fmt: Fmt<&Self, <Self as FodotOptions>::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
        super_prec: u32,
    ) -> std::fmt::Result {
        BinOpRef::fmt_with_prec(fmt.with_opts(&BinOpRef::from(fmt.value)), f, super_prec)
    }
}

impl Display for BinOpFormula {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", Fmt::with_defaults(self))
    }
}

display_as_debug!(BinOpFormula);

impl From<LogicBinOp> for BinOpFormula {
    fn from(value: LogicBinOp) -> Self {
        Self::Logic(value.into())
    }
}

impl From<Rc<LogicBinOp>> for BinOpFormula {
    fn from(value: Rc<LogicBinOp>) -> Self {
        Self::Logic(value)
    }
}

impl From<EqualityBinOp> for BinOpFormula {
    fn from(value: EqualityBinOp) -> Self {
        Self::Equality(value.into())
    }
}

impl From<Rc<EqualityBinOp>> for BinOpFormula {
    fn from(value: Rc<EqualityBinOp>) -> Self {
        Self::Equality(value)
    }
}

impl From<CmpBinOp> for BinOpFormula {
    fn from(value: CmpBinOp) -> Self {
        Self::Cmp(value.into())
    }
}

impl From<Rc<CmpBinOp>> for BinOpFormula {
    fn from(value: Rc<CmpBinOp>) -> Self {
        Self::Cmp(value)
    }
}

impl<'a> From<&'a BinOpFormula> for BinOpRef<'a> {
    fn from(value: &'a BinOpFormula) -> Self {
        match value {
            BinOpFormula::Logic(value) => Self::Logic(value),
            BinOpFormula::Equality(value) => Self::Equality(value),
            BinOpFormula::Cmp(value) => Self::Cmp(value),
        }
    }
}

impl TryFrom<BinOp> for BinOpFormula {
    type Error = NotBoolExprError;

    fn try_from(value: BinOp) -> Result<Self, Self::Error> {
        match value {
            BinOp::Logic(value) => Ok(BinOpFormula::Logic(value)),
            BinOp::Cmp(value) => Ok(BinOpFormula::Cmp(value)),
            BinOp::Equality(value) => Ok(BinOpFormula::Equality(value)),
            BinOp::Arithmetic(value) => Err(NotBoolExpr {
                found: value.codomain().into(),
            }
            .into()),
        }
    }
}

impl From<BinOpFormula> for BinOp {
    fn from(value: BinOpFormula) -> Self {
        match value {
            BinOpFormula::Logic(value) => Self::Logic(value),
            BinOpFormula::Equality(value) => Self::Equality(value),
            BinOpFormula::Cmp(value) => Self::Cmp(value),
        }
    }
}

impl From<BinOpFormula> for Expr {
    fn from(value: BinOpFormula) -> Self {
        BinOp::from(value).into()
    }
}

impl<'a> From<&'a BinOpFormula> for ExprRef<'a> {
    fn from(value: &'a BinOpFormula) -> Self {
        BinOpRef::from(value).into()
    }
}

impl PartialEq<BinOpRef<'_>> for BinOpFormula {
    fn eq(&self, other: &BinOpRef<'_>) -> bool {
        self.op() == other.op() && self.lhs() == other.lhs() && self.rhs() == other.rhs()
    }
}

impl PartialEq<BinOpFormula> for BinOpRef<'_> {
    fn eq(&self, other: &BinOpFormula) -> bool {
        BinOpFormula::eq(other, self)
    }
}

impl BinOpFormula {
    pub fn vocab_rc(&self) -> Option<&RcA<Vocabulary>> {
        BinOpRef::from(self).vocab_rc()
    }

    pub fn vocab(&self) -> Option<&Vocabulary> {
        self.vocab_rc().map(|f| f.as_ref())
    }

    pub fn codomain(&self) -> TypeRef {
        BinOpRef::from(self).codomain()
    }

    pub fn precedence(&self) -> u32 {
        self.op().precedence()
    }

    /// Returns the operator.
    pub fn op(&self) -> BinOps {
        BinOpRef::from(self).op()
    }

    /// Returns the left hand side of the binary operation.
    pub fn lhs(&self) -> ExprRef {
        BinOpRef::from(self).lhs()
    }

    /// Returns the right hand side of the binary operation.
    pub fn rhs(&self) -> ExprRef {
        BinOpRef::from(self).rhs()
    }

    pub fn syntax_eq(&self, other: &Self) -> bool {
        match (self, other) {
            (Self::Logic(value1), Self::Logic(value2)) => value1.syntax_eq(value2),
            (Self::Equality(value1), Self::Equality(value2)) => value1.syntax_eq(value2),
            (Self::Cmp(value1), Self::Cmp(value2)) => value1.syntax_eq(value2),
            _ => false,
        }
    }

    pub fn collect_wdcs<'a>(&'a self) -> Vec<WellDefinedCondition<'a>> {
        BinOpRef::from(self).collect_wdcs()
    }
}

impl FreeVariables for BinOpFormula {
    fn add_to_free_variable_iter<'a>(&'a self, iter: &mut FreeVariableIter<'a>) {
        match self {
            Self::Logic(value) => FreeVariables::add_to_free_variable_iter(value.as_ref(), iter),
            Self::Equality(value) => FreeVariables::add_to_free_variable_iter(value.as_ref(), iter),
            Self::Cmp(value) => FreeVariables::add_to_free_variable_iter(value.as_ref(), iter),
        }
    }
}

impl MetadataIm for BinOpFormula {
    type Metadata = Metadata;
    fn metadata(&self) -> Option<&Metadata> {
        match self {
            Self::Logic(value) => MetadataIm::metadata(value.as_ref()),
            Self::Equality(value) => MetadataIm::metadata(value.as_ref()),
            Self::Cmp(value) => MetadataIm::metadata(value.as_ref()),
        }
    }
}

impl MetadataMut for BinOpFormula {
    fn metadata_mut(&mut self) -> &mut Metadata {
        match self {
            Self::Logic(value) => MetadataMut::metadata_mut(Rc::make_mut(value)),
            Self::Equality(value) => MetadataMut::metadata_mut(Rc::make_mut(value)),
            Self::Cmp(value) => MetadataMut::metadata_mut(Rc::make_mut(value)),
        }
    }
}

#[derive(Clone, Copy, PartialEq, Eq)]
pub enum BinOpRef<'a> {
    Logic(&'a Rc<LogicBinOp>),
    Arithmetic(&'a Rc<ArithBinOp>),
    Equality(&'a Rc<EqualityBinOp>),
    Cmp(&'a Rc<CmpBinOp>),
}

impl FodotOptions for BinOpRef<'_> {
    type Options<'a> = FormatOptions;
}

impl FodotDisplay for BinOpRef<'_> {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        match fmt.value {
            Self::Logic(value) => FodotDisplay::fmt(fmt.with_opts(value.as_ref()), f),
            Self::Arithmetic(value) => FodotDisplay::fmt(fmt.with_opts(value.as_ref()), f),
            Self::Equality(value) => FodotDisplay::fmt(fmt.with_opts(value.as_ref()), f),
            Self::Cmp(value) => FodotDisplay::fmt(fmt.with_opts(value.as_ref()), f),
        }
    }
}

impl FodotPrecDisplay for BinOpRef<'_> {
    fn fmt_with_prec(
        fmt: Fmt<&Self, <Self as FodotOptions>::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
        super_prec: u32,
    ) -> std::fmt::Result {
        match fmt.value {
            Self::Logic(value) => {
                LogicBinOp::fmt_with_prec(fmt.with_opts(value.as_ref()), f, super_prec)
            }
            Self::Arithmetic(value) => {
                ArithBinOp::fmt_with_prec(fmt.with_opts(value.as_ref()), f, super_prec)
            }
            Self::Equality(value) => {
                EqualityBinOp::fmt_with_prec(fmt.with_opts(value.as_ref()), f, super_prec)
            }
            Self::Cmp(value) => {
                CmpBinOp::fmt_with_prec(fmt.with_opts(value.as_ref()), f, super_prec)
            }
        }
    }
}

impl Display for BinOpRef<'_> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", Fmt::with_defaults(self))
    }
}

impl<'a> From<&'a Rc<LogicBinOp>> for BinOpRef<'a> {
    fn from(value: &'a Rc<LogicBinOp>) -> Self {
        Self::Logic(value)
    }
}

impl<'a> From<&'a Rc<ArithBinOp>> for BinOpRef<'a> {
    fn from(value: &'a Rc<ArithBinOp>) -> Self {
        Self::Arithmetic(value)
    }
}

impl<'a> From<&'a Rc<EqualityBinOp>> for BinOpRef<'a> {
    fn from(value: &'a Rc<EqualityBinOp>) -> Self {
        Self::Equality(value)
    }
}

impl<'a> From<&'a Rc<CmpBinOp>> for BinOpRef<'a> {
    fn from(value: &'a Rc<CmpBinOp>) -> Self {
        Self::Cmp(value)
    }
}

display_as_debug!(BinOpRef<'_>);

impl<'a> BinOpRef<'a> {
    pub fn vocab_rc(&self) -> Option<&'a RcA<Vocabulary>> {
        match self {
            Self::Logic(value) => value.vocab_rc(),
            Self::Arithmetic(value) => value.vocab_rc(),
            Self::Equality(value) => value.vocab_rc(),
            Self::Cmp(value) => value.vocab_rc(),
        }
    }

    pub fn vocab(&self) -> Option<&Vocabulary> {
        self.vocab_rc().map(|f| f.as_ref())
    }

    pub fn codomain(&self) -> TypeRef<'a> {
        match self {
            Self::Logic(value) => value.codomain(),
            Self::Arithmetic(value) => value.codomain(),
            Self::Equality(value) => value.codomain(),
            Self::Cmp(value) => value.codomain(),
        }
    }

    pub fn precedence(&self) -> u32 {
        self.op().precedence()
    }

    /// Returns the operator.
    pub fn op(&self) -> BinOps {
        match self {
            Self::Logic(value) => value.op().into(),
            Self::Arithmetic(value) => value.op().into(),
            Self::Equality(value) => value.op().into(),
            Self::Cmp(value) => value.op().into(),
        }
    }

    /// Returns the left hand side of the binary operation.
    pub fn lhs(&self) -> ExprRef<'a> {
        match self {
            Self::Logic(value) => value.lhs().into(),
            Self::Arithmetic(value) => value.lhs().into(),
            Self::Equality(value) => value.lhs().into(),
            Self::Cmp(value) => value.lhs().into(),
        }
    }

    /// Returns the right hand side of the binary operation.
    pub fn rhs(&self) -> ExprRef<'a> {
        match self {
            Self::Logic(value) => value.rhs().into(),
            Self::Arithmetic(value) => value.rhs().into(),
            Self::Equality(value) => value.rhs().into(),
            Self::Cmp(value) => value.rhs().into(),
        }
    }

    pub fn syntax_eq(&self, other: &Self) -> bool {
        match (self, other) {
            (Self::Logic(value1), Self::Logic(value2)) => value1.syntax_eq(value2),
            (Self::Arithmetic(value1), Self::Arithmetic(value2)) => value1.syntax_eq(value2),
            (Self::Equality(value1), Self::Equality(value2)) => value1.syntax_eq(value2),
            (Self::Cmp(value1), Self::Cmp(value2)) => value1.syntax_eq(value2),
            _ => false,
        }
    }

    pub fn collect_wdcs(&self) -> Vec<WellDefinedCondition<'a>> {
        match self {
            Self::Logic(value) => LogicBinOp::collect_wdcs(value),
            Self::Arithmetic(value) => ArithBinOp::collect_wdcs(value),
            Self::Equality(value) => EqualityBinOp::collect_wdcs(value),
            Self::Cmp(value) => CmpBinOp::collect_wdcs(value),
        }
    }

    pub fn to_owned(&self) -> BinOp {
        match self {
            Self::Logic(value) => BinOp::Logic(Rc::clone(value)),
            Self::Arithmetic(value) => BinOp::Arithmetic(Rc::clone(value)),
            Self::Equality(value) => BinOp::Equality(Rc::clone(value)),
            Self::Cmp(value) => BinOp::Cmp(Rc::clone(value)),
        }
    }
}

impl FreeVariables for BinOpRef<'_> {
    fn add_to_free_variable_iter<'a>(&'a self, iter: &mut FreeVariableIter<'a>) {
        match self {
            Self::Logic(value) => FreeVariables::add_to_free_variable_iter(value.as_ref(), iter),
            Self::Arithmetic(value) => {
                FreeVariables::add_to_free_variable_iter(value.as_ref(), iter)
            }
            Self::Equality(value) => FreeVariables::add_to_free_variable_iter(value.as_ref(), iter),
            Self::Cmp(value) => FreeVariables::add_to_free_variable_iter(value.as_ref(), iter),
        }
    }
}

impl MetadataIm for BinOpRef<'_> {
    type Metadata = Metadata;
    fn metadata(&self) -> Option<&Metadata> {
        match self {
            Self::Logic(value) => value.metadata(),
            Self::Arithmetic(value) => value.metadata(),
            Self::Equality(value) => value.metadata(),
            Self::Cmp(value) => value.metadata(),
        }
    }
}

/// All possible binary operations.
#[non_exhaustive]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum BinOps {
    // Logical operators,
    And,
    Or,
    Implication,
    Equivalence,

    Add,
    Subtract,
    Rem,
    Mult,
    Division,

    Equal,
    NotEqual,

    LessThan,
    LessOrEqual,
    GreaterThan,
    GreaterOrEqual,
}

impl FodotOptions for BinOps {
    type Options<'a>
        = FormatOptions
    where
        Self: 'a;
}

impl FodotDisplay for BinOps {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        match fmt.value {
            BinOps::And => fmt.options.write_and(f),
            BinOps::Or => fmt.options.write_or(f),
            BinOps::Implication => fmt.options.write_rimpl(f),
            BinOps::Equivalence => fmt.options.write_eqv(f),
            BinOps::Add => f.write_char('+'),
            BinOps::Subtract => f.write_char('-'),
            BinOps::Rem => f.write_char('%'),
            BinOps::Mult => fmt.options.write_product(f),
            BinOps::Division => f.write_char('/'),
            BinOps::Equal => f.write_char('='),
            BinOps::NotEqual => fmt.options.write_neq(f),
            BinOps::LessThan => f.write_char('<'),
            BinOps::LessOrEqual => fmt.options.write_le(f),
            BinOps::GreaterThan => f.write_char('>'),
            BinOps::GreaterOrEqual => fmt.options.write_ge(f),
        }
    }
}

impl Display for BinOps {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", Fmt::with_defaults(self))
    }
}

impl BinOps {
    pub fn precedence(&self) -> u32 {
        match SplitBinOps::from(*self) {
            SplitBinOps::Logic(value) => value.precedence(),
            SplitBinOps::Arithmetic(value) => value.precedence(),
            SplitBinOps::Equality(value) => value.precedence(),
            SplitBinOps::Cmp(value) => value.precedence(),
        }
    }
}

#[non_exhaustive]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum SplitBinOps {
    Logic(LogicBinOps),
    Arithmetic(ArithBinOps),
    Equality(EqualityBinOps),
    Cmp(CmpBinOps),
}

impl From<BinOps> for SplitBinOps {
    fn from(value: BinOps) -> Self {
        match value {
            BinOps::And => Self::Logic(LogicBinOps::And),
            BinOps::Or => Self::Logic(LogicBinOps::Or),
            BinOps::Implication => Self::Logic(LogicBinOps::Implication),
            BinOps::Equivalence => Self::Logic(LogicBinOps::Equivalence),

            BinOps::Add => Self::Arithmetic(ArithBinOps::Add),
            BinOps::Subtract => Self::Arithmetic(ArithBinOps::Subtract),
            BinOps::Mult => Self::Arithmetic(ArithBinOps::Mult),
            BinOps::Rem => Self::Arithmetic(ArithBinOps::Rem),
            BinOps::Division => Self::Arithmetic(ArithBinOps::Division),

            BinOps::Equal => Self::Equality(EqualityBinOps::Equal),
            BinOps::NotEqual => Self::Equality(EqualityBinOps::NotEqual),

            BinOps::LessThan => Self::Cmp(CmpBinOps::LessThan),
            BinOps::LessOrEqual => Self::Cmp(CmpBinOps::LessOrEqual),
            BinOps::GreaterThan => Self::Cmp(CmpBinOps::GreaterThan),
            BinOps::GreaterOrEqual => Self::Cmp(CmpBinOps::GreaterOrEqual),
        }
    }
}

impl From<SplitBinOps> for BinOps {
    fn from(value: SplitBinOps) -> Self {
        match value {
            SplitBinOps::Logic(LogicBinOps::And) => Self::And,
            SplitBinOps::Logic(LogicBinOps::Or) => Self::Or,
            SplitBinOps::Logic(LogicBinOps::Implication) => Self::Implication,
            SplitBinOps::Logic(LogicBinOps::Equivalence) => Self::Equivalence,

            SplitBinOps::Arithmetic(ArithBinOps::Add) => Self::Add,
            SplitBinOps::Arithmetic(ArithBinOps::Subtract) => Self::Subtract,
            SplitBinOps::Arithmetic(ArithBinOps::Mult) => Self::Mult,
            SplitBinOps::Arithmetic(ArithBinOps::Rem) => Self::Rem,
            SplitBinOps::Arithmetic(ArithBinOps::Division) => Self::Division,

            SplitBinOps::Equality(EqualityBinOps::Equal) => Self::Equal,
            SplitBinOps::Equality(EqualityBinOps::NotEqual) => Self::NotEqual,

            SplitBinOps::Cmp(CmpBinOps::LessThan) => Self::LessThan,
            SplitBinOps::Cmp(CmpBinOps::LessOrEqual) => Self::LessOrEqual,
            SplitBinOps::Cmp(CmpBinOps::GreaterThan) => Self::GreaterThan,
            SplitBinOps::Cmp(CmpBinOps::GreaterOrEqual) => Self::GreaterOrEqual,
        }
    }
}

impl From<LogicBinOps> for BinOps {
    fn from(value: LogicBinOps) -> Self {
        SplitBinOps::Logic(value).into()
    }
}

impl From<ArithBinOps> for BinOps {
    fn from(value: ArithBinOps) -> Self {
        SplitBinOps::Arithmetic(value).into()
    }
}

impl From<EqualityBinOps> for BinOps {
    fn from(value: EqualityBinOps) -> Self {
        SplitBinOps::Equality(value).into()
    }
}

impl From<CmpBinOps> for BinOps {
    fn from(value: CmpBinOps) -> Self {
        SplitBinOps::Cmp(value).into()
    }
}

impl From<OrdOps> for BinOps {
    fn from(value: OrdOps) -> Self {
        match value {
            OrdOps::Equal => Self::Equal,
            OrdOps::NotEqual => Self::NotEqual,
            OrdOps::LessThan => Self::LessThan,
            OrdOps::LessOrEqual => Self::LessOrEqual,
            OrdOps::GreaterThan => Self::GreaterThan,
            OrdOps::GreaterOrEqual => Self::GreaterOrEqual,
        }
    }
}
