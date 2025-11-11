from sli_lib.fodot import Vocabulary, Assertions, Theory, Structure, structure
from sli_lib.solver import Z3Solver

def test_simple_theory():
    vocab = Vocabulary("V")
    vocab.add_type("A")
    vocab.add_pfunc("p", "A", "Bool")
    struct = Structure(vocab)
    struct.set_type_interp("A", structure.StrInterp(["a","b","c"]))
    assertions = Assertions(vocab)
    assertions.parse(
    """
        !x in A: p(x).
    """)
    theory = Theory(assertions, struct)
    z3_solver = Z3Solver(theory)
    assert z3_solver.check()
    model = z3_solver.get_model()
    assert model is not None
    assert model["p"].amount_known() == len(struct.get_type_interp("A"))

