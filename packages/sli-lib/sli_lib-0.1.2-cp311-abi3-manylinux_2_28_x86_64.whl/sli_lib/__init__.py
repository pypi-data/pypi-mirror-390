"""

# Introduction

sli-lib is a library for manipulating and using the FO(·) language using the rust sli-lib library.
sli-lib contains two major parts the `fodot` module for representing and manipulating FO(·) and the `solver` module for executing inference tasks on FO(·) theories.

# `fodot`

The `fodot` module contains three modules `vocabulary`, `theory` and `structure`.
Each containing datastructures and method for representing FO(·) constructs for vocabularies, theories and structures respectively.

# `solver`

In the `solver` module, solver implementations can be found and used with a `Theory` object from `fodot.theory`.
Each solver implements some inference tasks over this theory such as, satisfiability check, model expansion, back-bone propagation, ...

# Example

```python
from sli_lib.fodot import Vocabulary, Structure, Assertions, Theory
from sli_lib.fodot.structure import StrInterp
from sli_lib.solver import Z3Solver

# Create a vocabulary
vocab = Vocabulary("V")
vocab.add_type("Node")
vocab.add_type("Color")
vocab.add_pfunc("edge", ("Node", "Node"), "Bool")
vocab.add_pfunc("colorOf", ("Node",), "Color")
# Create some assertions
assertions = Assertions(vocab)
assertions.parse("!x, y in Node: edge(x, y) => colorOf(x) ~= colorOf(y).")
# Create a structure
struct = Structure(vocab)
struct.set_type_interp("Node", StrInterp(f"a{i}" for i in range(20)))
struct.set_type_interp("Color", StrInterp(["red", "green", "blue"]))
# Add some edges to struct
edge = struct["edge"]
for args in [
    ("a1", "a2"),
    ("a1", "a3"),
    ("a3", "a2"),
    ("a1", "a4"),
    ("a2", "a4"),
    ("a3", "a4"),
]:
    edge.set(args, True)
edge.set_all_unknown_to_value(False)
# Put our assertions and structure together in a Theory and ask for satisfiability from Z3Solver
theory = Theory(assertions, struct)
solver = Z3Solver(theory)
assert not solver.check() # this instance of graph colouring is unsatisfiable
```

# Free threading support

sli-lib does not rely on the Python global interpreter lock.
As such it fully supports free threaded Python.
Just like the builtin Python types, the sli-lib types, where needed, add locks to prevent memory unsafety and data races.
Do note that this requires building the api explicitly targeting free-threaded python.

"""

from .sli_lib import * # type: ignore[import-not-found]
from . import fodot as fodot
from . import solver as solver

def script_main():
    import sys
    sli_cli_main(sys.argv, True, False)

# Keep this up to date manually
__all__ = [
    "fodot",
    "solver",
]
