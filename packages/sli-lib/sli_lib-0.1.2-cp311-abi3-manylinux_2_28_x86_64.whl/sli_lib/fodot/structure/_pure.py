from typing import TypeAlias, TypeVar, TypeGuard, Protocol, overload
from ...fodot.vocabulary import Real
from ..structure import (
    PfuncInterp, GlobModelPfuncInterp, ModelPfuncInterp,
    IntInterp, RealInterp, StrInterp, PfuncInterpIter,
    GlobModelPfuncInterpIter, ModelPfuncInterpIter
)

TypeElement: TypeAlias = bool | int | Real | str
ExtTypeElement: TypeAlias = TypeElement | float
ExtReal: TypeAlias = Real | int | float
TypeInterp: TypeAlias = IntInterp | RealInterp | StrInterp

T = TypeVar("T", bound=TypeElement, covariant=True)

class PfuncGeneric(Protocol[T]):
    """
    Private protocol for any generic class about pfunc interpretations.
    """
    def _py_codomain(self) -> type[T]: ...

@overload
def has_codomain(
    interp: PfuncInterp[TypeElement],
    codomain: type[T]
) -> TypeGuard[PfuncInterp[T]]:
    return issubclass(interp._py_codomain(), codomain)
@overload
def has_codomain(
    interp: GlobModelPfuncInterp[TypeElement],
    codomain: type[T]
) -> TypeGuard[GlobModelPfuncInterp[T]]:
    return issubclass(interp._py_codomain(), codomain)
@overload
def has_codomain(
    interp: ModelPfuncInterp[TypeElement],
    codomain: type[T]
) -> TypeGuard[ModelPfuncInterp[T]]:
    return issubclass(interp._py_codomain(), codomain)
@overload
def has_codomain(
    interp: PfuncInterpIter[TypeElement],
    codomain: type[T]
) -> TypeGuard[PfuncInterpIter[T]]:
    return issubclass(interp._py_codomain(), codomain)
@overload
def has_codomain(
    interp: GlobModelPfuncInterpIter[TypeElement],
    codomain: type[T]
) -> TypeGuard[GlobModelPfuncInterpIter[T]]:
    return issubclass(interp._py_codomain(), codomain)
@overload
def has_codomain(
    interp: ModelPfuncInterpIter[TypeElement],
    codomain: type[T]
) -> TypeGuard[ModelPfuncInterpIter[T]]:
    return issubclass(interp._py_codomain(), codomain)
def has_codomain(
    interp: PfuncGeneric[TypeElement],
    codomain: type[T]
) -> TypeGuard[PfuncGeneric[T]]:
    """
    Used for checking the type of the codomain of some pfunc related object.

    Returns true if `codomain` is a subclass of the pfunc's codomain, false otherwise.
    This function tells static type analyzers to narrow the type of the given class.
    Do note that this functions works with unions, but unions do not work for narrowing the type,
    this is a limitation of the python type system.

    # Example
     
    ```python
    from sli_lib.fodot.structure import (
        PfuncInterp, PfuncInterpIter,
        has_codomain,
    )
    from typing import reveal_type

    def pfunc_interp(p: PfuncInterp) -> None:
        if has_codomain(p, bool):
            # This will be `PfuncInterp[bool]` instead of `PfuncInterp[TypeElement]`
            reveal_type(p)

    def pfunc_interp_iter(p: PfuncInterpIter) -> None:
        if has_codomain(p, bool):
            # This will be `PfuncInterpIter[bool]` instead of `PfuncInterpIter[TypeElement]`
            reveal_type(p)
    ```

    """
    return issubclass(interp._py_codomain(), codomain)

__all__ = [
    "TypeElement",
    "ExtTypeElement",
    "ExtReal",
    "TypeInterp",
    "PfuncInterp",
    "has_codomain",
    "PfuncGeneric",
]
