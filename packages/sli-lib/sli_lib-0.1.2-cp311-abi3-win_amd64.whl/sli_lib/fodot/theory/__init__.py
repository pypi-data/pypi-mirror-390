from ..._fodot.theory import *
from ..._fodot import theory
from ..._all_utils import filter__all__, rename_module

__all__ = filter__all__(theory.__all__)

# patch __module__ of everything to this module
rename_module(__all__, locals(), __name__)
