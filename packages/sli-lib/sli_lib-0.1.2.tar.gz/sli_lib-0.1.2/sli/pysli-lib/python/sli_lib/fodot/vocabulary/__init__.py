from ..._fodot.vocabulary import *
from ..._fodot import vocabulary

# Don't enumerate each thing we want to import here do it in __init__.pyi
from ._pure import *
from . import _pure
from ..._all_utils import filter__all__, merge__all__, rename_module

__all__ = merge__all__(
    filter__all__(vocabulary.__all__),
    _pure.__all__,
)

# patch __module__ of everything to this module
rename_module(__all__, locals(), __name__)
