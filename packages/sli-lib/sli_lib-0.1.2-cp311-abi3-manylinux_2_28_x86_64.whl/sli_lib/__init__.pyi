from typing import overload, NoReturn, Literal, Iterable

@overload
def sli_cli_main(
    args: Iterable[str],
    do_exit: Literal[False]=...,
    add_name: bool=...,
    abort_on_sig_int: bool=...,
) -> int: ...
@overload
def sli_cli_main(
    args: Iterable[str],
    do_exit: Literal[True],
    add_name: bool=...,
    abort_on_sig_int: bool=...,
) -> NoReturn: ...
@overload
def sli_cli_main(
    args: Iterable[str],
    do_exit: bool=False,
    add_name: bool=True,
    abort_on_sig_int: bool=True,
) -> int: ...
