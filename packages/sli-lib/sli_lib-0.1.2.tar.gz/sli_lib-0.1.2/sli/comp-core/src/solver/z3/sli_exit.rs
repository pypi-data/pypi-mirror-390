use crate::comp_core::constraints::BoundVarId;
use crate::comp_core::expression::{ExpressionRef, Expressions};
use crate::comp_core::node::{
    AggKind, AppliedAuxSymbNode, AppliedSymbNode, BinOpNode, BinOps, ElementNode, NodeEnum,
    QuantKind,
};
use crate::comp_core::structure::PartialStructure;
use crate::comp_core::structure::{TypeElement, TypeInterps};
use crate::comp_core::vocabulary::{DomainEnum, PfuncIndex, TypeElementIndex};
use crate::comp_core::{IndexRepr, Int};
use crate::comp_core::{
    structure::TypeInterp,
    vocabulary::{Type, TypeEnum, TypeIndex},
};
use core::panic;
use itertools::Either;
use sli_collections::hash_map::IdHashMap;
use std::{unimplemented, unreachable};
use z3::SortKind;
use z3::ast::{Bool, Dynamic, atleast, atmost};
use z3::{Context, DatatypeBuilder, ast, ast::Ast};

/// Generates Z3 datatypes for `String` types in FO(.).
/// These datatypes can then be used when declaring new Z3 variables.
pub fn generate_datatypes<'a>(
    structure: &PartialStructure,
    ctx: &'a Context,
) -> (
    IdHashMap<TypeIndex, z3::DatatypeSort<'a>>,
    IdHashMap<TypeElementIndex, z3::ast::Dynamic<'a>>,
) {
    let vocab = structure.vocab();
    let mut datatypes: IdHashMap<TypeIndex, z3::DatatypeSort> = Default::default();
    let mut constants: IdHashMap<_, z3::ast::Dynamic> = Default::default();
    for (type_id, _) in vocab.types.iter_enumerated() {
        // No need to do anything for int and real codomains.
        let type_interp = &structure.type_interps()[type_id];
        match type_interp {
            TypeInterp::Int(_) | TypeInterp::Real(_) => {
                continue;
            }
            TypeInterp::Custom(elements) => {
                // The type is a string, rejoice! Now we get to make a Z3 datatype.
                let name = format!("{}", IndexRepr::from(type_id));
                if elements.len() == 0 {
                    continue;
                }
                let mut datatype = DatatypeBuilder::new(ctx, name);
                for type_enum in elements.iter() {
                    let el = format!("{}", IndexRepr::from(type_enum));
                    datatype = datatype.variant(&el, vec![]);
                }
                let datatype = datatype.finish();
                // After finishing the datatype, loop over the elements again to gather all the datatype
                // constants. Seems a bit stupid, but there's no proper way to do it. Unfortunately, peanut
                // butter.
                for (i, _) in elements.iter().enumerate() {
                    let datatype_const = datatype.variants[i].constructor.apply(&[]).to_owned();
                    constants.insert(TypeElementIndex(type_id, i.into()), datatype_const);
                }
                datatypes.insert(type_id, datatype);
            }
        }
    }
    return (datatypes, constants);
}

/// Generate Z3-equivalent symbols for the FO(.) symbols.
pub fn generate_type_constraint<'a>(
    func_id: PfuncIndex,
    domain_enum: DomainEnum,
    type_interps: &'a TypeInterps,
    datatypes: &'a IdHashMap<TypeIndex, z3::DatatypeSort>,
    ctx: &'a Context,
) -> Option<ast::Bool<'a>> {
    let func = type_interps.vocab().pfuncs(func_id);
    let domain = func.domain;
    match (domain.as_ref(), func.codomain) {
        // Proposition
        ([], Type::Bool) => {
            None // Generating symbols is not necessary when working with ground constants
            // let prop = z3::FuncDecl::new(&ctx, name, &[], &z3::Sort::bool(&ctx));
            // symbols.insert(name.to_string(), prop);
        }

        // Constant on Int, Real And custom type
        ([], Type::Int | Type::Real | Type::Str(_)) => None,

        // Predicate
        ([_, ..], Type::Bool) => {
            None // Generating symbols is not necessary when working with ground constants
            // let mut vec: Vec<&z3::Sort> = Vec::new();
            // for domain in theory.fnc_domain[x].types.into_iter() {
            //     match domain {
            //         Type::Custom(x) => {
            //             let type_decl = &theory.types[*x];
            //             let type_name = &theory.source[type_decl.start..type_decl.end];
            //             vec.push(&datatypes[type_name].sort);
            //         },
            //         _ => {}
            //     }
            // }
            // // let fnc_domain = theory.fnc_domain[x];
            // let pred = z3::FuncDecl::new(&ctx, name, &vec, &z3::Sort::bool(&ctx));
            // symbols.insert(name.to_string(), pred);
        }

        // Function on Int and Real
        ([_, ..], Type::Int) => None,
        // Symbol on custom type
        (
            [..],
            Type::Str(codomain_id) | Type::IntType(codomain_id) | Type::RealType(codomain_id),
        ) => {
            // We want to generate type constraints for the function.
            // Fairly straightforward:
            // 1. Calculate Cartesian product of input domains
            // 2. Iterate over product, iterate over output range, generate giant disjunction
            //
            // The below code calculates the cartesian product of the input domains.
            // Fairly straightforward: iterate over the domains, and fill `domain_values`.
            // Collects the cartesian product as strings.
            //
            // Make a big disjunction containing all possible values for each possible set of
            // domain values.
            let applied_name = create_pfunc_name(func.index, domain_enum);
            let codomain_interp = &type_interps[codomain_id];
            let mut disjunction = ast::Bool::from_bool(&ctx, false); // TODO: check if there's
            // a better way to do
            // this.
            match codomain_interp {
                TypeInterp::Custom(_) => {
                    // If the type is a string, iterate over all variants of the datatype.
                    let applied_func =
                        ast::Datatype::new_const(&ctx, applied_name, &datatypes[&codomain_id].sort);
                    for output_val in &datatypes[&codomain_id].variants {
                        // let eq = &output_val.tester.apply(&[&applied_func]).as_bool().unwrap();
                        let output_const = &output_val.constructor.apply(&[]).to_owned();
                        disjunction = disjunction | output_const._eq(&applied_func.clone().into());
                    }
                }
                TypeInterp::Int(i) => {
                    // If the type is an Int/Real, grab the values from the decl.
                    let applied_func = ast::Int::new_const(ctx, applied_name);
                    for interp in i.iter() {
                        let value = ast::Int::from_i64(ctx, interp as i64);
                        disjunction = disjunction | applied_func._eq(&value);
                    }
                }
                TypeInterp::Real(i) => {
                    let applied_func = ast::Real::new_const(ctx, applied_name);
                    for interp in i.iter() {
                        let value = ast::Real::from_real_str(
                            ctx,
                            &interp.inner_ref().numer().to_string(),
                            &interp.inner_ref().denom().to_string(),
                        )
                        .expect("Internal error: creation of real failed");
                        disjunction = disjunction | applied_func._eq(&value);
                    }
                }
            }
            Some(disjunction)
        }
        _ => None,
    }
}

pub const AUX_PREFIX: &str = "aux_";

fn func_name_from_appauxsymb(
    applied_symb: &AppliedAuxSymbNode,
    expressions: &Expressions,
    var_values: &IdHashMap<BoundVarId, TypeEnum>,
) -> String {
    let dom_enum = applied_symb.get_domain_enum(expressions, var_values);
    let mut prefix_str = AUX_PREFIX.to_string();
    prefix_str.push_str(&create_pfunc_name(
        applied_symb.index.to_pfunc_index(),
        dom_enum,
    ));
    prefix_str
}

fn func_name_from_appsymb(
    applied_symb: &AppliedSymbNode,
    structure: &PartialStructure,
    var_values: &IdHashMap<BoundVarId, TypeEnum>,
) -> String {
    let dom_enum = applied_symb.get_domain_enum(structure, var_values);
    create_pfunc_name(applied_symb.index, dom_enum)
}

pub fn create_pfunc_name<'a>(pfunc_index: PfuncIndex, domain_enum: DomainEnum) -> String {
    format!("{}-{}", usize::from(pfunc_index), usize::from(domain_enum))
}

/// Parses symbol names of the form \d+-\d+.
/// Will return an error if it cannot do this, e.g., for symbols generated by Z3.
pub(super) fn parse_pfunc_name<'a>(name: &str) -> Result<(PfuncIndex, DomainEnum), ()> {
    let mut split_name = ["", ""];
    let mut splitted = name.split('-');
    split_name
        .iter_mut()
        .zip(&mut splitted)
        .for_each(|(part, split)| *part = split);
    if let Some(_) = splitted.next() {
        return Err(());
    }
    let func_index: usize = split_name[0].parse().map_err(|_| ())?;
    let func_index = PfuncIndex::from(func_index);
    let args: usize = split_name[1].parse().map_err(|_| ())?;
    let args = DomainEnum::from(args);
    Ok((func_index, args))
}

// convenience function for numeric comparison operators
fn numeric_comp_bin_op<'a>(left: Dynamic<'a>, right: Dynamic<'a>, op: BinOps) -> Bool<'a> {
    let ints = match (left.sort_kind(), right.sort_kind()) {
        (SortKind::Int, SortKind::Int) => Some((left.as_int().unwrap(), right.as_int().unwrap())),
        _ => None,
    };
    if let Some((left_int, right_int)) = ints {
        return match op {
            BinOps::Lt => left_int.lt(&right_int),
            BinOps::Le => left_int.le(&right_int),
            BinOps::Gt => left_int.gt(&right_int),
            BinOps::Ge => left_int.ge(&right_int),
            BinOps::Eq => left_int._eq(&right_int),
            BinOps::Neq => left_int._eq(&right_int).not(),
            _ => unreachable!(),
        };
    }
    let reals = match (left.sort_kind(), right.sort_kind()) {
        (SortKind::Int, SortKind::Real) => {
            Some((left.as_int().unwrap().to_real(), right.as_real().unwrap()))
        }
        (SortKind::Real, SortKind::Int) => {
            Some((left.as_real().unwrap(), right.as_int().unwrap().to_real()))
        }
        (SortKind::Real, SortKind::Real) => {
            Some((left.as_real().unwrap(), right.as_real().unwrap()))
        }
        _ => None,
    };
    if let Some((left_real, right_real)) = reals {
        return match op {
            BinOps::Lt => left_real.lt(&right_real),
            BinOps::Le => left_real.le(&right_real),
            BinOps::Gt => left_real.gt(&right_real),
            BinOps::Ge => left_real.ge(&right_real),
            BinOps::Eq => left_real._eq(&right_real),
            BinOps::Neq => left_real._eq(&right_real).not(),
            _ => unreachable!(),
        };
    } else {
        panic!("Type mismatch");
    }
}

fn comp_op<'a>(left: Dynamic<'a>, right: Dynamic<'a>, op: BinOps) -> Bool<'a> {
    let is_int = left.as_int().is_some();
    let is_real = left.as_real().is_some();
    if is_int || is_real {
        return numeric_comp_bin_op(left, right, op);
    }
    return match op {
        BinOps::Eq => left._eq(&right),
        BinOps::Neq => left._eq(&right).not(),
        _ => unreachable!(),
    };
}

/// Given a comparison operation between a numeric value and a cardinality constraint produces a
/// z3 constraint using atmost and atleast.
/// If a situation is encountered where it is not possible to produce the correct constraint using
/// combinations of atmost and atleast [None] is returned.
/// See #32 for more info.
fn create_const_card_constraint<'a>(
    bin_op: BinOps,
    lhs: ExpressionRef<'a>,
    rhs: ExpressionRef<'a>,
    structure: &'a PartialStructure,
    ctx: &'a z3::Context,
    datatypes: &IdHashMap<TypeIndex, z3::DatatypeSort<'a>>,
    type_elements: &IdHashMap<TypeElementIndex, z3::ast::Dynamic<'a>>,
    var_values: &mut IdHashMap<BoundVarId, TypeEnum>,
) -> Option<z3::ast::Bool<'a>> {
    // check if operation is one we can use atmost and atleast for
    if !matches!(
        bin_op,
        BinOps::Eq | BinOps::Neq | BinOps::Lt | BinOps::Le | BinOps::Gt | BinOps::Ge
    ) {
        return None;
    }
    // try to extract literal and aggregate, and normalize binary operation
    let (bin_op, card_sub_expression, variables, value) = match (
        (lhs.first_node_enum(), true),
        (rhs.first_node_enum(), false),
    ) {
        ((NodeEnum::Element(el), _), (NodeEnum::Agg(agg), on_left))
        | ((NodeEnum::Agg(agg), on_left), (NodeEnum::Element(el), _)) => {
            if let (Ok(value), AggKind::Card) = (
                <ElementNode as TryInto<TypeElement>>::try_into(el),
                agg.aggregate_type,
            ) {
                let value = match value {
                    TypeElement::Int(value) => Either::Left(value),
                    TypeElement::Real(value) => Either::Right(value),
                    _ => return None,
                };
                let bin_op = match (on_left, bin_op) {
                    (true, _) => bin_op,
                    (false, BinOps::Lt) => BinOps::Gt,
                    (false, BinOps::Gt) => BinOps::Lt,
                    (false, BinOps::Le) => BinOps::Ge,
                    (false, BinOps::Ge) => BinOps::Le,
                    (false, _) => bin_op,
                };
                let card_sub_expr = lhs.new_at(agg.formula);
                (bin_op, card_sub_expr, agg.variables, value)
            } else {
                return None;
            }
        }
        _ => return None,
    };

    // convert any numeric value to appropriate integer value
    let int_value = {
        match value {
            Either::Right(value) => {
                if let Ok(value) = Int::try_from(value) {
                    value
                } else {
                    match bin_op {
                        BinOps::Eq | BinOps::Neq => return None,
                        BinOps::Lt | BinOps::Le => Int::try_from(value.floor()).ok()?,
                        BinOps::Gt | BinOps::Ge => Int::try_from(value.ceil()).ok()?,
                        _ => unreachable!(),
                    }
                }
            }
            Either::Left(value) => value,
        }
    };
    // atmost and atleast do not accept negative values
    if int_value < 0 {
        return None;
    }

    // collect boolean expressions
    let mut bool_exp = Vec::new();
    card_sub_expression.expressions().iter_variables(
        &variables,
        structure.type_interps(),
        var_values,
        |var_values| {
            let ground_child = atom_to_smt(
                card_sub_expression,
                structure,
                &ctx,
                datatypes,
                type_elements,
                var_values,
            );
            bool_exp.push(ground_child);
        },
    );

    if bool_exp.len() == 0 {
        let card = z3::ast::Int::from_i64(ctx, 0);
        let int_value = z3::ast::Int::from_i64(ctx, int_value as i64);
        return match bin_op {
            BinOps::Eq => card._eq(&int_value),
            BinOps::Lt => card.lt(&int_value),
            BinOps::Le => card.le(&int_value),
            BinOps::Gt => card.gt(&int_value),
            BinOps::Ge => card.ge(&int_value),
            _ => unreachable!(),
        }
        .into();
    }
    match bin_op {
        BinOps::Eq => Some(
            atmost(ctx, &bool_exp, int_value.try_into().ok()?)
                & atleast(ctx, &bool_exp, int_value.try_into().ok()?),
        ),
        BinOps::Neq => {
            let lower_bound = int_value - 1;
            let higher_bound = int_value + 1;
            let mut ret = atleast(ctx, &bool_exp, higher_bound.try_into().ok()?);
            if lower_bound > 0 {
                ret |= atmost(ctx, &bool_exp, lower_bound.try_into().ok()?);
            }
            Some(ret)
        }
        BinOps::Lt => Some(atmost(ctx, &bool_exp, (int_value - 1).try_into().ok()?)),
        BinOps::Le => Some(atmost(ctx, &bool_exp, int_value.try_into().ok()?)),
        BinOps::Gt => Some(atleast(ctx, &bool_exp, (int_value + 1).try_into().ok()?)),
        BinOps::Ge => Some(atleast(ctx, &bool_exp, int_value.try_into().ok()?)),
        _ => unreachable!(),
    }
}

/// Translates an atom to its smt equivalent, and returns it.
/// Atoms are those types of expressions that evaluate to either `true` or `false`, such as
/// booleans, implications (p() => q()), comparisons (p() > q()), and more.
pub fn atom_to_smt<'a>(
    cur_expression: ExpressionRef<'a>,
    structure: &'a PartialStructure,
    ctx: &'a z3::Context,
    datatypes: &IdHashMap<TypeIndex, z3::DatatypeSort<'a>>,
    type_elements: &IdHashMap<TypeElementIndex, z3::ast::Dynamic<'a>>,
    var_values: &mut IdHashMap<BoundVarId, TypeEnum>,
) -> z3::ast::Bool<'a> {
    match cur_expression.first_node_enum() {
        NodeEnum::BinOps(BinOpNode {
            bin_op, lhs, rhs, ..
        }) => match bin_op {
            BinOps::And | BinOps::Or | BinOps::Impl | BinOps::Eqv => {
                let left_child = atom_to_smt(
                    cur_expression.new_at(lhs),
                    structure,
                    &ctx,
                    datatypes,
                    type_elements,
                    var_values,
                );
                let right_child = atom_to_smt(
                    cur_expression.new_at(rhs),
                    structure,
                    &ctx,
                    datatypes,
                    type_elements,
                    var_values,
                );
                match bin_op {
                    BinOps::And => left_child & right_child,
                    BinOps::Or => left_child | right_child,
                    BinOps::Eqv => left_child._eq(&right_child),
                    BinOps::Impl => left_child.implies(&right_child),
                    _ => unreachable!(),
                }
            }
            BinOps::Eq | BinOps::Neq | BinOps::Lt | BinOps::Le | BinOps::Gt | BinOps::Ge => {
                let lhs = cur_expression.new_at(lhs);
                let rhs = cur_expression.new_at(rhs);
                if let Some(atmost_atleast) = create_const_card_constraint(
                    bin_op,
                    lhs,
                    rhs,
                    structure,
                    ctx,
                    datatypes,
                    type_elements,
                    var_values,
                ) {
                    return atmost_atleast;
                }
                let left_child =
                    term_to_smt(lhs, structure, &ctx, datatypes, type_elements, var_values);
                let right_child =
                    term_to_smt(rhs, structure, &ctx, datatypes, type_elements, var_values);
                match bin_op {
                    BinOps::Eq => comp_op(left_child, right_child, bin_op),
                    BinOps::Neq => comp_op(left_child, right_child, bin_op),
                    BinOps::Lt => numeric_comp_bin_op(left_child, right_child, bin_op),
                    BinOps::Le => numeric_comp_bin_op(left_child, right_child, bin_op),
                    BinOps::Gt => numeric_comp_bin_op(left_child, right_child, bin_op),
                    BinOps::Ge => numeric_comp_bin_op(left_child, right_child, bin_op),
                    _ => unreachable!(),
                }
            }
            _ => unimplemented!(),
        },
        aps @ (NodeEnum::AppliedSymb(_) | NodeEnum::AppliedAuxSymb(_)) => {
            // Node represents a predicate or proposition. Its children are the arguments.
            // Based on the nb of children, we know the symbol's arity.
            let value = match &aps {
                NodeEnum::AppliedSymb(appsymb) => appsymb.get_value(structure, var_values),
                NodeEnum::AppliedAuxSymb(appsymb) => {
                    appsymb.get_value(cur_expression.expressions, var_values)
                }
                _ => unreachable!(),
            };

            if let Some(val) = value {
                return match val {
                    TypeElement::Bool(val) => ast::Bool::from_bool(ctx, val),
                    _ => unreachable!(),
                };
            }
            let func_name = match &aps {
                NodeEnum::AppliedSymb(appsymb) => {
                    func_name_from_appsymb(appsymb, structure, var_values)
                }
                NodeEnum::AppliedAuxSymb(appsymb) => {
                    func_name_from_appauxsymb(appsymb, cur_expression.expressions, var_values)
                }
                _ => unreachable!(),
            };
            return ast::Bool::new_const(&ctx, func_name);
        }
        NodeEnum::Neg(neg) => {
            // Negated formula. Quite straightforward.
            let child_id = neg.child;
            let child = atom_to_smt(
                cur_expression.new_at(child_id),
                structure,
                &ctx,
                datatypes,
                type_elements,
                var_values,
            );
            return child.not();
        }
        NodeEnum::IsInt(is_int) => {
            let child_id = is_int.child;
            let child = term_to_smt(
                cur_expression.new_at(child_id),
                structure,
                &ctx,
                datatypes,
                type_elements,
                var_values,
            )
            .as_real()
            .expect("type mismatch");
            return child.is_int();
        }
        NodeEnum::Quant(quant_node) => {
            let formula_id = quant_node.formula;
            let bool_type = match quant_node.quant_type {
                QuantKind::UniQuant => true,
                QuantKind::ExQuant => false,
            };
            // TODO: figure out if this can be avoided.
            let mut ground_formula = ast::Bool::from_bool(&ctx, bool_type);
            cur_expression.expressions().iter_variables(
                &quant_node.variables,
                structure.type_interps(),
                var_values,
                |var_values| {
                    let ground_child = atom_to_smt(
                        cur_expression.new_at(formula_id),
                        structure,
                        &ctx,
                        datatypes,
                        type_elements,
                        var_values,
                    );
                    match quant_node.quant_type {
                        QuantKind::UniQuant => {
                            ground_formula = &ground_formula & ground_child.clone()
                        }
                        QuantKind::ExQuant => {
                            ground_formula = &ground_formula | ground_child.clone()
                        }
                    }
                },
            );
            return ground_formula;
        }
        NodeEnum::Element(ElementNode::Bool(b)) => z3::ast::Bool::from_bool(&ctx, b.into()),
        e @ (NodeEnum::Agg(_)
        | NodeEnum::Ite(_)
        | NodeEnum::Rule(_)
        | NodeEnum::Def(_)
        | NodeEnum::NumNeg(_)
        | NodeEnum::Element(_)) => unimplemented!("unimplemented: {:?}", e),
    }
}

// convenience function for numeric binary operations
fn numeric_bin_op<'a>(
    left: &Dynamic<'a>,
    right: &Dynamic<'a>,
    op: BinOps,
    ctx: &'a Context,
) -> Dynamic<'a> {
    let ints = match (left.sort_kind(), right.sort_kind(), op) {
        // force real division
        (_, _, BinOps::Divide) => None,
        (SortKind::Int, SortKind::Int, _) => {
            Some((left.as_int().unwrap(), right.as_int().unwrap()))
        }
        _ => None,
    };
    if let Some((left_int, right_int)) = ints {
        return match op {
            BinOps::Add => (left_int + right_int).into(),
            BinOps::Sub => (left_int - right_int).into(),
            BinOps::Mult => (left_int * right_int).into(),
            BinOps::Divide => (left_int / right_int).into(),
            BinOps::Rem => (left_int % right_int).into(),
            BinOps::And
            | BinOps::Or
            | BinOps::Impl
            | BinOps::Eqv
            | BinOps::Lt
            | BinOps::Le
            | BinOps::Gt
            | BinOps::Ge
            | BinOps::Eq
            | BinOps::Neq => todo!(),
        };
    }
    let reals = match (left.sort_kind(), right.sort_kind()) {
        (SortKind::Int, SortKind::Int) => Some((
            left.as_int().unwrap().to_real(),
            right.as_int().unwrap().to_real(),
        )),
        (SortKind::Int, SortKind::Real) => {
            Some((left.as_int().unwrap().to_real(), right.as_real().unwrap()))
        }
        (SortKind::Real, SortKind::Int) => {
            Some((left.as_real().unwrap(), right.as_int().unwrap().to_real()))
        }
        (SortKind::Real, SortKind::Real) => {
            Some((left.as_real().unwrap(), right.as_real().unwrap()))
        }
        _ => None,
    };
    if let Some((left_real, right_real)) = reals {
        return match op {
            BinOps::Add => (left_real + right_real).into(),
            BinOps::Sub => (left_real - right_real).into(),
            BinOps::Mult => (left_real * right_real).into(),
            BinOps::Divide => (left_real / right_real).into(),
            // We do this for remainder calculation of reals (this comes from rust std docs):
            // x - (x/y).trunc() * y
            // This in smtlib land means:
            // (- x (* (_round_to_zero (/x y)) y))
            // Where we implement _round_to_zero as
            // (ite (= (< x 0) (< x 0)) (to_int (/ x y)) (- (to_int (- (/ x y)))))
            BinOps::Rem => {
                let is_positive = left_real
                    .lt(&ast::Real::from_real(ctx, 0, 1))
                    ._eq(&right_real.lt(&ast::Real::from_real(ctx, 0, 1)));
                let round_to_zero = is_positive.ite(
                    &(&left_real / &right_real).to_int(),
                    &(-(-&(&left_real / &right_real)).to_int()),
                );
                (left_real - round_to_zero.to_real() * right_real).into()
            }
            BinOps::And
            | BinOps::Or
            | BinOps::Impl
            | BinOps::Eqv
            | BinOps::Lt
            | BinOps::Le
            | BinOps::Gt
            | BinOps::Ge
            | BinOps::Eq
            | BinOps::Neq => todo!(),
        };
    } else {
        panic!("Type mismatch");
    }
}

/// Translates a term to its smt equivalent, and returns it.
/// Terms are those types of expressions that represent something other than `true` or `false`.
/// Terms cannot stand on their own -- they need to be included in e.g. a comparison or as function
/// arguments. Examples of terms are type elements (Ints, Reals, ..) and functions.
pub fn term_to_smt<'a>(
    cur_expression: ExpressionRef<'a>,
    structure: &'a PartialStructure,
    ctx: &'a z3::Context,
    datatypes: &IdHashMap<TypeIndex, z3::DatatypeSort<'a>>,
    type_elements: &IdHashMap<TypeElementIndex, z3::ast::Dynamic<'a>>,
    var_values: &mut IdHashMap<BoundVarId, TypeEnum>,
) -> z3::ast::Dynamic<'a> {
    // Depending on the type of node, we generate different SMT.
    match cur_expression.first_node_enum() {
        NodeEnum::BinOps(BinOpNode {
            bin_op:
                bin_op @ (BinOps::Add | BinOps::Sub | BinOps::Mult | BinOps::Divide | BinOps::Rem),
            lhs,
            rhs,
            ..
        }) => {
            let left_child = term_to_smt(
                cur_expression.new_at(lhs),
                structure,
                &ctx,
                datatypes,
                type_elements,
                var_values,
            );
            let right_child = term_to_smt(
                cur_expression.new_at(rhs),
                structure,
                &ctx,
                datatypes,
                type_elements,
                var_values,
            );
            numeric_bin_op(&left_child, &right_child, bin_op, ctx)
        }
        NodeEnum::NumNeg(neg) => {
            // Negated formula. Quite straightforward.
            let child_id = neg.child;
            let child = term_to_smt(
                cur_expression.new_at(child_id),
                structure,
                &ctx,
                datatypes,
                type_elements,
                var_values,
            );
            if let Some(value) = child.as_int() {
                return value.unary_minus().into();
            } else if let Some(value) = child.as_real() {
                return value.unary_minus().into();
            } else {
                panic!("type mismatch!");
            }
        }
        NodeEnum::Element(ElementNode::Type(tel)) => {
            let type_interp = &structure.type_interps()[tel.element.0];
            match type_interp {
                TypeInterp::Int(_) => {
                    // Should be unreachable since Integers become an IntElement not a type element
                    unreachable!();
                }
                TypeInterp::Real(_) => {
                    // Should be unreachable since Reals become a RealElement not a type element
                    unreachable!();
                }
                TypeInterp::Custom(_) => {
                    return type_elements[&tel.element].clone();
                }
            }
        }
        NodeEnum::Agg(agg) => {
            match agg.aggregate_type {
                AggKind::Card => {
                    let mut ground_formula: Option<z3::ast::Int> = None;
                    cur_expression.expressions().iter_variables(
                        &agg.variables,
                        structure.type_interps(),
                        var_values,
                        |var_values| {
                            let ground_child = atom_to_smt(
                                cur_expression.new_at(agg.formula),
                                structure,
                                &ctx,
                                datatypes,
                                type_elements,
                                var_values,
                            );
                            if let Some(form) = &ground_formula {
                                // z3 rust does not allow adding booleans
                                let ite = ground_child
                                    .clone()
                                    .ite(&ast::Int::from_i64(ctx, 1), &ast::Int::from_i64(ctx, 0));
                                ground_formula = (form + ite).into();
                            } else {
                                ground_formula = ground_child
                                    .clone()
                                    .ite(&ast::Int::from_i64(ctx, 1), &ast::Int::from_i64(ctx, 0))
                                    .into();
                            }
                        },
                    );
                    if let Some(form) = ground_formula {
                        form.into()
                    } else {
                        ast::Int::from_i64(ctx, 0).into()
                    }
                }
                AggKind::Sum => {
                    let mut ground_formula: Option<z3::ast::Dynamic> = None;
                    cur_expression.expressions().iter_variables(
                        &agg.variables,
                        structure.type_interps(),
                        var_values,
                        |var_values| {
                            let ground_child = term_to_smt(
                                cur_expression.new_at(agg.formula),
                                structure,
                                &ctx,
                                datatypes,
                                type_elements,
                                var_values,
                            );
                            if let Some(form) = &ground_formula {
                                ground_formula =
                                    numeric_bin_op(form, &ground_child, BinOps::Add, ctx).into();
                            } else {
                                ground_formula = ground_child.into();
                            }
                        },
                    );
                    if let Some(form) = ground_formula {
                        form.into()
                    } else {
                        ast::Int::from_i64(ctx, 0).into()
                    }
                }
            }
        }
        NodeEnum::Element(ElementNode::Int(int)) => {
            let e = int.num;
            return z3::ast::Int::from_i64(&ctx, e as i64).into();
        }
        NodeEnum::Element(ElementNode::Real(real)) => z3::ast::Real::from_real_str(
            ctx,
            &real.real.inner_ref().numer().to_string(),
            &real.real.inner_ref().denom().to_string(),
        )
        .expect("Internal error")
        .into(),
        NodeEnum::Element(ElementNode::Quant(quant_el)) => {
            let enum_index = var_values[&quant_el.bound_var_id];
            let type_enum = quant_el.type_enum;
            let (type_interp, type_id) = match type_enum {
                Type::Str(a) | Type::IntType(a) | Type::RealType(a) => {
                    (&structure.type_interps()[a], a)
                }
                _ => unimplemented!("Quantification over {:?} is not implemented", type_enum),
            };
            match type_interp {
                TypeInterp::Custom(_) => {
                    return type_elements[&TypeElementIndex(type_id, enum_index)].clone();
                }
                TypeInterp::Int(i) => {
                    let x = i.get(&enum_index);
                    return z3::ast::Int::from_i64(&ctx, x as i64).into();
                }
                e => unimplemented!("unimplemented: {:?}", e),
            };
        }
        aps @ (NodeEnum::AppliedSymb(_) | NodeEnum::AppliedAuxSymb(_)) => {
            // Node is a constant or function, with the children as its arguments.
            // let value = appsymb.get_value(&theory.structure, var_values);
            let (value, codomain, name) = match &aps {
                NodeEnum::AppliedSymb(appsymb) => (
                    appsymb.get_value(structure, var_values),
                    appsymb.symbol().codomain,
                    func_name_from_appsymb(appsymb, structure, var_values),
                ),
                NodeEnum::AppliedAuxSymb(appsymb) => (
                    appsymb.get_value(cur_expression.expressions, var_values),
                    appsymb.symbol().codomain,
                    func_name_from_appauxsymb(appsymb, cur_expression.expressions, var_values),
                ),
                _ => unreachable!(),
            };
            // let applied_symb = theory.vocabulary.funcs(appsymb.index);

            if let Some(val) = value {
                return match val {
                    TypeElement::Bool(_) => unreachable!(),
                    TypeElement::Int(val) => ast::Int::from_i64(&ctx, val as i64).into(),
                    TypeElement::Real(val) => ast::Real::from_real_str(
                        ctx,
                        &val.inner_ref().numer().to_string(),
                        &val.inner_ref().denom().to_string(),
                    )
                    .expect("Internal error: unable to create Real")
                    .into(),
                    TypeElement::Custom(tei) => type_elements[&tei].clone().into(),
                };
            }
            // let name = func_name_from_appsymb(&appsymb, &theory.structure, var_values);
            // Find the codomain.
            match codomain {
                Type::Int | Type::IntType(_) => return ast::Int::new_const(&ctx, name).into(),
                Type::Real | Type::RealType(_) => return ast::Real::new_const(&ctx, name).into(),
                Type::Str(codomain_id) => {
                    return ast::Datatype::new_const(&ctx, name, &datatypes[&codomain_id].sort)
                        .into();
                }
                _ => {
                    todo! {"Constants on custom types are not yet implemented"}
                }
            }
        }
        NodeEnum::Ite(ite) => {
            let cond = atom_to_smt(
                cur_expression.new_at(ite.cond),
                structure,
                ctx,
                datatypes,
                type_elements,
                var_values,
            );
            let then_term = term_to_smt(
                cur_expression.new_at(ite.then_term),
                structure,
                ctx,
                datatypes,
                type_elements,
                var_values,
            );
            let else_term = term_to_smt(
                cur_expression.new_at(ite.else_term),
                structure,
                ctx,
                datatypes,
                type_elements,
                var_values,
            );
            cond.ite(&then_term, &else_term)
        }
        e @ (NodeEnum::Neg(_)
        | NodeEnum::Quant(_)
        | NodeEnum::Rule(_)
        | NodeEnum::Def(_)
        | NodeEnum::BinOps(_)
        | NodeEnum::Element(ElementNode::Bool(_))
        | NodeEnum::IsInt(_)) => unimplemented!("unimplemented: {:?}", e),
    }
}

#[cfg(test)]
mod tests {
    use super::parse_pfunc_name;
    use duplicate::duplicate_item;

    #[duplicate_item(
        test_name name exp;
        [parse_func_name_0] ["0-0"] [Ok((0.into(), 0.into()))];
        [parse_func_name_1] ["0-0-0"] [Err(())];
        [parse_func_name_2] ["dsfad0-0"] [Err(())];
        [parse_func_name_3] ["0-asfd"] [Err(())];
        // number too big
        [parse_func_name_4] ["18446744073709551617-0"] [Err(())];
        [parse_func_name_5] ["aux_4-0"] [Err(())];
    )]
    #[test]
    fn test_name() {
        assert_eq!(parse_pfunc_name(name), exp);
    }
}
