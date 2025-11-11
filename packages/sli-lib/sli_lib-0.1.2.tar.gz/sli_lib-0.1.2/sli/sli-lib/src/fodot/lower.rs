use super::structure::{PartialStructure, partial};
use super::theory::{
    AggType, Assertion, Assertions, BinOps, Definition, ElementExpr, Expr, ExprRef, OrdOps,
    QuantType, Quantees, Variable, VariableBinder, VariableDecl, VariableDeclRef,
    WellDefinedCondition,
};
use super::vocabulary::{ConstructorRef, PfuncIndex, PfuncRc, Symbol, SymbolError, Type, TypeRc};
use comp_core::expression::AuxIndex;
use comp_core::node::{
    AggKind, AggregateNodeBuilder, AppliedAuxSymbBuilder, AppliedSymbBuilder, BinOpNode,
    BoolElement, DefinitionBuilder, ElementNode, IndexAppliedSymbBuilder, IntElementNode,
    IsIntNode, IteNode, NegNode, NumNegNode, QuantElementNode, QuantKind, QuantNodeBuilder,
    RuleBuilder, RuleHeadBuilder, VariablesBuilder,
};
use comp_core::vocabulary::{TypeElementIndex, Vocabulary as CCVocabulary};
use comp_core::{
    constraints::{BoundVarId, NodeIndex, ParsedConstraints},
    node::BinOps as CCBinOps,
    structure::{TypeElement as CCTypeElement, backend},
    vocabulary::Type as CCType,
};
use itertools::Either;
use sli_collections::hash_map::IdHashMap;
use std::collections::{HashMap, hash_map};

#[derive(Debug)]
enum VarValue {
    CC((BoundVarId, CCType)),
    // TODO: think about if we actually ever want to unroll quantifications here
    // Element(CCTypeElement),
}

impl From<(BoundVarId, CCType)> for VarValue {
    fn from(value: (BoundVarId, CCType)) -> Self {
        Self::CC(value)
    }
}

struct Lower<'a> {
    structure: &'a PartialStructure,
    var_translate: HashMap<VariableDeclRef, VarValue>,
    raise_expr: Vec<(TypeRc, Expr, VariableDeclRef)>,
    is_enumerated_aux_mapping: HashMap<PfuncIndex, AuxIndex>,
    cc_constraints: &'a mut ParsedConstraints,
}

pub fn translate_assertions(
    assertions: &Assertions,
    type_interps: &PartialStructure,
    parsed_constraints: &mut ParsedConstraints,
) -> Result<(), SymbolError> {
    if !assertions.vocab().exact_eq(type_interps.vocab()) {
        return Err(SymbolError::IDK);
    }
    let mut lower = Lower::new(type_interps, parsed_constraints);
    for assertion in assertions {
        let index = lower.translate_assertion(assertion.clone())?;
        lower.cc_constraints.add_constraint(index);
    }
    Ok(())
}

impl<'a> Lower<'a> {
    fn cc_vocab(&self) -> &'a CCVocabulary {
        self.structure.type_interps().cc().vocab()
    }

    fn new(
        structure: &'a PartialStructure,
        cc_constraints: &'a mut ParsedConstraints,
    ) -> Lower<'a> {
        Self {
            structure,
            var_translate: Default::default(),
            raise_expr: Default::default(),
            is_enumerated_aux_mapping: Default::default(),
            cc_constraints,
        }
    }

    fn translate_assertion(&mut self, assertion: Assertion) -> Result<NodeIndex, SymbolError> {
        match &assertion {
            Assertion::Bool(value) => self.translate_expression(value.into()),
            Assertion::Ite(value) => self.translate_expression(value.into()),
            Assertion::BinOp(value) => self.translate_expression(value.into()),
            Assertion::ChainedCmp(value) => self.translate_expression(value.into()),
            Assertion::Negation(value) => self.translate_expression(value.into()),
            Assertion::AppliedSymbol(value) => self.translate_expression(value.into()),
            Assertion::Quantification(value) => self.translate_expression(value.into()),
            Assertion::Definition(value) => self.translate_definition(value),
            Assertion::InEnumeration(value) => self.translate_expression(value.into()),
            Assertion::ConjuctiveGuard(value) => self.translate_expression(value.into()),
            Assertion::ImplicativeGuard(value) => self.translate_expression(value.into()),
            Assertion::IfGuard(value) => self.translate_expression(value.into()),
            Assertion::IsEnumerated(value) => self.translate_expression(value.into()),
        }
    }

    // TODO: maybe remove mapped variables to reduce memory footprint and cleanliness of code
    fn translate_expression(&mut self, expression: ExprRef) -> Result<NodeIndex, SymbolError> {
        let node_index = match expression {
            ExprRef::BinOp(bin_op) => {
                let cc_bin_op = match bin_op.op() {
                    BinOps::Or => CCBinOps::Or,
                    BinOps::And => CCBinOps::And,
                    BinOps::Implication => CCBinOps::Impl,
                    BinOps::Equivalence => CCBinOps::Eqv,
                    BinOps::Add => CCBinOps::Add,
                    BinOps::Subtract => CCBinOps::Sub,
                    BinOps::Mult => CCBinOps::Mult,
                    BinOps::Equal => CCBinOps::Eq,
                    BinOps::NotEqual => CCBinOps::Neq,
                    BinOps::LessThan => CCBinOps::Lt,
                    BinOps::LessOrEqual => CCBinOps::Le,
                    BinOps::GreaterThan => CCBinOps::Gt,
                    BinOps::GreaterOrEqual => CCBinOps::Ge,
                    BinOps::Rem => CCBinOps::Rem,
                    BinOps::Division => CCBinOps::Divide,
                };
                let lhs = self.translate_expression(bin_op.lhs().into())?;
                let rhs = self.translate_expression(bin_op.rhs().into())?;
                Ok(self
                    .cc_constraints
                    .push_node(BinOpNode::new(cc_bin_op, lhs, rhs), 0, 0))
            }
            ExprRef::ChainedCmp(chained_cmp) => {
                let first = chained_cmp.first();
                let get_bin_op = |value: OrdOps| match value {
                    OrdOps::Equal => CCBinOps::Eq,
                    OrdOps::NotEqual => CCBinOps::Neq,
                    OrdOps::LessThan => CCBinOps::Lt,
                    OrdOps::LessOrEqual => CCBinOps::Le,
                    OrdOps::GreaterThan => CCBinOps::Gt,
                    OrdOps::GreaterOrEqual => CCBinOps::Ge,
                };
                let cc_bin_op = get_bin_op(first.1);
                let lhs = self.translate_expression(first.0.into())?;
                let mut last = self.translate_expression(first.2.into())?;
                let mut cur =
                    self.cc_constraints
                        .push_node(BinOpNode::new(cc_bin_op, lhs, last), 0, 0);
                let mut rest = chained_cmp.iter();
                rest.next();
                for (_, op, other) in rest {
                    let cc_bin_op = get_bin_op(op);
                    let rhs = self.translate_expression(other.into())?;
                    let new =
                        self.cc_constraints
                            .push_node(BinOpNode::new(cc_bin_op, last, rhs), 0, 0);
                    cur = self.cc_constraints.push_node(
                        BinOpNode::new(CCBinOps::And, cur, new),
                        0,
                        0,
                    );
                    last = rhs;
                }
                Ok(cur)
            }
            ExprRef::Negation(negation) => {
                let sub_formula = self.translate_expression(negation.subformula().into())?;
                Ok(self
                    .cc_constraints
                    .push_node(NegNode::new(sub_formula), 0, 0))
            }
            ExprRef::NumNegation(negation) => {
                let sub_formula = self.translate_expression(negation.subexpr().into())?;
                Ok(self
                    .cc_constraints
                    .push_node(NumNegNode::new(sub_formula), 0, 0))
            }
            ExprRef::Quantification(quant) => {
                let quant_type = match quant.quant_type() {
                    QuantType::Universal => QuantKind::UniQuant,
                    QuantType::Existential => QuantKind::ExQuant,
                };
                let cc_variables = self.translate_quantees(quant.quantees())?;
                let subformula = self.translate_expression(quant.subformula().into())?;
                Ok(self.cc_constraints.push_node(
                    QuantNodeBuilder::new(quant_type, cc_variables, subformula),
                    0,
                    0,
                ))
            }
            ExprRef::CardinalityAggregate(card) => {
                let cc_variables = self.translate_quantees(card.quantees())?;
                let subformula = self.translate_expression(card.subformula().into())?;
                Ok(self.cc_constraints.push_node(
                    AggregateNodeBuilder::new(AggKind::Card, cc_variables, subformula),
                    0,
                    0,
                ))
            }
            ExprRef::Aggregate(agg) => {
                let cc_variables = self.translate_quantees(agg.quantees())?;
                let term = self.translate_expression(agg.term().into())?;
                let cond = self.translate_expression(agg.formula().into())?;
                match agg.agg_type() {
                    AggType::Sum => {
                        let zero = self.cc_constraints.push_node(IntElementNode::from(0), 0, 0);
                        let ite = self.cc_constraints.push_node(
                            IteNode {
                                cond,
                                then_term: term,
                                else_term: zero,
                            },
                            0,
                            0,
                        );
                        Ok(self.cc_constraints.push_node(
                            AggregateNodeBuilder::new(AggKind::Sum, cc_variables, ite),
                            0,
                            0,
                        ))
                    }
                }
            }
            ExprRef::AppliedSymbol(applied_symb) => {
                let symb = applied_symb.symbol();
                match symb {
                    Symbol::Type(applied_type) => {
                        let arg = applied_symb.args().first().unwrap();
                        let arg_codomain = arg.codomain();
                        match (applied_type, arg_codomain) {
                            (Type::Bool, Type::Bool)
                            | (Type::Int, Type::Int | Type::IntType(_))
                            | (Type::Real, Type::Int | Type::IntType(_))
                            | (Type::Real, Type::Real | Type::RealType(_)) => {
                                Ok(self.cc_constraints.push_node(BoolElement::new(true), 0, 0))
                            }
                            (Type::Int, Type::RealType(_) | Type::Real) => {
                                let arg_cc = self.translate_expression(arg.as_ref())?;
                                Ok(self.cc_constraints.push_node(IsIntNode::new(arg_cc), 0, 0))
                            }
                            (
                                Type::IntType(_) | Type::RealType(_),
                                Type::IntType(_) | Type::RealType(_) | Type::Int | Type::Real,
                            ) => {
                                match (applied_type, arg_codomain) {
                                    (Type::IntType(ap_type), Type::IntType(codomain))
                                        if codomain == ap_type.as_ref() =>
                                    {
                                        return Ok(self.cc_constraints.push_node(
                                            BoolElement::new(true),
                                            0,
                                            0,
                                        ));
                                    }
                                    (Type::RealType(ap_type), Type::RealType(codomain))
                                        if codomain == ap_type.as_ref() =>
                                    {
                                        return Ok(self.cc_constraints.push_node(
                                            BoolElement::new(true),
                                            0,
                                            0,
                                        ));
                                    }
                                    _ => (),
                                }
                                let new_var = self.cc_constraints.new_bound_var();
                                let var_type = applied_type.clone().to_cc();
                                let mut vars_builder = VariablesBuilder::new();
                                vars_builder.add_var(new_var, var_type);
                                let arg_cc = self.translate_expression(arg.as_ref())?;
                                let var = self.cc_constraints.push_node(
                                    QuantElementNode::new(new_var, var_type),
                                    0,
                                    0,
                                );
                                let eq_formula = self.cc_constraints.push_node(
                                    BinOpNode::new(CCBinOps::Eq, var, arg_cc),
                                    0,
                                    0,
                                );
                                let existential_quant = QuantNodeBuilder::new(
                                    QuantKind::ExQuant,
                                    vars_builder,
                                    eq_formula,
                                );
                                Ok(self.cc_constraints.push_node(existential_quant, 0, 0))
                            }
                            (Type::StrType(applied_str_type), Type::StrType(arg_codomain)) => {
                                Ok(self.cc_constraints.push_node(
                                    BoolElement::new(applied_str_type == &arg_codomain),
                                    0,
                                    0,
                                ))
                            }
                            (
                                Type::StrType(_),
                                Type::Bool
                                | Type::Int
                                | Type::Real
                                | Type::IntType(_)
                                | Type::RealType(_),
                            )
                            | (
                                Type::Bool,
                                Type::Int
                                | Type::Real
                                | Type::IntType(_)
                                | Type::RealType(_)
                                | Type::StrType(_),
                            )
                            | (
                                Type::Int | Type::Real | Type::IntType(_) | Type::RealType(_),
                                Type::Bool | Type::StrType(_),
                            ) => Ok(self.cc_constraints.push_node(BoolElement::new(false), 0, 0)),
                        }
                    }
                    Symbol::Pfunc(pfunc) => {
                        let mut as_builder = AppliedSymbBuilder::new(pfunc.to_cc());
                        self.build_applied_symbol(
                            &mut as_builder,
                            pfunc.clone(),
                            &applied_symb.args(),
                        )?;
                        Ok(self.cc_constraints.push_node(as_builder, 0, 0))
                    }
                    Symbol::Constructor(constr) => Ok(self.translate_constructor(constr.into())),
                }
            }
            ExprRef::Element(element) => Ok(self.translate_element(&element)),
            ExprRef::Variable(var) => Ok(self.translate_variable(&var)),
            ExprRef::Ite(ite) => {
                let cond = self.translate_expression(ite.if_formula().into())?;
                let then_term = self.translate_expression(ite.then_expr().into())?;
                let else_term = self.translate_expression(ite.else_expr().into())?;
                if ite.codomain() == Type::Bool {
                    let neg_cond = self.cc_constraints.push_node(NegNode::new(cond), 0, 0);
                    let impl_then = self.cc_constraints.push_node(
                        BinOpNode::new(CCBinOps::Impl, cond, then_term),
                        0,
                        0,
                    );
                    let impl_else = self.cc_constraints.push_node(
                        BinOpNode::new(CCBinOps::Impl, neg_cond, else_term),
                        0,
                        0,
                    );
                    Ok(self.cc_constraints.push_node(
                        BinOpNode::new(CCBinOps::And, impl_then, impl_else),
                        0,
                        0,
                    ))
                } else {
                    Ok(self.cc_constraints.push_node(
                        IteNode {
                            cond,
                            then_term,
                            else_term,
                        },
                        0,
                        0,
                    ))
                }
            }
            ExprRef::InEnumeration(in_enum) => {
                if in_enum.enumeration().len() == 0 {
                    return Ok(self.cc_constraints.push_node(BoolElement::new(false), 0, 0));
                }
                let expr = self.translate_expression(in_enum.expr().into())?;
                let mut big_disjunct = None;
                let mut eq = None;
                for enume in in_enum.enumeration() {
                    let eq_val = if let Some(eq) = eq {
                        eq
                    } else {
                        let new_eq = if enume.codomain().is_bool() {
                            CCBinOps::Eqv
                        } else {
                            CCBinOps::Eq
                        };
                        eq = Some(new_eq);
                        new_eq
                    };
                    let enume_expr = self.translate_expression(enume.into())?;
                    let eq = self.cc_constraints.push_node(
                        BinOpNode::new(eq_val, expr, enume_expr),
                        0,
                        0,
                    );
                    big_disjunct = if let Some(big_dis) = big_disjunct {
                        self.cc_constraints
                            .push_node(BinOpNode::new(CCBinOps::Or, big_dis, eq), 0, 0)
                            .into()
                    } else {
                        eq.into()
                    };
                }
                Ok(big_disjunct.unwrap())
            }
            ExprRef::Bool(value) => {
                Ok(self
                    .cc_constraints
                    .push_node(BoolElement::new(value.value), 0, 0))
            }
            ExprRef::ConjuctiveGuard(value) => {
                let weldef_cc = self.lower_welldef_condition(value.subformula().collect_wdcs())?;
                let subformula = self.translate_expression(value.subformula().into())?;
                if let Some(weldef_cc) = weldef_cc {
                    Ok(self.cc_constraints.push_node(
                        BinOpNode::new(CCBinOps::And, weldef_cc, subformula),
                        0,
                        0,
                    ))
                } else {
                    Ok(subformula)
                }
            }
            ExprRef::ImplicativeGuard(value) => {
                let weldef_cc = self.lower_welldef_condition(value.subformula().collect_wdcs())?;
                let subformula = self.translate_expression(value.subformula().into())?;
                if let Some(weldef_cc) = weldef_cc {
                    Ok(self.cc_constraints.push_node(
                        BinOpNode::new(CCBinOps::Impl, weldef_cc, subformula),
                        0,
                        0,
                    ))
                } else {
                    Ok(subformula)
                }
            }
            ExprRef::IfGuard(value) => {
                let weldef_cc = self.lower_welldef_condition(value.term().collect_wdcs())?;
                let term = self.translate_expression(value.term().into())?;
                let is_bool = value.codomain().is_bool();
                if let Some(weldef_cc) = weldef_cc {
                    let else_term = self.translate_expression(value.else_term().into())?;
                    if is_bool {
                        let neg_cond = self.cc_constraints.push_node(NegNode::new(weldef_cc), 0, 0);
                        let impl_then = self.cc_constraints.push_node(
                            BinOpNode::new(CCBinOps::Impl, weldef_cc, term),
                            0,
                            0,
                        );
                        let impl_else = self.cc_constraints.push_node(
                            BinOpNode::new(CCBinOps::Impl, neg_cond, else_term),
                            0,
                            0,
                        );
                        Ok(self.cc_constraints.push_node(
                            BinOpNode::new(CCBinOps::And, impl_then, impl_else),
                            0,
                            0,
                        ))
                    } else {
                        Ok(self.cc_constraints.push_node(
                            IteNode {
                                cond: weldef_cc,
                                then_term: term,
                                else_term,
                            },
                            0,
                            0,
                        ))
                    }
                } else {
                    Ok(term)
                }
            }
            ExprRef::IsEnumerated(value) => {
                match value.applied_symbol.symbol() {
                    Symbol::Pfunc(pfunc) => {
                        let interp = self.structure.get(pfunc.into());
                        use partial::immutable::FuncInterp as FI;
                        match interp.try_into_complete() {
                            Ok(_) => {
                                Ok(self.cc_constraints.push_node(BoolElement::new(true), 0, 0))
                            }
                            Err(incomplete) => match incomplete.split() {
                                Either::Left(nullary) => {
                                    if nullary.is_complete() {
                                        Ok(self.cc_constraints.push_node(
                                            BoolElement::new(true),
                                            0,
                                            0,
                                        ))
                                    } else {
                                        Ok(self.cc_constraints.push_node(
                                            BoolElement::new(false),
                                            0,
                                            0,
                                        ))
                                    }
                                }
                                Either::Right(function) => {
                                    let aux_index = *self.is_enumerated_aux_mapping.entry(pfunc.0)
                                        .or_insert_with(|| match function {
                                            FI::Pred(pred) => {
                                                let pred = match pred.interp.split_ct_cf() {
                                                    Ok((ct, cf)) => {
                                                        ct.store.clone().union(&cf.store)
                                                    }
                                                    // Can occur if the interpretation is empty
                                                    Err(_) => {
                                                        backend::complete_interp::owned::Pred::default()
                                                    }
                                                };
                                                let new_aux = self.cc_constraints.get_mut_expressions()
                                                    .new_aux_from(pfunc.to_cc())
                                                    .finish();
                                                self.cc_constraints.get_mut_expressions().set_aux_pred(
                                                    new_aux,
                                                    pred.into()
                                                );
                                                new_aux
                                            }
                                            func => {
                                                let new_aux = self.cc_constraints.get_mut_expressions()
                                                    .new_aux_from(pfunc.to_cc())
                                                    .with_codomain(CCType::Bool)
                                                    .finish();
                                                self.cc_constraints.get_mut_expressions().set_aux_pred(
                                                    new_aux,
                                                    backend::complete_interp::owned::Pred::from_iter(
                                                        func.iter().map(|f| f.0.domain_enum)
                                                    ).into()
                                                );
                                                new_aux
                                            }
                                        });
                                    let mut as_builder = AppliedAuxSymbBuilder::new(aux_index);
                                    self.build_applied_symbol(
                                        &mut as_builder,
                                        pfunc.clone(),
                                        value.applied_symbol.args(),
                                    )?;
                                    Ok(self.cc_constraints.push_node(as_builder, 0, 0))
                                }
                            },
                        }
                    }
                    Symbol::Constructor(_) | Symbol::Type(_) => {
                        Ok(self.cc_constraints.push_node(BoolElement::new(true), 0, 0))
                    }
                }
            }
        };
        if self.raise_expr.len() != 0 && Type::Bool == expression.codomain() {
            let mut var_builder = VariablesBuilder::new();
            let mut subformulas = Vec::new();
            let mut raise_expr = self.raise_expr.clone();
            // dont retranslate already translated things
            let mut cur_index = 0;
            loop {
                // gather all nested symbols
                for to_raise in raise_expr[cur_index..].iter() {
                    subformulas.push(self.translate_expression((&to_raise.1).into())?);
                }
                if raise_expr.len() == self.raise_expr.len() {
                    // all nested symbols have been gathered
                    break;
                }
                cur_index = raise_expr.len();
                raise_expr = self.raise_expr.clone()
            }
            // take all raised expressions and clear them
            raise_expr = core::mem::take(&mut self.raise_expr);
            for (to_raise, node_index) in raise_expr.iter().zip((&mut subformulas).into_iter()) {
                let raise_variable = &self.var_translate[&to_raise.2];
                let VarValue::CC(raise_variable) = raise_variable;
                var_builder.add_var(raise_variable.0, raise_variable.1);
                let var_index = self.cc_constraints.push_node(
                    QuantElementNode::new(raise_variable.0, raise_variable.1),
                    0,
                    0,
                );
                *node_index = self.cc_constraints.push_node(
                    BinOpNode::new(CCBinOps::Eq, *node_index, var_index),
                    0,
                    0,
                );
            }
            if var_builder.len() != 0 {
                let formula = self
                    .create_op_chain(
                        CCBinOps::And,
                        &mut subformulas
                            .iter()
                            .copied()
                            .chain(core::iter::once(node_index?)),
                    )
                    .unwrap();
                let quant = QuantNodeBuilder::new(QuantKind::ExQuant, var_builder, formula);
                return Ok(self.cc_constraints.push_node(quant, 0, 0));
            }
            expression.codomain();
        }
        node_index
    }

    fn build_applied_symbol<I: Copy>(
        &mut self,
        cc: &mut IndexAppliedSymbBuilder<I>,
        pfunc: PfuncRc,
        args: &[Expr],
    ) -> Result<(), SymbolError> {
        for (arg, symb_dom) in args.iter().zip(pfunc.domain_rc().iter_rc()) {
            match arg {
                Expr::AppliedSymbol(symb)
                    if symb.symbol().is_constructor() && symb.symbol().domain().arity() == 0 =>
                {
                    let constr = match symb.symbol() {
                        Symbol::Constructor(constr) => constr,
                        _ => unreachable!(),
                    };
                    cc.add_arg(ElementNode::from(CCTypeElement::Custom(
                        self.convert_nullary_constructor(constr.into()),
                    )))
                }
                Expr::Element(value) => cc.add_arg(self.convert_element(value)),
                Expr::Variable(var) => cc.add_arg(self.convert_variable(&var)),
                _ => {
                    let new_var = VariableDecl::new("nest_lift".into(), symb_dom.clone()).finish();
                    let (cc_var, cc_type) = self.create_new_cc_variable(&new_var)?;
                    self.raise_expr
                        .push((symb_dom, arg.clone(), new_var.decl().clone()));
                    cc.add_arg(QuantElementNode::new(cc_var, cc_type).into())
                }
            }
        }
        Ok(())
    }

    fn lower_welldef_condition(
        &mut self,
        wdcs: Vec<WellDefinedCondition>,
    ) -> Result<Option<NodeIndex>, SymbolError> {
        let mut cond = None;
        for wdc in wdcs {
            if let Some(cond_id) = cond {
                let other_cond = self.translate_expression(wdc.condition().into())?;
                cond = Some(self.cc_constraints.push_node(
                    BinOpNode::new(CCBinOps::And, cond_id, other_cond),
                    0,
                    0,
                ));
            } else {
                cond = Some(self.translate_expression(wdc.condition().into())?);
            }
        }
        Ok(cond)
    }

    fn translate_definition(&mut self, def: &Definition) -> Result<NodeIndex, SymbolError> {
        // Extra vars in quantee past canon format of comp core need to be moved to the body.
        // This can be done by binding them to a top level existential quantification in the body.
        // e.g.
        // ```idp
        // { !x, y, z: P(x, y) <- T(z). }
        // // becomes
        // { !x, y: P(x, y) <- ?z: T(z). }
        // ```
        // Nested arguments get handled by creating a new variable which will be used everywhere.
        // The nested argument is then compared using equality with the conan variable the argument
        // was replaced with.
        // e.g.
        // ```idp
        // { !x, y: P(D(x), y) <- T(x, y). }
        // // becomes
        // { !x1, y: P(x1, y) <- ?x in D(x) = x1 & T(x, y). }
        // ```
        let mut def_builder = DefinitionBuilder::new();
        let mut rule_heads: IdHashMap<_, _> = def
            .rules()
            .iter()
            .filter_map(|f| {
                if let Symbol::Pfunc(pfunc) = f.head().definiendum() {
                    let symbol = self.cc_vocab().pfuncs(pfunc.to_cc());
                    Some((
                        pfunc.to_cc(),
                        RuleHeadBuilder::new(symbol, self.cc_constraints.get_mut_expressions()),
                    ))
                } else {
                    None
                }
            })
            .collect();
        let mut combined_bodies = IdHashMap::default();
        for rule in def.rules() {
            let (cc_pfunc_index, pfunc) = match rule.head().definiendum() {
                Symbol::Type(_) => return Err(SymbolError::IDK),
                Symbol::Pfunc(pfunc) => (pfunc.to_cc(), pfunc),
                Symbol::Constructor(_) => return Err(SymbolError::IDK),
            };
            // contains canon variables
            // for predicates:
            // !x, y: P(x, y) <- ...
            // for functions:
            // !x, y, z: F(x, y) = z <- ...
            let rule_head = &rule_heads[&cc_pfunc_index];
            let mut exis_vars = Vec::new();
            // Note: for functions the expression on the left side of eq is also considered an
            // 'arg' here.
            let mut left_over_args = Vec::new();
            let codomain_iter = if pfunc.codomain() == Type::Bool {
                None
            } else {
                Some(pfunc.codomain())
            };
            // Currently every fodot pfunc domain must map to a comp core pfunc domain 1 for 1
            debug_assert_eq!(
                rule_head.variables.len(),
                pfunc.domain().arity() + if codomain_iter.is_some() { 1 } else { 0 }
            );
            // Map variable to canon variable and collect vars that do not belong to canon
            // variables.
            if let Some(quantees) = rule.quantees() {
                let rule_symb = rule.head().applied_symbol().symbol();
                for (pos, arg) in rule
                    .head()
                    .applied_symbol()
                    .args()
                    .iter()
                    // add function 'arg'
                    .chain(rule.head().eq())
                    .enumerate()
                {
                    // find variables used verbatim in arguments
                    if let Some(var) = quantees.iter().find(|f| {
                        *f == arg && !self.var_translate.contains_key(f.decl()) &&
                                // We must check if the codomain is exactly the same
                                if pos >= rule_symb.domain().arity() {
                                    f.var_type() == rule.head().applied_symbol().codomain()
                                } else {
                                    true
                                }
                    }) {
                        // variable has been used verbatim
                        // now map it to the canonical variable
                        self.var_translate.insert(
                            var.decl().clone(),
                            rule_head.variables.get(pos).unwrap().into(),
                        );
                    } else {
                        // variable not use verbatim, remember position of where this happens
                        left_over_args.push(pos);
                    }
                }
                for var in quantees.iter() {
                    if !self.var_translate.contains_key(var.decl()) {
                        // create new variable for each non translated variable
                        // and add them to variables which we will add to top level
                        // existential quantification.
                        let cc_var = self.create_new_cc_variable(var)?;
                        exis_vars.push(cc_var);
                    }
                }
            } else {
                let eq = rule.head().eq().is_some() as usize;
                for pos in 0..(rule.head().applied_symbol().args().len() + eq) {
                    left_over_args.push(pos);
                }
            }
            let fodot_body = self.translate_expression(rule.body().into())?;
            let mut translated_left_over_eq = Vec::new();
            // equal arguments in head to corresponding argument variable
            for pos in &left_over_args {
                let arg_id = self.translate_expression(
                    rule.head()
                        .applied_symbol()
                        .args()
                        .get(*pos)
                        // Out of bounds index would correspond to accessing the 'arg' of functions
                        // which is the expression on the rhs of the eq.
                        .unwrap_or_else(|| {
                            debug_assert_eq!(*pos, rule.head().applied_symbol().args().len());
                            rule.head().eq().unwrap()
                        })
                        .into(),
                )?;
                let var_tup = rule_head.variables.get(*pos).unwrap();
                let var = self.cc_constraints.push_node(
                    QuantElementNode {
                        bound_var_id: var_tup.0,
                        type_enum: var_tup.1,
                    },
                    0,
                    0,
                );
                // Eq argument to var in head
                let eq =
                    self.cc_constraints
                        .push_node(BinOpNode::new(CCBinOps::Eq, arg_id, var), 0, 0);
                translated_left_over_eq.push(eq);
            }
            // create existential quantification for leftover variables
            let cc_body_id = self
                .create_op_chain(
                    CCBinOps::And,
                    &mut translated_left_over_eq
                        .into_iter()
                        .chain(core::iter::once(fodot_body)),
                )
                .unwrap();
            let cc_body_id = if exis_vars.len() == 0 {
                // Don't bother creating quantification if there are no variables.
                cc_body_id
            } else {
                let exis_variable = VariablesBuilder::from_iter(exis_vars);
                self.cc_constraints.push_node(
                    QuantNodeBuilder::new(QuantKind::ExQuant, exis_variable, cc_body_id),
                    0,
                    0,
                )
            };
            match combined_bodies.entry(cc_pfunc_index) {
                hash_map::Entry::Vacant(vacant) => {
                    vacant.insert(cc_body_id);
                }
                hash_map::Entry::Occupied(mut occ) => {
                    let new_id = self.cc_constraints.push_node(
                        BinOpNode::new(CCBinOps::Or, *occ.get(), cc_body_id),
                        0,
                        0,
                    );
                    occ.insert(new_id);
                }
            }
        }
        for (definiendum, body) in combined_bodies {
            let head = rule_heads.remove(&definiendum).unwrap();
            let rule = RuleBuilder::new(head, body);
            def_builder.add_rule(rule, self.cc_constraints.get_mut_expressions())
        }
        Ok(self.cc_constraints.push_node(def_builder, 0, 0))
    }

    fn convert_element(&mut self, element: &ElementExpr) -> ElementNode {
        ElementNode::from(element.element.clone())
    }

    fn translate_element(&mut self, element: &ElementExpr) -> NodeIndex {
        let element = self.convert_element(element);
        self.cc_constraints.push_node(element, 0, 0)
    }

    fn convert_nullary_constructor(&mut self, constr: ConstructorRef) -> TypeElementIndex {
        if constr.domain().arity() != 0 {
            panic!();
        }
        constr.to_cc()
    }

    fn translate_constructor(&mut self, constr: ConstructorRef) -> NodeIndex {
        if constr.domain().arity() != 0 {
            unimplemented!()
        }
        let el_id = self.convert_nullary_constructor(constr);
        self.cc_constraints
            .push_node(ElementNode::from(CCTypeElement::Custom(el_id)), 0, 0)
    }

    fn convert_variable(&mut self, var: &Variable) -> ElementNode {
        let VarValue::CC(var) = self.var_translate[var.var_decl()];
        QuantElementNode::new(var.0, var.1).into()
    }

    fn translate_variable(&mut self, var: &Variable) -> NodeIndex {
        let VarValue::CC(var) = self.var_translate[var.var_decl()];
        self.cc_constraints
            .push_node(QuantElementNode::new(var.0, var.1), 0, 0)
    }

    fn translate_quantees(&mut self, quantees: &Quantees) -> Result<VariablesBuilder, SymbolError> {
        let mut cc_variables = VariablesBuilder::new();
        let add_cc_var =
            |lower: &mut Self, cc_variables: &mut VariablesBuilder, variable: &VariableBinder| {
                let (new_var, type_e) = lower.create_new_cc_variable(variable)?;
                cc_variables.add_var(new_var, type_e);
                Ok(())
            };
        for variable in quantees.iter() {
            add_cc_var(self, &mut cc_variables, variable)?
        }
        Ok(cc_variables)
    }

    fn create_new_cc_variable(
        &mut self,
        variable: &VariableBinder,
    ) -> Result<(BoundVarId, CCType), SymbolError> {
        let new_var = self.cc_constraints.new_bound_var();
        let var_type = (new_var, variable.var_type().to_cc());
        self.var_translate
            .insert(variable.decl().clone(), var_type.clone().into());
        Ok(var_type)
    }

    fn create_op_chain(
        &mut self,
        op: CCBinOps,
        iter: &mut impl Iterator<Item = NodeIndex>,
    ) -> Option<NodeIndex> {
        if let Some(n) = iter.next() {
            if let Some(n2) = self.create_op_chain(op, iter) {
                Some(
                    self.cc_constraints
                        .push_node(BinOpNode::new(op, n, n2), 0, 0),
                )
            } else {
                Some(n)
            }
        } else {
            None
        }
    }
}
