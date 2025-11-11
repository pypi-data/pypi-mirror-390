from mypy import api
from sys import stderr, stdout

def test_typing():
    out, err, exit_code = api.run(["--disallow-untyped-defs", "-p", "sli_lib"])
    print(out, file=stdout)
    print(err, file=stderr)
    assert exit_code == 0
