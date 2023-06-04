#! python3
"""Template for python shell script.

"""

import types
import sys
import argparse

try:
    from icecream import ic
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("infile", nargs='?',
                    help="File to read from;  stdin if not provided.",
                    type=argparse.FileType('r'), default=sys.stdin)
parser.add_argument("outfile", nargs='?',
                    help="File to write to;  stdout if not provided.",
                    type=argparse.FileType('w'), default=sys.stdout)
# parser.add_argument...

args = parser.parse_args()

if not isinstance(ic, types.FunctionType):
    if args.debug:
        ic.enable()
        ic.configureOutput(includeContext=True)
    else:
        ic.disable()
ic(args)


# ----------------------------------------------------------
# main
# ----------------------------------------------------------


def main():
    """main
    """


if __name__ == '__main__':
    main()
