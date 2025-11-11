use rstest::rstest;
use sli_lib::{
    fodot::{error::GetRangeErrorKind, structure::TypeFull, theory::Theory},
    solver::{ModelResult, Solver, Z3Solver},
};

fn _check_get_range(idp_spec: &str) {
    let fodot_theory = Theory::from_specification(idp_spec).unwrap();
    let mut z3_solver = Z3Solver::initialize(&fodot_theory);
    let ModelResult::Sat(a_model) = z3_solver.check_get_model() else {
        panic!();
    };
    let Some(prop_struct) = z3_solver.propagate() else {
        panic!();
    };
    for pfunc in fodot_theory.structure().iter() {
        let pfunc_domain = pfunc.domain_full();
        for arg in pfunc_domain.iter_args_ref() {
            let set = match z3_solver.get_range(pfunc.decl_rc(), arg.clone()) {
                Ok(Some(value)) => value,
                Ok(None) => panic!("aaag"),
                Err(err) => match err.kind() {
                    GetRangeErrorKind::DomainMismatch(_)
                    | GetRangeErrorKind::VocabMismatchError(_)
                    | GetRangeErrorKind::TypeInterpsMismatchError(_) => panic!("aaah"),
                    GetRangeErrorKind::InfiniteCodomainError(_) => continue,
                },
            };
            let model_pfunc = a_model.as_ref().get(pfunc.decl());
            let codomain_len = match model_pfunc.codomain_full() {
                TypeFull::Bool => 2,
                TypeFull::Int => unreachable!(),
                TypeFull::Real => unreachable!(),
                TypeFull::IntType(i) => i.interp().len(),
                TypeFull::RealType(i) => i.interp().len(),
                TypeFull::Str(i) => i.interp().len(),
            };
            let value = model_pfunc.get(arg.clone()).unwrap();
            match value {
                Some(pfunc_value) => {
                    for i in &set {
                        let value = i.get(0);
                        assert_ne!(pfunc_value, value)
                    }
                    // we can only be sure that the only possibly true value is the one in the
                    // model if it existed before we asked the solver (or if we propagate)
                    if fodot_theory
                        .structure()
                        .get(pfunc.decl())
                        .get(arg.clone())
                        .unwrap()
                        .is_some()
                        || prop_struct
                            .get(pfunc.decl())
                            .get(arg.clone())
                            .unwrap()
                            .is_some()
                    {
                        assert_eq!(set.cardinality(), codomain_len.saturating_sub(1));
                    }
                }
                None => assert_eq!(set.cardinality(), 0),
            }
        }
    }
}

#[rstest]
fn consistency(
    #[files("tests/test_files/**/*.idp")]
    #[mode = str]
    idp_spec: &str,
) {
    _check_get_range(idp_spec);
}
