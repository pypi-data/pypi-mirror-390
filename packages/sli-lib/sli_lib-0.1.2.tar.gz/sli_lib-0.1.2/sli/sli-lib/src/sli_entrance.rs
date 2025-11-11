use itertools::Either;

use crate::{
    ast::{
        self, Ast, BinaryOp, CmpOp, Enumeration, EnumerationElement, EnumerationInterpretation,
        EnumerationRange, MaybePoisoned, ParseError, PfuncDeclaration, SetElement, Span, Spanned,
        SymbolInterpretation, Tuple, TupleOrElement, TypeDeclaration,
    },
    fodot::{
        Metadata, MetadataMut, TryFromCtx, TryIntoCtx,
        error::{
            ApplyErrorKind, ArgMismatchKind, BuiltinTypeInterpretationError, DefRuleErrorKind,
            ExprBinOpErrorKind, ExprMismatchErrorKind, ExprSubMismatchErrorKind,
            ExtendedPfuncErrorKind, InconsistentAssignment, InterpretationType,
            InvalidDefHeadError, MismatchedArity, MissingSymbol, NotAllowedError,
            NullaryConstructorApplicationError, NullaryErrorKind, ParseArgCreationError,
            ParseBaseTypeError, ParseBoolError, ParseInterpMultiImage, ParseTypeElementError,
            Redeclaration, SetTypeInterpIncompleteErrorKind, TypeMismatch, VocabMismatchError,
            WithPartialInterpsErrorKind, WrongPfuncInterpretation, WrongTypeInterpretation,
            parse::{Diagnostics, IDPError},
        },
        fmt::BOOL_ASCII,
        structure::{
            ArgsBuilder, IncompleteStructure, IntInterp, PartialTypeInterps, RealInterp, StrInterp,
            StructureBlock, TypeElement, TypeInterp, partial,
        },
        theory::{
            AggType, Aggregate, AppliedSymbol, Assertion, Assertions, BinOp, BinOps,
            CardinalityAggregate, ChainedCmp, ConjuctiveGuard, Definition, DefinitionalHead,
            DefinitionalRule, Element, ElementExpr, Expr, Formula, IfGuard, ImplicativeGuard,
            InEnumeration, IsEnumerated, Ite, Negation, NumNegation, OrdOps, QuantType, Quantees,
            QuanteesBuilder, Quantification, Theory, TheoryBlock, Variable, VariableDecl,
            WellDefinedFormula,
        },
        vocabulary::{
            BaseType, CustomType, Int, Real, Symbol, Type, TypeStr, Vocabulary, parse_bool_value,
            parse_bool_value_or_string, parse_int_value,
        },
    },
};
use sli_collections::rc::Rc;
use std::{
    borrow::Cow,
    collections::{BTreeSet, HashMap},
    ops::RangeInclusive,
    str::FromStr,
};

/// A mapping from names to [Variable]s.
struct QuantVariableStack<'a> {
    variables: core::cell::RefCell<HashMap<Cow<'a, str>, Variable>>,
}

impl<'a> QuantVariableStack<'a> {
    fn new() -> Self {
        Self {
            variables: Default::default(),
        }
    }

    fn get_var_ref(&self, value: &str) -> Option<Variable> {
        self.variables
            .borrow()
            .get(value)
            .map(|f| f.create_var_ref())
    }

    fn insert(&self, name: Cow<'a, str>, var: Variable) -> Option<Variable> {
        self.variables.borrow_mut().insert(name, var)
    }

    fn quantees_context(&self, quantees: Quantees) -> QuanteesContext<'a, '_> {
        QuanteesContext {
            quantees,
            stack: self,
        }
    }

    fn remove_quantees(&self, quantees: &Quantees) {
        let mut variables = self.variables.borrow_mut();
        for quant in quantees.iter() {
            variables.remove(quant.name());
        }
    }
}

/// We use this to ensure we remove added variables to the name variable mapping.
///
/// This struct ensures we remove the names even with whacky code paths were we bail out early.
/// This is ensured by the [Drop] implementation.
struct QuanteesContext<'a, 'b> {
    quantees: Quantees,
    stack: &'b QuantVariableStack<'a>,
}

impl<'a, 'b> QuanteesContext<'a, 'b> {
    fn destroy(self) -> Quantees {
        self.stack.remove_quantees(&self.quantees);
        // We must use unsafe here because a [Drop] implementation disallows us to destructure a
        // struct.
        // Safety: this is alright since we forget the original owner, manually transferring
        // ownership
        //
        // This is needed to get quantees, since the drop implementation doesn't allow us to move
        // quantees out of self
        let quantees = unsafe { core::ptr::read(&self.quantees) };
        // We must forget here so we don't deallocate something we are actually still using
        // And so we don't remove quantees twice, which won't be much of a problem but still
        core::mem::forget(self);
        quantees
    }
}

impl<'a, 'b> Drop for QuanteesContext<'a, 'b> {
    fn drop(&mut self) {
        self.stack.remove_quantees(&self.quantees)
    }
}

pub(crate) fn parse_range(
    range: &EnumerationRange,
    source: &dyn ast::Source,
    diagnostics: &mut Diagnostics,
) -> Option<RangeInclusive<Int>> {
    let start = parse_int_value(&range.start.get_str(source))
        .map_err(|f| diagnostics.add_error(IDPError::new(f.into(), range.start)))
        .ok();
    let end = parse_int_value(&range.end.get_str(source))
        .map_err(|f| diagnostics.add_error(IDPError::new(f.into(), range.end)))
        .ok();
    let start = start?;
    let end = end?;
    Some(start..=end)
}

/// Adds the declaration given by the [ast::Declaration] to the [Vocabulary].
fn create_decl(
    vocabulary: &mut Vocabulary,
    source: &dyn ast::Source,
    cur: &ast::Declaration<impl TypeDeclaration, impl PfuncDeclaration>,
    diagnostics: &mut Diagnostics,
) -> Option<()> {
    match cur {
        ast::Declaration::Type(type_decl) => {
            let mut interp = None;
            let decl_super_type: Result<Option<BaseType>, _> = type_decl
                .supertype()
                .map(|f| {
                    f.get_str(source)
                        .parse()
                        .map_err(|err: ParseBaseTypeError| (err, f))
                })
                .transpose()
                .map_err(|(err, span)| diagnostics.add_error(IDPError::new(err.into(), span)));
            let (super_type_poisoned, decl_super_type) =
                (decl_super_type.is_err(), decl_super_type.ok().flatten());
            let super_type;
            match (
                type_decl.enumeration(),
                decl_super_type,
                super_type_poisoned,
            ) {
                (_, _, true) => {
                    super_type = Some(BaseType::Str);
                }
                (Some(x), Some(decl_super_type), _) => {
                    super_type = Some(decl_super_type);
                    interp = create_type_interps(source, decl_super_type, x, diagnostics)
                }
                (Some(x), None, _) => {
                    let value =
                        infer_and_create_type_interps(source, decl_super_type, x, diagnostics)
                            .map(|f| (Some(f.0), f.1));
                    if let Some(value) = value {
                        (interp, super_type) = (value.0, Some(value.1));
                    } else {
                        (interp, super_type) = (None, None);
                    }
                }
                (None, Some(value), _) => {
                    super_type = Some(value);
                }
                (None, None, _) => {
                    super_type = Some(BaseType::Str);
                }
            }

            let name = type_decl.name().get_str(source);
            let super_type = super_type?;
            vocabulary
                .add_type_decl(&name, super_type.into())
                .map_err(|f| diagnostics.add_error(IDPError::new(f.into(), type_decl.span())))
                .ok()?;
            let metadata = vocabulary
                .type_metadata_mut(&name)
                .unwrap()
                .set_metadata(Metadata::default().with_span(type_decl.span()))
                .set_name_span(type_decl.name());
            if let Some(superset) = type_decl.supertype() {
                metadata.set_superset_span(superset);
            }
            if let Some(interp) = interp {
                vocabulary
                    .add_voc_type_interp(&name, interp)
                    .map_err(|f| {
                        diagnostics.add_error(IDPError::new(
                            f.into(),
                            type_decl.enumeration().unwrap().span(),
                        ))
                    })
                    .ok()?;
            }
        }
        ast::Declaration::Pfunc(pfunc_decl) => {
            let codomain_value = pfunc_decl.codomain();
            let (mut func_builder, poisoned) = if let Some(Ok(value)) =
                codomain_value.value().map(|codomain_span| {
                    vocabulary
                        .build_pfunc_decl(&codomain_span.get_str(source))
                        .map(|f| (f, Some(codomain_span)))
                        .map_err(|f| diagnostics.add_error(IDPError::new(f.into(), codomain_span)))
                }) {
                value
            } else {
                // build a pfunc with a boolean codomain so we can find errors in the domain of the
                // pfunc
                (vocabulary.build_pfunc_decl(BOOL_ASCII).unwrap(), None)
            };
            let mut domain_spans = Vec::new();
            for domain_span in pfunc_decl.domain() {
                let domain = domain_span.get_str(source);
                let _ = func_builder
                    .add_to_domain(&domain)
                    .map_err(|f| diagnostics.add_error(IDPError::new(f.into(), domain_span)));
                domain_spans.push(domain_span);
            }
            let domain_spans: Rc<[Span]> = domain_spans.into();
            let pfunc_metadata = Metadata::default().with_span(pfunc_decl.span());

            for name_span in pfunc_decl.names() {
                let name = name_span.get_str(source);
                if let Some(codomain_span) = poisoned {
                    let _ = func_builder
                        .complete_with_name(&name)
                        .map_err(|f| diagnostics.add_error(IDPError::new(f.into(), name_span)));
                    func_builder
                        .vocab_mut()
                        .pfunc_metadata_mut(&name)
                        .unwrap()
                        .set_metadata(pfunc_metadata.clone())
                        .set_pfunc_span(name_span)
                        .set_domain_span(domain_spans.clone())
                        .set_codomain_span(codomain_span);
                } else {
                    if func_builder.vocab().parse_symbol(&name).is_ok() {
                        diagnostics.add_error(IDPError::new(
                            Redeclaration(name.as_ref().into()).into(),
                            name_span,
                        ))
                    }
                }
            }
        }
    }
    Some(())
}

/// Lowers the given vocabulary.
fn parse_vocab(
    source: &dyn ast::Source,
    vocab_block: &impl ast::VocabBlock,
    diagnostics: &mut Diagnostics,
) -> Vocabulary {
    let vocab_name = vocab_block.name().map(|f| f.get_str(source));
    let mut vocabulary = Vocabulary::new(vocab_name.as_deref().unwrap_or("V"));
    parse_vocab_decls(source, &mut vocabulary, vocab_block.decls(), diagnostics);
    return vocabulary;
}

pub(crate) fn parse_vocab_decls(
    source: &dyn ast::Source,
    vocabulary: &mut Vocabulary,
    decls: impl ast::VocabDecls,
    diagnostics: &mut Diagnostics,
) {
    for decl in decls.iter_decls() {
        create_decl(vocabulary, source, &decl, diagnostics);
    }
}

fn infer_and_create_type_interps(
    source: &dyn ast::Source,
    base_type: Option<BaseType>,
    set: impl ast::Enumeration,
    diagnostics: &mut Diagnostics,
) -> Option<(TypeInterp, BaseType)> {
    let base_type = base_type.unwrap_or_else(|| {
        let mut supertype = BaseType::Int;
        for value in set.values() {
            let Some(value) = value.set() else {
                continue;
            };
            let parsed_type = match value {
                SetElement::El(ast::Element::String(value)) => {
                    if parse_bool_value(&value.get_str(source)).is_ok() {
                        // ignore this since create_type_interps will create an error here
                        continue;
                    }
                    BaseType::Str
                }
                SetElement::El(ast::Element::Int(_)) => BaseType::Int,
                SetElement::El(ast::Element::Real(_)) => BaseType::Real,
                SetElement::Range(_) => BaseType::Int,
                // ignore this since create_type_interps will create an error here
                SetElement::Tuple(_) => continue,
            };
            // TODO do this properly
            match (supertype, parsed_type) {
                (_, BaseType::Str) => {
                    supertype = parsed_type;
                    break;
                }
                (BaseType::Int, BaseType::Real) => {
                    supertype = parsed_type;
                }
                (BaseType::Str, _) => {
                    break;
                }
                (BaseType::Real, _) => {
                    break;
                }
                _ => {}
            }
        }
        supertype
    });
    create_type_interps(source, base_type, set, diagnostics).map(|f| (f, base_type))
}

fn create_type_interps(
    source: &dyn ast::Source,
    base_type: BaseType,
    set: impl ast::Enumeration,
    diagnostics: &mut Diagnostics,
) -> Option<TypeInterp> {
    Some(match base_type {
        BaseType::Int => {
            let mut btree_set = BTreeSet::new();
            for value in set.values() {
                let Some(set_value) = value
                    .set()
                    .ok_or_else(|| {
                        diagnostics
                            .add_error(IDPError::new(WrongTypeInterpretation.into(), set.span()))
                    })
                    .ok()
                else {
                    continue;
                };
                match set_value {
                    SetElement::El(el) => {
                        let el_span = el.span();
                        let thing;
                        let Some(value) = parse_int_value(match el {
                            ast::Element::Int(span) => {
                                thing = span.get_str(source);
                                &thing
                            }
                            ast::Element::Real(span) => {
                                diagnostics.add_error(IDPError::new(
                                    TypeMismatch {
                                        found: TypeStr::Real,
                                        expected: TypeStr::Int,
                                    }
                                    .into(),
                                    span,
                                ));
                                continue;
                            }
                            ast::Element::String(span) => {
                                diagnostics.add_error(IDPError::new(
                                    TypeMismatch {
                                        found: TypeStr::custom(
                                            "TODO: custom string or something".into(),
                                        ),
                                        expected: TypeStr::Int,
                                    }
                                    .into(),
                                    span,
                                ));
                                continue;
                            }
                        })
                        .map_err(|f| diagnostics.add_error(IDPError::new(f.into(), el_span)))
                        .ok() else {
                            continue;
                        };
                        btree_set.insert(value);
                    }
                    SetElement::Range(range_node) => {
                        let Some(range) = parse_range(&range_node, source, diagnostics) else {
                            continue;
                        };
                        for value in range {
                            btree_set.insert(value);
                        }
                    }
                    SetElement::Tuple(tuple) => {
                        diagnostics.add_error(IDPError::new(
                            MismatchedArity {
                                expected: 1,
                                found: tuple.len(),
                            }
                            .into(),
                            tuple.span(),
                        ));
                        continue;
                    }
                }
            }
            IntInterp::try_from_iterator(btree_set)
                .map_err(|f| diagnostics.add_error(IDPError::new(f.into(), set.span())))
                .map(|f| f.into())
                .ok()?
        }
        BaseType::Real => {
            let mut btree_set = BTreeSet::<Real>::new();
            for value in set.values() {
                let value_span = value.span();
                let Some(value) = value
                    .set()
                    .ok_or_else(|| {
                        diagnostics
                            .add_error(IDPError::new(WrongTypeInterpretation.into(), value_span))
                    })
                    .ok()
                else {
                    continue;
                };
                let el = match value {
                    SetElement::Range(_) => {
                        diagnostics.add_error(IDPError::new(
                            NotAllowedError {
                                message: "ranges are not allowed for interpreting real types",
                            }
                            .into(),
                            value_span,
                        ));
                        continue;
                    }
                    SetElement::Tuple(_) => {
                        diagnostics
                            .add_error(IDPError::new(WrongTypeInterpretation.into(), value_span));
                        continue;
                    }
                    SetElement::El(el) => el,
                };
                let Some(value) = Real::from_str(
                    &match el {
                        ast::Element::Real(value) => value,
                        ast::Element::Int(value) => value,
                        ast::Element::String(_) => {
                            diagnostics.add_error(IDPError::new(
                                TypeMismatch {
                                    found: TypeStr::custom(
                                        "TODO: custom string or something".into(),
                                    ),
                                    expected: TypeStr::Real,
                                }
                                .into(),
                                value_span,
                            ));
                            continue;
                        }
                    }
                    .get_str(source),
                )
                .map_err(|f| diagnostics.add_error(IDPError::new(f.into(), value_span)))
                .ok() else {
                    continue;
                };
                btree_set.insert(value);
            }
            RealInterp::from_iter(btree_set).into()
        }
        BaseType::Str => {
            let mut btree_set = BTreeSet::<Rc<str>>::new();
            for value in set.values() {
                let value_span = value.span();
                let Some(value) = value
                    .set()
                    .ok_or_else(|| {
                        diagnostics
                            .add_error(IDPError::new(WrongTypeInterpretation.into(), value_span))
                    })
                    .ok()
                else {
                    continue;
                };
                let el = match value {
                    SetElement::Range(_) => {
                        diagnostics.add_error(IDPError::new(
                            NotAllowedError {
                                message: "ranges are not allowed for interpreting str types",
                            }
                            .into(),
                            value_span,
                        ));
                        continue;
                    }
                    SetElement::Tuple(_) => {
                        diagnostics
                            .add_error(IDPError::new(WrongTypeInterpretation.into(), value_span));
                        continue;
                    }
                    SetElement::El(el) => el,
                };
                let Some(value) = parse_bool_value_or_string(
                    match el {
                        ast::Element::Int(_) => {
                            diagnostics.add_error(IDPError::new(
                                TypeMismatch {
                                    found: TypeStr::Int,
                                    expected: TypeStr::custom(
                                        "TODO: custom string or something".into(),
                                    ),
                                }
                                .into(),
                                value_span,
                            ));
                            continue;
                        }
                        ast::Element::Real(_) => {
                            diagnostics.add_error(IDPError::new(
                                TypeMismatch {
                                    found: TypeStr::Real,
                                    expected: TypeStr::custom(
                                        "TODO: custom string or something".into(),
                                    ),
                                }
                                .into(),
                                value_span,
                            ));
                            continue;
                        }
                        ast::Element::String(value) => value,
                    }
                    .get_str(source),
                )
                .right()
                .ok_or_else(|| {
                    diagnostics.add_error(IDPError::new(
                        TypeMismatch {
                            found: TypeStr::Bool,
                            expected: TypeStr::custom("TODO: custom string or something".into()),
                        }
                        .into(),
                        value_span,
                    ))
                })
                .ok()
                .map(|f| f.into()) else {
                    continue;
                };
                btree_set.insert(value);
            }
            StrInterp::from_iter(btree_set).into()
        }
    })
}

fn parse_type_interps(
    structure: &mut IncompleteStructure,
    vocab: &Vocabulary,
    source: &dyn ast::Source,
    ast_interp: &impl ast::SymbolInterpretation,
    diagnostics: &mut Diagnostics,
) -> Option<()> {
    let name = ast_interp.name().get_str(source);
    let Ok(type_) = vocab.parse_type(&name) else {
        return Some(());
    };
    let custom_type = CustomType::try_from(type_)
        .map_err(|_| {
            diagnostics.add_error(IDPError::new(
                BuiltinTypeInterpretationError.into(),
                ast_interp.name(),
            ))
        })
        .ok()?;
    match ast_interp.interpretation() {
        ast::Interpretation::Enumeration(value) => {
            if let Some(else_element) = value.else_element() {
                diagnostics.add_error(IDPError::new(
                    WrongPfuncInterpretation {
                        expected: InterpretationType::Set,
                        found: InterpretationType::Map,
                    }
                    .into(),
                    else_element.span(),
                ));
            }
            if ast_interp.interpretation_kind().is_partial() {
                diagnostics.add_error(IDPError::new(
                    NotAllowedError {
                        message: "types must be completely interpreted",
                    }
                    .into(),
                    ast_interp.interpretation_kind_span(),
                ));
            }
            let set = value.enumeration();
            let interp = create_type_interps(source, custom_type.super_type(), set, diagnostics)?;
            if let Some(value) = structure.type_interps().get_interp(custom_type).unwrap() {
                return if value != interp {
                    diagnostics.add_error(IDPError::new(
                        InconsistentAssignment {
                            symbol_name: custom_type.name().to_string(),
                        }
                        .into(),
                        ast_interp.span(),
                    ));
                    None
                } else {
                    Some(())
                };
            }
            structure
                .set_interp(custom_type, interp)
                .map(|_| ())
                .map_err(|f| {
                    diagnostics.add_error(IDPError::new(
                        match f.take_kind() {
                            SetTypeInterpIncompleteErrorKind::BaseTypeMismatchError(value) => {
                                value.into()
                            }
                            // unreachable because we always diverge if the type already has an
                            // interpretation.
                            SetTypeInterpIncompleteErrorKind::TypeInterpDependence(_) => {
                                unreachable!()
                            }
                            SetTypeInterpIncompleteErrorKind::VocabMismatchError(_) => {
                                unreachable!()
                            }
                        },
                        value.span(),
                    ))
                })
                .ok()
        }
        _ => {
            diagnostics.add_error(IDPError::new(
                WrongTypeInterpretation.into(),
                ast_interp.interpretation().span(),
            ));
            None
        }
    }
}

/// Fill in the function interp from the given node.
fn add_pfunc_interp<SI: SymbolInterpretation>(
    interpretation: &SI,
    structure: &mut IncompleteStructure,
    source: &dyn ast::Source,
    diagnostics: &mut Diagnostics,
) -> Option<()> {
    let vocab = structure.vocab_rc().clone();
    let pfunc_decl = vocab
        .parse_pfunc(&interpretation.name().get_str(source))
        .map_err(|f| diagnostics.add_error(IDPError::new(f.into(), interpretation.name())))
        .ok()?;
    if pfunc_decl.domain().is_infinite() {
        diagnostics.add_error(IDPError::new(
            NotAllowedError {
                message: "interpretations for infinite domain pfuncs are not allowed",
            }
            .into(),
            interpretation.span(),
        ));
        return None;
    }
    let symbol_interp = structure
        .get_mut(pfunc_decl)
        .map_err(|f| diagnostics.add_error(IDPError::new(f.into(), interpretation.span())))
        .ok()?;
    let kind = interpretation.interpretation_kind();
    if matches!(
        interpretation.interpretation(),
        ast::Interpretation::Constant(_)
    ) && kind.is_partial()
    {
        diagnostics.add_error(IDPError::new(
            NotAllowedError {
                message: "constant interpretations are not allowed to be partial",
            }
            .into(),
            interpretation.interpretation_kind_span(),
        ))
    }
    // If the symbol is not a const/bool, the elements of the interpretation are the children
    // of `enumeration` (between `{}` in FO(.)). If the symbol is a bool or const instead,
    // `enumeration` _is_ the interpretation.
    use partial::mutable as pfunc;
    match (interpretation.interpretation(), symbol_interp.split()) {
        (ast::Interpretation::Constant(const_interp), Either::Left(mut symb)) => {
            let codomain = symb.codomain_full();
            // TODO: fix this, i.e. add parse method for ast::Element
            let val: TypeElement = const_interp
                .span()
                .get_str(source)
                .as_ref()
                .try_into_ctx(codomain)
                .map_err(|f: ParseTypeElementError| {
                    diagnostics.add_error(IDPError::new(f.into(), const_interp.span()))
                })
                .ok()?;
            symb.set(Some(val))
                .map_err(|f| {
                    diagnostics.add_error(match f.take_kind() {
                        NullaryErrorKind::TypeMismatch(f) => {
                            IDPError::new(f.into(), const_interp.span())
                        }
                        NullaryErrorKind::CodomainError(f) => {
                            IDPError::new(f.into(), const_interp.span())
                        }
                        NullaryErrorKind::TypeInterpsMismatchError(_) => unreachable!(),
                    })
                })
                .ok()?;
        }
        (interp @ ast::Interpretation::Constant(_), Either::Right(pfunc::FuncInterp::Pred(_))) => {
            diagnostics.add_error(IDPError::new(
                WrongPfuncInterpretation {
                    expected: InterpretationType::Set,
                    found: InterpretationType::Constant,
                }
                .into(),
                interp.span(),
            ));
            return None;
        }
        (interp @ ast::Interpretation::Constant(_), _) => {
            diagnostics.add_error(IDPError::new(
                WrongPfuncInterpretation {
                    expected: InterpretationType::Map,
                    found: InterpretationType::Constant,
                }
                .into(),
                interp.span(),
            ));
            return None;
        }
        (
            ast::Interpretation::Enumeration(enum_interp),
            Either::Right(
                mut symb @ (pfunc::FuncInterp::IntFunc(_)
                | pfunc::FuncInterp::RealFunc(_)
                | pfunc::FuncInterp::StrFunc(_)),
            ),
        ) => {
            let else_term = enum_interp
                .else_element()
                .map(|f| {
                    f.span()
                        .get_str(source)
                        .as_ref()
                        .try_into_ctx(symb.codomain_full())
                        .map_err(|err: ParseTypeElementError| (err, f.span()))
                        .map(|value| (value, f.span()))
                })
                .transpose()
                .map_err(|(f, span)| diagnostics.add_error(IDPError::new(f.into(), span)))
                .ok()
                .flatten();
            let set_else_term = |mut symb, diagnostics: &mut Diagnostics| -> Option<()> {
                if let Some((else_term, span)) = else_term {
                    match (&mut symb, else_term) {
                        (
                            pfunc::FuncInterp::IntFunc(pfunc::IntFuncSymbolInterp::Int(i)),
                            TypeElement::Int(val),
                        ) => {
                            i.set_all_unknown_to_value(val.into());
                            Some(())
                        }
                        (
                            pfunc::FuncInterp::IntFunc(pfunc::IntFuncSymbolInterp::IntType(i)),
                            TypeElement::Int(val),
                        ) => {
                            i.set_all_unknown_to_value(val.into())
                                .map_err(|f| diagnostics.add_error(IDPError::new(f.into(), span)))
                                .ok()?;
                            Some(())
                        }
                        (
                            pfunc::FuncInterp::RealFunc(pfunc::RealFuncSymbolInterp::Real(i)),
                            TypeElement::Real(val),
                        ) => {
                            i.set_all_unknown_to_value(val.into());
                            Some(())
                        }
                        (
                            pfunc::FuncInterp::RealFunc(pfunc::RealFuncSymbolInterp::RealType(i)),
                            TypeElement::Real(val),
                        ) => {
                            i.set_all_unknown_to_value(val.into())
                                .map_err(|f| diagnostics.add_error(IDPError::new(f.into(), span)))
                                .ok()?;
                            Some(())
                        }
                        (pfunc::FuncInterp::StrFunc(i), TypeElement::Str(val)) => {
                            i.set_all_unknown_to_value(val)
                                .map_err(|f| {
                                    diagnostics.add_error(match f.take_kind() {
                                        NullaryErrorKind::TypeInterpsMismatchError(_) => {
                                            unreachable!()
                                        }
                                        NullaryErrorKind::TypeMismatch(f) => {
                                            IDPError::new(f.into(), span)
                                        }
                                        NullaryErrorKind::CodomainError(f) => {
                                            IDPError::new(f.into(), span)
                                        }
                                    })
                                })
                                .ok()?;
                            Some(())
                        }
                        _ => unreachable!(),
                    }
                } else {
                    Some(())
                }
            };
            let enumeration = enum_interp.enumeration();
            let mut arg_builder = symb.domain_full().build_args();
            for enum_value in enumeration.values() {
                let enum_value_span = enum_value.span();
                let Some((args, value)) = enum_value
                    .map()
                    .ok_or_else(|| {
                        diagnostics.add_error(IDPError::new(
                            WrongPfuncInterpretation {
                                expected: InterpretationType::Map,
                                found: InterpretationType::Set,
                            }
                            .into(),
                            enum_value_span,
                        ))
                    })
                    .ok()
                else {
                    continue;
                };
                let args_span = args.span();
                let image_el = TypeElement::try_from_ctx(
                    value.span().get_str(source).as_ref(),
                    symb.codomain_full(),
                )
                .map_err(|f| diagnostics.add_error(IDPError::new(f.into(), value.span())))
                .ok();
                let mut poisoned = false;
                match args {
                    TupleOrElement::El(element) => {
                        let _ = arg_builder
                            .add_argument(element.span().get_str(source).as_ref())
                            .map_err(|f| {
                                diagnostics.add_error(IDPError::new(f.into(), element.span()));
                                poisoned = true;
                            });
                    }
                    TupleOrElement::Tuple(tuple) => {
                        for args in tuple.values() {
                            let _ = arg_builder
                                .add_argument(args.span().get_str(source).as_ref())
                                .map_err(|f| {
                                    diagnostics.add_error(IDPError::new(f.into(), tuple.span()));
                                    poisoned = true;
                                });
                        }
                    }
                }
                if poisoned {
                    continue;
                }
                let Some(args) = arg_builder
                    .finish()
                    .map_err(|f| diagnostics.add_error(IDPError::new(f.into(), args_span)))
                    .ok()
                else {
                    continue;
                };
                let Some(image_el) = image_el else {
                    continue;
                };
                arg_builder.reset();
                let Some(has_been_set) = symb
                    .set_if_unknown(args.clone(), image_el.clone())
                    .map_err(|f| {
                        diagnostics.add_error(IDPError::new(
                            match f.take_kind() {
                                ExtendedPfuncErrorKind::CodomainError(f) => f.into(),
                                ExtendedPfuncErrorKind::DomainMismatch(f) => f.into(),
                                ExtendedPfuncErrorKind::TypeMismatch(f) => f.into(),
                                ExtendedPfuncErrorKind::TypeInterpsMismatchError(_) => {
                                    unreachable!()
                                }
                            },
                            value.span(),
                        ))
                    })
                    .ok()
                else {
                    continue;
                };
                // e.g. := {a -> b, a -> c}.
                if !has_been_set && symb.get(args.clone()).ok().flatten() != Some(image_el) {
                    diagnostics.add_error(IDPError::new(
                        ParseInterpMultiImage {
                            args: args.iter().map(|f| f.into()).collect(),
                        }
                        .into(),
                        enum_value_span,
                    ));
                    continue;
                }
            }
            set_else_term(symb, diagnostics)?;
            // TODO check if all have been set if not check if partial enumenration
            // else complain
        }
        (
            ast::Interpretation::Enumeration(enum_interp),
            Either::Right(pfunc::FuncInterp::Pred(mut pred)),
        ) => {
            let else_term: Option<bool> = enum_interp
                .else_element()
                .map(|f| {
                    f.span()
                        .get_str(source)
                        .as_ref()
                        .parse()
                        .map_err(|_| ((), f.span()))
                })
                .transpose()
                .map_err(|(_, span)| {
                    diagnostics.add_error(IDPError::new(ParseBoolError.into(), span))
                })
                .ok()
                .flatten();
            let enumeration = enum_interp.enumeration();
            let domain_range = pred.domain().arity() == 1
                && pred.domain().get(0).super_type() == Some(BaseType::Int);
            for enum_values in enumeration.values() {
                match enum_values {
                    interp @ (EnumerationElement::Set(SetElement::El(_) | SetElement::Tuple(_))
                    | EnumerationElement::Map(_)) => {
                        let args_of_element =
                            |element: ast::Element, diagnostics: &mut Diagnostics| {
                                let type_element = element.span().get_str(source);
                                [type_element.as_ref()]
                                    .try_into_ctx(pred.domain_full())
                                    .map_err(|f: ParseArgCreationError| {
                                        diagnostics
                                            .add_error(IDPError::new(f.into(), element.span()))
                                    })
                                    .ok()
                            };
                        let args_of_tuple = |tuple: SI::Tuple, diagnostics: &mut Diagnostics| {
                            tuple
                                .values()
                                .map(|f| f.span().get_str(source))
                                .try_into_ctx(pred.domain_full())
                                .map_err(|f: ParseArgCreationError| {
                                    diagnostics.add_error(IDPError::new(f.into(), tuple.span()))
                                })
                                .ok()
                        };
                        let (args, value, domain_span) = match interp {
                            EnumerationElement::Set(SetElement::El(element)) => {
                                let element_span = element.span();
                                let Some(args) = args_of_element(element, diagnostics) else {
                                    continue;
                                };
                                (args, true, element_span)
                            }
                            EnumerationElement::Set(SetElement::Tuple(tuple)) => {
                                let tuple_span = tuple.span();
                                let Some(args) = args_of_tuple(tuple, diagnostics) else {
                                    continue;
                                };
                                (args, true, tuple_span)
                            }
                            EnumerationElement::Map((map_args, element)) => {
                                let Some(value) = element
                                    .span()
                                    .get_str(source)
                                    .parse()
                                    .map_err(|_| {
                                        diagnostics.add_error(IDPError::new(
                                            ParseBoolError.into(),
                                            element.span(),
                                        ))
                                    })
                                    .ok()
                                else {
                                    continue;
                                };
                                let Some((args, map_args_span)) = (match map_args {
                                    TupleOrElement::El(value) => {
                                        let value_span = value.span();
                                        args_of_element(value, diagnostics).map(|f| (f, value_span))
                                    }
                                    TupleOrElement::Tuple(tuple) => {
                                        let tuple_span = tuple.span();
                                        args_of_tuple(tuple, diagnostics).map(|f| (f, tuple_span))
                                    }
                                }) else {
                                    continue;
                                };
                                (args, value, map_args_span)
                            }
                            _ => unreachable!(),
                        };
                        let _ = pred.set(args, Some(value)).map_err(|f| {
                            diagnostics.add_error(IDPError::new(
                                match f.take_kind() {
                                    ArgMismatchKind::DomainMismatch(f) => f.into(),
                                    ArgMismatchKind::TypeInterpsMismatchError(_) => {
                                        unreachable!()
                                    }
                                },
                                domain_span,
                            ))
                        });
                    }
                    EnumerationElement::Set(SetElement::Range(range_span)) => {
                        if !domain_range {
                            if pred.domain().arity() != 1 {
                                diagnostics.add_error(IDPError::new(
                                    MismatchedArity {
                                        expected: pred.domain().arity(),
                                        found: 1,
                                    }
                                    .into(),
                                    range_span.span(),
                                ));
                            } else {
                                let domain = pred.domain();
                                let type_value = domain.iter().next().unwrap();
                                if !matches!(type_value, Type::Int | Type::IntType(_)) {
                                    diagnostics.add_error(IDPError::new(
                                        TypeMismatch {
                                            expected: type_value.into(),
                                            found: TypeStr::Int,
                                        }
                                        .into(),
                                        range_span.span(),
                                    ));
                                }
                            }
                            continue;
                        }
                        let Some(range) = parse_range(&range_span, source, diagnostics) else {
                            continue;
                        };
                        let mut args = ArgsBuilder::new(pred.domain_full());
                        for value in range {
                            if args
                                .add_argument(TypeElement::from(value))
                                .map_err(|f| {
                                    diagnostics
                                        .add_error(IDPError::new(f.into(), range_span.span()))
                                })
                                .is_err()
                            {
                                continue;
                            }
                            let _ = pred
                                .set(args.get_args().unwrap(), true.into())
                                .map_err(|f| {
                                    diagnostics.add_error(IDPError::new(
                                        match f.take_kind() {
                                            ArgMismatchKind::DomainMismatch(f) => f.into(),
                                            ArgMismatchKind::TypeInterpsMismatchError(_) => {
                                                unreachable!()
                                            }
                                        },
                                        range_span.span(),
                                    ))
                                });
                            args.reset();
                        }
                    }
                }
            }
            if let Some(else_value) = else_term {
                pred.set_all_unknown_to_value(else_value);
            } else if kind.is_total() {
                pred.set_all_unknown_to_value(false);
            }
        }
        (interp @ ast::Interpretation::Enumeration(_), _) => {
            diagnostics.add_error(IDPError::new(
                WrongPfuncInterpretation {
                    expected: InterpretationType::Constant,
                    found: InterpretationType::Set,
                }
                .into(),
                interp.span(),
            ));
            return None;
        }
    }
    return Some(());
}

/// Fill in all the pfunc interpretations in the structure.
fn parse_pfunc_interps(
    structure: &mut IncompleteStructure,
    source: &dyn ast::Source,
    interp: &impl ast::SymbolInterpretation,
    diagnostics: &mut Diagnostics,
) -> Option<()> {
    let name = interp.name().get_str(source);
    let vocab = Rc::clone(structure.vocab_rc());
    match vocab
        .parse_symbol(&name)
        .map_err(|f| diagnostics.add_error(IDPError::new(f.into(), interp.name())))
        .ok()?
    {
        Symbol::Pfunc(_) => {}
        // ignore type interpretations since these have already been handled.
        Symbol::Type(_) => return Some(()),
        Symbol::Constructor(_) => {
            diagnostics.add_error(IDPError::new(
                NotAllowedError {
                    message: "cannot give a constructor an interpretation",
                }
                .into(),
                interp.span(),
            ));
            return None;
        }
    }
    add_pfunc_interp(interp, structure, source, diagnostics)?;
    return Some(());
}

/// Lowers the given structure.
fn parse_struct(
    partial_type_interps: PartialTypeInterps,
    vocab: &Rc<Vocabulary>,
    block: &impl ast::StructureBlock,
    source: &dyn ast::Source,
    diagnostics: &mut Diagnostics,
) -> Option<StructureBlock> {
    let names = block.names();
    let structure_name = names.as_ref().map(|f| f.structure_name.get_str(source));
    // First, interpret the types in our unfinished structure.
    let mut structure = IncompleteStructure::new(partial_type_interps);
    parse_partial_struct_decls(&mut structure, vocab, block.decls(), source, diagnostics);

    // Now that our structure is no longer unfinished, we can also parse any other symbol
    // interpretations in the structure.
    parse_struct_decls(&mut structure, block.decls(), source, diagnostics);
    return Some(StructureBlock {
        name: structure_name.as_deref().unwrap_or("").into(),
        structure: structure.into(),
    });
}

fn parse_partial_struct_decls(
    structure: &mut IncompleteStructure,
    vocab: &Rc<Vocabulary>,
    block: impl ast::StructureDecls,
    source: &dyn ast::Source,
    diagnostics: &mut Diagnostics,
) {
    for interps in block.interpretations() {
        parse_type_interps(structure, vocab.as_ref(), source, &interps, diagnostics);
    }
}

pub(crate) fn parse_struct_decls(
    structure: &mut IncompleteStructure,
    block: impl ast::StructureDecls,
    source: &dyn ast::Source,
    diagnostics: &mut Diagnostics,
) {
    for interps in block.interpretations() {
        parse_pfunc_interps(structure, source, &interps, diagnostics);
    }
}

/// Parses [Quantees].
fn parse_quantees<'a, 'b, 'c, 'd>(
    vocabulary: &Rc<Vocabulary>,
    quantification_variables: impl Iterator<Item = impl ast::Variables>,
    quant_names: &'d QuantVariableStack<'b>,
    source: &'b dyn ast::Source,
    diagnostics: &mut Diagnostics,
) -> Option<QuanteesContext<'b, 'd>>
where
    'a: 'b,
{
    let mut quants = QuanteesBuilder::new();
    let mut poisoned = false;
    for quantification in quantification_variables {
        let Some((type_span, type_name)) = quantification
            .var_type()
            .value()
            .map(|f| (f, f.get_str(source)))
        else {
            poisoned = true;
            continue;
        };
        let type_rc = Vocabulary::parse_type_rc(vocabulary, &type_name)
            .map_err(|f| diagnostics.add_error(IDPError::new(f.into(), type_span)))
            .ok()?;
        for variable in quantification.vars() {
            let var_name = variable.get_str(source);
            if let Ok(_) = vocabulary.parse_symbol(&var_name) {
                diagnostics.add_error(IDPError::new(
                    Redeclaration(var_name.as_ref().into()).into(),
                    variable,
                ));
                continue;
            }
            let var_decl = VariableDecl::new(var_name.as_ref().into(), type_rc.clone())
                .with_span(quantification.span())
                .with_var_span(type_span)
                .with_type_span(variable)
                .finish();
            if let Some(_) = quant_names.insert(var_name.clone(), var_decl.create_var_ref()) {
                // redeclaration of quantification variable
                diagnostics.add_error(IDPError::new(
                    Redeclaration(var_name.as_ref().into()).into(),
                    variable,
                ));
                poisoned = true;
            }
            quants.add_decl(var_decl);
        }
    }
    if !poisoned {
        Some(quant_names.quantees_context(
            // This can only be caused by a parsing error.
            // Since a quantification must contain at least 1 variable
            quants.finish().ok()?,
        ))
    } else {
        None
    }
}

fn convert_cmp_op(bin_op: ast::CmpOpKind) -> OrdOps {
    use ast::CmpOpKind as C;
    match bin_op {
        C::Neq => OrdOps::NotEqual,
        C::Eq => OrdOps::Equal,
        C::Lt => OrdOps::LessThan,
        C::Le => OrdOps::LessOrEqual,
        C::Gt => OrdOps::GreaterThan,
        C::Ge => OrdOps::GreaterOrEqual,
    }
}

/// Creates an [Expr] from the given node.
fn create_node<'b, 'a>(
    vocabulary: &Rc<Vocabulary>,
    expression: ast::Expression<impl ast::Expressions>,
    quant_names: &QuantVariableStack<'b>,
    source: &'a dyn ast::Source,
    diagnostics: &mut Diagnostics,
) -> Option<Expr>
where
    'a: 'b,
{
    match expression {
        ast::Expression::BinOp(bin_op_node) => {
            use ast::BinaryOpKind as B;
            let mut canon_lhs = bin_op_node.lhs();
            let mut canon_rhs = bin_op_node.rhs();
            let bin_op = match bin_op_node.kind() {
                B::Neq => BinOps::NotEqual,
                B::Eq => BinOps::Equal,
                B::Eqv => BinOps::Equivalence,
                B::Lt => BinOps::LessThan,
                B::Le => BinOps::LessOrEqual,
                B::Gt => BinOps::GreaterThan,
                B::Ge => BinOps::GreaterOrEqual,
                B::Rem => BinOps::Rem,
                B::Sum => BinOps::Add,
                B::Sub => BinOps::Subtract,
                B::Mult => BinOps::Mult,
                B::Or => BinOps::Or,
                B::And => BinOps::And,
                B::Div => BinOps::Division,
                B::Limpl => {
                    core::mem::swap(&mut canon_lhs, &mut canon_rhs);
                    BinOps::Implication
                }
                B::Rimpl => BinOps::Implication,
            };
            let lhs = canon_lhs
                .value()
                .map(|f| create_node(vocabulary, f, quant_names, source, diagnostics));
            let rhs = canon_rhs
                .value()
                .map(|f| create_node(vocabulary, f, quant_names, source, diagnostics));
            let lhs = lhs.flatten()?;
            let rhs = rhs.flatten()?;
            BinOp::new(lhs, bin_op, rhs)
                .map_err(|f| {
                    diagnostics.add_error(IDPError::new(
                        match f.take_kind() {
                            ExprBinOpErrorKind::VocabMismatchError(_) => unreachable!(),
                            ExprBinOpErrorKind::BoolEqualityError(value) => value.into(),
                            ExprBinOpErrorKind::TypeMismatch(value) => value.into(),
                            ExprBinOpErrorKind::SubTypeMismatch(value) => value.into(),
                            ExprBinOpErrorKind::DivByZeroError(value) => value.into(),
                            ExprBinOpErrorKind::NotBoolExpr(value) => value.into(),
                        },
                        bin_op_node.span(),
                    ))
                })
                .ok()
                .map(|f| f.with_span(bin_op_node.span()))
                .map(|f| Expr::from(f))
        }
        ast::Expression::CmpOp(cmp_op) => {
            let first = cmp_op.first();
            let lhs = first.0.value().and_then(|f| {
                let f_span = f.span();
                create_node(vocabulary, f, quant_names, source, diagnostics).map(|d| (d, f_span))
            });
            let op = convert_cmp_op(first.1);
            let rhs = first.2.value().and_then(|f| {
                let f_span = f.span();
                create_node(vocabulary, f, quant_names, source, diagnostics).map(|d| (d, f_span))
            });
            let (lhs, lhs_span) = lhs?;
            let (rhs, rhs_span) = rhs?;
            let mut prev_span = rhs_span;
            let mut cur = ChainedCmp::new(lhs, op, rhs)
                .map_err(|f| {
                    diagnostics.add_error(IDPError::new(
                        match f.take_kind() {
                            ExprSubMismatchErrorKind::VocabMismatchError(_) => unreachable!(),
                            ExprSubMismatchErrorKind::TypeMismatch(value) => value.into(),
                            ExprSubMismatchErrorKind::SubTypeMismatch(value) => value.into(),
                        },
                        Span::from(lhs_span.start..rhs_span.end),
                    ))
                })
                .ok()?;
            let mut poisoned = false;
            for (rest_op, rest_form) in cmp_op.rest() {
                let op = convert_cmp_op(rest_op);
                let rest_span = rest_form.span();
                let Some(rhs) =
                    create_node(vocabulary, rest_form, quant_names, source, diagnostics)
                else {
                    poisoned = true;
                    continue;
                };
                if cur
                    .add_op(op, rhs)
                    .map_err(|f| {
                        diagnostics.add_error(IDPError::new(
                            match f.take_kind() {
                                ExprSubMismatchErrorKind::VocabMismatchError(_) => unreachable!(),
                                ExprSubMismatchErrorKind::TypeMismatch(value) => value.into(),
                                ExprSubMismatchErrorKind::SubTypeMismatch(value) => value.into(),
                            },
                            Span::from(prev_span.start..rest_span.end),
                        ))
                    })
                    .is_err()
                {
                    poisoned = true;
                }
                prev_span = rest_span;
            }
            if !poisoned {
                Some(cur.with_span(cmp_op.span()).into())
            } else {
                None
            }
        }
        ast::Expression::UnaryOp(un_op) => {
            let subformula = ast::UnaryOp::subformula(&un_op).value()?;
            let subformula_span = subformula.span();
            let form_node = create_node(vocabulary, subformula, quant_names, source, diagnostics)?;
            match ast::UnaryOp::kind(&un_op) {
                ast::UnaryOpKind::Negation => Some(
                    Negation::new(
                        Formula::try_from(form_node)
                            .map_err(|f| {
                                diagnostics.add_error(IDPError::new(f.into(), subformula_span))
                            })
                            .map(|f| f.into())
                            .ok()?,
                    )
                    .with_span(un_op.span())
                    .into(),
                ),
                ast::UnaryOpKind::NumericNegation => Some(
                    NumNegation::new(form_node)
                        .map_err(|f| diagnostics.add_error(IDPError::new(f.into(), un_op.span())))
                        .ok()?
                        .with_span(un_op.span())
                        .into(),
                ),
            }
        }
        ast::Expression::Quantification(quant) => {
            let quant_kind = match ast::Quantification::kind(&quant) {
                ast::QuantificationKind::Universal => QuantType::Universal,
                ast::QuantificationKind::Existential => QuantType::Existential,
            };
            let variables = parse_quantees(
                vocabulary,
                ast::Quantification::variables(&quant),
                quant_names,
                source,
                diagnostics,
                // Early return here since we don't wanna add missing variable errors
                // maybe add poisoned variables to the mapping in the future so we can continue
                // from here without producing spurious errors.
            )?;
            let quant_form = ast::Quantification::subformula(&quant).value()?;
            let quant_form_span = quant_form.span();
            let formula = create_node(vocabulary, quant_form, quant_names, source, diagnostics)?;
            Some(
                Quantification::new(
                    quant_kind,
                    variables.destroy(),
                    Formula::try_from(formula)
                        .map_err(|f| {
                            diagnostics.add_error(IDPError::new(f.into(), quant_form_span))
                        })
                        .ok()?,
                )
                .unwrap()
                .with_span(quant.span())
                .into(),
            )
        }
        ast::Expression::Count(count) => {
            let variables = parse_quantees(
                vocabulary,
                ast::CountAgg::variables(&count),
                quant_names,
                source,
                diagnostics,
            )?;
            let agg_cond = ast::CountAgg::subformula(&count).value()?;
            let agg_cond_span = agg_cond.span();
            let formula = create_node(vocabulary, agg_cond, quant_names, source, diagnostics)?;
            Some(
                CardinalityAggregate::new(
                    variables.destroy(),
                    Formula::try_from(formula)
                        .map_err(|f| diagnostics.add_error(IDPError::new(f.into(), agg_cond_span)))
                        .map(|f| f.into())
                        .ok()?,
                )
                .unwrap()
                .with_span(count.span())
                .into(),
            )
        }
        ast::Expression::Sum(sum) => {
            let variables = parse_quantees(
                vocabulary,
                ast::SumAgg::variables(&sum),
                quant_names,
                source,
                diagnostics,
            )?;
            let agg_cond = ast::SumAgg::subformula(&sum).value();
            let agg_term = ast::SumAgg::term(&sum).value();
            let formula = agg_cond
                .map(|f| {
                    let span = f.span();
                    create_node(vocabulary, f, quant_names, source, diagnostics).map(|d| (d, span))
                })
                .flatten();
            let term = agg_term
                .map(|f| create_node(vocabulary, f, quant_names, source, diagnostics))
                .flatten();
            let (formula, formula_span) = formula?;
            let term = term?;
            Aggregate::new(
                AggType::Sum,
                variables.destroy(),
                term,
                Formula::try_from(formula)
                    .map_err(|f| diagnostics.add_error(IDPError::new(f.into(), formula_span)))
                    .map(|f| f.into())
                    .ok()?,
            )
            .map_err(|f| {
                diagnostics.add_error(IDPError::new(
                    match f.take_kind() {
                        ExprSubMismatchErrorKind::VocabMismatchError(_) => unreachable!(),
                        ExprSubMismatchErrorKind::TypeMismatch(value) => value.into(),
                        ExprSubMismatchErrorKind::SubTypeMismatch(value) => value.into(),
                    },
                    sum.span(),
                ))
            })
            .map(|f| f.with_span(sum.span()))
            .map(|f| f.into())
            .ok()
        }
        ast::Expression::Ite(ite) => {
            let cond_ast = ast::Ite::if_formula(&ite).value();
            let then_ast = ast::Ite::then_term(&ite).value();
            let else_ast = ast::Ite::else_term(&ite).value();
            let cond = cond_ast
                .map(|f| create_node(vocabulary, f, quant_names, source, diagnostics))
                .flatten();
            let then_term = then_ast
                .map(|f| create_node(vocabulary, f, quant_names, source, diagnostics))
                .flatten();
            let else_term = else_ast
                .map(|f| create_node(vocabulary, f, quant_names, source, diagnostics))
                .flatten();
            let cond = cond?;
            let then_term = then_term?;
            let else_term = else_term?;
            Ite::try_new(cond, then_term, else_term)
                .map_err(|f| {
                    diagnostics.add_error(IDPError::new(
                        match f.take_kind() {
                            ExprMismatchErrorKind::VocabMismatchError(_) => unreachable!(),
                            ExprMismatchErrorKind::TypeMismatch(value) => value.into(),
                        },
                        ite.span(),
                    ))
                })
                .map(|f| f.with_span(ite.span()))
                .map(|f| f.into())
                .ok()
        }
        ast::Expression::AppliedSymbol(ap_sym) => {
            parse_applied_symbol(vocabulary, ap_sym, quant_names, source, diagnostics)
                .map(|f| f.into())
        }
        ast::Expression::IsEnumerated(is_enumerated) => {
            let ap_symb = parse_applied_symbol(
                vocabulary,
                ast::IsEnumerated::applied_symbol(&is_enumerated).value()?,
                quant_names,
                source,
                diagnostics,
            )?;
            Some(
                IsEnumerated::new(ap_symb)
                    .with_span(is_enumerated.span())
                    .into(),
            )
        }
        ast::Expression::Element(element) => {
            // TODO: do this beter
            let el_name = element.span().get_str(source);
            if let Ok(el) = Element::from_str(&el_name) {
                Some(ElementExpr::from(el).with_span(element.span()).into())
            } else if let Ok(symb @ Symbol::Constructor(_)) =
                Vocabulary::parse_symbol_rc(vocabulary, &el_name)
            {
                if symb.domain().arity() != 0 {
                    diagnostics.add_error(IDPError::new(
                        NotAllowedError {
                            message: "Non nullary constructor needs to be applied with arguments",
                        }
                        .into(),
                        element.span(),
                    ));
                    None
                } else {
                    // nullary constructor
                    symb.try_apply([])
                        .map_err(|f| {
                            diagnostics.add_error(IDPError::new(
                                match f.take_kind() {
                                    ApplyErrorKind::MismatchedArity(value) => value.into(),
                                    ApplyErrorKind::TypeMismatch(value) => value.into(),
                                    ApplyErrorKind::VocabMismatchError(_) => unreachable!(),
                                },
                                element.span(),
                            ))
                        })
                        .map(|f| f.with_span(element.span()))
                        .map(|f| f.into())
                        .ok()
                }
            } else if let Some(var) = quant_names.get_var_ref(&el_name) {
                Some(var.with_span(element.span()).into())
            } else {
                diagnostics.add_error(IDPError::new(
                    MissingSymbol(el_name.as_ref().into()).into(),
                    element.span(),
                ));
                None
            }
        }
        ast::Expression::InEnumeration(in_enumeration) => {
            let expr = ast::InEnumeration::expr(&in_enumeration)
                .value()
                .map(|f| create_node(vocabulary, f, quant_names, source, diagnostics))
                .flatten();
            let enumeration: Vec<_> = ast::InEnumeration::enumeration(&in_enumeration)
                .filter_map(|f| create_node(vocabulary, f, quant_names, source, diagnostics))
                .collect();
            let expr = expr?;
            InEnumeration::new(expr, enumeration)
                .map_err(|f| {
                    diagnostics.add_error(IDPError::new(
                        match f.take_kind() {
                            ExprSubMismatchErrorKind::SubTypeMismatch(value) => value.into(),
                            ExprSubMismatchErrorKind::VocabMismatchError(_) => unreachable!(),
                            ExprSubMismatchErrorKind::TypeMismatch(value) => value.into(),
                        },
                        in_enumeration.span(),
                    ))
                })
                .map(|f| f.with_span(in_enumeration.span()))
                .map(|f| f.into())
                .ok()
        }
        ast::Expression::ConjuctiveGuard(conj_guard) => {
            let subformula = ast::ConjuctiveGuard::subformula(&conj_guard).value()?;
            let subformula_span = subformula.span();
            let subformula = create_node(vocabulary, subformula, quant_names, source, diagnostics)?;
            ConjuctiveGuard::new(
                Formula::try_from(subformula)
                    .map_err(|f| diagnostics.add_error(IDPError::new(f.into(), subformula_span)))
                    .ok()?,
            )
            .map_err(|f| diagnostics.add_error(IDPError::new(f.into(), conj_guard.span())))
            .map(|f| f.with_span(conj_guard.span()))
            .map(|f| f.into())
            .ok()
        }
        ast::Expression::ImplicativeGuard(impl_guard) => {
            let subformula = ast::ImplicativeGuard::subformula(&impl_guard).value()?;
            let subformula_span = subformula.span();
            let subformula = create_node(vocabulary, subformula, quant_names, source, diagnostics)?;
            ImplicativeGuard::new(
                Formula::try_from(subformula)
                    .map_err(|f| diagnostics.add_error(IDPError::new(f.into(), subformula_span)))
                    .ok()?,
            )
            .map_err(|f| diagnostics.add_error(IDPError::new(f.into(), impl_guard.span())))
            .map(|f| f.with_span(impl_guard.span()))
            .map(|f| f.into())
            .ok()
        }
        ast::Expression::IfGuard(if_guard) => {
            let term = create_node(
                vocabulary,
                ast::IfGuard::term(&if_guard).value()?,
                quant_names,
                source,
                diagnostics,
            );
            let else_term = create_node(
                vocabulary,
                ast::IfGuard::else_term(&if_guard).value()?,
                quant_names,
                source,
                diagnostics,
            );
            let subformula = term?;
            let else_term = else_term?;
            IfGuard::new(subformula, else_term)
                .map_err(|f| diagnostics.add_error(IDPError::new(f.into(), if_guard.span())))
                .map(|f| f.with_span(if_guard.span()))
                .map(|f| f.into())
                .ok()
        }
    }
}

fn parse_applied_symbol<'b, 'a>(
    vocabulary: &Rc<Vocabulary>,
    ap_sym: impl ast::AppliedSymbol,
    quant_names: &QuantVariableStack<'b>,
    source: &'a dyn ast::Source,
    diagnostics: &mut Diagnostics,
) -> Option<AppliedSymbol>
where
    'a: 'b,
{
    let symb_name = ast::AppliedSymbol::name(&ap_sym).get_str(source);
    let symbol = Vocabulary::parse_symbol_rc(vocabulary, &symb_name)
        .map_err(|f| {
            diagnostics.add_error(IDPError::new(f.into(), ast::AppliedSymbol::name(&ap_sym)))
        })
        .ok();
    let mut args = Vec::with_capacity(ast::AppliedSymbol::args_len(&ap_sym));
    let mut poisoned = false;
    for arg in ast::AppliedSymbol::args(&ap_sym) {
        let Some(arg) = create_node(vocabulary, arg, quant_names, source, diagnostics) else {
            poisoned = true;
            continue;
        };
        args.push(arg);
    }
    let args = args.into_boxed_slice();
    let symbol = symbol?;
    if symbol.is_constructor() && symbol.domain().arity() == 0 {
        diagnostics.add_error(IDPError::new(
            NullaryConstructorApplicationError.into(),
            ap_sym.span(),
        ));
        return None;
    }
    if poisoned {
        return None;
    }
    symbol
        .try_apply(args)
        .map_err(|f| {
            diagnostics.add_error(IDPError::new(
                match f.take_kind() {
                    ApplyErrorKind::TypeMismatch(value) => value.into(),
                    ApplyErrorKind::MismatchedArity(value) => value.into(),
                    ApplyErrorKind::VocabMismatchError(_) => unreachable!(),
                },
                ap_sym.span(),
            ))
        })
        .map(|f| f.with_span(ap_sym.span()))
        .map(|f| f.into())
        .ok()
}

fn def_head_handle_eq<F: BinaryOp>(
    bin_op: F,
    diagnostics: &mut Diagnostics,
    poisoned: &mut bool,
) -> (
    Option<<F::Formula as ast::Expressions>::AppliedSymbol>,
    Option<ast::Expression<F::Formula>>,
) {
    (
        bin_op
            .lhs()
            .value()
            .map(|f| {
                let span = f.span();
                f.applied_symbol().ok_or_else(|| {
                    diagnostics.add_error(IDPError::new(InvalidDefHeadError.into(), span))
                })
            })
            .transpose()
            .ok()
            .flatten(),
        match bin_op.rhs() {
            MaybePoisoned::Value(value) => Some(value),
            MaybePoisoned::Poisoned => {
                *poisoned = true;
                None
            }
        },
    )
}

/// Creates a definitional rule from the given node.
fn create_definitional_rule<'b, 'a>(
    vocabulary: &Rc<Vocabulary>,
    definition: impl ast::DefinitionalRule,
    quant_names: &QuantVariableStack<'b>,
    source: &'a dyn ast::Source,
    diagnostics: &mut Diagnostics,
) -> Option<DefinitionalRule>
where
    'a: 'b,
{
    let head = definition.head().value()?;
    let head_span = head.span();
    let quant;
    let mut poisoned = false;
    let (variables, applied_symb_node, eq) = match head {
        ast::Expression::AppliedSymbol(app_symb) => (None, Some(app_symb), None),
        ast::Expression::BinOp(bin_op) => {
            if ast::BinaryOpKind::Eq != ast::BinaryOp::kind(&bin_op) {
                diagnostics.add_error(IDPError::new(
                    InvalidDefHeadError.into(),
                    ast::BinaryOp::binop_span(&bin_op),
                ));
                (None, None, None)
            } else {
                let val = def_head_handle_eq(bin_op, diagnostics, &mut poisoned);
                (None, val.0, val.1)
            }
        }
        ast::Expression::Quantification(quant2) => {
            quant = quant2;
            let variables = ast::Quantification::variables(&quant);
            if ast::Quantification::kind(&quant) != ast::QuantificationKind::Universal {
                // TODO: fix this
                diagnostics.add_error(IDPError::new(
                    NotAllowedError {
                        message: "quantification over a definitional rule must be universal",
                    }
                    .into(),
                    ast::Quantification::kind_span(&quant),
                ));
                (Some(variables), None, None)
            } else {
                match ast::Quantification::subformula(&quant) {
                    MaybePoisoned::Value(ast::Expression::AppliedSymbol(app_symb)) => {
                        (Some(variables), Some(app_symb), None)
                    }
                    MaybePoisoned::Value(ast::Expression::BinOp(bin_op)) => {
                        if ast::BinaryOpKind::Eq != ast::BinaryOp::kind(&bin_op) {
                            diagnostics.add_error(IDPError::new(
                                InvalidDefHeadError.into(),
                                ast::BinaryOp::binop_span(&bin_op),
                            ));
                            (Some(variables), None, None)
                        } else {
                            let val = def_head_handle_eq(bin_op, diagnostics, &mut poisoned);
                            (Some(variables), val.0, val.1)
                        }
                    }
                    MaybePoisoned::Value(expr) => {
                        diagnostics
                            .add_error(IDPError::new(InvalidDefHeadError.into(), expr.span()));
                        (Some(variables), None, None)
                    }
                    // error whilst parsing
                    MaybePoisoned::Poisoned => {
                        poisoned = true;
                        (Some(variables), None, None)
                    }
                }
            }
        }
        expr => {
            diagnostics.add_error(IDPError::new(InvalidDefHeadError.into(), expr.span()));
            return None;
        }
    };
    let variables = variables
        .map(|f| parse_quantees(vocabulary, f, quant_names, source, diagnostics).ok_or(()))
        .transpose()
        .ok()?;
    let eq = if let Some(eq) = eq {
        let eq_span = eq.span();
        create_node(vocabulary, eq, quant_names, source, diagnostics).map(|f| (f, eq_span))
    } else {
        None
    };
    let rule_body = definition.body().value()?;
    let rule_body_span = rule_body.span();
    let body = create_node(vocabulary, rule_body, quant_names, source, diagnostics);
    let as_builder = parse_applied_symbol(
        vocabulary,
        applied_symb_node?,
        quant_names,
        source,
        diagnostics,
    )?;
    let body = body?;
    if poisoned {
        return None;
    }
    let def_head: Expr = if let Some((eq, eq_span)) = eq {
        BinOp::new(as_builder.into(), BinOps::Equal, eq)
            .map_err(|f| {
                diagnostics.add_error(IDPError::new(
                    match f.take_kind() {
                        ExprBinOpErrorKind::VocabMismatchError(_) => unreachable!(),
                        ExprBinOpErrorKind::BoolEqualityError(value) => value.into(),
                        ExprBinOpErrorKind::SubTypeMismatch(value) => value.into(),
                        ExprBinOpErrorKind::TypeMismatch(value) => value.into(),
                        ExprBinOpErrorKind::DivByZeroError(_) => unreachable!(),
                        ExprBinOpErrorKind::NotBoolExpr(_) => unreachable!(),
                    },
                    eq_span,
                ))
            })
            .map(|f| f.with_span(eq_span))
            .ok()?
            .into()
    } else {
        as_builder.into()
    };
    let rule_head = DefinitionalHead::try_from(def_head)
        .map_err(|f| diagnostics.add_error(IDPError::new(f.into(), head_span)))
        .ok()?;
    DefinitionalRule::new(
        variables.map(|f| f.destroy()),
        rule_head,
        WellDefinedFormula::try_from(body)
            .map_err(|f| diagnostics.add_error(IDPError::new(f.into(), rule_body_span)))
            .ok()?,
    )
    .map_err(|f| {
        diagnostics.add_error(match f.take_kind() {
            DefRuleErrorKind::TypeMismatch(body_mismatch) => {
                IDPError::new(body_mismatch.into(), rule_body_span)
            }
            DefRuleErrorKind::DefFreeVarError(free_vars) => {
                IDPError::new(free_vars.into(), definition.span())
            }
        })
    })
    .map(|f| f.with_span(definition.span()))
    .ok()
}

/// Creates an [Assertion] from the given node.
fn create_assertion<'b, 'a>(
    vocabulary: &Rc<Vocabulary>,
    assertion: ast::Assertion<impl ast::Expressions, impl ast::Definition>,
    quant_names: &QuantVariableStack<'b>,
    source: &'a dyn ast::Source,
    diagnostics: &mut Diagnostics,
) -> Option<Assertion>
where
    'a: 'b,
{
    match assertion {
        ast::Assertion::Def(def) => {
            let mut rules = Vec::new();
            for rule_node in def.rules() {
                let Some(rule) = create_definitional_rule(
                    vocabulary,
                    rule_node,
                    quant_names,
                    source,
                    diagnostics,
                ) else {
                    continue;
                };
                rules.push(rule);
            }
            Some(
                Definition::new(rules.into())
                    .map_err(|f| if f == VocabMismatchError {})
                    .unwrap()
                    .into(),
            )
        }
        ast::Assertion::Expr(expr) => {
            let expr_span = expr.span();
            let Some(expr) = create_node(vocabulary, expr, quant_names, source, diagnostics) else {
                return None;
            };
            Assertion::try_from(expr)
                .map_err(|f| diagnostics.add_error(IDPError::new(f.into(), expr_span)))
                .ok()
        }
    }
}

/// Parse an FO(·) theory.
fn parse_theory(
    vocabulary: &Rc<Vocabulary>,
    theory: &impl ast::TheoryBlock,
    source: &dyn ast::Source,
    diagnostics: &mut Diagnostics,
) -> TheoryBlock {
    let mut assertions = Assertions::new(vocabulary.clone());
    let names = theory.names();
    let theory_name = names.as_ref().map(|f| f.theory_name.get_str(source));
    parse_theory_decls(
        vocabulary,
        &mut assertions,
        theory.decls(),
        source,
        diagnostics,
    );
    return TheoryBlock::new(theory_name.as_deref().unwrap_or(""), assertions);
}

pub(crate) fn parse_theory_decls(
    vocabulary: &Rc<Vocabulary>,
    assertions: &mut Assertions,
    decls: impl ast::TheoryDecls,
    source: &dyn ast::Source,
    diagnostics: &mut Diagnostics,
) {
    // This is used to keep track of which quantification variables have been introduced
    // when parsing a formula. This is to ensure that all variables are quantified.
    let quant_vars = QuantVariableStack::new();
    for assertion in decls.iter_decls() {
        let Some(constr) =
            create_assertion(vocabulary, assertion, &quant_vars, source, diagnostics)
        else {
            continue;
        };
        assertions
            .add_assertion(constr)
            .expect("Should be same vocabulary");
    }
}

impl Theory {
    /// Create a theory from a specification.
    ///
    /// The source string must contain 1 vocabulary, 1 theory and 1 structure.
    pub fn from_specification(source: &str) -> Result<Self, Diagnostics> {
        let mut diagnostics = Diagnostics::new();
        let ast = ast::Parser::parse(&mut ast::tree_sitter::TsParser::new(), source);
        for (err, span) in ast.parse_errors() {
            diagnostics.add_error(IDPError::new(err.into(), span));
        }
        let parse_error_amount = diagnostics.errors().len();
        let vocab = ast.iter_decls().find_map(|f| f.vocab()).ok_or_else(|| {
            diagnostics.add_error(IDPError::new(
                ParseError {
                    message: "only one vocabulary allowed".into(),
                }
                .into(),
                Span { start: 0, end: 0 },
            ))
        });
        let theory = ast.iter_decls().find_map(|f| f.theory()).ok_or_else(|| {
            diagnostics.add_error(IDPError::new(
                ParseError {
                    message: "only one theory allowed".into(),
                }
                .into(),
                Span { start: 0, end: 0 },
            ))
        });
        let structure = ast.iter_decls().find_map(|f| f.structure()).ok_or_else(|| {
            diagnostics.add_error(IDPError::new(
                ParseError {
                    message: "only one structure allowed".into(),
                }
                .into(),
                Span { start: 0, end: 0 },
            ))
        });
        let Ok(vocab) = vocab else {
            return Err(diagnostics);
        };
        let Ok(theory) = theory else {
            return Err(diagnostics);
        };
        let Ok(structure) = structure else {
            return Err(diagnostics);
        };
        let vocab = parse_vocab(&source, &vocab, &mut diagnostics);
        if diagnostics.errors().len() > parse_error_amount {
            return Err(diagnostics);
        }
        let (vocab, part_type_interps) = vocab.complete_vocab();
        let theory_block = parse_theory(&vocab, &theory, &source, &mut diagnostics);
        let structure_block = parse_struct(
            part_type_interps,
            &vocab,
            &structure,
            &source,
            &mut diagnostics,
        );

        if let Some(structure_block) = structure_block {
            let theory = Self::from_blocks(theory_block, structure_block).map_err(|f| {
                diagnostics.add_error(IDPError::new(
                    match f.take_kind() {
                        WithPartialInterpsErrorKind::VocabMismatchError(_) => unreachable!(),
                        WithPartialInterpsErrorKind::MissingTypeInterps(value) => value.into(),
                    },
                    structure.span(),
                ))
            });
            if diagnostics.errors().len() > 0 {
                Err(diagnostics)
            } else {
                Ok(theory.unwrap())
            }
        } else {
            Err(diagnostics)
        }
    }
}
