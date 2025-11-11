use super::{BinOpRef, Expr, ExprRef, Metadata, MetadataIm, MetadataMut};
use crate::ast::Span;
use crate::fodot::error::NoVarQuanteesError;
use crate::fodot::fmt::FodotOptions;
use crate::fodot::{
    fmt::{Fmt, FodotDisplay, FormatOptions},
    vocabulary::{TypeRc, TypeRef, Vocabulary},
};
use itertools::Itertools;
use sli_collections::rc::{Rc, RcA};
use std::collections::HashSet;
use std::iter::FusedIterator;
use std::{
    borrow::Borrow,
    fmt::{Debug, Display},
};
use std::{hash::Hash, ops::Deref};

/// A variable declaration.
///
/// See [VariableBinder] for more info on variables in sli.
#[derive(Clone)]
pub struct VariableDecl {
    name: Box<str>,
    var_type: TypeRc,
    metadata: Option<Box<VarMetadata>>,
}

impl FodotOptions for VariableDecl {
    type Options<'a>
        = FormatOptions
    where
        Self: 'a;
}

impl FodotDisplay for VariableDecl {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        write!(f, "{} ", &fmt.value.name())?;
        fmt.options.write_in(f)?;
        write!(f, " {}", fmt.with_format_opts(&fmt.value.var_type()))
    }
}

impl Display for VariableDecl {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

impl Debug for VariableDecl {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("VariableDecl")
            .field("name", &self.name())
            .field("type", &format!("{}", self.var_type()))
            .finish()
    }
}

impl VariableDecl {
    /// Creates a new variable with the given name and type.
    pub fn new(name: &str, var_type: TypeRc) -> Self {
        Self {
            name: name.into(),
            var_type,
            metadata: Default::default(),
        }
    }

    /// Return the name of the variable.
    ///
    /// See [VariableBinder] for more info about variable names.
    pub fn name(&self) -> &str {
        &self.name
    }

    pub fn vocab(&self) -> Option<&Vocabulary> {
        self.vocab_rc().map(|f| f.as_ref())
    }

    pub fn vocab_rc(&self) -> Option<&RcA<Vocabulary>> {
        self.var_type.vocab_rc()
    }

    /// Returns the type of the variable.
    pub fn var_type(&self) -> TypeRef {
        self.var_type.borrow().into()
    }

    /// Creates a [VariableBinder] which can be used to bind a variable quantification.
    pub fn finish(self) -> VariableBinder {
        VariableBinder {
            decl: VariableDeclRef {
                decl: Rc::new(self),
            },
        }
    }

    pub fn type_span(&self) -> Option<Span> {
        self.metadata().and_then(|f| f.type_span)
    }

    pub fn var_span(&self) -> Option<Span> {
        self.metadata().and_then(|f| f.var_span)
    }

    pub fn with_type_span(mut self, type_span: Span) -> Self {
        self.metadata_mut().type_span = Some(type_span);
        self
    }

    pub fn with_var_span(mut self, var_span: Span) -> Self {
        self.metadata_mut().var_span = Some(var_span);
        self
    }
}

#[derive(Clone, Default, Hash, PartialEq, Eq)]
pub struct VarMetadata {
    metadata: Metadata,
    var_span: Option<Span>,
    type_span: Option<Span>,
}

impl AsRef<Metadata> for VarMetadata {
    fn as_ref(&self) -> &Metadata {
        &self.metadata
    }
}

impl AsMut<Metadata> for VarMetadata {
    fn as_mut(&mut self) -> &mut Metadata {
        &mut self.metadata
    }
}

impl MetadataIm for VariableDecl {
    type Metadata = VarMetadata;
    fn metadata(&self) -> Option<&Self::Metadata> {
        self.metadata.as_deref()
    }
}

impl MetadataMut for VariableDecl {
    fn metadata_mut(&mut self) -> &mut Self::Metadata {
        self.metadata.get_or_insert_default()
    }
}

/// A immutable owning reference to a [VariableDecl].
///
/// Exists to prevent multiple [VariableBinder]s pointing to the same [VariableDecl] to exist.
#[derive(Clone)]
pub struct VariableDeclRef {
    decl: Rc<VariableDecl>,
}

impl FodotOptions for VariableDeclRef {
    type Options<'a>
        = FormatOptions
    where
        Self: 'a;
}

impl FodotDisplay for VariableDeclRef {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        write!(f, "{}", fmt.with_opts(fmt.value.decl.as_ref()))
    }
}

impl Display for VariableDeclRef {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

impl Debug for VariableDeclRef {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("VariableDeclRef")
            .field("name", &self.name())
            .field("type", &format!("{}", self.var_type()))
            .field("addr", &(format!("{:#x}", Rc::as_ptr(&self.decl) as usize)))
            .finish()
    }
}

impl Deref for VariableDeclRef {
    type Target = VariableDecl;

    fn deref(&self) -> &Self::Target {
        &self.decl
    }
}

impl PartialEq for VariableDeclRef {
    fn eq(&self, other: &Self) -> bool {
        core::ptr::eq(Rc::as_ptr(&self.decl), Rc::as_ptr(&other.decl))
    }
}

impl Eq for VariableDeclRef {}

impl Hash for VariableDeclRef {
    fn hash<H: std::hash::Hasher>(&self, state: &mut H) {
        Rc::as_ptr(&self.decl).hash(state)
    }
}

impl PartialEq<Variable> for Expr {
    fn eq(&self, other: &Variable) -> bool {
        self.eq(&other.decl)
    }
}

impl PartialEq<VariableBinder> for Expr {
    fn eq(&self, other: &VariableBinder) -> bool {
        self.eq(&other.decl)
    }
}

impl PartialEq<Expr> for Variable {
    fn eq(&self, other: &Expr) -> bool {
        other.eq(self)
    }
}

impl PartialEq<Expr> for VariableBinder {
    fn eq(&self, other: &Expr) -> bool {
        other.eq(self)
    }
}

/// Used for binding variables to quantification.
///
/// Variables may be bound only once to a quantification.
/// This reduces the amount of edge cases by 80 quadrillion. For this reason [Clone] is not
/// implemented on [VariableBinder]. Make sure you don't lose it before you use it!
/// Note: a [VariableDecl] is allowed to have the same name as other [VariableDecl]s
/// since a [VariableBinder] is bound by memory address not by name. This can result in weird
/// [Display] results.
pub struct VariableBinder {
    /// This field should only ever be owned by the quantifier that quantifies over this
    /// variable and all the variables references.
    /// It should never be quantified over twice anywhere.
    decl: VariableDeclRef,
}

impl PartialEq for VariableBinder {
    fn eq(&self, other: &Self) -> bool {
        self.decl == other.decl
    }
}

impl Eq for VariableBinder {}

// TODO: is this ok?
impl Hash for VariableBinder {
    fn hash<H: std::hash::Hasher>(&self, state: &mut H) {
        self.decl.hash(state)
    }
}

impl AsRef<str> for VariableBinder {
    fn as_ref(&self) -> &str {
        &self.name()
    }
}

impl FodotOptions for VariableBinder {
    type Options<'a>
        = FormatOptions
    where
        Self: 'a;
}

impl FodotDisplay for VariableBinder {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        write!(f, "{}", fmt.with_opts(&fmt.value.decl))
    }
}

impl Display for VariableBinder {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", Fmt::with_defaults(self))
    }
}

impl Debug for VariableBinder {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        <VariableDeclRef as Debug>::fmt(&self.decl, f)
    }
}

impl Deref for VariableBinder {
    type Target = VariableDecl;

    fn deref(&self) -> &Self::Target {
        &self.decl
    }
}

impl VariableBinder {
    pub fn decl(&self) -> &VariableDeclRef {
        &self.decl
    }

    /// Create a variable to be used in an expression.
    pub fn create_var_ref(&self) -> Variable {
        Variable {
            // This and other variable creation locations should be the only place where
            // we clone the Rc of decl_info.
            decl: self.decl.clone(),
            metadata: Default::default(),
        }
    }
}

/// A variable to be used in expressions.
#[derive(Clone)]
pub struct Variable {
    decl: VariableDeclRef,
    metadata: Option<Box<Metadata>>,
}

impl PartialEq for Variable {
    fn eq(&self, other: &Self) -> bool {
        self.decl == other.decl
    }
}

impl PartialEq<VariableDeclRef> for Variable {
    fn eq(&self, other: &VariableDeclRef) -> bool {
        self.decl == *other
    }
}

impl PartialEq<VariableBinder> for Variable {
    fn eq(&self, other: &VariableBinder) -> bool {
        self.decl == other.decl
    }
}

impl Eq for Variable {}

// TODO: is this ok?
impl Hash for Variable {
    fn hash<H: std::hash::Hasher>(&self, state: &mut H) {
        self.decl.hash(state)
    }
}

impl FodotOptions for Variable {
    type Options<'a>
        = FormatOptions
    where
        Self: 'a;
}

impl FodotDisplay for Variable {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        write!(f, "{}", &fmt.value.decl.name)
    }
}

impl Display for Variable {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", Fmt::with_defaults(self))
    }
}

impl Debug for Variable {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        <VariableDeclRef as Debug>::fmt(&self.decl, f)
    }
}

impl FreeVariables for Rc<Variable> {
    fn add_to_free_variable_iter<'a>(&'a self, iter: &mut FreeVariableIter<'a>) {
        iter.add_expr(ExprRef::Variable(self))
    }
}

impl Variable {
    pub fn vocab_rc(&self) -> Option<&RcA<Vocabulary>> {
        self.decl.vocab_rc()
    }

    pub fn var_decl(&self) -> &VariableDeclRef {
        &self.decl
    }

    pub fn codomain(&self) -> TypeRef {
        (&self.decl.var_type).into()
    }

    /// Create a new variable 'ref' to be used in expressions.
    ///
    /// The metadata of this new variable will be empty.
    /// Use the clone method if you want to have the same metadata.
    pub fn create_var_ref(&self) -> Self {
        Self {
            decl: self.decl.clone(),
            metadata: Default::default(),
        }
    }
}

impl MetadataIm for Variable {
    type Metadata = Metadata;
    fn metadata(&self) -> Option<&Metadata> {
        self.metadata.as_deref()
    }
}

impl MetadataMut for Variable {
    fn metadata_mut(&mut self) -> &mut Metadata {
        self.metadata.get_or_insert_default()
    }
}

impl Borrow<str> for Variable {
    fn borrow(&self) -> &str {
        &self.decl.name
    }
}

impl AsRef<str> for Variable {
    fn as_ref(&self) -> &str {
        &self.decl.name
    }
}

/// A builder for quantees to be bound in a quantification.
///
/// Also see [Quantees].
#[derive(Debug)]
pub struct QuanteesBuilder {
    decls: Vec<VariableBinder>,
}

impl QuanteesBuilder {
    pub fn new() -> Self {
        Self {
            decls: Default::default(),
        }
    }

    /// Create a new variable and add it.
    pub fn add_new_var(&mut self, name: &str, var_type: TypeRc) -> Variable {
        let var = VariableDecl::new(name, var_type).finish();
        let var_ref = var.create_var_ref();
        self.decls.push(var);
        var_ref
    }

    pub fn add_decl(&mut self, decl: VariableBinder) {
        self.decls.push(decl)
    }

    pub fn iter_vars<'a>(&'a self) -> impl Iterator<Item = &'a VariableBinder> {
        self.decls.iter()
    }

    /// Finish the [QuanteesBuilder] returning a [Quantees], fails if not a single variable has
    /// been bound.
    pub fn finish(self) -> Result<Quantees, NoVarQuanteesError> {
        if self.decls.len() != 0 {
            Ok(Quantees {
                decls: self.decls.into(),
            })
        } else {
            Err(NoVarQuanteesError)
        }
    }
}

impl<I: Into<VariableBinder>> FromIterator<I> for QuanteesBuilder {
    fn from_iter<T: IntoIterator<Item = I>>(iter: T) -> Self {
        Self {
            decls: iter.into_iter().map(|f| f.into()).collect(),
        }
    }
}

/// A list of quantees.
///
/// This list at minimum contains 1 variable.
///
/// Quantees are the variables used in quantification, e.g. `x` in `!x in T: ...`.
#[derive(Debug, PartialEq, Eq)]
pub struct Quantees {
    // Is never empty
    decls: Box<[VariableBinder]>,
}

impl FodotOptions for Quantees {
    type Options<'a>
        = FormatOptions
    where
        Self: 'a;
}

impl FodotDisplay for Quantees {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        write!(
            f,
            "{}",
            fmt.value
                .iter_decls()
                .map(|f| fmt.with_format_opts(f))
                .format(", ")
        )
    }
}

impl Display for Quantees {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

impl Quantees {
    pub(crate) fn duplicate(&self) -> Self {
        Self {
            decls: self
                .decls
                .iter()
                .map(|f| VariableBinder {
                    decl: f.decl().clone(),
                })
                .collect(),
        }
    }

    pub fn vocab(&self) -> Option<&Vocabulary> {
        self.vocab_rc().map(|f| f.as_ref())
    }

    pub fn vocab_rc(&self) -> Option<&RcA<Vocabulary>> {
        for decl in self.decls.iter() {
            if let Some(val) = decl.vocab_rc() {
                return Some(val);
            }
        }
        None
    }

    pub fn iter_decls<'a>(&'a self) -> impl Iterator<Item = &'a VariableBinder> {
        self.decls.iter()
    }

    pub fn get_decl(&self, pos: usize) -> Option<&VariableBinder> {
        self.iter_decls().nth(pos)
    }

    /// Iterates over all the variables.
    pub fn iter<'a>(&'a self) -> impl Iterator<Item = &'a VariableBinder> {
        self.decls.iter()
    }
}

/// An iterator over free variables in an expression.
pub struct FreeVariableIter<'a> {
    bound_vars: HashSet<VariableDeclRef>,
    remaining_exprs: Vec<VarIterBoundary<'a>>,
}

enum VarIterBoundary<'a> {
    Expr(ExprRef<'a>),
    Boundary(&'a Quantees),
}

impl<'a> From<&'a Expr> for VarIterBoundary<'a> {
    fn from(value: &'a Expr) -> Self {
        Self::Expr(value.into())
    }
}

impl<'a> From<ExprRef<'a>> for VarIterBoundary<'a> {
    fn from(value: ExprRef<'a>) -> Self {
        Self::Expr(value)
    }
}

impl<'a> From<&'a Quantees> for VarIterBoundary<'a> {
    fn from(value: &'a Quantees) -> Self {
        Self::Boundary(value)
    }
}

impl<'a> FreeVariableIter<'a> {
    /// Create a new [FreeVariableIter] from the given [FreeVariables] implementor.
    pub fn new<F: FreeVariables>(start: &'a F) -> Self {
        let mut this = Self::new_empty();
        this.add_free_vars(start);
        this
    }

    /// Create an empty [FreeVariableIter].
    ///
    /// To be used with methods such as [Self::add_quantees], [Self::with_quantees], ...
    pub fn new_empty() -> Self {
        Self {
            bound_vars: Default::default(),
            remaining_exprs: Default::default(),
        }
    }

    /// Consuming version of [Self::add_quantees].
    pub fn with_quantees(mut self, quantees: &'a Quantees) -> Self {
        self.add_quantees(quantees);
        self
    }

    /// Consuming version of [Self::add_free_vars].
    pub fn with_free_vars<T: FreeVariables>(mut self, free_vars: &'a T) -> Self {
        free_vars.add_to_free_variable_iter(&mut self);
        self
    }

    /// Add [Quantees] to current state as bound variables.
    pub fn add_quantees(&mut self, quantees: &'a Quantees) {
        for var_decl in quantees.iter() {
            self.bound_vars.insert(var_decl.decl().clone());
        }
        self.remaining_exprs.push(quantees.into());
    }

    /// Add an implementer of [FreeVariables] to the current state of the iterator.
    pub fn add_free_vars<T: FreeVariables>(&mut self, free_vars: &'a T) {
        free_vars.add_to_free_variable_iter(self);
    }

    /// Add an [Expr] to iterate over its free variables.
    pub fn add_expr(&mut self, expr: ExprRef<'a>) {
        self.remaining_exprs.push(expr.into())
    }
}

pub trait FreeVariables {
    /// Adds [Self] to a [FreeVariableIter] instance.
    fn add_to_free_variable_iter<'a>(&'a self, iter: &mut FreeVariableIter<'a>);
}

pub trait IterFreeVariables {
    /// Returns an iterator over all free variables in [Self].
    fn iter_free_variables(&self) -> FreeVariableIter;

    /// Returns true if [Self] contains free variables.
    fn contains_free_variables(&self) -> bool {
        self.iter_free_variables().next().is_some()
    }
}

impl<T: FreeVariables> IterFreeVariables for T {
    fn iter_free_variables(&self) -> FreeVariableIter {
        let mut iter = FreeVariableIter::new_empty();
        self.add_to_free_variable_iter(&mut iter);
        iter
    }
}

impl<'a> Iterator for FreeVariableIter<'a> {
    type Item = Rc<Variable>;

    fn next(&mut self) -> Option<Self::Item> {
        loop {
            let expr = match self.remaining_exprs.pop()? {
                VarIterBoundary::Expr(expr) => expr,
                VarIterBoundary::Boundary(quantees) => {
                    for var_decl in quantees.iter_decls() {
                        self.bound_vars.remove(&var_decl.decl());
                    }
                    continue;
                }
            };
            match expr {
                ExprRef::Variable(var) => {
                    if !self.bound_vars.contains(var.var_decl()) {
                        return Some(var.clone());
                    }
                }
                ExprRef::BinOp(bin_op) => match bin_op {
                    BinOpRef::Logic(value) => value.add_to_free_variable_iter(self),
                    BinOpRef::Arithmetic(value) => value.add_to_free_variable_iter(self),
                    BinOpRef::Equality(value) => value.add_to_free_variable_iter(self),
                    BinOpRef::Cmp(value) => value.add_to_free_variable_iter(self),
                },
                ExprRef::ChainedCmp(chained_cmp) => {
                    chained_cmp.add_to_free_variable_iter(self);
                }
                ExprRef::Ite(ite) => {
                    ite.add_to_free_variable_iter(self);
                }
                ExprRef::Quantification(quant) => {
                    quant.add_to_free_variable_iter(self);
                }
                ExprRef::CardinalityAggregate(card_ag) => {
                    card_ag.add_to_free_variable_iter(self);
                }
                ExprRef::Aggregate(agg) => {
                    agg.add_to_free_variable_iter(self);
                }
                ExprRef::AppliedSymbol(ap_symb) => {
                    ap_symb.add_to_free_variable_iter(self);
                }
                ExprRef::IsEnumerated(is_enumerated) => {
                    is_enumerated.add_to_free_variable_iter(self);
                }
                ExprRef::Negation(neg) => {
                    neg.add_to_free_variable_iter(self);
                }
                ExprRef::NumNegation(neg) => {
                    neg.add_to_free_variable_iter(self);
                }
                ExprRef::InEnumeration(in_enum) => {
                    in_enum.add_to_free_variable_iter(self);
                }
                ExprRef::ConjuctiveGuard(conj_guard) => {
                    conj_guard.add_to_free_variable_iter(self);
                }
                ExprRef::ImplicativeGuard(conj_guard) => {
                    conj_guard.add_to_free_variable_iter(self);
                }
                ExprRef::IfGuard(conj_guard) => {
                    conj_guard.add_to_free_variable_iter(self);
                }
                ExprRef::Element(_) => {}
                ExprRef::Bool(_) => {}
            }
        }
    }
}

impl FusedIterator for FreeVariableIter<'_> {}
