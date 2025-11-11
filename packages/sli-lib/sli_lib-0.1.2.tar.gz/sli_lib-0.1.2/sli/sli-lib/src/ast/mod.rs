//! Abstract definition of FO(·) syntax used by sli.
//!
//! Any implementer of [Parser] can be used to lower from ast to [fodot](crate::fodot).

use std::{borrow::Cow, fmt::Display, ops::Range};

use itertools::Either;

pub mod tree_sitter;

/// An ast value that may have been poisoned.
///
/// Communicates the fact that some node int ast must exist for it to be correct FO(·), but is
/// allowed to be missing to increase caught errors.
pub enum MaybePoisoned<V> {
    Value(V),
    Poisoned,
}

impl<V> From<Option<V>> for MaybePoisoned<V> {
    fn from(value: Option<V>) -> Self {
        match value {
            Some(value) => Self::Value(value),
            None => Self::Poisoned,
        }
    }
}

impl<V> MaybePoisoned<V> {
    pub fn value(self) -> Option<V> {
        match self {
            Self::Value(value) => Some(value),
            Self::Poisoned => None,
        }
    }
}

/// A FO(·) block.
pub enum BlockType<V, T, S> {
    Vocab(V),
    Theory(T),
    Structure(S),
}

/// A generic parse error.
#[derive(Clone, Debug)]
pub struct ParseError {
    pub message: String,
}

impl Display for ParseError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.message)
    }
}

/// Abstract representation of a FO(·) source.
pub trait Source {
    fn write_slice(&self, range: &Span, write: &mut dyn core::fmt::Write) -> core::fmt::Result;
    fn next_char(&self, pos: usize) -> Option<char>;
    fn char_at(&self, pos: usize) -> Option<char>;
    fn prev_char(&self, pos: usize) -> Option<char>;
    fn slice<'a>(&'a self, range: &Span) -> Cow<'a, str>;
    fn previous_char_pos(&self, offset: usize, char: char) -> Option<usize>;
    fn next_char_pos(&self, offset: usize, char: char) -> Option<usize>;
    fn len(&self) -> usize;
}

impl<'a> Source for &'a str {
    fn write_slice(&self, range: &Span, write: &mut dyn core::fmt::Write) -> core::fmt::Result {
        write!(write, "{}", &self[range.start..range.end])
    }

    fn next_char(&self, pos: usize) -> Option<char> {
        self[pos..].chars().nth(1)
    }

    fn char_at(&self, pos: usize) -> Option<char> {
        self[pos..].chars().next()
    }

    fn prev_char(&self, pos: usize) -> Option<char> {
        self[..pos].chars().next_back()
    }

    fn slice(&self, range: &Span) -> Cow<'a, str> {
        Cow::Borrowed(&self[range.start..range.end])
    }

    fn previous_char_pos(&self, offset: usize, char: char) -> Option<usize> {
        self[..offset].rfind(char)
    }

    fn next_char_pos(&self, offset: usize, char: char) -> Option<usize> {
        self[offset..].find(char).map(|f| f + offset)
    }

    fn len(&self) -> usize {
        str::len(self)
    }
}

/// An iterator over the lines of a [Source].
#[derive(Clone)]
pub struct LinesIter<'a, S: Source + ?Sized> {
    source: &'a S,
    cur: Option<usize>,
    end: usize,
}

impl<'a, S: Source + ?Sized> LinesIter<'a, S> {
    pub fn new(source: &'a S, range: &Span) -> Self {
        Self {
            source,
            cur: Some(range.start),
            end: range.end,
        }
    }
}

impl<'a, S: Source + ?Sized> Iterator for LinesIter<'a, S> {
    type Item = Span;

    fn next(&mut self) -> Option<Self::Item> {
        let cur = self.cur?;
        let next_new_line = self.source.next_char_pos(cur, '\n')?;
        let mut new_cur = next_new_line;
        if self.source.next_char_pos(next_new_line, '\r').is_some() {
            new_cur = new_cur.checked_add(1)?;
        }
        if next_new_line > self.end {
            self.cur = None;
            return None;
        }
        self.cur = new_cur.checked_add(1);
        Some(Span {
            start: cur,
            end: next_new_line,
        })
    }
}

/// Span of ast nodes.
pub trait Spanned {
    fn span(&self) -> Span;
}

/// Parser trait.
///
/// A parser must produce the same [Ast], no matter the [Source].
pub trait Parser<T: Source>: AstParser {
    fn parse(&mut self, source: T) -> Self::Ast;
    fn parse_vocab(&mut self, source: T) -> <Self::Ast as Ast>::VocabAst;
    fn parse_theory(&mut self, source: T) -> <Self::Ast as Ast>::TheoryAst;
    fn parse_structure(&mut self, source: T) -> <Self::Ast as Ast>::StructureAst;
}

/// The [Ast] type a parser produces.
pub trait AstParser {
    type Ast: Ast;
}

/// Block nodes in the [Ast].
pub trait Ast {
    type Vocab<'a>: VocabBlock
    where
        Self: 'a;
    type Theory<'a>: TheoryBlock
    where
        Self: 'a;
    type Structure<'a>: StructureBlock
    where
        Self: 'a;
    type VocabAst: for<'a> VocabAst<Decls<'a> = <Self::Vocab<'a> as VocabBlock>::Decls>;
    type TheoryAst: for<'a> TheoryAst<Decls<'a> = <Self::Theory<'a> as TheoryBlock>::Decls>;
    type StructureAst: for<'a> StructureAst<
        Decls<'a> = <Self::Structure<'a> as StructureBlock>::Decls,
    >;
    fn iter_decls(&self) -> impl Iterator<Item = AstBlock<Self>>;
    fn parse_errors(&self) -> impl Iterator<Item = (ParseError, Span)>;
}

pub trait VocabAst {
    type Decls<'a>: VocabDecls
    where
        Self: 'a;

    fn decls(&self) -> Self::Decls<'_>;
    fn parse_errors(&self) -> impl Iterator<Item = (ParseError, Span)>;
}

pub trait TheoryAst {
    type Decls<'a>: TheoryDecls
    where
        Self: 'a;

    fn decls(&self) -> Self::Decls<'_>;
    fn parse_errors(&self) -> impl Iterator<Item = (ParseError, Span)>;
}

pub trait StructureAst {
    type Decls<'a>: StructureDecls
    where
        Self: 'a;

    fn decls(&self) -> Self::Decls<'_>;
    fn parse_errors(&self) -> impl Iterator<Item = (ParseError, Span)>;
}

/// A span in a FO(·) source.
#[derive(Debug, Clone, Copy, Hash, PartialEq, Eq)]
pub struct Span {
    pub start: usize,
    pub end: usize,
}

impl From<Range<usize>> for Span {
    fn from(value: Range<usize>) -> Self {
        Self {
            start: value.start,
            end: value.end,
        }
    }
}

impl Span {
    pub fn get_str<'a>(&self, source: &'a (impl Source + ?Sized)) -> Cow<'a, str> {
        source.slice(&self)
    }
}

/// Type alias for [Block].
pub type AstBlock<'a, A> =
    Block<<A as Ast>::Vocab<'a>, <A as Ast>::Theory<'a>, <A as Ast>::Structure<'a>>;

/// Enum of FO(·) blocks.
#[non_exhaustive]
pub enum Block<V, T, S> {
    Vocab(V),
    Theory(T),
    Structure(S),
}

impl<V, T, S> Block<V, T, S> {
    pub fn vocab(self) -> Option<V> {
        if let Self::Vocab(vocab) = self {
            Some(vocab)
        } else {
            None
        }
    }

    pub fn theory(self) -> Option<T> {
        if let Self::Theory(theory) = self {
            Some(theory)
        } else {
            None
        }
    }

    pub fn structure(self) -> Option<S> {
        if let Self::Structure(structure) = self {
            Some(structure)
        } else {
            None
        }
    }
}

/// Ast of a vocabulary block.
pub trait VocabBlock: Spanned {
    type Decls: VocabDecls;
    fn name(&self) -> Option<Span>;
    fn decls<'a>(&'a self) -> Self::Decls;
}

pub trait VocabDecls {
    type Type: TypeDeclaration;
    type Pfunc: PfuncDeclaration;
    fn iter_decls<'a>(&'a self) -> impl Iterator<Item = Declaration<Self::Type, Self::Pfunc>> + 'a;
}

/// Types of declarations in a [VocabBlock].
#[non_exhaustive]
pub enum Declaration<T, P> {
    Type(T),
    Pfunc(P),
}

/// A type declaration in a [VocabBlock].
pub trait TypeDeclaration: Sized + Spanned {
    type Enumeration: Enumeration;
    fn name(&self) -> Span;
    fn supertype(&self) -> Option<Span>;
    fn enumeration(&self) -> Option<Self::Enumeration>;
}

/// A pfunc declaration in a [VocabBlock].
pub trait PfuncDeclaration: Spanned {
    fn names<'a>(&'a self) -> impl Iterator<Item = Span> + 'a;
    fn domain<'a>(&'a self) -> impl Iterator<Item = Span> + 'a;
    fn codomain(&self) -> MaybePoisoned<Span>;
}

/// The names of a [TheoryBlock].
pub struct TheoryNames {
    pub theory_name: Span,
    pub vocab_name: Span,
}

/// Ast of a theory block.
pub trait TheoryBlock: Spanned {
    type Decls: TheoryDecls;
    fn names(&self) -> Option<TheoryNames>;
    fn decls(&self) -> Self::Decls;
}

pub trait TheoryDecls {
    type Expressions: Expressions;
    type Definition: Definition;
    fn iter_decls(&self) -> impl Iterator<Item = Assertion<Self::Expressions, Self::Definition>>;
}

/// Expressions of a singular [Parser].
pub trait Expressions {
    type BinaryOp: BinaryOp<Formula = Self>;
    type CmpOp: CmpOp<Formula = Self>;
    type UnaryOp: UnaryOp<Formula = Self>;
    type Variables: Variables;
    type Quantification: Quantification<Formula = Self>;
    type CountAgg: CountAgg<Formula = Self>;
    type SumAgg: SumAgg<Formula = Self>;
    type Ite: Ite<Formula = Self>;
    type AppliedSymbol: AppliedSymbol<Formula = Self>;
    type InEnumeration: InEnumeration<Formula = Self>;
    type ConjuctiveGuard: ConjuctiveGuard<Formula = Self>;
    type ImplicativeGuard: ImplicativeGuard<Formula = Self>;
    type IfGuard: IfGuard<Formula = Self>;
    type IsEnumerated: IsEnumerated<Formula = Self>;
}

/// Assertion node in an [Ast].
pub enum Assertion<E: Expressions, D: Definition> {
    Expr(Expression<E>),
    Def(D),
}

impl<E: Expressions, D: Definition> Spanned for Assertion<E, D> {
    fn span(&self) -> Span {
        match self {
            Self::Expr(value) => value.span(),
            Self::Def(value) => value.span(),
        }
    }
}

/// An enum of [Expressions].
pub enum Expression<E: Expressions> {
    BinOp(E::BinaryOp),
    CmpOp(E::CmpOp),
    UnaryOp(E::UnaryOp),
    Quantification(E::Quantification),
    Count(E::CountAgg),
    Sum(E::SumAgg),
    Ite(E::Ite),
    AppliedSymbol(E::AppliedSymbol),
    Element(Element),
    InEnumeration(E::InEnumeration),
    ConjuctiveGuard(E::ConjuctiveGuard),
    ImplicativeGuard(E::ImplicativeGuard),
    IfGuard(E::IfGuard),
    IsEnumerated(E::IsEnumerated),
}

impl<E: Expressions> Spanned for Expression<E> {
    fn span(&self) -> Span {
        match self {
            Self::BinOp(value) => value.span(),
            Self::CmpOp(value) => value.span(),
            Self::UnaryOp(value) => value.span(),
            Self::Quantification(value) => value.span(),
            Self::Count(value) => value.span(),
            Self::Sum(value) => value.span(),
            Self::Ite(value) => value.span(),
            Self::AppliedSymbol(value) => value.span(),
            Self::Element(value) => value.span(),
            Self::InEnumeration(in_enum) => in_enum.span(),
            Self::ConjuctiveGuard(value) => value.span(),
            Self::ImplicativeGuard(value) => value.span(),
            Self::IfGuard(value) => value.span(),
            Self::IsEnumerated(value) => value.span(),
        }
    }
}

impl<E: Expressions> Expression<E> {
    pub fn applied_symbol(self) -> Option<E::AppliedSymbol> {
        if let Self::AppliedSymbol(app_symb) = self {
            Some(app_symb)
        } else {
            None
        }
    }
}

/// Types of binary operations.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum BinaryOpKind {
    And,
    Or,
    Rimpl,
    Limpl,
    Eqv,
    Sum,
    Sub,
    Mult,
    Div,
    Rem,
    Eq,
    Gt,
    Lt,
    Ge,
    Le,
    Neq,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CmpOpKind {
    Eq,
    Gt,
    Lt,
    Ge,
    Le,
    Neq,
}

/// Ast of a binary operation.
pub trait BinaryOp: Spanned {
    type Formula: Expressions<BinaryOp = Self>;
    fn kind(&self) -> BinaryOpKind;
    fn binop_span(&self) -> Span;
    fn lhs(&self) -> MaybePoisoned<Expression<Self::Formula>>;
    fn rhs(&self) -> MaybePoisoned<Expression<Self::Formula>>;
}

/// Ast of a chained compare operation
pub trait CmpOp: Spanned {
    type Formula: Expressions<CmpOp = Self>;
    fn first(
        &self,
    ) -> (
        MaybePoisoned<Expression<Self::Formula>>,
        CmpOpKind,
        MaybePoisoned<Expression<Self::Formula>>,
    );
    fn rest(&self) -> impl Iterator<Item = (CmpOpKind, Expression<Self::Formula>)>;
}

/// Types of unary operations.
#[non_exhaustive]
#[derive(Clone, Copy, PartialEq, Eq)]
pub enum UnaryOpKind {
    Negation,
    NumericNegation,
}

/// Ast of a unary operation.
pub trait UnaryOp: Spanned {
    type Formula: Expressions<UnaryOp = Self>;
    fn kind(&self) -> UnaryOpKind;
    fn subformula(&self) -> MaybePoisoned<Expression<Self::Formula>>;
}

/// Ast of a variable(s) declaration.
///
/// In `!x, y in B, z in A: ...` both the `x, y in B` and `z in A` correspond to [Variables].
pub trait Variables: Spanned {
    fn vars<'a>(&'a self) -> impl Iterator<Item = Span> + 'a;
    fn var_type(&self) -> MaybePoisoned<Span>;
}

/// Types of quantification.
#[derive(Clone, Copy, PartialEq, Eq)]
pub enum QuantificationKind {
    Universal,
    Existential,
}

/// Ast of a quantification.
pub trait Quantification: Spanned {
    type Formula: Expressions<Quantification = Self>;
    fn variables<'a>(
        &'a self,
    ) -> impl Iterator<Item = <Self::Formula as Expressions>::Variables> + 'a;
    fn kind(&self) -> QuantificationKind;
    fn kind_span(&self) -> Span;
    fn subformula(&self) -> MaybePoisoned<Expression<Self::Formula>>;
}

/// Ast of a cardinality aggregate.
pub trait CountAgg: Spanned {
    type Formula: Expressions<CountAgg = Self>;
    fn subformula(&self) -> MaybePoisoned<Expression<Self::Formula>>;
    fn variables<'a>(
        &'a self,
    ) -> impl Iterator<Item = <Self::Formula as Expressions>::Variables> + 'a;
}

/// Ast of a sum aggregate.
pub trait SumAgg: Spanned {
    type Formula: Expressions<SumAgg = Self>;
    fn variables<'a>(
        &'a self,
    ) -> impl Iterator<Item = <Self::Formula as Expressions>::Variables> + 'a;
    fn term(&self) -> MaybePoisoned<Expression<Self::Formula>>;
    fn subformula(&self) -> MaybePoisoned<Expression<Self::Formula>>;
}

/// Ast of an if then else expression.
pub trait Ite: Spanned {
    type Formula: Expressions<Ite = Self>;
    fn if_formula(&self) -> MaybePoisoned<Expression<Self::Formula>>;
    fn then_term(&self) -> MaybePoisoned<Expression<Self::Formula>>;
    fn else_term(&self) -> MaybePoisoned<Expression<Self::Formula>>;
}

/// Ast of an applied symbol expression.
pub trait AppliedSymbol: Spanned {
    type Formula: Expressions<AppliedSymbol = Self>;
    fn name(&self) -> Span;
    fn args_len(&self) -> usize;
    fn args(&self) -> impl Iterator<Item = Expression<Self::Formula>>;
}

/// Ast of a definition.
pub trait Definition: Spanned {
    type Formula: Expressions;
    type Rule: DefinitionalRule;
    fn rules(&self) -> impl Iterator<Item = Self::Rule>;
}

/// Ast of a definitional rule.
pub trait DefinitionalRule: Spanned {
    type Formula: Expressions;
    fn head(&self) -> MaybePoisoned<Expression<Self::Formula>>;
    fn body(&self) -> MaybePoisoned<Expression<Self::Formula>>;
}

pub trait InEnumeration: Spanned {
    type Formula: Expressions;
    fn expr(&self) -> MaybePoisoned<Expression<Self::Formula>>;
    fn enumeration(&self) -> impl Iterator<Item = Expression<Self::Formula>>;
}

pub trait ConjuctiveGuard: Spanned {
    type Formula: Expressions;
    fn subformula(&self) -> MaybePoisoned<Expression<Self::Formula>>;
}

pub trait ImplicativeGuard: Spanned {
    type Formula: Expressions;
    fn subformula(&self) -> MaybePoisoned<Expression<Self::Formula>>;
}

pub trait IfGuard: Spanned {
    type Formula: Expressions;
    fn term(&self) -> MaybePoisoned<Expression<Self::Formula>>;
    fn else_term(&self) -> MaybePoisoned<Expression<Self::Formula>>;
}

pub trait IsEnumerated: Spanned {
    type Formula: Expressions;
    fn applied_symbol(&self) -> MaybePoisoned<<Self::Formula as Expressions>::AppliedSymbol>;
}

/// The names of a [StructureBlock].
pub struct StructureNames {
    pub structure_name: Span,
    pub vocab_name: Span,
}

/// Ast of a structure block.
pub trait StructureBlock: Spanned {
    type Decls: StructureDecls;
    fn names(&self) -> Option<StructureNames>;
    fn decls(&self) -> Self::Decls;
}

pub trait StructureDecls {
    type Interp: SymbolInterpretation;
    fn interpretations(&self) -> impl Iterator<Item = Self::Interp>;
}

/// Enum representing an element.
#[non_exhaustive]
#[derive(Debug, Clone)]
pub enum Element {
    Int(Span),
    Real(Span),
    String(Span),
}

impl Spanned for Element {
    fn span(&self) -> Span {
        match self {
            Self::Int(span) | Self::Real(span) | Self::String(span) => *span,
        }
    }
}

impl Element {
    pub fn int(self) -> Option<Span> {
        if let Self::Int(int) = self {
            Some(int)
        } else {
            None
        }
    }

    pub fn real_or_int(self) -> Option<Span> {
        match self {
            Self::Int(int) => Some(int),
            Self::Real(real) => Some(real),
            _ => None,
        }
    }

    pub fn real(self) -> Option<Span> {
        if let Self::Real(real) = self {
            Some(real)
        } else {
            None
        }
    }

    pub fn string(self) -> Option<Span> {
        if let Self::String(real) = self {
            Some(real)
        } else {
            None
        }
    }
}

/// Ast of a tuple.
pub trait Tuple: Spanned {
    fn get(&self, index: usize) -> Option<Element>;
    fn len(&self) -> usize;
    fn values<'a>(&'a self) -> impl Iterator<Item = Element> + 'a;
}

/// The types of an interpretation.
#[non_exhaustive]
#[derive(Clone, Copy, PartialEq, Eq)]
pub enum InterpKind {
    Total,
    Partial,
}

impl InterpKind {
    pub fn is_total(&self) -> bool {
        matches!(self, Self::Total)
    }

    pub fn is_partial(&self) -> bool {
        matches!(self, Self::Partial)
    }
}

/// Ast of a symbol interpretation.
///
/// i.e. `p := ...`
pub trait SymbolInterpretation: Spanned {
    type Tuple: Tuple;
    type Enumeration: EnumerationInterpretation<Enumeration: Enumeration<Tuple = Self::Tuple>>;
    fn name(&self) -> Span;
    fn interpretation_kind(&self) -> InterpKind;
    fn interpretation_kind_span(&self) -> Span;
    fn interpretation(&self) -> Interpretation<Self::Enumeration>;
}

/// An enum representing either a constant interpretation or an enumeration interpretation.
pub enum Interpretation<E> {
    Constant(Element),
    Enumeration(E),
}

impl<E: EnumerationInterpretation> Spanned for Interpretation<E> {
    fn span(&self) -> Span {
        match self {
            Self::Constant(constant) => constant.span(),
            Self::Enumeration(enumeration) => enumeration.span(),
        }
    }
}

/// Ast of an enumeration interpretation.
///
/// i.e. `{...} else ...`.
pub trait EnumerationInterpretation: Spanned {
    type Enumeration: Enumeration;
    fn enumeration(&self) -> Self::Enumeration;
    fn else_element(&self) -> Option<Element>;
}

/// Ast of the 'set' of an [EnumerationInterpretation].
pub trait Enumeration: Spanned {
    type Tuple: Tuple;
    fn values(&self) -> impl Iterator<Item = EnumerationElement<Self::Tuple>>;
}

/// A singular interpretation element allowed in an [Enumeration].
///
/// Do note that we allow parsing more than is possible.
/// i.e. there is no symbol with a correct interpretation consisting of an element and a mapping.
pub enum EnumerationElement<T: Tuple> {
    Set(SetElement<T>),
    Map((TupleOrElement<T>, Element)),
}

impl<T: Tuple> Spanned for EnumerationElement<T> {
    fn span(&self) -> Span {
        match self {
            Self::Set(value) => value.span(),
            Self::Map(value) => {
                let arg = value.0.span();
                let value = value.1.span();
                Span {
                    start: arg.start.min(value.start),
                    end: arg.end.max(value.end),
                }
            }
        }
    }
}

impl<T: Tuple> EnumerationElement<T> {
    pub fn set(self) -> Option<SetElement<T>> {
        if let Self::Set(value) = self {
            Some(value)
        } else {
            None
        }
    }

    pub fn map(self) -> Option<(TupleOrElement<T>, Element)> {
        if let Self::Map(value) = self {
            Some(value)
        } else {
            None
        }
    }
}

/// The range allowed in an enumeration.
pub struct EnumerationRange {
    pub start: Span,
    pub end: Span,
}

impl Spanned for EnumerationRange {
    fn span(&self) -> Span {
        Span::from(self.start.start..self.end.end)
    }
}

/// All types of interpretation elements for a set.
pub enum SetElement<T: Tuple> {
    El(Element),
    Tuple(T),
    Range(EnumerationRange),
}

impl<T: Tuple> Spanned for SetElement<T> {
    fn span(&self) -> Span {
        match self {
            Self::El(value) => value.span(),
            Self::Tuple(value) => value.span(),
            Self::Range(value) => value.span(),
        }
    }
}

impl<T: Tuple> SetElement<T> {
    pub fn element(self) -> Option<Element> {
        if let Self::El(element) = self {
            Some(element)
        } else {
            None
        }
    }

    pub fn range(self) -> Option<EnumerationRange> {
        if let Self::Range(range) = self {
            Some(range)
        } else {
            None
        }
    }

    pub fn range_or_element(self) -> Option<Either<EnumerationRange, Element>> {
        match self {
            Self::El(el) => Some(Either::Right(el)),
            Self::Range(range) => Some(Either::Left(range)),
            _ => None,
        }
    }

    pub fn tuple(self) -> Option<T> {
        if let Self::Tuple(tuple) = self {
            Some(tuple)
        } else {
            None
        }
    }
}

/// Either a tuple or an element.
pub enum TupleOrElement<T> {
    Tuple(T),
    El(Element),
}

impl<T: Tuple> Spanned for TupleOrElement<T> {
    fn span(&self) -> Span {
        match self {
            Self::Tuple(value) => value.span(),
            Self::El(value) => value.span(),
        }
    }
}

impl<T> TupleOrElement<T> {
    pub fn element(self) -> Option<Element> {
        if let Self::El(element) = self {
            Some(element)
        } else {
            None
        }
    }

    pub fn tuple(self) -> Option<T> {
        if let Self::Tuple(tuple) = self {
            Some(tuple)
        } else {
            None
        }
    }
}
