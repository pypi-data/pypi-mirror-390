from sli_lib.fodot import Theory
from sli_lib.solver import Z3Solver
import pytest

def test_z3_solver():
    theory  = Theory.from_specification("""
vocabulary {
    type T := { 0, 1 }
    p: T -> Bool
    t: T -> T
}
theory {
    !x in T: p(x) => t(x) = x.
}
structure {}
""")
    solver = Z3Solver(theory)
    assert solver.check()
    solver_iter = solver.iter_models()
    solver_iter.disable_skip_infinite()
    solver_iter.enable_skip_infinite()
    next(solver_iter)
    solver.check()
    with pytest.raises(RuntimeError):
        next(solver_iter)
    solver_iter = solver.iter_glob_models()
    for _ in solver_iter:
        pass
    assert not solver.check()
