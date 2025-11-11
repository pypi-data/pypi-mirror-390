"""

# Subscripting (`__getitem__`)

All structure like classes (`Structure`, `GlobModel`, ...) can be subscripted (`structure["p"]`) with an `..vocabulary.ExtPfunc` to acquire the interpretation of that pfunc, or raise an exception if this pfunc doesn't exist in the vocabulary or the structure.
"""

from ..._fodot.structure import *
from ..._fodot import structure

# Don't enumerate each thing we want to import here do it in __init__.pyi
from ._pure import *
from . import _pure
from ..._all_utils import filter__all__, merge__all__, rename_module

__all__ = merge__all__(
    filter__all__(structure.__all__),
    _pure.__all__,
)

# patch __module__ of everything to this module
rename_module(__all__, locals(), __name__)
