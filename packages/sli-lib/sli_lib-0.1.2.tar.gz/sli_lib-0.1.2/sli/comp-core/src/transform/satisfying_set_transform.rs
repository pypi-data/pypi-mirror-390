use super::{
    ExpressionTransformer, Transformer,
    simplify_transform::{
        SimplifyResult, contains_bound_var, simplify_node_with_var_with_extra_vars,
    },
    tranform_assistor::InnerIterTransform,
};
use crate::{
    comp_core::{
        constraints::{BoundVarId, NodeIndex},
        expression::{ExpressionRef, Expressions, IDomainPredicate, TypeMap},
        node::{
            AggKind, AggregateNode, AppliedSymbChildrenIter, BinOpNode, BinOps, ElementNode,
            IteNode, NegNode, NodeEnum, NodeWVariables, NodeWVariablesStandalone, QuantElementNode,
            QuantKind, QuantNode, StandaloneNode,
        },
        structure::{
            DomainEnumBuilder, PartialStructure, TypeElement, TypeInterp, complete,
            domain_enum_of_element_args,
            partial::{self, immutable},
        },
        theory::Theory,
        vocabulary::Type,
    },
    expression::AuxSignature,
    interp_structures::{
        InterpContext, LayoutIntFunc, LayoutRealFunc, LayoutSatSet, LayoutSymbol,
        LayoutTypeEnumFunc, LayoutVec, satisfying_set::OrScalar,
    },
    node::{
        AggregateNodeBuilder, AppliedAuxSymbBuilder, AppliedSymbBuilder, DefinitionBuilder,
        ExprType, IntElementNode, IsIntNode, Kind, NumNegNode, Rule, RuleBuilder, RuleHeadBuilder,
        Rules, RulesBuilder, Variables, VariablesBuilder,
    },
    structure::{DomainEnumErrors, backend::PartialRoaring},
    vocabulary::PfuncIndex,
};
use itertools::{Either, Itertools};
use sli_collections::{hash::IdBuildHasher, hash_map::IdHashMap, hash_set::IdHashSet};
use std::{fmt::Debug, ops::DerefMut, unimplemented, unreachable};

#[derive(Debug)]
enum PfuncSolve {
    NoInterp,
    PartialPred { cf: LayoutSatSet, ct: LayoutSatSet },
    PartialFunc(LayoutSatSet),
    Interp(LayoutSymbol),
}

fn build_predicate(
    pred: &complete::immutable::PredInterp,
    args: AppliedSymbChildrenIter,
    context: &InterpContext,
) -> LayoutSymbol {
    let all_vars = LayoutSatSet::with_new_vars(pred);
    let mut new_type_map =
        TypeMap::with_capacity_and_hasher(pred.domain().len(), IdBuildHasher::default());
    new_type_map.extend(
        pred.domain()
            .iter()
            .enumerate()
            .map(|(var, typ_e)| (BoundVarId::from(var), typ_e.clone())),
    );
    let temp_context = InterpContext::new(&new_type_map, context.type_interps());
    // Copy over from structure, meaning layout contains all new variables.
    let mut all_vars = LayoutSymbol::from(all_vars);
    let mut seen_var = IdHashMap::default();
    let mut vars_to_quant = Vec::with_capacity(args.len());
    let mut new_layout = LayoutVec::new();
    // Find all args different of the all var layout
    for (corr_var, mut arg) in args
        .enumerate()
        .map(|(var, arg)| (BoundVarId::from(var), arg))
    {
        if let ElementNode::Quant(var) = arg.clone() {
            // Is not different unless the variable has already been seen
            if !seen_var.contains_key(&var.bound_var_id) {
                new_layout.add_var(var.bound_var_id);
                seen_var.insert(var.bound_var_id, corr_var);
                continue;
            }
            // If already seen we have to eq the seen_var (mapped to the
            // var in the layout) to the current corr_var
            arg = QuantElementNode::new(seen_var[&var.bound_var_id], var.type_enum).into();
        }
        // eq to corresponding var
        let with = el_eq_var(arg, corr_var, &temp_context);
        vars_to_quant.push(corr_var);
        all_vars = all_vars.and(with, &temp_context).unwrap();
    }
    let final_bv = all_vars.exists(&vars_to_quant, &temp_context).unwrap();
    // translate the layout
    let final_translated = match final_bv {
        LayoutSymbol::Predicate(mut value) => {
            debug_assert_eq!(value.layout().len(), new_layout.len());
            *value.mut_layout() = new_layout;
            value.into()
        }
        other => other,
    };
    final_translated
}

impl PfuncSolve {
    pub fn from_func(
        func_interp: immutable::SymbolInterp,
        args: AppliedSymbChildrenIter,
        context: &InterpContext,
        in_inner: bool,
        splitted_func: bool,
    ) -> Self {
        match func_interp.split() {
            Either::Left(const_symb) => {
                if let Some(val) = const_symb.get() {
                    Self::Interp(val.into())
                } else {
                    Self::NoInterp
                }
            }
            Either::Right(symb) => {
                if !symb.any_known() {
                    return Self::NoInterp;
                }
                let mut layout = LayoutVec::new();
                let mut boundedfb = DomainEnumBuilder::new(symb.domain(), symb.type_interps());
                for arg in args.clone() {
                    match arg {
                        ElementNode::Quant(e) => {
                            let type_enum = e.type_enum;
                            if let Type::Str(_) | Type::IntType(_) | Type::RealType(_) = type_enum {
                            } else {
                                unimplemented!("Domain arg of {:?} not implemented", type_enum)
                            };
                            boundedfb
                                .add_var(e.bound_var_id)
                                .expect("Internal error: adding var to func enum builder failed");
                            layout.add_var(e.bound_var_id);
                        }
                        el => {
                            boundedfb
                                .add_type_el_arg(el.try_into().expect("unreachable"))
                                .expect("Internal error: creating func enum failed");
                        }
                    }
                }
                if let Ok(full_known_index) = boundedfb.get_index() {
                    if let Some(val) = symb.get_i(full_known_index) {
                        Self::Interp(val.into())
                    } else {
                        Self::NoInterp
                    }
                } else {
                    let symb = if let immutable::FuncInterp::Pred(pred) = symb {
                        match pred.split_ct_cf() {
                            Ok((ct, cf)) => {
                                // If we are in an inner transform just ignore partial predicates,
                                // otherwise we end up overflowing the stack.
                                if in_inner {
                                    return Self::NoInterp;
                                }
                                let ct = build_predicate(&ct, args.clone(), context);
                                let cf = build_predicate(&cf, args, context);
                                match (&ct, &cf) {
                                    (
                                        symb @ LayoutSymbol::Scalar(TypeElement::Bool(_)),
                                        LayoutSymbol::Scalar(_),
                                    ) => {
                                        return Self::Interp(symb.clone());
                                    }
                                    _ => {}
                                }
                                // unwrap_satset cannot panic, because we handle scalar case, and
                                // ct and cf being a scalars independently from each other should
                                // never happen (scalar case should also never happen but ok).
                                return Self::PartialPred {
                                    cf: cf.unwrap_satset(),
                                    ct: ct.unwrap_satset(),
                                };
                            }
                            Err(complete) => complete.into(),
                        }
                    } else if !symb.is_complete() {
                        if splitted_func {
                            return match symb {
                                partial::immutable::FuncInterp::IntFunc(ref func) => {
                                    let domain_size = layout.domain_len(context);
                                    let mut int_vec = LayoutIntFunc::new(domain_size, layout);
                                    for (i, dom_enum) in boundedfb.iter_indexes().enumerate() {
                                        let Some(val) = func.get_i(dom_enum) else {
                                            continue;
                                        };
                                        int_vec.set(i.into(), val);
                                    }
                                    Self::Interp(int_vec.into())
                                }
                                partial::immutable::FuncInterp::RealFunc(ref func) => {
                                    let domain_size = layout.domain_len(context);
                                    let mut int_vec = LayoutRealFunc::new(domain_size, layout);
                                    for (i, dom_enum) in boundedfb.iter_indexes().enumerate() {
                                        let Some(val) = func.get_i(dom_enum) else {
                                            continue;
                                        };
                                        int_vec.set(i.into(), val);
                                    }
                                    Self::Interp(int_vec.into())
                                }
                                partial::immutable::FuncInterp::StrFunc(ref func) => {
                                    let domain_size = layout.domain_len(context);
                                    let mut int_vec = LayoutTypeEnumFunc::new(
                                        domain_size,
                                        layout,
                                        func.codomain_index(),
                                    );
                                    for (i, dom_enum) in boundedfb.iter_indexes().enumerate() {
                                        let Some(val) = func.get_i(dom_enum) else {
                                            continue;
                                        };
                                        int_vec.set(i.into(), val);
                                    }
                                    Self::Interp(int_vec.into())
                                }
                                partial::immutable::FuncInterp::Pred(_) => unreachable!(),
                            };
                        }
                        if in_inner {
                            return Self::NoInterp;
                        }
                        return match symb {
                            partial::immutable::FuncInterp::IntFunc(ref func) => {
                                let domain_size = layout.domain_len(context);
                                let mut guard = LayoutSatSet::new(domain_size, layout);
                                for (i, dom_enum) in boundedfb.iter_indexes().enumerate() {
                                    let Some(_) = func.get_i(dom_enum) else {
                                        continue;
                                    };
                                    guard.set(i.into());
                                }
                                Self::PartialFunc(guard)
                            }
                            partial::immutable::FuncInterp::RealFunc(ref func) => {
                                let domain_size = layout.domain_len(context);
                                let mut guard = LayoutSatSet::new(domain_size, layout);
                                for (i, dom_enum) in boundedfb.iter_indexes().enumerate() {
                                    let Some(_) = func.get_i(dom_enum) else {
                                        continue;
                                    };
                                    guard.set(i.into());
                                }
                                Self::PartialFunc(guard)
                            }
                            partial::immutable::FuncInterp::StrFunc(ref func) => {
                                let domain_size = layout.domain_len(context);
                                let mut guard = LayoutSatSet::new(domain_size, layout);
                                for (i, dom_enum) in boundedfb.iter_indexes().enumerate() {
                                    let Some(_) = func.get_i(dom_enum) else {
                                        continue;
                                    };
                                    guard.set(i.into());
                                }
                                Self::PartialFunc(guard)
                            }
                            partial::immutable::FuncInterp::Pred(_) => unreachable!(),
                        };
                    } else {
                        symb
                    };
                    // The symbol must be complete here
                    match symb.try_into_complete().map_err(|_| ()).unwrap() {
                        complete::immutable::FuncInterp::Pred(ref pred) => {
                            Self::Interp(build_predicate(pred, args, context))
                        }
                        complete::immutable::FuncInterp::IntFunc(ref func) => {
                            let domain_size = layout.domain_len(context);
                            let mut int_vec = LayoutIntFunc::new(domain_size, layout);
                            for (i, dom_enum) in boundedfb.iter_indexes().enumerate() {
                                let val = func.get_i(dom_enum);
                                int_vec.set(i.into(), val);
                            }
                            Self::Interp(int_vec.into())
                        }
                        complete::immutable::FuncInterp::RealFunc(ref func) => {
                            let domain_size = layout.domain_len(context);
                            let mut real_vec = LayoutRealFunc::new(domain_size, layout);
                            for (i, dom_enum) in boundedfb.iter_indexes().enumerate() {
                                let val = func.get_i(dom_enum);
                                real_vec.set(i.into(), val);
                            }
                            Self::Interp(real_vec.into())
                        }
                        complete::immutable::FuncInterp::StrFunc(ref func) => {
                            let domain_size = layout.domain_len(context);
                            let mut type_enum_vec =
                                LayoutTypeEnumFunc::new(domain_size, layout, func.codomain_index());
                            for (i, dom_enum) in boundedfb.iter_indexes().enumerate() {
                                let val = func.get_i(dom_enum);
                                type_enum_vec.set(i.into(), val);
                            }
                            Self::Interp(type_enum_vec.into())
                        }
                    }
                }
            }
        }
    }
}

impl LayoutSymbol {
    pub fn from_element(element: ElementNode, context: &InterpContext) -> Self {
        match element {
            ElementNode::Bool(b) => b.value.into(),
            ElementNode::Int(i) => LayoutSymbol::from(i.num),
            ElementNode::Real(r) => LayoutSymbol::from(r.real),
            ElementNode::Type(t) => LayoutSymbol::from(t.element),
            ElementNode::Quant(q) => {
                let type_e = context.get_type_map()[&q.bound_var_id];
                let type_index = if let Type::Str(i) | Type::IntType(i) | Type::RealType(i) = type_e
                {
                    i
                } else {
                    unimplemented!()
                };
                let type_interp = &context.type_interps()[type_index];
                let vec;
                let mut layout = LayoutVec::new();
                layout.add_var(q.bound_var_id);
                match type_interp {
                    TypeInterp::Int(int) => {
                        let mut int_vec = LayoutIntFunc::new(int.len(), layout);
                        for (i, val) in int.into_iter().enumerate() {
                            int_vec.set(i.into(), val);
                        }
                        vec = Self::Int(int_vec);
                    }
                    TypeInterp::Real(real) => {
                        let mut real_vec = LayoutRealFunc::new(real.len(), layout);
                        for (i, val) in real.into_iter().enumerate() {
                            real_vec.set(i.into(), *val);
                        }
                        vec = Self::Real(real_vec);
                    }
                    TypeInterp::Custom(custom) => {
                        let mut type_enum_vec =
                            LayoutTypeEnumFunc::new(custom.len(), layout, type_index);
                        for (i, _) in custom.iter().enumerate() {
                            type_enum_vec.set(i.into(), i.into());
                        }
                        vec = Self::TypeEnum(type_enum_vec);
                    }
                }
                vec
            }
        }
    }

    fn push_scalar_or<'a, T, F>(
        &self,
        expr: &mut ExpressionTransformer,
        from_expr: ExpressionRef<'a>,
        or: F,
    ) -> NodeIndex
    where
        T: Into<StandaloneNode>,
        F: FnOnce() -> T,
    {
        match self {
            Self::Scalar(element) => expr.push_node(*element, from_expr),
            _ => expr.push_node(or(), from_expr),
        }
    }

    fn push_scalar_or_else<'a, F>(
        &self,
        expr: &mut ExpressionTransformer,
        from_expr: ExpressionRef<'a>,
        or: F,
    ) -> NodeIndex
    where
        F: FnOnce(&mut ExpressionTransformer) -> NodeIndex,
    {
        match self {
            Self::Scalar(element) => expr.push_node(*element, from_expr),
            _ => or(expr),
        }
    }

    fn push_interpretation(
        self,
        expr_transformer: &mut ExpressionTransformer,
        from_expr: ExpressionRef,
        context: &InterpContext,
    ) -> NodeIndex {
        if !self.is_scalar() {
            match from_expr.first_node().expr {
                ExprType::AppliedSymb | ExprType::AppliedAuxSymb => {
                    return expr_transformer.rec_copy(from_expr);
                }
                _ => {}
            }
        }
        match self {
            LayoutSymbol::Scalar(value) => expr_transformer.push_node(value, from_expr),
            LayoutSymbol::Int(value) => {
                let aux_signature = AuxSignature {
                    codomain: Type::Int,
                    domain: value.layout().get_domain(context.get_type_map()),
                };
                let new_aux = expr_transformer.get_mut_expr_ref().add_aux(aux_signature);
                let mut aux = AppliedAuxSymbBuilder::new(new_aux);
                value.layout().iter().for_each(|f| {
                    aux.add_arg(
                        expr_transformer
                            .translate_quant_element(
                                QuantElementNode::new(f, context.get_type_map()[&f].clone()),
                                from_expr.expressions,
                            )
                            .into(),
                    )
                });
                let partial::mutable::SymbolInterp::IntFunc(
                    partial::mutable::IntCoFuncInterp::Int(mut func),
                ) = expr_transformer.get_mut_expr_ref().get_mut(new_aux)
                else {
                    unreachable!();
                };
                **func.store.deref_mut() = value.inner().into();
                expr_transformer.push_translated_node(aux, from_expr)
            }
            LayoutSymbol::Real(value) => {
                let aux_signature = AuxSignature {
                    codomain: Type::Real,
                    domain: value.layout().get_domain(context.get_type_map()),
                };
                let new_aux = expr_transformer.get_mut_expr_ref().add_aux(aux_signature);
                let mut aux = AppliedAuxSymbBuilder::new(new_aux);
                value.layout().iter().for_each(|f| {
                    aux.add_arg(
                        expr_transformer
                            .translate_quant_element(
                                QuantElementNode::new(f, context.get_type_map()[&f].clone()),
                                from_expr.expressions,
                            )
                            .into(),
                    )
                });
                let partial::mutable::SymbolInterp::RealFunc(
                    partial::mutable::RealCoFuncInterp::Real(mut func),
                ) = expr_transformer.get_mut_expr_ref().get_mut(new_aux)
                else {
                    unreachable!();
                };
                *func.store.deref_mut() = value.inner().into();
                expr_transformer.push_translated_node(aux, from_expr)
            }
            LayoutSymbol::TypeEnum(value) => {
                let aux_signature = AuxSignature {
                    codomain: Type::Str(value.get_type_index()),
                    domain: value.layout().get_domain(context.get_type_map()),
                };
                let new_aux = expr_transformer.get_mut_expr_ref().add_aux(aux_signature);
                let mut aux = AppliedAuxSymbBuilder::new(new_aux);
                value.layout().iter().for_each(|f| {
                    aux.add_arg(
                        expr_transformer
                            .translate_quant_element(
                                QuantElementNode::new(f, context.get_type_map()[&f].clone()),
                                from_expr.expressions,
                            )
                            .into(),
                    )
                });
                let partial::mutable::SymbolInterp::StrFunc(mut func) =
                    expr_transformer.get_mut_expr_ref().get_mut(new_aux)
                else {
                    unreachable!();
                };
                **func.store.deref_mut() = value.inner().into();
                expr_transformer.push_translated_node(aux, from_expr)
            }
            LayoutSymbol::Predicate(value) => {
                let aux_signature = AuxSignature {
                    codomain: Type::Bool,
                    domain: value.layout().get_domain(context.get_type_map()),
                };
                let new_aux = expr_transformer.get_mut_expr_ref().add_aux(aux_signature);
                let mut aux = AppliedAuxSymbBuilder::new(new_aux);
                value.layout().iter().for_each(|f| {
                    aux.add_arg(
                        expr_transformer
                            .translate_quant_element(
                                QuantElementNode::new(f, context.get_type_map()[&f].clone()),
                                from_expr.expressions,
                            )
                            .into(),
                    )
                });
                let partial::mutable::SymbolInterp::Pred(pred) =
                    expr_transformer.get_mut_expr_ref().get_mut(new_aux)
                else {
                    unreachable!();
                };
                *pred.store = PartialRoaring::Full(value.inner().inner().into());
                expr_transformer.push_translated_node(aux, from_expr)
            }
        }
    }
}

fn partial_interpreted_quant_split<'a, T>(
    mut bvs: T,
    context: &InterpContext,
) -> Option<LayoutSatSet>
where
    T: Iterator<Item = (&'a LayoutSatSet, bool)>,
{
    let bv_bool = bvs.next()?;
    let mut bv = {
        let mut bvc = bv_bool.0.clone();
        if !bv_bool.1 {
            bvc = bvc.neg();
        }
        bvc
    };
    for rest in bvs {
        if rest.1 {
            bv = bv.and(rest.0.clone(), context);
        } else {
            bv = bv.and(rest.0.clone().neg(), context);
        }
    }
    Some(bv)
}

/// The variables in [Self::quant] need to be preambled and postambled between transformation.
struct QuantSplitter<'a> {
    quant: NodeIndex,
    replace: NodeChecker<'a>,
    vars_to_remove: &'a IdHashSet<usize>,
    got_simplified: bool,
}

#[derive(Debug)]
struct NodeChecker<'a> {
    nodes: &'a IdHashMap<NodeIndex, usize>,
    cur: usize,
}

#[allow(unused)]
struct NodeCheckerDebug<'a> {
    checker: &'a NodeChecker<'a>,
    expr: &'a Expressions,
}

impl<'a> Debug for NodeCheckerDebug<'a> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        for (&value, _) in self.checker.nodes.iter() {
            write!(
                f,
                "{:?} -> {:}\n",
                self.expr.to_expression(value),
                self.checker.get(value).unwrap()
            )?;
        }
        Ok(())
    }
}

impl<'a> NodeChecker<'a> {
    #[allow(unused)]
    fn debug_print<'b>(&'b self, expr: &'b Expressions) -> NodeCheckerDebug<'b> {
        NodeCheckerDebug {
            checker: self,
            expr,
        }
    }

    fn get(&self, index: NodeIndex) -> Option<bool> {
        if let Some(i) = self.nodes.get(&index) {
            Some((self.cur & 1 << i) != 0)
        } else {
            None
        }
    }
}

impl<'a> Transformer<'a> for QuantSplitter<'_> {
    fn transform_expression(
        &mut self,
        from_expr: ExpressionRef<'a>,
        expr_transformer: &mut ExpressionTransformer,
    ) -> NodeIndex {
        if let Some(val) = self.replace.get(from_expr.start()) {
            expr_transformer.push_node(val, from_expr)
        } else {
            if from_expr.start() == self.quant {
                let quant_node =
                    NodeWVariables::try_from((from_expr.start(), from_expr.expressions()))
                        .expect("Internal error");
                let mut quant =
                    NodeWVariablesStandalone::from_ref_without_guard(quant_node.clone());
                let formula =
                    self.transform_expression(from_expr.new_at(quant.formula), expr_transformer);
                quant.formula = formula;
                // translate the node
                let translated =
                    expr_transformer.translate_node(quant.into(), from_expr.expressions());
                let translated_quant = NodeWVariablesStandalone::try_from(translated).unwrap();
                // simplify it with the variables that will exist in the quant guard
                // (further code cleans up truly no longer needer variables)
                let mut count = 0;
                let simplified = simplify_node_with_var_with_extra_vars(
                    translated_quant,
                    expr_transformer.get_expressions(),
                    |_| {
                        let ret = !self.vars_to_remove.contains(&count);
                        count += 1;
                        ret
                    },
                    true,
                );
                match simplified {
                    SimplifyResult::Node(node) => {
                        expr_transformer.push_translated_simplified_node(node, from_expr)
                    }
                    SimplifyResult::Existing(ex) => {
                        self.got_simplified = true;
                        ex
                    }
                }
            } else {
                expr_transformer.apply(from_expr, |s, b| self.transform_expression(b, s))
            }
        }
    }
}

pub struct SatisfyingSetTransform<'a> {
    context: InterpContext<'a>,
    ignore_set: IdHashSet<PfuncIndex>,
    node_with_interp: Vec<(NodeIndex, LayoutSatSet)>,
    structure: &'a PartialStructure,
    inner: bool,
}

impl<'a> Debug for SatisfyingSetTransform<'a> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("BitVectorTransform")
            .field("node_with_interp", &self.node_with_interp)
            .finish_non_exhaustive()
    }
}

pub struct VectorReturn(Option<LayoutSymbol>, NodeIndex);

impl From<(Option<LayoutSymbol>, NodeIndex)> for VectorReturn {
    fn from(value: (Option<LayoutSymbol>, NodeIndex)) -> Self {
        VectorReturn(value.0, value.1)
    }
}

impl<'a> Into<NodeIndex> for &'a VectorReturn {
    fn into(self) -> NodeIndex {
        self.1
    }
}

impl From<NodeIndex> for VectorReturn {
    fn from(value: NodeIndex) -> Self {
        VectorReturn(None, value)
    }
}

impl<'a> Transformer<'a> for SatisfyingSetTransform<'_> {
    fn transform_expression(
        &mut self,
        from_expr: ExpressionRef<'a>,
        expr_transformer: &mut ExpressionTransformer,
    ) -> NodeIndex {
        self.transform(from_expr, expr_transformer).1
    }
}

/// Try to get the lhs and rhs of the bin_op as [ElementNode]s.
fn get_el_node_and_el_node(
    bin_op: &BinOpNode,
    expr: &Expressions,
) -> Option<(ElementNode, ElementNode)> {
    match (
        expr.new_at(bin_op.lhs).first_node_enum(),
        expr.new_at(bin_op.rhs).first_node_enum(),
    ) {
        (NodeEnum::Element(first), NodeEnum::Element(second)) => Some((first, second)),
        _ => return None,
    }
}

/// A more optimized way to create a satisfying set for eq between elements (including variables)
fn el_eq_var(el: ElementNode, var: BoundVarId, context: &InterpContext) -> LayoutSymbol {
    if let Ok(ty_el) = TypeElement::try_from(el.clone()) {
        let layout = LayoutVec::from_iter(core::iter::once(var));
        let domain = layout.get_domain(context.get_type_map());
        let size = layout.domain_len(context);
        let mut bv = LayoutSatSet::new(size, layout);
        match domain_enum_of_element_args(&[ty_el], &domain, context.type_interps()) {
            Err(DomainEnumErrors::WrongType) => {}
            Err(err) => panic!("Correct domain!, {}", err),
            Ok(domain_enum) => {
                bv.set(domain_enum);
            }
        }
        bv.into()
    } else {
        let ElementNode::Quant(other_var) = el else {
            unreachable!();
        };
        if var == other_var.bound_var_id {
            return true.into();
        }
        let layout = LayoutVec::from_iter([var, other_var.bound_var_id]);
        let size = layout.domain_len(context);
        let domain = layout.get_domain(context.get_type_map());
        let mut dom_enum_builder = DomainEnumBuilder::new(&domain, context.type_interps());
        dom_enum_builder.add_var(BoundVarId::from(0)).unwrap();
        dom_enum_builder.add_var(BoundVarId::from(0)).unwrap();
        let mut bv = LayoutSatSet::new(size, layout);
        for same_dom in dom_enum_builder.iter_indexes() {
            bv.set(same_dom)
        }
        return bv.into();
    }
}

/// Eq optimizations
fn eq_element(
    left: ElementNode,
    right: ElementNode,
    context: &InterpContext,
) -> Option<LayoutSymbol> {
    match (left, right) {
        (ElementNode::Quant(var), other) | (other, ElementNode::Quant(var)) => {
            Some(el_eq_var(other, var.bound_var_id, context))
        }
        _ => None,
    }
}

fn find_vars_to_remove(variables: &Variables, expr: ExpressionRef) -> IdHashSet<BoundVarId> {
    let mut vars_to_remove: IdHashSet<_> = variables.iter_vars().copied().collect();
    expr.for_each(&mut |f| match f {
        NodeEnum::Agg(agg) => {
            agg.variables.iter_vars().for_each(|f| {
                vars_to_remove.remove(f);
            });
        }
        NodeEnum::Quant(quant) => {
            quant.variables.iter_vars().for_each(|f| {
                vars_to_remove.remove(f);
            });
        }
        NodeEnum::Element(ElementNode::Quant(n)) => {
            vars_to_remove.remove(&n.bound_var_id);
        }
        NodeEnum::AppliedSymb(n) => {
            n.child_iter()
                .filter_map(|f| {
                    if let ElementNode::Quant(q) = f {
                        Some(q)
                    } else {
                        None
                    }
                })
                .for_each(|f| {
                    vars_to_remove.remove(&f.bound_var_id);
                });
        }
        NodeEnum::AppliedAuxSymb(n) => {
            n.child_iter()
                .filter_map(|f| {
                    if let ElementNode::Quant(q) = f {
                        Some(q)
                    } else {
                        None
                    }
                })
                .for_each(|f| {
                    vars_to_remove.remove(&f.bound_var_id);
                });
        }
        NodeEnum::Rule(rule) => {
            rule.head.variables.iter_vars().for_each(|f| {
                vars_to_remove.remove(f);
            });
        }
        _ => (),
    });
    vars_to_remove
}

struct ExtraSplit<'a> {
    cur_guard: LayoutSatSet,
    to_remove: &'a [BoundVarId],
    to_split: &'a [BoundVarId],
    quant_loc: NodeIndex,
    expr_transformer: &'a mut ExpressionTransformer,
    from: ExpressionRef<'a>,
    context: &'a InterpContext<'a>,
    back_translation: &'a IdHashMap<BoundVarId, BoundVarId>,
}

impl<'b> SatisfyingSetTransform<'b> {
    pub fn new(structure: &'b PartialStructure, context: InterpContext<'b>) -> Self {
        Self {
            context,
            ignore_set: Default::default(),
            node_with_interp: Vec::new(),
            structure,
            inner: false,
        }
    }

    fn new_inner(
        structure: &'b PartialStructure,
        context: InterpContext<'b>,
        ignore_set: IdHashSet<PfuncIndex>,
    ) -> Self {
        Self {
            context,
            ignore_set,
            node_with_interp: Vec::new(),
            structure,
            inner: true,
        }
    }

    pub fn from_theory(theory: &'b Theory) -> Self {
        let context = InterpContext::from_theory(theory);
        Self::new(&theory.structure, context)
    }

    fn bin_op_optimize<'a>(
        &self,
        bin_op: BinOpNode,
        from_expr: ExpressionRef,
        expr_transformer: &mut ExpressionTransformer,
    ) -> Option<VectorReturn> {
        match bin_op.bin_op {
            eq @ (BinOps::Eq | BinOps::Neq) => {
                let neq = eq == BinOps::Neq;
                let (el1, el2) = get_el_node_and_el_node(&bin_op, from_expr.expressions())?;
                let mut symb = eq_element(el1, el2, &self.context)?;
                if neq {
                    symb = symb.neg().unwrap();
                }
                let loc = expr_transformer.rec_copy(from_expr);
                VectorReturn(symb.into(), loc).into()
            }
            _ => None,
        }
    }

    fn quant_splitting<'a>(
        &mut self,
        q: NodeWVariables<'a>,
        start: NodeIndex,
        // Prevents the return of the given boolean value if the cardinality is zero.
        // This is required for universal- and existential quantification since if quant split
        // returned a false or a true respectively doesn't actually mean these
        // boolean values are correct depending on the guard (that must still be calculated)
        card_check_on: Option<bool>,
        // Possible removal of variables that only exist in the guard and not in the sub formula of
        // the quantification.
        // Also allows the propagation of the guard that contains variables not from the
        // quantification it is guarding, allowing further simplification.
        remove_extra_vars: impl Fn(ExtraSplit) -> Either<NodeIndex, LayoutSatSet> + 'a,
        expr_transformer: &'a mut ExpressionTransformer,
    ) -> Either<
        QuantSplitIter<
            'a,
            impl FnMut(ExpressionRef<'_>, &mut ExpressionTransformer) -> Option<NodeIndex> + 'a,
        >,
        NodeIndex,
    >
    where
        'b: 'a,
    {
        if self.node_with_interp.len() == 0 {
            return Either::Right(start);
        }
        let quant_index = start;
        // collect all relevant bit vectors
        let nodes: IdHashMap<_, _> = self
            .node_with_interp
            .iter()
            .filter(|f| f.1.layout().contains_any_variables(&q.variables))
            .map(|f| f.0)
            .enumerate()
            .map(|f| (f.1, f.0))
            .collect();
        let cur_node_with_interp: Vec<_>;
        // split into relevant interps and irrelevant interps
        (cur_node_with_interp, self.node_with_interp) = {
            let taken = core::mem::replace(&mut self.node_with_interp, Vec::new());
            taken.into_iter().partition_map(|val| {
                if nodes.contains_key(&val.0) {
                    Either::Left(val)
                } else {
                    Either::Right(val)
                }
            })
        };
        // collect variables that can be removed when simplifying
        let mut variables_to_remove: IdHashSet<usize> = IdHashSet::default();
        let quant_inner = NodeWVariables::try_from((
            quant_index,
            expr_transformer
                .get_expressions()
                .new_at(start)
                .expressions(),
        ))
        .unwrap();
        let sub_expr = expr_transformer
            .get_expressions()
            .new_at(quant_inner.formula);
        quant_inner
            .variables
            .iter_vars()
            .enumerate()
            .for_each(|(id, val)| {
                if !contains_bound_var(sub_expr, *val) {
                    variables_to_remove.insert(id);
                }
            });

        // collect extra variables that need to be removed
        let dom_el = q.variables.get_i_dom_pred();
        // check again if empty, we might have no interpretation that contains
        // the variable of this quantification
        if nodes.len() == 0 {
            return Either::Right(start);
        }
        let node_with_interp = cur_node_with_interp;
        let quant_map = expr_transformer.get_quant_translation().clone();

        let mut states =
            0..(2 as usize).pow(node_with_interp.len().try_into().expect("Theory too big"));
        let context = self.context.clone();
        let transform_iter =
            expr_transformer.inner_transform_iter(start, move |from, expr_transformer| {
                let quant_inner =
                    NodeWVariables::try_from((quant_index, from.expressions())).unwrap();
                expr_transformer.preamble_variables(&quant_inner.variables);
                loop {
                    let i = states.next()?;
                    let mut qs = QuantSplitter {
                        quant: quant_index,
                        got_simplified: false,
                        vars_to_remove: &variables_to_remove,
                        replace: NodeChecker {
                            nodes: &nodes,
                            cur: i,
                        },
                    };
                    let quant_split_id = qs.transform_expression(from, expr_transformer);
                    // Check if the quantification hasn't been simplified.
                    // And is still the same quantification we have split!
                    if let (Ok(quant), false) = (
                        NodeWVariables::try_from((
                            quant_split_id,
                            expr_transformer.get_expressions(),
                        )),
                        qs.got_simplified,
                    ) {
                        // This vector has layout with expression from outside closure.
                        // Any bound var in inner transform we use, is a bound var from
                        // expr_transformer from in this closure.
                        let bv = partial_interpreted_quant_split(
                            node_with_interp.iter().enumerate().map(move |(j, bv)| {
                                if i & 1 << j != 0 {
                                    (&bv.1, true)
                                } else {
                                    (&bv.1, false)
                                }
                            }),
                            &context,
                        )
                        // this can never be None since we check if node_with_interp is
                        // empty
                        .unwrap();
                        let mut bv = if let Some(f) = dom_el {
                            bv.and(f.bit_vec.clone(), &context)
                        } else {
                            bv
                        };
                        // skip adding this quantification since it is completely guarded
                        if bv.cardinality() == 0 {
                            continue;
                        }
                        // translate layout from original layout to transformed layout
                        // then transformed layout goes to inner layout in add_i_dom_pred
                        bv.mut_layout().translate_layout(&quant_map);
                        let back_translation: IdHashMap<_, _> = expr_transformer
                            .get_quant_translation()
                            .iter()
                            .map(|f| (*f.1, *f.0))
                            .collect();
                        let vars_to_remove = find_vars_to_remove(
                            &quant.variables,
                            expr_transformer.get_expressions().new_at(quant.formula),
                        );
                        let vars_to_remove: Box<[_]> = vars_to_remove
                            .into_iter()
                            .map(|f| back_translation.get(&f).copied().unwrap_or(f))
                            .collect();
                        let mut vars_to_split_from = Vec::with_capacity(bv.layout().len());
                        let mut vars_to_split = Vec::with_capacity(bv.layout().len());
                        for var in bv.layout().iter() {
                            let var_translated = expr_transformer
                                .get_quant_translation()
                                .get(&var)
                                .copied()
                                .unwrap_or(var);
                            if !quant.variables.contains(var_translated) {
                                vars_to_split_from.push(var);
                                vars_to_split.push(var_translated);
                            }
                        }
                        if vars_to_remove.len() != 0 || vars_to_split.len() != 0 {
                            // Copy free variable types to this type map
                            for (old, new) in vars_to_split_from.iter().zip(&vars_to_split) {
                                let type_e = from.get_type_map()[old].clone();
                                expr_transformer
                                    .get_mut_expr_ref()
                                    .get_type_map_mut()
                                    .insert(*new, type_e);
                            }
                            let transformed_context = InterpContext::new(
                                from.get_type_map(),
                                &from.expressions.rc_type_interps(),
                            );
                            let removed = remove_extra_vars(ExtraSplit {
                                cur_guard: bv,
                                to_remove: &vars_to_remove,
                                to_split: &vars_to_split,
                                back_translation: &back_translation,
                                from,
                                expr_transformer,
                                context: &transformed_context,
                                quant_loc: quant_split_id,
                            });
                            // there is no need to check if the cardinality of the guard is
                            // zero. We are only ever here if we need to remove some
                            // variables (not all!).
                            // If the original cardinality wasn't zero (checked little higher)
                            // then this one also can't.
                            match removed {
                                Either::Left(new) => return Some(new),
                                Either::Right(sat_set) => {
                                    let quant = NodeWVariables::try_from((
                                        quant_split_id,
                                        expr_transformer.get_expressions(),
                                    ))
                                    .unwrap();
                                    expr_transformer.add_i_dom_pred(
                                        quant.variables.dom_pred_id(),
                                        IDomainPredicate::from_satset(sat_set, from.get_type_map()),
                                    );
                                    return Some(quant_split_id);
                                }
                            }
                        }
                        expr_transformer.add_i_dom_pred(
                            quant.variables.dom_pred_id(),
                            IDomainPredicate::from_satset(bv, from.get_type_map()),
                        )
                    } else {
                        // Check for boolean value if we need to check the cardinality
                        match (
                            card_check_on,
                            expr_transformer
                                .get_expressions()
                                .new_at(quant_split_id)
                                .try_into_bool(),
                        ) {
                            (Some(card_check), Some(simplified)) if card_check == simplified => {
                                let bv = partial_interpreted_quant_split(
                                    node_with_interp.iter().enumerate().map(move |(j, bv)| {
                                        if i & 1 << j != 0 {
                                            (&bv.1, true)
                                        } else {
                                            (&bv.1, false)
                                        }
                                    }),
                                    &context,
                                )
                                .unwrap();
                                if bv.cardinality() == 0 {
                                    continue;
                                }
                            }
                            _ => {}
                        }
                    }
                    return Some(quant_split_id);
                }
            });
        return Either::Left(QuantSplitIter {
            inner: transform_iter,
            structure: self.structure,
        });
    }

    fn transform<'a>(
        &mut self,
        from: ExpressionRef<'a>,
        expr_transformer: &mut ExpressionTransformer,
    ) -> VectorReturn {
        let transform = |from, t_expr: &mut _| self._transform(from, t_expr);
        expr_transformer.transform(from, transform)
    }

    // TODO find alternatives to recursion (each stack frame of this function is heavy)
    // or partially move some of the variables on the heap ((bit)vectors)
    fn _transform<'a>(
        &mut self,
        from_expr: ExpressionRef<'a>,
        expr_transformer: &mut ExpressionTransformer,
    ) -> VectorReturn {
        let node_enum = if let Ok(value) = from_expr.try_first_node_enum() {
            value
        } else {
            return self.transform_custom_exprs(from_expr, expr_transformer);
        };
        match node_enum {
            NodeEnum::BinOps(b) => {
                if let Some(val) = self.bin_op_optimize(b.clone(), from_expr, expr_transformer) {
                    return val;
                }
                let VectorReturn(bv_left, lhs) =
                    self.transform(from_expr.new_at(b.lhs), expr_transformer);
                let VectorReturn(bv_right, rhs) =
                    self.transform(from_expr.new_at(b.rhs), expr_transformer);
                match b.bin_op {
                    op @ (BinOps::And | BinOps::Or | BinOps::Impl | BinOps::Eqv) => {
                        let node = BinOpNode::new(b.bin_op, lhs, rhs);
                        match (bv_left, bv_right) {
                            (Some(l), Some(r)) => {
                                let bv = match op {
                                    BinOps::And => {
                                        l.and(r, &self.context).expect("Type mismatch").into()
                                    }
                                    BinOps::Or => {
                                        l.or(r, &self.context).expect("Type mismatch").into()
                                    }
                                    BinOps::Impl => {
                                        let neg_l = l.neg().expect("Type mismatch");
                                        neg_l.or(r, &self.context).expect("Type mismatch").into()
                                    }
                                    BinOps::Eqv => {
                                        let a = l.xor(r, &self.context).expect("Type mismatch");
                                        a.neg().expect("Type mismatch")
                                    }
                                    _ => unreachable!(),
                                };
                                let loc = bv.push_scalar_or(expr_transformer, from_expr, || node);
                                VectorReturn(bv.into(), loc)
                            }
                            val @ ((Some(_), None) | (None, Some(_))) => {
                                let loc = expr_transformer.push_node(node, from_expr);
                                use LayoutSymbol as L;
                                match val {
                                    (Some(L::Predicate(bv)), None) => {
                                        self.node_with_interp.push((lhs, bv))
                                    }
                                    (None, Some(L::Predicate(bv))) => {
                                        self.node_with_interp.push((rhs, bv))
                                    }
                                    (Some(L::Scalar(TypeElement::Bool(_))), None)
                                    | (None, Some(L::Scalar(TypeElement::Bool(_)))) => {}
                                    _ => unreachable!(),
                                }
                                VectorReturn(None, loc)
                            }
                            _ => {
                                let loc = expr_transformer.push_node(node, from_expr);
                                VectorReturn(None, loc)
                            }
                        }
                    }
                    op @ (BinOps::Eq
                    | BinOps::Neq
                    | BinOps::Add
                    | BinOps::Sub
                    | BinOps::Mult
                    | BinOps::Lt
                    | BinOps::Le
                    | BinOps::Gt
                    | BinOps::Ge
                    | BinOps::Rem
                    | BinOps::Divide) => {
                        let mut node = BinOpNode::new(b.bin_op, lhs, rhs);
                        match (bv_left, bv_right) {
                            (Some(bv_left), Some(bv_right)) => {
                                let bv = match op {
                                    BinOps::Eq => {
                                        bv_left.eq(bv_right, &self.context).expect("Type mismatch")
                                    }
                                    BinOps::Neq => {
                                        bv_left.neq(bv_right, &self.context).expect("Type mismatch")
                                    }
                                    BinOps::Add => {
                                        bv_left.add(bv_right, &self.context).expect("Type mismatch")
                                    }
                                    BinOps::Sub => {
                                        bv_left.sub(bv_right, &self.context).expect("Type mismatch")
                                    }
                                    BinOps::Mult => bv_left
                                        .mult(bv_right, &self.context)
                                        .expect("Type mismatch"),
                                    BinOps::Lt => {
                                        bv_left.lt(bv_right, &self.context).expect("Type mismatch")
                                    }
                                    BinOps::Le => {
                                        bv_left.le(bv_right, &self.context).expect("Type mismatch")
                                    }
                                    BinOps::Gt => {
                                        bv_left.gt(bv_right, &self.context).expect("Type mismatch")
                                    }
                                    BinOps::Ge => {
                                        bv_left.ge(bv_right, &self.context).expect("Type mismatch")
                                    }
                                    BinOps::Divide => {
                                        bv_left.div(bv_right, &self.context).expect("Type mismatch")
                                    }
                                    BinOps::Rem => {
                                        bv_left.rem(bv_right, &self.context).expect("Type mismatch")
                                    }
                                    BinOps::Or | BinOps::And | BinOps::Impl | BinOps::Eqv => {
                                        unreachable!()
                                    }
                                };
                                let loc = bv.push_scalar_or(expr_transformer, from_expr, || node);
                                VectorReturn(bv.into(), loc)
                            }
                            (left, right) => {
                                if let Some(left) = left {
                                    node.lhs = left.push_interpretation(
                                        expr_transformer,
                                        from_expr,
                                        &self.context,
                                    );
                                }
                                if let Some(right) = right {
                                    node.rhs = right.push_interpretation(
                                        expr_transformer,
                                        from_expr,
                                        &self.context,
                                    );
                                }
                                let loc = expr_transformer.push_node(node, from_expr);
                                VectorReturn(None, loc)
                            }
                        }
                    }
                }
            }
            NodeEnum::Neg(n) => {
                let VectorReturn(bv, sub_form) =
                    self.transform(from_expr.new_at(n.child), expr_transformer);
                match bv {
                    Some(bv) => {
                        let bv = bv.neg().expect("Type mismatch");
                        let loc = bv
                            .push_scalar_or(expr_transformer, from_expr, || NegNode::new(sub_form));
                        VectorReturn(bv.into(), loc)
                    }
                    None => {
                        let loc = expr_transformer.push_node(NegNode::new(sub_form), from_expr);
                        VectorReturn(None, loc)
                    }
                }
            }
            NodeEnum::NumNeg(n) => {
                let VectorReturn(bv, sub_form) =
                    self.transform(from_expr.new_at(n.child), expr_transformer);
                match bv {
                    Some(bv) => {
                        let bv = bv.num_neg().expect("Type mismatch");
                        let loc = bv.push_scalar_or(expr_transformer, from_expr, || {
                            NumNegNode::new(sub_form)
                        });
                        VectorReturn(bv.into(), loc)
                    }
                    None => {
                        let loc = expr_transformer.push_node(NumNegNode::new(sub_form), from_expr);
                        VectorReturn(None, loc)
                    }
                }
            }
            NodeEnum::IsInt(n) => {
                let VectorReturn(bv, sub_form) =
                    self.transform(from_expr.new_at(n.child), expr_transformer);
                match bv {
                    Some(bv) => {
                        let bv = bv.is_int().expect("Type mismatch");
                        let loc = bv.push_scalar_or(expr_transformer, from_expr, || {
                            IsIntNode::new(sub_form)
                        });
                        VectorReturn(bv.into(), loc)
                    }
                    None => {
                        let loc = expr_transformer.push_node(IsIntNode::new(sub_form), from_expr);
                        VectorReturn(None, loc)
                    }
                }
            }
            aps @ (NodeEnum::AppliedSymb(_) | NodeEnum::AppliedAuxSymb(_)) => {
                match aps {
                    NodeEnum::AppliedSymb(ap) if self.ignore_set.contains(&ap.index) => {
                        return expr_transformer.rec_copy(from_expr).into();
                    }
                    _ => {}
                }
                let splitted_func = self.inner
                    && match &aps {
                        NodeEnum::AppliedSymb(ap) => ap.get_kind().is_splitted(),
                        NodeEnum::AppliedAuxSymb(ap) => ap.get_kind().is_splitted(),
                        _ => unreachable!(),
                    };
                let func_sol = match &aps {
                    NodeEnum::AppliedSymb(ap) => PfuncSolve::from_func(
                        self.structure.get(ap.index),
                        ap.child_iter(),
                        &self.context,
                        self.inner,
                        splitted_func,
                    ),
                    NodeEnum::AppliedAuxSymb(ap) => PfuncSolve::from_func(
                        from_expr.expressions.get(ap.index),
                        ap.child_iter(),
                        &self.context,
                        self.inner,
                        splitted_func,
                    ),
                    _ => unreachable!(),
                };
                match func_sol {
                    PfuncSolve::NoInterp => {
                        let loc = expr_transformer.rec_copy(from_expr);
                        VectorReturn(None, loc)
                    }
                    PfuncSolve::PartialPred { ct, cf } => {
                        // a fake aux symbol, to make sure no simplification can occur.
                        let aux_symb = expr_transformer.get_mut_expr_ref().add_aux(AuxSignature {
                            codomain: Type::Bool,
                            domain: Vec::new().into(),
                        });
                        // i.e. ~p_f(x) & (p_t(x) | p(x))
                        let ct_fake = expr_transformer
                            .push_translated_node(AppliedAuxSymbBuilder::new(aux_symb), from_expr);
                        self.node_with_interp.push((ct_fake, ct));
                        let cf_fake = expr_transformer
                            .push_translated_node(AppliedAuxSymbBuilder::new(aux_symb), from_expr);
                        self.node_with_interp.push((cf_fake, cf.neg()));
                        let original = expr_transformer.rec_copy(from_expr);
                        let ct_op = expr_transformer
                            .push_node(BinOpNode::new(BinOps::Or, ct_fake, original), from_expr);
                        expr_transformer
                            .push_node(BinOpNode::new(BinOps::And, cf_fake, ct_op), from_expr)
                            .into()
                    }
                    PfuncSolve::PartialFunc(guard) => {
                        // a fake aux symbol, to make sure no simplification can occur.
                        let aux_symb = expr_transformer.get_mut_expr_ref().add_aux(AuxSignature {
                            codomain: Type::Bool,
                            domain: Vec::new().into(),
                        });
                        let cond = expr_transformer
                            .push_translated_node(AppliedAuxSymbBuilder::new(aux_symb), from_expr);
                        let then_term = match aps {
                            NodeEnum::AppliedSymb(aps) => {
                                let mut builder = AppliedSymbBuilder::from(aps);
                                builder = builder.map_children(|f| {
                                    expr_transformer.translate_element(f, from_expr.expressions())
                                });
                                builder.kind = Kind::Splitted;
                                expr_transformer.push_translated_node(builder, from_expr)
                            }
                            NodeEnum::AppliedAuxSymb(aps) => {
                                let mut builder = AppliedAuxSymbBuilder::from(aps);
                                builder = builder.map_children(|f| {
                                    expr_transformer.translate_element(f, from_expr.expressions())
                                });
                                builder.kind = Kind::Splitted;
                                expr_transformer.push_translated_node(builder, from_expr)
                            }
                            _ => unreachable!(),
                        };
                        let else_term = expr_transformer.rec_copy(from_expr);
                        self.node_with_interp.push((cond, guard));
                        let ite = IteNode {
                            cond,
                            then_term,
                            else_term,
                        };
                        expr_transformer.push_node(ite, from_expr).into()
                    }
                    PfuncSolve::Interp(bv) => {
                        let loc = bv.push_scalar_or_else(expr_transformer, from_expr, |expr| {
                            expr.interpreted_node(from_expr)
                        });
                        VectorReturn(bv.into(), loc)
                    }
                }
            }
            NodeEnum::Quant(q) => {
                let VectorReturn(bv, child) =
                    self.transform(from_expr.new_at(q.formula), expr_transformer);
                match bv {
                    Some(bv) => {
                        let dom_el = q.variables.get_i_dom_pred();
                        let bv = if let Some(f) = dom_el {
                            match q.quant_type {
                                QuantKind::UniQuant => {
                                    let l_neg = f.bit_vec.clone().neg().into();
                                    bv.or(l_neg, &self.context).expect("Type mismatch")
                                }
                                QuantKind::ExQuant => bv
                                    .and(f.bit_vec.clone().into(), &self.context)
                                    .expect("Type mismatch"),
                            }
                        } else {
                            bv
                        };
                        let new_bv = match q.quant_type {
                            QuantKind::ExQuant => bv
                                .exists(q.variables.slice_vars(), &self.context)
                                .expect("Type mismatch"),
                            QuantKind::UniQuant => bv
                                .universal(q.variables.slice_vars(), &self.context)
                                .expect("Type mismatch"),
                        };
                        let loc = new_bv.push_scalar_or(expr_transformer, from_expr, || {
                            QuantNode::new(q.quant_type, q.variables.clone(), child).standalone()
                        });
                        VectorReturn(new_bv.into(), loc)
                    }
                    None => {
                        let loc = expr_transformer.push_node(
                            QuantNode::new(q.quant_type, q.variables.clone(), child).standalone(),
                            from_expr,
                        );
                        // Check if node has not been simplified
                        if NodeEnum::has_variable(loc, expr_transformer.get_expr_ref()) {
                            let quant_type = q.quant_type;
                            let abort_value = match quant_type {
                                QuantKind::ExQuant => true,
                                QuantKind::UniQuant => false,
                            };
                            let op_chained = {
                                let splitted = self.quant_splitting(
                                    q.into(),
                                    loc,
                                    Some(abort_value),
                                    Self::extra_split_quant,
                                    expr_transformer,
                                );
                                let mut quant_iter = match splitted {
                                    Either::Left(iter) => iter,
                                    Either::Right(no_change) => return no_change.into(),
                                };
                                let mut op_chained: Option<VectorReturn> = None;
                                let op = match quant_type {
                                    QuantKind::ExQuant => BinOps::Or,
                                    QuantKind::UniQuant => BinOps::And,
                                };
                                while let Some(vec_ret) = quant_iter.next(self) {
                                    let value = quant_iter
                                        .expr_transformer()
                                        .get_expressions()
                                        .to_expression(vec_ret.1)
                                        .try_into_bool();
                                    if value == Some(abort_value) {
                                        return vec_ret.into();
                                    }
                                    if let Some(op_chainedd) = op_chained {
                                        let get_bin_op =
                                            || BinOpNode::new(op, op_chainedd.1, vec_ret.1);
                                        let get_op_chained_id =
                                            |quant_iter: &mut QuantSplitIter<'_, _>| {
                                                quant_iter
                                                    .expr_transformer_mut()
                                                    .push_node(get_bin_op(), from_expr)
                                            };
                                        op_chained = match (op_chainedd.0, vec_ret.0) {
                                            (None, None) => {
                                                Some(get_op_chained_id(&mut quant_iter).into())
                                            }
                                            (Some(value), None) => {
                                                // scalar is also possible
                                                if let LayoutSymbol::Predicate(value) = value {
                                                    self.node_with_interp
                                                        .push((op_chainedd.1, value));
                                                }
                                                Some(get_op_chained_id(&mut quant_iter).into())
                                            }
                                            (None, Some(value)) => {
                                                // scalar is also possible
                                                if let LayoutSymbol::Predicate(value) = value {
                                                    self.node_with_interp.push((vec_ret.1, value));
                                                }
                                                Some(get_op_chained_id(&mut quant_iter).into())
                                            }
                                            (Some(op_chain), Some(vecr)) => {
                                                let new = op_chain
                                                    .or(vecr, &self.context)
                                                    .expect("type mismatch");
                                                let id = new.push_scalar_or(
                                                    quant_iter.expr_transformer_mut(),
                                                    from_expr,
                                                    get_bin_op,
                                                );
                                                Some(VectorReturn(Some(new), id))
                                            }
                                        };
                                    } else {
                                        op_chained = Some(vec_ret)
                                    }
                                }
                                op_chained
                            };
                            op_chained.unwrap_or_else(|| match quant_type {
                                QuantKind::ExQuant => VectorReturn(
                                    Some(false.into()),
                                    expr_transformer.push_node(false, from_expr),
                                ),
                                QuantKind::UniQuant => VectorReturn(
                                    Some(true.into()),
                                    expr_transformer.push_node(true, from_expr),
                                ),
                            })
                        } else {
                            VectorReturn(None, loc)
                        }
                    }
                }
            }
            NodeEnum::Agg(agg) => {
                let VectorReturn(bv, formula) =
                    self.transform(from_expr.new_at(agg.formula), expr_transformer);
                let node = AggregateNode::new(agg.aggregate_type, formula, agg.variables.clone());
                match bv {
                    Some(bv) => {
                        let dom_el = agg.variables.get_i_dom_pred();
                        let bv = if let Some(f) = dom_el {
                            match agg.aggregate_type {
                                AggKind::Sum => LayoutSymbol::from(f.bit_vec.clone())
                                    .ite(bv, 0.into(), &self.context)
                                    .expect("Type mismatch"),
                                AggKind::Card => bv
                                    .and(f.bit_vec.clone().into(), &self.context)
                                    .expect("Type mismatch"),
                            }
                        } else {
                            bv
                        };
                        let new_bv = match agg.aggregate_type {
                            AggKind::Card => bv
                                .cardinality(agg.variables.slice_vars(), &self.context)
                                .expect("Type error"),
                            AggKind::Sum => bv
                                .sum(agg.variables.slice_vars(), &self.context)
                                .expect("Type error"),
                        };
                        let loc = new_bv
                            .push_scalar_or(expr_transformer, from_expr, || node.standalone());
                        VectorReturn(new_bv.into(), loc)
                    }
                    None => {
                        let loc = expr_transformer.push_node(node.standalone(), from_expr);
                        let op_chained = {
                            let mut quant_iter = match self.quant_splitting(
                                agg.into(),
                                loc,
                                None,
                                Self::extra_split_aggregate,
                                expr_transformer,
                            ) {
                                Either::Left(iter) => iter,
                                Either::Right(no_change) => return no_change.into(),
                            };
                            let mut op_chained: Option<VectorReturn> = None;
                            while let Some(vec_ret) = quant_iter.next(self) {
                                if let Some(op_chainedd) = op_chained {
                                    let get_bin_op =
                                        |left, right| BinOpNode::new(BinOps::Add, left, right);
                                    let get_op_chained_id =
                                        |left, right, quant_iter: &mut QuantSplitIter<'_, _>| {
                                            quant_iter
                                                .expr_transformer_mut()
                                                .push_node(get_bin_op(left, right), from_expr)
                                        };
                                    op_chained = match (op_chainedd.0, vec_ret.0) {
                                        (None, None) => Some(
                                            get_op_chained_id(
                                                op_chainedd.1,
                                                vec_ret.1,
                                                &mut quant_iter,
                                            )
                                            .into(),
                                        ),
                                        (Some(value), None) => {
                                            let left = value.push_interpretation(
                                                quant_iter.expr_transformer_mut(),
                                                from_expr,
                                                &self.context,
                                            );
                                            Some(
                                                get_op_chained_id(left, vec_ret.1, &mut quant_iter)
                                                    .into(),
                                            )
                                        }
                                        (None, Some(value)) => {
                                            let right = value.push_interpretation(
                                                quant_iter.expr_transformer_mut(),
                                                from_expr,
                                                &self.context,
                                            );
                                            Some(
                                                get_op_chained_id(
                                                    op_chainedd.1,
                                                    right,
                                                    &mut quant_iter,
                                                )
                                                .into(),
                                            )
                                        }
                                        (Some(op_chain), Some(vecr)) => {
                                            let new = op_chain
                                                .add(vecr, &self.context)
                                                .expect("type mismatch");
                                            let id = new.push_scalar_or(
                                                quant_iter.expr_transformer_mut(),
                                                from_expr,
                                                || get_bin_op(op_chainedd.1, vec_ret.1),
                                            );
                                            Some(VectorReturn(Some(new), id))
                                        }
                                    };
                                } else {
                                    op_chained = Some(vec_ret)
                                }
                            }
                            op_chained
                        };
                        op_chained.unwrap_or_else(|| {
                            VectorReturn(
                                Some(0.into()),
                                expr_transformer.push_node(IntElementNode::from(0), from_expr),
                            )
                        })
                    }
                }
            }
            NodeEnum::Element(e) => {
                let loc = expr_transformer.push_node(e.clone(), from_expr);
                VectorReturn(LayoutSymbol::from_element(e, &self.context).into(), loc)
            }
            NodeEnum::Ite(ite) => {
                let VectorReturn(cond, cond_child) =
                    self.transform(from_expr.new_at(ite.cond), expr_transformer);
                let VectorReturn(then_term, then_child) =
                    self.transform(from_expr.new_at(ite.then_term), expr_transformer);
                let VectorReturn(else_term, else_child) =
                    self.transform(from_expr.new_at(ite.else_term), expr_transformer);
                let mut node = IteNode {
                    cond: cond_child,
                    then_term: then_child,
                    else_term: else_child,
                };
                match (cond, then_term, else_term) {
                    (Some(cond), Some(then_term), Some(else_term)) => {
                        let new_v = cond
                            .ite(then_term, else_term, &self.context)
                            .expect("Type mismatch!");
                        let loc = new_v.push_scalar_or(expr_transformer, from_expr, || node);
                        VectorReturn(new_v.into(), loc)
                    }
                    (cond, then_term, else_term) => {
                        if let Some(then_term) = then_term {
                            node.then_term = then_term.push_interpretation(
                                expr_transformer,
                                from_expr,
                                &self.context,
                            );
                        }
                        if let Some(else_term) = else_term {
                            node.else_term = else_term.push_interpretation(
                                expr_transformer,
                                from_expr,
                                &self.context,
                            );
                        }
                        let loc = expr_transformer.push_node(node, from_expr);
                        if let Some(cond) = cond {
                            if let LayoutSymbol::Predicate(p) = cond {
                                self.node_with_interp.push((cond_child, p));
                            }
                        }
                        VectorReturn(None, loc)
                    }
                }
            }
            NodeEnum::Def(def) => {
                let mut new_def = DefinitionBuilder::new();
                for definiendum in def.iter_definiendums() {
                    self.ignore_set.insert(definiendum);
                }
                for rule_id in def.iter_indexes() {
                    let VectorReturn(set, id) =
                        self.transform(from_expr.new_at(rule_id), expr_transformer);
                    debug_assert!(set.is_none());
                    if let Ok(rules) = Rules::try_from((id, expr_transformer.get_expressions())) {
                        // This is fine, since these rules come from quant splitting, and quant
                        // splitting guarantees that all returned nodes with variables have a
                        // disjoint domain, the combined domains are equal to the original domain
                        // (if no rules has been simplified, i.e p() <- false)
                        rules.rules.iter().for_each(|f| {
                            new_def.add_rule_index(*f, expr_transformer.get_expressions());
                        })
                    } else {
                        new_def.add_rule_index(id, expr_transformer.get_expressions());
                    }
                }
                for definiendum in def.iter_definiendums() {
                    self.ignore_set.remove(&definiendum);
                }
                expr_transformer.push_node(new_def, from_expr).into()
            }
            NodeEnum::Rule(rule) => self.transform_rule(rule, from_expr, expr_transformer),
        }
    }

    /// Further quant splitting for aggregates.
    ///
    /// Here we remove the extra variables that only exist in the guard.
    /// We also propagate variables in the guard not contained in the variables in the
    /// quantification.
    fn extra_split_aggregate(
        ExtraSplit {
            back_translation,
            cur_guard,
            context,
            from,
            expr_transformer,
            quant_loc,
            to_remove,
            to_split,
            ..
        }: ExtraSplit,
    ) -> Either<NodeIndex, LayoutSatSet> {
        let agg = AggregateNode::try_from((quant_loc, expr_transformer.get_expressions())).unwrap();
        // final layout, used to remove variables in aggregate
        let mut new_layout = cur_guard.layout().clone();
        to_remove
            .iter()
            .for_each(|f| new_layout.eliminate_var_mut(*f));
        to_split
            .iter()
            .for_each(|f| new_layout.eliminate_var_mut(*f));
        new_layout.translate_layout(back_translation);
        let const_to_add = cur_guard.clone().card_agg(to_remove, context);
        let new_sat_set = cur_guard.exists(to_remove, context);
        let new_variables = VariablesBuilder::from_iter(
            new_layout
                .iter()
                .map(|f| (f, from.get_type_map()[&f].clone())),
        );
        let mut agg_builder =
            AggregateNodeBuilder::new(agg.aggregate_type, new_variables, agg.formula);
        match agg_builder.aggregate_type {
            AggKind::Sum => {
                let new_formula = BinOpNode::new(
                    BinOps::Mult,
                    agg_builder.formula,
                    match const_to_add {
                        OrScalar::Value(value) => LayoutSymbol::Int(value).push_interpretation(
                            expr_transformer,
                            from,
                            context,
                        ),
                        OrScalar::Scalar(value) => {
                            expr_transformer.push_node(IntElementNode::from(value), from)
                        }
                    },
                );
                agg_builder.formula = expr_transformer.push_node(new_formula, from);
            }
            AggKind::Card => {
                let new_formula = IteNode {
                    cond: agg_builder.formula,
                    then_term: match const_to_add {
                        OrScalar::Value(value) => LayoutSymbol::Int(value).push_interpretation(
                            expr_transformer,
                            from,
                            context,
                        ),
                        OrScalar::Scalar(value) => {
                            expr_transformer.push_node(IntElementNode::from(value), from)
                        }
                    },
                    else_term: expr_transformer.push_node(IntElementNode::from(0), from),
                };
                agg_builder.aggregate_type = AggKind::Sum;
                agg_builder.formula = expr_transformer.push_node(new_formula, from);
            }
        }
        match new_sat_set {
            OrScalar::Value(value) => {
                if to_split.len() == 0 {
                    agg_builder
                        .variables
                        .set_i_dom_pred(IDomainPredicate::from_satset(value, from.get_type_map()));
                } else {
                    let split_remove: Vec<_> = value
                        .layout()
                        .iter()
                        .filter(|f| !to_split.contains(f))
                        .collect();
                    let left = LayoutSymbol::from(value.clone().exists(&split_remove, context));
                    let left = left.push_interpretation(expr_transformer, from, context);
                    agg_builder
                        .variables
                        .set_i_dom_pred(IDomainPredicate::from_satset(value, from.get_type_map()));
                    let quant = expr_transformer.push_node(agg_builder, from);
                    let else_term = expr_transformer.push_node(IntElementNode::from(0), from);
                    return Either::Left(expr_transformer.push_node(
                        IteNode {
                            cond: left,
                            then_term: quant,
                            else_term,
                        },
                        from,
                    ));
                }
            }
            OrScalar::Scalar(value) => {
                // we somehow have an empty guard, don't know if this is even possible, as such
                // we should handle it properly
                if !value {
                    return Either::Left(expr_transformer.push_node(IntElementNode::from(0), from));
                }
            }
        }
        if agg_builder.variables.len() == 0 {
            Either::Left(agg_builder.formula)
        } else {
            let ret = expr_transformer.push_node(agg_builder, from);
            Either::Left(ret)
        }
    }

    /// Further quant splitting for universal and existential quantification.
    ///
    /// Here we remove the extra variables that only exist in the guard.
    /// We also propagate variables in the guard not contained in the variables in the
    /// quantification.
    fn extra_split_quant(
        ExtraSplit {
            cur_guard,
            context,
            from,
            expr_transformer,
            quant_loc,
            to_remove,
            to_split,
            ..
        }: ExtraSplit,
    ) -> Either<NodeIndex, LayoutSatSet> {
        let quant = QuantNode::try_from((quant_loc, expr_transformer.get_expressions())).unwrap();
        let quant_type = quant.quant_type;
        let abort_value = match quant_type {
            QuantKind::ExQuant => true,
            QuantKind::UniQuant => false,
        };
        match cur_guard.exists(to_remove, context) {
            OrScalar::Value(sat_set) => {
                if to_split.len() == 0 {
                    return Either::Right(sat_set);
                }
                let split_remove: Vec<_> = sat_set
                    .layout()
                    .iter()
                    .filter(|f| !to_split.contains(f))
                    .collect();
                let left_side = LayoutSymbol::from(sat_set.clone().exists(&split_remove, context));
                expr_transformer.add_i_dom_pred(
                    quant.variables.dom_pred_id(),
                    IDomainPredicate::from_satset(sat_set, from.get_type_map()),
                );
                let left_side = match quant_type {
                    QuantKind::UniQuant => left_side.neg().unwrap(),
                    QuantKind::ExQuant => left_side,
                }
                .push_interpretation(expr_transformer, from, context);
                Either::Left(expr_transformer.push_node(
                    BinOpNode::new(
                        match quant_type {
                            QuantKind::UniQuant => BinOps::Or,
                            QuantKind::ExQuant => BinOps::And,
                        },
                        left_side,
                        quant_loc,
                    ),
                    from,
                ))
            }
            OrScalar::Scalar(value) => {
                if value {
                    Either::Left(quant_loc)
                } else {
                    Either::Left(expr_transformer.push_node(abort_value, from))
                }
            }
        }
    }

    fn transform_rule<'a>(
        &mut self,
        rule: Rule<'a>,
        from_expr: ExpressionRef<'a>,
        expr_transformer: &mut ExpressionTransformer,
    ) -> VectorReturn {
        let rule_id = from_expr.start;
        let VectorReturn(set, new_body) =
            self.transform(from_expr.new_at(rule.body), expr_transformer);
        if let Some(LayoutSymbol::Scalar(value)) = &set {
            let head: RuleHeadBuilder = rule.head.clone().into();
            let body = expr_transformer.push_node(value.clone(), from_expr.new_at(rule.body));
            let rule = RuleBuilder::new(head, body);
            expr_transformer
                .push_node(rule, from_expr.new_at(rule_id))
                .into()
        } else {
            if let Some(LayoutSymbol::Predicate(pred)) = set {
                self.node_with_interp.push((new_body, pred));
            }
            let loc = expr_transformer.push_node(
                RuleBuilder::new(rule.head.clone().into(), new_body),
                from_expr,
            );
            let rules = {
                let mut quant_iter = match self.quant_splitting(
                    rule.into(),
                    loc,
                    None,
                    |extra_split| {
                        debug_assert!(
                            extra_split.to_split.len() == 0,
                            "free variables in definitions are not allowed"
                        );
                        Either::Right(extra_split.cur_guard)
                    },
                    expr_transformer,
                ) {
                    Either::Left(iter) => iter,
                    Either::Right(no_change) => return no_change.into(),
                };
                let mut rules = RulesBuilder::new();
                while let Some(vec_ret) = quant_iter.next(self) {
                    let new_rule = vec_ret.1;
                    // Satisfying set transform cannot simplify a rule
                    debug_assert!(vec_ret.0.is_none());
                    if let Ok(other_rules) =
                        Rules::try_from((new_rule, quant_iter.expr_transformer().get_expressions()))
                    {
                        for rule in other_rules.rules {
                            rules.add_rule_index_unchecked(*rule);
                        }
                    } else {
                        debug_assert!(
                            Rule::try_from((
                                new_rule,
                                quant_iter.expr_transformer().get_expressions()
                            ))
                            .is_ok()
                        );
                        rules.add_rule_index_unchecked(new_rule);
                    }
                }
                rules
            };
            match rules.complete() {
                // there are multiple rules
                Ok(rules) => expr_transformer.push_node(rules, from_expr).into(),
                // there is only one rule.
                Err(Either::Left(rule)) => rule.into(),
                // there are no rules, this can never happen: quant splitting
                // can (should) never produce less rules than we started with!
                // As such this should be unreachable.
                Err(Either::Right(_)) => unreachable!(),
            }
        }
    }

    fn transform_custom_exprs<'a>(
        &mut self,
        from_expr: ExpressionRef<'a>,
        expr_transformer: &mut ExpressionTransformer,
    ) -> VectorReturn {
        // this is the only special expr satset uses
        let rules = Rules::try_from((from_expr.start(), from_expr.expressions())).unwrap();
        let mut new_rules = RulesBuilder::new();
        for (rule, rule_id) in rules.iter_rules_and_indexes(from_expr.expressions()) {
            let VectorReturn(set, new_rule) =
                self.transform_rule(rule, from_expr.new_at(rule_id), expr_transformer);
            debug_assert!(set.is_none());
            new_rules.add_rule_index_unchecked(new_rule);
        }
        match new_rules.complete() {
            // there are multiple rules
            Ok(rules) => expr_transformer.push_node(rules, from_expr).into(),
            // there is only one rule.
            Err(Either::Left(rule)) => rule.into(),
            // there are no rules, this can never happen: only quant splitting can produce Rules,
            // but it can (should) never produce less rules than we started with!
            // As such this should be unreachable.
            Err(Either::Right(_)) => unreachable!(),
        }
    }
}

struct QuantSplitIter<'a, F>
where
    F: FnMut(ExpressionRef<'_>, &mut ExpressionTransformer) -> Option<NodeIndex>,
{
    inner: InnerIterTransform<'a, F>,
    structure: &'a PartialStructure,
}

impl<'a, F> QuantSplitIter<'a, F>
where
    F: FnMut(ExpressionRef<'_>, &mut ExpressionTransformer) -> Option<NodeIndex>,
{
    pub fn expr_transformer(&self) -> &ExpressionTransformer {
        self.inner.expr_transformer()
    }

    pub fn expr_transformer_mut(&mut self) -> &mut ExpressionTransformer {
        self.inner.expr_transformer_mut()
    }

    pub fn next(&mut self, outer_satset: &mut SatisfyingSetTransform) -> Option<VectorReturn> {
        let new = self.inner.next()?;
        let (outer, inner, context) = (
            &mut *self.inner.outer,
            &mut self.inner.inner,
            &mut self.inner.empty_context,
        );
        let type_map = outer.get_expressions().get_type_map().clone();
        let ignore_set = core::mem::take(&mut outer_satset.ignore_set);
        let mut satset_transform = SatisfyingSetTransform::new_inner(
            self.structure,
            InterpContext::new(&type_map, outer_satset.context.type_interps()),
            ignore_set,
        );
        let mut inner_loc = outer.cinner_transform_with_other(
            new,
            |from_expr, expr_transformer| satset_transform.transform(from_expr, expr_transformer),
            inner,
        );
        let to_map = satset_transform
            .node_with_interp
            .iter()
            .map(|f| f.0)
            .collect();
        context.clear();
        let (final_id, mapped) = outer.copy_from_inner_transform_with_context_mapped(
            inner,
            inner_loc.1,
            context,
            &to_map,
        );
        inner_loc
            .0
            .as_mut()
            .map(|f| f.mut_layout())
            .flatten()
            .map(|f| {
                for var in f.iter_mut() {
                    let translation = outer
                        .get_quant_translation()
                        .iter()
                        .find(|f| f.1 == var)
                        .map(|f| *f.0)
                        .unwrap_or(*var);
                    *var = translation;
                }
            });
        outer_satset.node_with_interp.extend(
            satset_transform
                .node_with_interp
                .into_iter()
                .map(|f| (*mapped.get(&f.0).unwrap(), f.1))
                // Translate the BoundVarIds back to outer BoundVarIds
                .map(|mut f| {
                    for var in f.1.mut_layout().iter_mut() {
                        let translation = outer
                            .get_quant_translation()
                            .iter()
                            .find(|f| f.1 == var)
                            .map(|f| *f.0)
                            .unwrap_or(*var);
                        *var = translation;
                    }
                    f
                }),
        );
        outer_satset.ignore_set = satset_transform.ignore_set;
        Some(VectorReturn(inner_loc.0, final_id))
    }
}
