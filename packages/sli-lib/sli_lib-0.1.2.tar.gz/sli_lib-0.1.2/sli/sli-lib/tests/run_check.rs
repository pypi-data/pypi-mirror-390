use rstest::rstest;
use sli_lib::{
    fodot::{
        structure::Precision,
        theory::{Assertion, Theory},
    },
    solver::{InterpMethod, SatResult, Solver, SolverIter, Z3Solver},
};

const MAX_MODELS: usize = 10;

fn expand_with_config(idp_spec: &str, interp_method: InterpMethod) {
    let fodot_theory = Theory::from_specification(idp_spec).unwrap();
    let mut z3_solver = Z3Solver::initialize_with(&fodot_theory, interp_method);
    let complete_model_iter = z3_solver.iter_models().complete();
    for model in complete_model_iter.take(MAX_MODELS) {
        let mut new_theory = fodot_theory.clone();
        _ = new_theory.set_structure(model.into_partial()).unwrap();
        let mut sat_set_interp =
            Z3Solver::initialize_with(&new_theory, InterpMethod::SatisfyingSetInterp);
        for (pos, expr) in fodot_theory.assertions().iter().enumerate() {
            // TODO if satisfying set transform is ever capable of simplifying def remove this
            if !matches!(expr, Assertion::Definition(_)) {
                if let Some(simpl) = sat_set_interp.has_been_simplified(pos) {
                    println!("{}: simplified: {}", expr, simpl);
                    assert!(simpl);
                } else {
                    panic!("unsimplified non-definition assertion")
                }
            }
        }
        assert!(matches!(sat_set_interp.check(), SatResult::Sat));
        let mut naive_interp = Z3Solver::initialize_with(&new_theory, InterpMethod::NaiveInterp);
        assert!(matches!(naive_interp.check(), SatResult::Sat));
        let mut no_interp = Z3Solver::initialize_with(&new_theory, InterpMethod::NoInterp);
        assert!(matches!(no_interp.check(), SatResult::Sat));
    }
}

fn propagate_with_config(idp_spec: &str, interp_method: InterpMethod) {
    // Run propagation, generate a model, and check whether the result of the propagation is a
    // subset of the model.
    let fodot_theory = Theory::from_specification(idp_spec).unwrap();
    let mut z3_solver = Z3Solver::initialize_with(&fodot_theory, interp_method);
    let prop_result = z3_solver.propagate().unwrap();
    let model = z3_solver.get_model().unwrap();
    assert!(prop_result.is_less_precise(model.as_ref()));
}

#[rstest]
fn check_expand_sat_set(
    #[files("tests/test_files/**/*.idp")]
    #[files("tests/unsat_test_files/**/*.idp")]
    #[mode = str]
    idp_spec: &str,
) {
    expand_with_config(idp_spec, InterpMethod::SatisfyingSetInterp);
}

#[rstest]
fn check_expand_naive(
    #[files("tests/test_files/**/*.idp")]
    #[files("tests/unsat_test_files/**/*.idp")]
    #[mode = str]
    idp_spec: &str,
) {
    expand_with_config(idp_spec, InterpMethod::NaiveInterp);
}

#[rstest]
fn check_expand_no_reduc(
    #[files("tests/test_files/**/*.idp")]
    #[files("tests/unsat_test_files/**/*.idp")]
    #[mode = str]
    idp_spec: &str,
) {
    expand_with_config(idp_spec, InterpMethod::NoInterp);
}

#[rstest]
fn check_prop_sat_set(
    #[files("tests/test_files/**/*.idp")]
    #[mode = str]
    idp_spec: &str,
) {
    propagate_with_config(idp_spec, InterpMethod::SatisfyingSetInterp);
}

#[rstest]
fn check_prop_naive_(
    #[files("tests/test_files/**/*.idp")]
    #[mode = str]
    idp_spec: &str,
) {
    propagate_with_config(idp_spec, InterpMethod::NaiveInterp);
}

#[rstest]
fn check_prop_no_reduc(
    #[files("tests/test_files/**/*.idp")]
    #[mode = str]
    idp_spec: &str,
) {
    propagate_with_config(idp_spec, InterpMethod::NoInterp);
}
