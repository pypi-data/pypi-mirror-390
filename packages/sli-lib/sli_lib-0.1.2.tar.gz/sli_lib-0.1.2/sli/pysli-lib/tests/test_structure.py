from sli_lib.fodot import Vocabulary, Structure
from mypy import api
from sys import stdout, stderr
import pytest

def run_in_mypy(to_run: str) -> tuple[str, str, int]:
    ret = api.run(["-c", to_run])
    return ret

def test_incomplete_ops():
    vocab = Vocabulary("V").parse(
        """
        type A := {1,2,3}
        p: A * A -> Bool
        t: A * A -> A
        """)
    structure = Structure(vocab)
    t_decl = vocab.parse_pfunc("t")
    t = structure["t"]
    t = structure[t_decl]
    try:
        t.set((1,1), 4)
    except ValueError:
        pass
    try:
        t.set((1,1), True)
    except ValueError:
        pass
    assert not t.any_known()
    t.set((1,1), 1)
    A = vocab.parse_type("A")
    assert t.get(1,1) == t(1,1) == 1
    assert t.amount_known() == 1
    assert t.amount_unknown() == len(structure.get_type_interp("A"))**2 - 1
    assert t.amount_unknown() == len(structure.get_type_interp(A))**2 - 1
    t_iter = iter(t)
    t_iter2 = iter(t)
    assert next(t_iter) == ((1,1), 1)
    assert next(t_iter2) == ((1,1), 1)
    with pytest.raises(StopIteration):
        next(t_iter)
    with pytest.raises(StopIteration):
        next(t_iter2)

def test_type_narrowing():
    to_run = """
from sli_lib.fodot.structure import (
    has_codomain, PfuncInterp, GlobModelPfuncInterp, ModelPfuncInterp,
    GlobModel, Model
)
from sli_lib.fodot import Structure
from typing import assert_type

def a(structure: Structure) -> None:
    p = structure["p"]
    if has_codomain(p, bool):
        reveal_type(p)
        assert_type(p, PfuncInterp[bool])

def b(glob_model: GlobModel) -> None:
    p = glob_model["p"]
    if has_codomain(p, bool):
        reveal_type(p)
        assert_type(p, GlobModelPfuncInterp[bool])

def c(model: Model) -> None:
    p = model["p"]
    if has_codomain(p, bool):
        reveal_type(p)
        assert_type(p, ModelPfuncInterp[bool])
"""
    out, err, exit_code = run_in_mypy(to_run)
    print(out, file=stdout)
    print(err, file=stderr)
    assert exit_code == 0
