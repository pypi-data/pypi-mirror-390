use super::{
    AppliedSymbol, BinOps, Expr, ExprRef, FreeVariableIter, FreeVariables, Metadata, MetadataIm,
    MetadataMut, Quantees, VocabIterCheck, WellDefinedFormula,
};
use crate::fodot::display_as_debug;
use crate::fodot::error::{
    DefFreeVarError, DefHeadError, DefRuleError, InvalidDefHeadError, TypeMismatch,
    VocabMismatchError,
};
use crate::fodot::fmt::FodotOptions;
use crate::fodot::{
    fmt::{Fmt, FodotDisplay, FormatOptions},
    vocabulary::{SymbolRc, Type, TypeRef, Vocabulary},
};
use sli_collections::rc::{Rc, RcA};
use std::fmt::{Display, Write};

/// A definitional head.
///
/// A definitional head must be either an [AppliedSymbol] with codomain [Type::Bool] (a predicate).
/// Or equality between a function and an expression.
///
/// The [Symbol](crate::fodot::vocabulary::Symbol) being defined must be a
/// [Pfunc](crate::fodot::vocabulary::Pfunc).
#[derive(PartialEq, Eq)]
pub enum DefinitionalHead {
    Pred(Rc<AppliedSymbol>),
    Eq(Rc<AppliedSymbol>, Expr),
}

impl FodotOptions for DefinitionalHead {
    type Options<'a>
        = FormatOptions
    where
        Self: 'a;
}

impl FodotDisplay for DefinitionalHead {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        match fmt.value {
            DefinitionalHead::Pred(ap_symb) => {
                write!(f, "{}", fmt.with_format_opts(ap_symb.as_ref()))
            }
            DefinitionalHead::Eq(ap_symb, rhs) => {
                write!(
                    f,
                    "{} = {}",
                    fmt.with_format_opts(ap_symb.as_ref()),
                    fmt.with_format_opts(rhs),
                )
            }
        }
    }
}

impl Display for DefinitionalHead {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

display_as_debug!(DefinitionalHead);

impl TryFrom<Expr> for DefinitionalHead {
    type Error = DefHeadError;

    fn try_from(value: Expr) -> Result<Self, Self::Error> {
        match value {
            Expr::AppliedSymbol(app_symb) => {
                if app_symb.codomain() != Type::Bool {
                    return Err(TypeMismatch {
                        found: app_symb.codomain().into(),
                        expected: TypeRef::Bool.into(),
                    }
                    .into());
                }
                Ok(Self::Pred(app_symb))
            }
            Expr::BinOp(bin_op) => match (bin_op.lhs(), bin_op.op(), bin_op.rhs()) {
                (ExprRef::AppliedSymbol(app_symb), BinOps::Equal, rhs) => {
                    if app_symb.codomain() == Type::Bool {
                        return Err(InvalidDefHeadError.into());
                    }
                    Ok(Self::Eq(app_symb.clone(), rhs.to_owned()))
                }
                _ => Err(InvalidDefHeadError.into()),
            },
            _ => Err(InvalidDefHeadError.into()),
        }
    }
}

impl DefinitionalHead {
    fn free_var_check(&self, quantees: Option<&Quantees>) -> Option<DefFreeVarError> {
        match self {
            Self::Pred(pred) => {
                let mut iter = FreeVariableIter::new_empty();
                quantees.map(|f| iter.add_quantees(f));
                pred.as_ref().add_to_free_variable_iter(&mut iter);

                if iter.next().is_some() {
                    return Some(DefFreeVarError);
                }
            }
            Self::Eq(func, rhs) => {
                let mut iter = FreeVariableIter::new_empty();
                quantees.map(|f| iter.add_quantees(f));
                func.as_ref().add_to_free_variable_iter(&mut iter);
                iter.add_expr(rhs.into());
                if iter.next().is_some() {
                    return Some(DefFreeVarError);
                }
            }
        }
        None
    }

    /// Returns the definiendum (the symbol being defined).
    pub fn definiendum(&self) -> &SymbolRc {
        self.applied_symbol().symbol()
    }

    pub fn eq(&self) -> Option<&Expr> {
        match self {
            Self::Eq(_, rhs) => Some(rhs),
            _ => None,
        }
    }

    pub fn applied_symbol(&self) -> &AppliedSymbol {
        match self {
            Self::Pred(value) | Self::Eq(value, _) => value,
        }
    }

    pub fn vocab_rc(&self) -> Option<&RcA<Vocabulary>> {
        match self {
            Self::Pred(expr) => expr.vocab_rc(),
            Self::Eq(ap_symb, expr) => ap_symb.vocab_rc().or(expr.vocab_rc()),
        }
    }
}

/// A definitional rule.
///
/// Consists of a possibly some variables as [Quantees], a [DefinitionalHead] and a body [Expr]
/// with a [Type::Bool] codomain.
pub struct DefinitionalRule {
    quantees: Option<Quantees>,
    head: DefinitionalHead,
    body: WellDefinedFormula,
    metadata: Option<Box<Metadata>>,
}

impl FodotOptions for DefinitionalRule {
    type Options<'a>
        = FormatOptions
    where
        Self: 'a;
}

impl FodotDisplay for DefinitionalRule {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        if let Some(quantees) = &fmt.value.quantees {
            fmt.options.write_uni_quant(f)?;
            write!(f, "{}: ", fmt.with_format_opts(quantees))?;
        }
        write!(f, "{} ", fmt.with_format_opts(&fmt.value.head))?;
        fmt.options.write_def_limpl(f)?;
        write!(f, " {}", fmt.with_format_opts(&fmt.value.body))?;
        Ok(())
    }
}

impl Display for DefinitionalRule {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

display_as_debug!(DefinitionalRule);

impl PartialEq for DefinitionalRule {
    fn eq(&self, other: &Self) -> bool {
        self.head == other.head && self.quantees == other.quantees
    }
}

impl Eq for DefinitionalRule {}

impl MetadataIm for DefinitionalRule {
    type Metadata = Metadata;
    fn metadata(&self) -> Option<&Metadata> {
        self.metadata.as_deref()
    }
}

impl MetadataMut for DefinitionalRule {
    fn metadata_mut(&mut self) -> &mut Metadata {
        self.metadata.get_or_insert_default()
    }
}

impl DefinitionalRule {
    pub fn new(
        quantees: Option<Quantees>,
        head: DefinitionalHead,
        body: WellDefinedFormula,
    ) -> Result<Self, DefRuleError> {
        if let Some(error) = head.free_var_check(quantees.as_ref()) {
            return Err(error.into());
        }
        let mut body_free_vars = FreeVariableIter::new_empty();
        quantees.as_ref().map(|f| body_free_vars.add_quantees(f));
        body_free_vars.add_expr((&body).into());
        if body_free_vars.next().is_some() {
            return Err(DefFreeVarError.into());
        }
        Ok(Self {
            quantees,
            head,
            body,
            metadata: Default::default(),
        })
    }

    pub fn quantees(&self) -> Option<&Quantees> {
        self.quantees.as_ref()
    }

    pub fn head(&self) -> &DefinitionalHead {
        &self.head
    }

    pub fn body(&self) -> &WellDefinedFormula {
        &self.body
    }

    pub fn vocab_rc(&self) -> Option<&RcA<Vocabulary>> {
        self.head.vocab_rc().or(self.body.as_formula().vocab_rc())
    }
}

/// A definition. This is a list of [DefinitionalRule]s.
pub struct Definition {
    rules: Box<[DefinitionalRule]>,
    vocab: Option<RcA<Vocabulary>>,
    metadata: Option<Box<Metadata>>,
}

impl FodotOptions for Definition {
    type Options<'a>
        = FormatOptions
    where
        Self: 'a;
}

impl FodotDisplay for Definition {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        f.write_str("{\n")?;
        for def_rule in fmt.value.rules.iter() {
            fmt.options.write_indent_extra(f, 1)?;
            writeln!(f, "{}.", fmt.with_format_opts(def_rule))?;
        }
        fmt.options.write_indent(f)?;
        f.write_char('}')
    }
}

impl Display for Definition {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

display_as_debug!(Definition);

impl PartialEq for Definition {
    fn eq(&self, other: &Self) -> bool {
        self.rules == other.rules
    }
}

impl Eq for Definition {}

impl MetadataIm for Definition {
    type Metadata = Metadata;
    fn metadata(&self) -> Option<&Metadata> {
        self.metadata.as_deref()
    }
}

impl MetadataMut for Definition {
    fn metadata_mut(&mut self) -> &mut Metadata {
        self.metadata.get_or_insert_default()
    }
}

impl Definition {
    pub fn new(rules: Box<[DefinitionalRule]>) -> Result<Self, VocabMismatchError> {
        let mut vocab_checker = VocabIterCheck::new(rules.iter().map(|f| f.vocab_rc()));
        if !vocab_checker.check_if_consistent() {
            return Err(VocabMismatchError);
        }
        let vocab = vocab_checker.take_vocab().cloned();
        Ok(Self {
            rules,
            vocab,
            metadata: Default::default(),
        })
    }

    pub fn vocab_rc(&self) -> Option<&RcA<Vocabulary>> {
        self.vocab.as_ref()
    }

    pub fn rules(&self) -> &[DefinitionalRule] {
        &self.rules
    }
}
