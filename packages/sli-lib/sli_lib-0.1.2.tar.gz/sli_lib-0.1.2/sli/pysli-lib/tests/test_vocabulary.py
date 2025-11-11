from sli_lib.fodot.vocabulary import Vocabulary, BuiltinTypes
from sli_lib.fodot.structure import StrInterp
import pytest

def test_add_type():
    vocab = Vocabulary("V")
    vocab.add_type("T1")
    vocab.add_type("T2")
    T1 = vocab.parse_type("T1")
    vocab.add_voc_type_interp(T1, StrInterp(["a", "b", "c"]))
    with pytest.raises(ValueError):
        vocab.add_voc_type_interp("T2", StrInterp(["a", "b", "c"]))
    vocab2 = Vocabulary("V")
    vocab2.add_type("T2")
    T12 = vocab2.parse_type("T2")
    with pytest.raises(ValueError):
        vocab.add_voc_type_interp(T12, StrInterp(["d", "e", "f"]))
    vocab.add_voc_type_interp("T2", StrInterp(["d", "e", "f"]))

def test_add_pfunc():
    vocab = Vocabulary("V")
    vocab.add_type("T")
    vocab.add_pfunc("p", (), "Bool")
    with pytest.raises(TypeError):
        vocab.add_pfunc(2, (), "Bool") # type: ignore
    with pytest.raises(TypeError):
        vocab.add_pfunc(("ttt", 4), (), "Bool")  # type: ignore
    vocab.add_pfunc((f"p{i}" for i in range(5)), (), "Int")
    vocab.add_pfunc((f"t{i}" for i in range(5)), ("T" for _ in range(3)), "Int")
    T = vocab.parse_type("T")
    vocab.add_pfunc("w", (T, T), BuiltinTypes.INT)
    vocab2 = Vocabulary("T")
    vocab2.add_type("T")
    T2 = vocab2.parse_type("T")
    with pytest.raises(ValueError):
        vocab.add_pfunc("T", (T2,), "Bool")
    vocab.add_pfunc("o", (), BuiltinTypes.BOOL)
