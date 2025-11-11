import pytest
from pdoc.doc import Module, Doc, Namespace
from typing import Generator, Iterable, NamedTuple, Self
import importlib
import sys


def iter_module(module: Module) -> Generator[Doc, None, None]:
    yield module
    for value in module.submodules:
        yield value
        yield from iter_module(value)
    for value in module.classes:
        yield value
        yield from iter_namespace(value)
    for value in module.functions:
        yield value
    for value in module.variables:
        yield value


def iter_namespace(namespace: Namespace) -> Generator[Doc, None, None]:
    for value in namespace.members.values():
        if isinstance(value, Namespace):
            yield from iter_namespace(value)
        else:
            yield value


class Doctest(NamedTuple):
    item: Doc
    doctest: str
    doctest_index: int

    @classmethod
    def gather_doctests(cls, doc: Doc) -> Generator[Self, None, None]:
        cur = 0
        count = 0
        BEGIN = "\n```python\n"
        END = "\n```"
        while True:
            begin = doc.docstring.find(BEGIN, cur)
            if begin < 0:
                break
            if begin + len(BEGIN) > len(doc.docstring):
                break
            end = doc.docstring.find(END, begin + len(BEGIN))
            if end < 0:
                break
            doctest = doc.docstring[begin + len(BEGIN) : end]
            cur = end
            yield cls(doc, doctest, count)
            count += 1

    def __str__(self) -> str:
        return f"{self.item.fullname}[{self.doctest_index}]"

    def __repr__(self) -> str:
        return f"<{self.item.fullname}[{self.doctest_index}]>"


def collect_docs(module: Module) -> Iterable[Doctest]:
    for item in iter_module(module):
        yield from Doctest.gather_doctests(item)


@pytest.mark.parametrize(
    "sli_lib_doc",
    collect_docs(Module(importlib.import_module("sli_lib"))),
    ids=map(
        lambda x: str(x),
        collect_docs(Module(importlib.import_module("sli_lib"))),
    ),
    scope="session",
)
def test_sli_lib_docs(sli_lib_doc: Doctest):
    print(sli_lib_doc.doctest, file=sys.stderr)
    exec(sli_lib_doc.doctest)
