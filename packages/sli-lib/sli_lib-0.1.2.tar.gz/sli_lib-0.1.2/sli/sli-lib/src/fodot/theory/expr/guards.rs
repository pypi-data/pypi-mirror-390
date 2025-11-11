use super::{
    Expr, ExprRef, Formula, FreeVariableIter, FreeVariables, Metadata, MetadataIm, MetadataMut,
    WellDefinedCondition,
};
use crate::fodot::display_as_debug;
use crate::fodot::error::{BoundVariablesInGuard, GuardError, TypeMismatch};
use crate::fodot::fmt::{FodotOptions, FodotPrecDisplay};
use crate::fodot::{
    fmt::{Fmt, FodotDisplay, FormatOptions},
    vocabulary::{Type, TypeRef, Vocabulary},
};
use sli_collections::{hash_set::HashSet, rc::RcA};
use std::fmt::{Display, Write};

fn check_correct_implicit_guard(
    subformula: ExprRef,
    wdcs: &Vec<WellDefinedCondition>,
) -> Option<BoundVariablesInGuard> {
    let mut bound_variables = HashSet::new();
    subformula.for_each_quantees(&mut |quantees| {
        quantees.iter().for_each(|f| {
            bound_variables.insert(f.decl());
        })
    });
    let mut bound_and_in_guard = Vec::new();
    for wdc in wdcs {
        wdc.condition.as_ref().for_each(&mut |f| match f {
            ExprRef::Variable(var) => {
                if bound_variables.contains(var.var_decl()) {
                    bound_and_in_guard.push(var.var_decl().clone());
                }
            }
            _ => (),
        });
    }
    if bound_and_in_guard.len() == 0 {
        None
    } else {
        Some(BoundVariablesInGuard {
            unguardable_vars: bound_and_in_guard,
        })
    }
}

/// A conjunctive guard.
///
/// Implicitly guards the sub formula using a conjunction.
#[derive(Clone, PartialEq, Eq)]
pub struct ConjuctiveGuard {
    subformula: Formula,
    metadata: Option<Box<Metadata>>,
}

impl FodotOptions for ConjuctiveGuard {
    type Options<'a> = FormatOptions;
}

impl FodotDisplay for ConjuctiveGuard {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        fmt.options.write_conj_guard_left(f)?;
        FodotDisplay::fmt(fmt.with_opts(&fmt.value.subformula), f)?;
        fmt.options.write_conj_guard_right(f)
    }
}

impl Display for ConjuctiveGuard {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

display_as_debug!(ConjuctiveGuard);

impl FreeVariables for ConjuctiveGuard {
    fn add_to_free_variable_iter<'a>(&'a self, iter: &mut FreeVariableIter<'a>) {
        iter.add_expr(self.subformula().into());
    }
}

impl MetadataIm for ConjuctiveGuard {
    type Metadata = Metadata;
    fn metadata(&self) -> Option<&Metadata> {
        self.metadata.as_deref()
    }
}

impl MetadataMut for ConjuctiveGuard {
    fn metadata_mut(&mut self) -> &mut Metadata {
        self.metadata.get_or_insert_default()
    }
}

impl ConjuctiveGuard {
    pub fn new(subformula: Formula) -> Result<Self, BoundVariablesInGuard> {
        check_correct_implicit_guard(subformula.as_ref(), &subformula.collect_wdcs())
            .map_or(Ok(()), Err)?;
        Ok(Self {
            subformula,
            metadata: Default::default(),
        })
    }

    pub fn subformula(&self) -> &Formula {
        &self.subformula
    }

    pub fn vocab_rc(&self) -> Option<&RcA<Vocabulary>> {
        self.subformula.vocab_rc()
    }

    pub fn codomain(&self) -> TypeRef {
        Type::Bool
    }
}

/// An implicative guard.
///
/// Implicitly guards the sub formula using a implication.
#[derive(Clone, PartialEq, Eq)]
pub struct ImplicativeGuard {
    subformula: Formula,
    metadata: Option<Box<Metadata>>,
}

impl FodotOptions for ImplicativeGuard {
    type Options<'a> = FormatOptions;
}

impl FodotDisplay for ImplicativeGuard {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        fmt.options.write_impl_guard_left(f)?;
        FodotDisplay::fmt(fmt.with_opts(&fmt.value.subformula), f)?;
        fmt.options.write_impl_guard_right(f)
    }
}

impl Display for ImplicativeGuard {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

display_as_debug!(ImplicativeGuard);

impl FreeVariables for ImplicativeGuard {
    fn add_to_free_variable_iter<'a>(&'a self, iter: &mut FreeVariableIter<'a>) {
        iter.add_expr(self.subformula().into());
    }
}

impl MetadataIm for ImplicativeGuard {
    type Metadata = Metadata;
    fn metadata(&self) -> Option<&Metadata> {
        self.metadata.as_deref()
    }
}

impl MetadataMut for ImplicativeGuard {
    fn metadata_mut(&mut self) -> &mut Metadata {
        self.metadata.get_or_insert_default()
    }
}

impl ImplicativeGuard {
    pub fn new(subformula: Formula) -> Result<Self, BoundVariablesInGuard> {
        check_correct_implicit_guard(subformula.as_ref(), &subformula.collect_wdcs())
            .map_or(Ok(()), Err)?;
        Ok(Self {
            subformula,
            metadata: Default::default(),
        })
    }

    pub fn subformula(&self) -> &Formula {
        &self.subformula
    }

    pub fn vocab_rc(&self) -> Option<&RcA<Vocabulary>> {
        self.subformula.vocab_rc()
    }

    pub fn codomain(&self) -> TypeRef {
        Type::Bool
    }
}

/// An implicit if guard.
///
/// Implicitly guards the sub formula using a if then else statement.
#[derive(Clone, PartialEq, Eq)]
pub struct IfGuard {
    term: Expr,
    else_term: Expr,
    metadata: Option<Box<Metadata>>,
}

impl FodotOptions for IfGuard {
    type Options<'a> = FormatOptions;
}

impl FodotDisplay for IfGuard {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        FodotPrecDisplay::fmt_with_prec(fmt, f, 0)
    }
}

impl FodotPrecDisplay for IfGuard {
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
        write!(f, "ifdef ")?;
        FodotDisplay::fmt(fmt.with_opts(&fmt.value.term), f)?;
        write!(f, " else ")?;
        FodotPrecDisplay::fmt_with_prec(fmt.with_opts(&fmt.value.else_term), f, this_prec)?;
        if needs_bracket {
            f.write_char(')')?;
        }
        Ok(())
    }
}

impl Display for IfGuard {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

display_as_debug!(IfGuard);

impl FreeVariables for IfGuard {
    fn add_to_free_variable_iter<'a>(&'a self, iter: &mut FreeVariableIter<'a>) {
        iter.add_expr(self.term().into());
        iter.add_expr(self.else_term().into());
    }
}

impl MetadataIm for IfGuard {
    type Metadata = Metadata;
    fn metadata(&self) -> Option<&Metadata> {
        self.metadata.as_deref()
    }
}

impl MetadataMut for IfGuard {
    fn metadata_mut(&mut self) -> &mut Metadata {
        self.metadata.get_or_insert_default()
    }
}

impl IfGuard {
    pub fn new(term: Expr, else_term: Expr) -> Result<Self, GuardError> {
        if term.codomain().into_root_type() != else_term.codomain().into_root_type() {
            return Err(TypeMismatch {
                found: else_term.codomain().into(),
                expected: term.codomain().into(),
            }
            .into());
        }
        check_correct_implicit_guard(term.as_ref(), &term.collect_wdcs()).map_or(Ok(()), Err)?;
        Ok(Self {
            term,
            else_term,
            metadata: Default::default(),
        })
    }

    pub fn precedence(&self) -> u32 {
        50
    }

    pub fn term(&self) -> &Expr {
        &self.term
    }

    pub fn else_term(&self) -> &Expr {
        &self.else_term
    }

    pub fn vocab_rc(&self) -> Option<&RcA<Vocabulary>> {
        self.term.vocab_rc().or_else(|| self.else_term.vocab_rc())
    }

    pub fn codomain(&self) -> TypeRef {
        // TODO: fix this
        self.term.codomain().into_root_type().into()
    }

    pub fn collect_wdcs(&self) -> Vec<WellDefinedCondition> {
        self.else_term.collect_wdcs()
    }
}
