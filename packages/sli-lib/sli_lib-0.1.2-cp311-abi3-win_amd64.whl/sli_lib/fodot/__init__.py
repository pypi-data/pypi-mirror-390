"""
Module containing methods and data structures for representing FO(·).

# Re-exports

- `.vocabulary.Vocabulary`
- `.structure.Structure`
- `.theory.Theory`
- `.theory.Assertions`

"""

from . import theory as theory
from . import structure as structure
from . import vocabulary as vocabulary

from .vocabulary import Vocabulary as Vocabulary
from .structure import Structure as Structure
from .theory import Theory as Theory, Assertions as Assertions

__all__ = [
    "theory",
    "structure",
    "vocabulary",
    "Vocabulary",
    "Structure",
    "Theory",
    "Assertions",
]
