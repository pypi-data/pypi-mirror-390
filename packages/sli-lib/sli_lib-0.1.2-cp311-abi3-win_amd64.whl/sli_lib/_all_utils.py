from typing import Iterable, List, Any
from itertools import chain


def filter__all__(value: Iterable[str]) -> List[str]:
    return list(
        filter(
            lambda x: not x.startswith("_"),
            iter(value),
        )
    )


def merge__all__(*args: Iterable[str]) -> List[str]:
    return list(chain(*args))

def rename_module(all: Iterable[Any], local_values: dict, new_name: str) -> None:
    for type in all:
        try:
            local_values[type].__module__ = new_name
        except AttributeError:
            pass
