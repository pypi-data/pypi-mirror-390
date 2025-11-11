use self::{
    def_transform::DefTransform,
    sli_exit::{create_pfunc_name, parse_pfunc_name},
};
use super::{InfiniteCodomainErr, InterpMethod, SatResult, Solver, TimeMeasurements, Timings};
use crate::{
    DiscreteInt,
    comp_core::{
        self, IndexRange, IndexRepr, Int, Real,
        constraints::{ParsedConstraints, TransformedConstraints},
        node::{BoolElement, ElementNode, NodeEnum},
        structure::{
            GlobModel, IntInterp, PartialStructure, RealInterp, StrInterp, TypeElement, TypeFull,
            backend::complete_interp::owned::Pred, domain_enum_of_element_iter,
        },
        vocabulary::{Domain, DomainEnum, PfuncIndex, Type, TypeElementIndex, TypeIndex},
    },
    interp_structures::InterpContext,
    transform::{
        ConstraintTransformer, naive_transform::NaiveTransform,
        satisfying_set_transform::SatisfyingSetTransform,
    },
};

use duplicate::duplicate_item;
use sli_collections::hash_map::IdHashMap;
use sli_collections::rc::Rc;
use std::{
    fmt::Debug,
    mem::{MaybeUninit, transmute},
    pin::Pin,
    ptr::addr_of_mut,
    str::FromStr,
};
use z3::{
    DatatypeSort, SortKind,
    ast::{Ast, Dynamic},
};

mod def_transform;
mod sli_exit;
pub use def_transform::validate_expr;
use sli_exit::{atom_to_smt, generate_datatypes, generate_type_constraint};

/// This struct bundles a [z3::Solver] and a [z3::Context].
/// Doing this is not trivial since [z3::Solver] contains a reference to [z3::Context].
/// As such this is a self referential struct. In order to avoid segmentation faults we have to make sure
/// all instances of this struct a re pinned, since a datastructure wrapped in [Pin] is not able to
/// move in memory. One must construct a [SolverCtx] using [`SolverCtx::new`](method@SolverCtx::new).
/// Without unsafe it is not possible to construct a SolverCtx using struct instantiation. If you
/// were to force this using unsafe the program will crash due to a segmentation fault if the
/// struct were to be used.
#[derive(Debug)]
struct SolverCtx {
    // Has to be first otherwise we get a segmentation fault when trying to drop solver since
    // context has already been dropped
    solver: z3::Solver<'static>,
    _context: z3::Context,
}

impl std::ops::Deref for SolverCtx {
    type Target = z3::Solver<'static>;

    fn deref(&self) -> &Self::Target {
        &self.solver
    }
}

impl std::ops::DerefMut for SolverCtx {
    fn deref_mut(&mut self) -> &mut Self::Target {
        &mut self.solver
    }
}

impl SolverCtx {
    pub fn new(config: z3::Config) -> Pin<Box<Self>> {
        let mut uninit: Pin<Box<MaybeUninit<Self>>> = Box::pin(MaybeUninit::uninit());
        let ptr = uninit.as_mut_ptr();

        let context = z3::Context::new(&config);
        // write context to uninit SolverCtx
        unsafe { addr_of_mut!((*ptr)._context).write(context) };

        // create z3::Solver using ptr from uninit SolverCtx
        let solver = z3::Solver::new(unsafe { &(*ptr)._context });
        unsafe { addr_of_mut!((*ptr).solver).write(solver) };

        // assume struct is initialized
        unsafe { transmute(uninit) }
    }
}

pub struct Z3Solver<'a> {
    // fodot_theory: &'a Theory<'a>,
    constraints: Rc<ParsedConstraints>,
    structure: &'a PartialStructure,
    instantiated: TransformedConstraints,
    /// Maps the type index of String types on their Z3 equivalent datatypes, which is required to create new Z3 constants.
    datatypes: IdHashMap<TypeIndex, DatatypeSort<'a>>,
    /// Maps type elements of String types on their Z3 equivalent AST node.
    type_elements: IdHashMap<TypeElementIndex, Dynamic<'a>>,
    solver: Pin<Box<SolverCtx>>,
}

// Safety:
// We don't pass any Z3 pointer out of this struct and according to
// https://github.com/Z3Prover/z3/issues/4762#issuecomment-718570133 as long as one thread acts on
// only one context at a time it is safe.
// Any calls to z3 are behind mutable references ensuring only one thread accesses it at a time.
unsafe impl<'a> Sync for Z3Solver<'a> {}
unsafe impl<'a> Send for Z3Solver<'a> {}

#[derive(Debug)]
enum Z3SortConvertError {
    TooBig,
    NoValueGiven,
    TypeMismatch,
    UnkownValue,
}

impl TypeElement {
    fn from_z3_dynamic<'a>(
        value: Dynamic<'a>,
        type_e: TypeFull,
    ) -> Result<TypeElement, Z3SortConvertError> {
        match (value.sort_kind(), type_e) {
            (SortKind::Bool, TypeFull::Bool) => {
                let value = value
                    .as_bool()
                    .ok_or(Z3SortConvertError::TypeMismatch)?
                    .as_bool()
                    .ok_or(Z3SortConvertError::NoValueGiven)?;
                Ok(TypeElement::Bool(value))
            }
            (SortKind::Int, TypeFull::Int | TypeFull::IntType(_)) => {
                let val: comp_core::Int = value
                    .as_int()
                    .unwrap()
                    .as_i64()
                    .ok_or(Z3SortConvertError::NoValueGiven)?
                    .try_into()
                    .or(Err(Z3SortConvertError::TooBig))?;
                Ok(TypeElement::Int(val))
            }
            (SortKind::Datatype, TypeFull::Str((i, interp))) => {
                let datatype_value = &value
                    .as_datatype()
                    .ok_or(Z3SortConvertError::TypeMismatch)?
                    .to_string();
                let trimmed_value = datatype_value.trim_matches('|');
                let type_enum = IndexRepr::from_str(&trimmed_value)
                    .map_err(|_| Z3SortConvertError::UnkownValue)?
                    .into();
                debug_assert!(interp.contains(&type_enum));
                Ok(TypeElement::Custom(TypeElementIndex(i, type_enum)))
            }
            (SortKind::Real, TypeFull::Real | TypeFull::RealType(_)) => {
                let value = &value.as_real().ok_or(Z3SortConvertError::TypeMismatch)?;
                if let Some((denom, num)) = value.as_real() {
                    Real::from_fraction(
                        denom.try_into().expect("Number too big!"),
                        num.try_into().expect("Number too big!"),
                    )
                    .map(|f| f.into())
                    .ok_or(Z3SortConvertError::UnkownValue)
                } else {
                    let val = value.approx(10);
                    let real = if val.chars().last() == Some('?') {
                        Real::from_str(&val[0..val.len() - 1])
                    } else {
                        Real::from_str(&val)
                    }
                    .map_err(|_| Z3SortConvertError::UnkownValue)?;
                    Ok(real.into())
                }
            }
            _ => Err(Z3SortConvertError::TypeMismatch),
        }
    }
}

impl<'a> Debug for Z3Solver<'a> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.solver.solver)
    }
}

impl<'a> Z3Solver<'a> {
    pub fn get_smtlib(&mut self) -> String {
        format!("{:?}", self.solver.solver)
    }

    pub fn get_statistics(&mut self) -> z3::Statistics {
        self.solver.get_statistics()
    }

    fn interpret_with(
        constraints: &'a ParsedConstraints,
        structure: &'a PartialStructure,
        interp_method: InterpMethod,
    ) -> TransformedConstraints {
        match interp_method {
            InterpMethod::SatisfyingSetInterp => {
                let satset_transformed = ConstraintTransformer::new(SatisfyingSetTransform::new(
                    structure,
                    InterpContext::new(
                        constraints.get_expressions().get_type_map(),
                        structure.type_interps(),
                    ),
                ))
                .transform_formulas(constraints.formulas_iter());
                ConstraintTransformer::new(DefTransform::new())
                    .transform_formulas(satset_transformed.formulas_iter())
            }
            InterpMethod::NoInterp => ConstraintTransformer::new(DefTransform::new())
                .transform_formulas(constraints.formulas_iter()),
            InterpMethod::NaiveInterp => {
                let level_mapped = ConstraintTransformer::new(DefTransform::new())
                    .transform_formulas(constraints.formulas_iter());
                ConstraintTransformer::new(NaiveTransform::new(structure))
                    .transform_formulas(level_mapped.formulas_iter())
            }
        }
    }

    fn create_propagate_var_name(
        index: PfuncIndex,
        domain_enum: DomainEnum,
        codomain_num: usize,
    ) -> String {
        format!(
            "prop_{}_{}_{}",
            IndexRepr::from(index),
            IndexRepr::from(domain_enum),
            codomain_num
        )
    }

    // Note: we technically don't have to introduce a new proposition for these
    // symbols, but doing so seems easier for now. It should be trivial anyway for z3
    fn build_bool_propagate(
        &mut self,
        index: PfuncIndex,
        domain_enum: DomainEnum,
        func_var: &z3::ast::Bool<'a>,
    ) -> (z3::ast::Bool<'a>, z3::ast::Bool<'a>) {
        let prop_name = Self::create_propagate_var_name(index, domain_enum, 0);
        let prop_var = z3::ast::Bool::new_const(&self.solver.get_context(), prop_name);

        (prop_var.clone(), prop_var._eq(&func_var))
    }

    #[duplicate_item(
        function_name interp_type build_type_el return_ty func_var_ty;
        [build_inttype_propagate] [IntInterp]
            [
                z3::ast::Int::from_i64(
                    &self.solver.get_context(),
                    type_element.try_into().unwrap(),
                )
            ]
            [Int]
            [z3::ast::Int<'a>];
        [build_realtype_propagate] [RealInterp]
            [
                z3::ast::Real::from_real_str(
                    &self.solver.get_context(),
                    &type_element.inner_ref().numer().to_string(),
                    &type_element.inner_ref().denom().to_string(),
                ).unwrap()
            ]
            [Real]
            [z3::ast::Real<'a>];
    )]
    fn function_name<'b>(
        &'b self,
        index: PfuncIndex,
        codomain_interp: &'b interp_type,
        domain_enum: DomainEnum,
        func_var: &'b func_var_ty,
    ) -> impl Iterator<Item = (z3::ast::Bool<'a>, z3::ast::Bool<'a>, return_ty)> + 'b {
        codomain_interp
            .into_iter()
            .enumerate()
            .map(move |(j, type_element)| {
                let prop_name = Self::create_propagate_var_name(index, domain_enum, j);
                let prop_var = z3::ast::Bool::new_const(&self.solver.get_context(), prop_name);
                let el = build_type_el;
                let eq = &func_var._eq(&el);
                (prop_var.clone(), prop_var._eq(eq), type_element.clone())
            })
    }

    fn build_custom_propagate<'b>(
        &'b self,
        index: PfuncIndex,
        type_id: TypeIndex,
        codomain_interp: &'b StrInterp,
        domain_enum: DomainEnum,
        func_var: &'b z3::ast::Dynamic<'a>,
    ) -> impl Iterator<Item = (z3::ast::Bool<'a>, z3::ast::Bool<'a>, TypeElement)> + 'b {
        codomain_interp
            .into_iter()
            .enumerate()
            .map(move |(j, type_enum)| {
                let prop_name = Self::create_propagate_var_name(index, domain_enum, j);
                let prop_var = z3::ast::Bool::new_const(&self.solver.get_context(), prop_name);
                let type_element_index = TypeElementIndex(type_id, type_enum.into());
                let eq = &func_var._eq(self.type_elements.get(&type_element_index).unwrap());
                (
                    prop_var.clone(),
                    prop_var._eq(eq),
                    type_element_index.into(),
                )
            })
    }
}

impl<'a> Solver<'a> for Z3Solver<'a> {
    fn initialize_with_timing(
        constraints: Rc<ParsedConstraints>,
        structure: &'a PartialStructure,
        interp_method: InterpMethod,
        timings: &mut dyn Timings,
    ) -> Self
    where
        Self: Sized,
    {
        let transform_timer = timings.start(TimeMeasurements::Transform);
        let instantiated = Z3Solver::interpret_with(&constraints, structure, interp_method);
        let mut z3_solver = Z3Solver {
            constraints,
            structure,
            instantiated,
            datatypes: IdHashMap::default(),
            type_elements: IdHashMap::default(),
            solver: SolverCtx::new(z3::Config::new()),
        };
        transform_timer.end();
        let grounding_timer = timings.start(TimeMeasurements::Grounding);
        let mut all = Some(true);
        for a in z3_solver.instantiated.formulas_iter() {
            let val = match a.first_node_enum() {
                NodeEnum::Element(ElementNode::Bool(BoolElement { value: true })) => Some(true),
                NodeEnum::Element(ElementNode::Bool(BoolElement { value: false })) => Some(false),
                _ => None,
            };
            if let (Some(all_val), Some(val)) = (all, val) {
                all = Some(all_val && val);
            } else {
                all = None;
                break;
            }
        }
        let ctx = z3_solver.solver.get_context();
        if let Some(all) = all {
            z3_solver.solver.assert(&z3::ast::Bool::from_bool(ctx, all));
            return z3_solver;
        }

        let (datatypes, type_elements) = generate_datatypes(&structure, ctx);
        z3_solver.datatypes = datatypes;
        z3_solver.type_elements = type_elements;

        for node in z3_solver.instantiated.formulas_iter() {
            let mut var_values = Default::default();
            let formula = atom_to_smt(
                node,
                &structure,
                &ctx,
                &z3_solver.datatypes,
                &z3_solver.type_elements,
                &mut var_values,
            );
            z3_solver.solver.assert(&formula);
        }
        for pfunc_id in structure.vocab().iter_pfuncs() {
            let symb_interp = structure.get(pfunc_id);
            if matches!(symb_interp.codomain(), Type::Bool | Type::Int | Type::Real) {
                continue;
            }
            for domain_enum in symb_interp.domain().iter_index(structure.type_interps()) {
                if symb_interp.has_interp(domain_enum).unwrap() {
                    continue;
                }
                let type_contraint_opt = generate_type_constraint(
                    pfunc_id,
                    domain_enum,
                    &structure.type_interps(),
                    &z3_solver.datatypes,
                    ctx,
                );
                if let Some(type_con) = type_contraint_opt {
                    z3_solver.solver.assert(&type_con);
                }
            }
        }
        grounding_timer.end();
        z3_solver
    }

    fn initial_constraints(&self) -> &ParsedConstraints {
        &self.constraints
    }

    fn constraints(&self) -> &TransformedConstraints {
        &self.instantiated
    }

    fn check(&mut self) -> SatResult {
        match self.solver.check() {
            z3::SatResult::Sat => SatResult::Sat,
            z3::SatResult::Unsat => SatResult::Unsat,
            z3::SatResult::Unknown => SatResult::Unknown,
        }
    }

    fn get_model(&mut self) -> Option<GlobModel> {
        let model = self.solver.get_model();
        match model {
            Some(model) => {
                let mut structure = self.structure.clone();
                let type_interps = &self.structure.type_interps();
                for variable in model.iter() {
                    let (pfunc_index, args) = if let Ok(val) = parse_pfunc_name(&variable.name()) {
                        val
                    } else {
                        continue;
                    };
                    let value = match model.get_const_interp(&variable.apply(&[])) {
                        Some(x) => x,
                        _ => panic!("AaAaA"),
                    };
                    if structure.get(pfunc_index).has_interp(args).unwrap() {
                        continue;
                    }
                    let pfunc_codomain = structure
                        .vocab()
                        .pfuncs(pfunc_index)
                        .codomain
                        .with_interps(type_interps);
                    let type_element_val = TypeElement::from_z3_dynamic(value, pfunc_codomain)
                        .expect("Internal error");
                    structure
                        .get_mut(pfunc_index)
                        .set_i(args, Some(type_element_val));
                }
                Some(structure.into_glob_model(self.constraints.clone()))
            }
            None => None,
        }
    }

    fn next_model(&mut self) {
        let model = self.solver.get_model();
        match model {
            Some(model) => {
                let mut neg_model = z3::ast::Bool::from_bool(&self.solver.get_context(), true);
                for variable in model.iter() {
                    // TODO: test impact of including aux symbols on performance
                    if let Err(_) = parse_pfunc_name(&variable.name()) {
                        continue;
                    }
                    let value = match model.get_const_interp(&variable.apply(&[])) {
                        Some(x) => x,
                        _ => panic!("AaAaA"),
                    };

                    // Start building a formula representing the model, so that we can negate it
                    variable.apply(&[])._eq(&value);
                    neg_model = &neg_model & variable.apply(&[])._eq(&value);
                }
                self.solver.assert(&neg_model.not());
            }
            None => (),
        }
    }

    /// Propagate the consequences of a theory and structure.
    fn propagate(&mut self) -> Option<PartialStructure> {
        match self.check() {
            SatResult::Unsat => return None,
            SatResult::Unknown => panic!("Unknown sat"),
            SatResult::Sat => {}
        };
        let model = self.solver.get_model().unwrap();
        self.solver.push();

        // Propagation uses Z3's consequences API ([z3::solver::consequences]).
        // This method accepts a list of assumptions (propositions that are true) and a list of propositions to propagate.
        // Because we can only query propositions, we need to represent symbols of a higher arity
        // with a proposition for each pair of (domain enum, output value). For example, for a
        // function `color_of(Country) -> Color`, we would effectively generate the following:
        // * color_of(BE) = red <=> prop_0_0_0().
        // * color_of(BE) = blue <=> prop_0_0_1().
        // * color_of(NL) = red <=> prop_0_1_0().
        // * color_of(NL) = blue <=> prop_0_1_1().
        // * ...
        //
        // Exception: as we cannot enumerate all possible values of symbols with an infinite
        // codomain (Int, Real), we instead use the value of a model that was generated
        // before-hand.
        //
        // These auxiliary propositions are stored in a vector `vars` and given to the API.
        // We also maintain a `var_map` to map these propositions on the original symbol, which we
        // characterise as (PfuncIndex, DomainEnum, TypeElement).
        let mut var_map: IdHashMap<z3::ast::Bool, (PfuncIndex, DomainEnum, TypeElement)> =
            Default::default();
        let mut vars: Vec<z3::ast::Bool> = vec![];
        for usymbol in self
            .structure
            .vocab()
            .iter_symbols()
            .filter(|x| !self.structure.get(x.index).is_complete())
        {
            let symbol = usymbol.clone().with_interps(self.structure.type_interps());
            for dom_id in symbol.domain.iter_index(self.structure.type_interps()) {
                let func_name = create_pfunc_name(symbol.index, dom_id);
                match &symbol.codomain {
                    TypeFull::Bool => {
                        // Predicates and propositions
                        let func_var =
                            z3::ast::Bool::new_const(&self.solver.get_context(), func_name);
                        let (prop_var, eq) =
                            self.build_bool_propagate(symbol.index, dom_id, &func_var);
                        self.solver.assert(&eq);
                        vars.push(prop_var.clone());
                        var_map.insert(prop_var, (symbol.index, dom_id, TypeElement::Bool(true)));
                    }
                    // functions of various codomains
                    // We create a proposition for each possible output value.
                    TypeFull::IntType((_, interp)) => {
                        let func_var =
                            z3::ast::Int::new_const(self.solver.get_context(), func_name);
                        for (prop_var, eq, value) in
                            self.build_inttype_propagate(symbol.index, interp, dom_id, &func_var)
                        {
                            self.solver.assert(&eq);
                            vars.push(prop_var.clone());
                            var_map.insert(prop_var, (symbol.index, dom_id, value.into()));
                        }
                    }
                    TypeFull::RealType((_, interp)) => {
                        let func_var =
                            z3::ast::Real::new_const(self.solver.get_context(), func_name);
                        for (prop_var, eq, value) in
                            self.build_realtype_propagate(symbol.index, interp, dom_id, &func_var)
                        {
                            self.solver.assert(&eq);
                            vars.push(prop_var.clone());
                            var_map.insert(prop_var, (symbol.index, dom_id, value.into()));
                        }
                    }
                    TypeFull::Str((type_id, interp)) => {
                        let sort = &self.datatypes[&type_id].sort;
                        let func_var: z3::ast::Dynamic = z3::ast::Datatype::new_const(
                            &self.solver.get_context(),
                            func_name,
                            sort,
                        )
                        .into();
                        for (prop_var, eq, value) in self.build_custom_propagate(
                            symbol.index,
                            *type_id,
                            interp,
                            dom_id,
                            &func_var,
                        ) {
                            self.solver.assert(&eq);
                            vars.push(prop_var.clone());
                            var_map.insert(prop_var, (symbol.index, dom_id, value.into()));
                        }
                    }
                    TypeFull::Int => {
                        let func_var =
                            z3::ast::Int::new_const(&self.solver.get_context(), func_name);
                        let value = match model.get_const_interp(&func_var) {
                            Some(x) => x,
                            None => continue,
                        };
                        let prop_name = Self::create_propagate_var_name(symbol.index, dom_id, 0);
                        let prop_var =
                            z3::ast::Bool::new_const(&self.solver.get_context(), prop_name);
                        self.solver.assert(&prop_var._eq(&func_var._eq(&value)));

                        let type_element =
                            TypeElement::Int(value.as_i64().unwrap().try_into().unwrap());
                        vars.push(prop_var.clone());
                        var_map.insert(prop_var, (symbol.index, dom_id, type_element));
                    }
                    TypeFull::Real => {
                        let func_var =
                            z3::ast::Real::new_const(&self.solver.get_context(), func_name);
                        let value = match model.get_const_interp(&func_var) {
                            Some(x) => x,
                            None => continue,
                        };
                        let prop_name = Self::create_propagate_var_name(symbol.index, dom_id, 0);
                        let prop_var =
                            z3::ast::Bool::new_const(&self.solver.get_context(), prop_name);
                        self.solver.assert(&prop_var._eq(&func_var._eq(&value)));

                        let type_element = TypeElement::Real(Real::new(
                            value
                                .as_real()
                                .map(|f| {
                                    (
                                        DiscreteInt::try_from(f.0).expect("Too big!"),
                                        DiscreteInt::try_from(f.1).expect("Too big!"),
                                    )
                                })
                                .expect("Too big!")
                                .into(),
                        ));
                        vars.push(prop_var.clone());
                        var_map.insert(prop_var, (symbol.index, dom_id, type_element));
                    }
                }
            }
        }

        // Now we can propagate and expand our struct with the consequences.
        let mut new_struct = self.structure.clone();
        let consequences = self.solver.get_consequences(&[], &vars);
        for cons in consequences.iter() {
            // Consequences are of the form `(=> true prop_x)` or `(=> true not(prop_x))`.
            // Therefore, if the second child (`prop_x`) has a child of itself, it's value was
            // negatively derived. If the second child is a constant, it's value was positively
            // derived.
            let child = cons.nth_child(1).unwrap();
            let var_value = child.is_const();
            let var = match child.nth_child(0) {
                Some(x) => x,
                None => child,
            };
            let (func_index, dom_enum, type_element) = var_map[&var.as_bool().expect("oh no")];
            match (var_value, type_element) {
                (true, TypeElement::Bool(_)) => {
                    let _ = new_struct
                        .get_mut(func_index)
                        .set_i(dom_enum, Some(var_value.into()));
                }
                (false, TypeElement::Bool(_)) => {
                    let _ = new_struct
                        .get_mut(func_index)
                        .set_i(dom_enum, Some(var_value.into()));
                }
                (true, _) => {
                    let _ = new_struct
                        .get_mut(func_index)
                        .set_i(dom_enum, Some(type_element));
                }
                (false, _) => {} // We can ignore negative values for constants/functions, as
                                 // there is no support for false positives yet.
            }
        }
        self.solver.pop(1);
        Some(new_struct)
    }

    fn get_range(
        &mut self,
        pfunc: PfuncIndex,
        dom_id: DomainEnum,
    ) -> Result<Option<Pred>, InfiniteCodomainErr> {
        self.solver.push();

        // distilled version of propagate
        let mut var_map: IdHashMap<z3::ast::Bool, TypeElement> = Default::default();
        let mut vars: Vec<z3::ast::Bool> = vec![];
        let symbol = self.structure.vocab().pfuncs(pfunc);
        let codomain_array = Domain([symbol.codomain.clone()]);
        if matches!(symbol.codomain, Type::Int | Type::Real) {
            return Err(InfiniteCodomainErr);
        }
        // NOTE: change this if structures ever get cf functions
        if let Some(value) = self
            .structure
            .get(pfunc)
            .get(dom_id)
            .expect("valid argument")
        {
            if self.check().is_sat() {
                let mut pt = Pred::new();
                pt.set(
                    domain_enum_of_element_iter(
                        core::iter::once(value),
                        &codomain_array,
                        self.structure.type_interps(),
                    )
                    .unwrap(),
                    true,
                );
                pt.negate_over_range(IndexRange::new(
                    0..codomain_array.domain_len(self.structure.type_interps()),
                ));
                return Ok(Some(pt));
            } else {
                return Ok(None);
            }
        }
        let func_name = create_pfunc_name(symbol.index, dom_id);
        let codomain_full = symbol.codomain.with_interps(self.structure.type_interps());
        match codomain_full {
            TypeFull::Bool => {
                let func_var = z3::ast::Bool::new_const(&self.solver.get_context(), func_name);
                let (prop_var, eq) = self.build_bool_propagate(symbol.index, dom_id, &func_var);
                self.solver.assert(&eq);
                vars.push(prop_var.clone());
                var_map.insert(prop_var, true.into());
            }
            TypeFull::IntType((_, interp)) => {
                let func_var = z3::ast::Int::new_const(self.solver.get_context(), func_name);
                for (prop_var, eq, value) in
                    self.build_inttype_propagate(symbol.index, interp, dom_id, &func_var)
                {
                    self.solver.assert(&eq);
                    vars.push(prop_var.clone());
                    var_map.insert(prop_var, value.into());
                }
            }
            TypeFull::RealType((_, interp)) => {
                let func_var = z3::ast::Real::new_const(self.solver.get_context(), func_name);
                for (prop_var, eq, value) in
                    self.build_realtype_propagate(symbol.index, interp, dom_id, &func_var)
                {
                    self.solver.assert(&eq);
                    vars.push(prop_var.clone());
                    var_map.insert(prop_var, value.into());
                }
            }
            TypeFull::Str((type_id, interp)) => {
                let sort = &self.datatypes[&type_id].sort;
                let func_var: z3::ast::Dynamic =
                    z3::ast::Datatype::new_const(&self.solver.get_context(), func_name, sort)
                        .into();
                for (prop_var, eq, value) in
                    self.build_custom_propagate(symbol.index, type_id, interp, dom_id, &func_var)
                {
                    self.solver.assert(&eq);
                    vars.push(prop_var.clone());
                    var_map.insert(prop_var, value.into());
                }
            }
            _ => return Err(InfiniteCodomainErr),
        }

        let mut set = Pred::new();
        let consequences = self.solver.get_consequences(&[], &vars);
        for cons in consequences.iter() {
            let child = cons.nth_child(1).unwrap();
            let var_value = child.is_const();
            let var = match child.nth_child(0) {
                Some(x) => x,
                None => child,
            };
            let type_element = var_map[&var.as_bool().expect("oh no")];
            match (var_value, type_element) {
                (false, value) => set.insert(
                    domain_enum_of_element_iter(
                        core::iter::once(value),
                        &codomain_array,
                        self.structure.type_interps(),
                    )
                    .unwrap(),
                ),
                // ignore certainly true values, only if the symbol does not have a boolean
                // codomain
                (true, value) => {
                    if matches!(codomain_full, TypeFull::Bool) {
                        set.insert(
                            domain_enum_of_element_iter(
                                core::iter::once(value),
                                &codomain_array,
                                self.structure.type_interps(),
                            )
                            .unwrap(),
                        );
                        set.negate_over_range(IndexRange::new(0..2));
                        break;
                    }
                }
            }
        }
        self.solver.pop(1);
        Ok(Some(set))
    }
}
