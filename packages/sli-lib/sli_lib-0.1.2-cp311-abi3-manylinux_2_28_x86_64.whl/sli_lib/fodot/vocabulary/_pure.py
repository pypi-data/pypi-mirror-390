from ..._fodot.vocabulary import _bool, _int, _real, _parse_builtin_type  # type: ignore
from ..vocabulary import (
    BuiltinBool,
    BuiltinInt,
    BuiltinReal,
    IntType,
    RealType,
    StrType,
    Pfunc,
)
from enum import Enum, EnumType
from typing import TypeVar, Self, TypeAlias, Any
from abc import ABC


class ParseAble(ABC):
    @classmethod
    def parse(cls, _: str) -> Self: ... # type: ignore[empty-body]


_EnumMember = TypeVar("_EnumMember", bound=ParseAble)


class ParseAbleEnumType(EnumType, ParseAble):
    def __contains__(cls: type[_EnumMember], member: Any) -> bool: # type: ignore[misc]
        if isinstance(member, str):
            try:
                member = cls.parse(member)
            except ValueError:
                pass
        return super().__contains__(member) # type: ignore[misc]

    def __getitem__(cls: type[_EnumMember], name: str) -> _EnumMember: # type: ignore[misc]
        try:
            return super().__getitem__(name)  # type: ignore
        except KeyError:
            return cls.parse(name)


class BuiltinTypes(Enum, metaclass=ParseAbleEnumType):
    """
    An `enum.Enum` of builtin types available in all FO(·) vocabularies.

    Aquire the actual type values using the `value` attribute on the enum members.

    See also the python `Enum` documentation.

    # `__getitem__`

    Standard `__getitem__` behaviour on an `Enum` only recognizes the names of the enum members.
    This behaviour is extended to allow any string that can be parsed by `BuiltinTypes.parse`.

    ```python
    from sli_lib.fodot.vocabulary import BuiltinTypes
    assert BuiltinTypes.BOOL == BuiltinTypes["Bool"] == BuiltinTypes["𝔹"]
    ```

    # `__contains__`

    The behaviour of `__contains__` has been similarly extended to allow parseable strings.

    ```python
    from sli_lib.fodot.vocabulary import BuiltinTypes
    assert "Bool" in BuiltinTypes
    assert "𝔹" in BuiltinTypes
    ```
    """

    @classmethod
    def parse(cls, value: str) -> Self:
        """
        Parse the given value as a builtin type.
        """
        return cls(_parse_builtin_type(value))

    BOOL = _bool
    """
    Builtin `Bool` type in FO(·).

    This member is of type `BuiltinBool`.
    """
    INT = _int
    """
    Builtin `Int` type in FO(·).

    This member is of type `BuiltinInt`.
    """
    REAL = _real
    """
    Builtin `Real` type in FO(·).

    This member is of type `BuiltinReal`.
    """

    def __str__(self) -> str:
        return str(self.value)


BuiltinTypeAlias: TypeAlias = BuiltinTypes | BuiltinBool | BuiltinInt | BuiltinReal

Type: TypeAlias = BuiltinTypeAlias | IntType | RealType | StrType

CustomType: TypeAlias = IntType | RealType | StrType

ExtType: TypeAlias = Type | str

ExtCustomType: TypeAlias = CustomType | str

ExtPfunc: TypeAlias = Pfunc | str

__all__ = [
    "BuiltinTypes",
    "BuiltinTypeAlias",
    "Type",
    "CustomType",
    "ExtCustomType",
    "ExtType",
    "ExtPfunc",
]
