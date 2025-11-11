import sys
from sli_lib import sli_cli_main

if __name__ == "__main__":
    args = sys.argv
    args[0] = "python -m sli_lib"
    sli_cli_main(args, True, False)

