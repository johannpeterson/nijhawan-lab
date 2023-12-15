#! python3
"""compare_barcodes.py
   Script to compare the ranking of barcodes between two samples or analyses.

"""

import types
import sys
import argparse
import pandas as pd

try:
    from icecream import ic
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("-d", "--debug",
                    help="Enable debugging output", action="store_true")
parser.add_argument("-1", "--file1",
                    help="First table in TSV from.",
                    type=argparse.FileType('r'))
parser.add_argument("-2", "--file2",
                    help="Second table in TSV from.",
                    type=argparse.FileType('r'))
parser.add_argument("-f","--forward",
                    help="Tag for the forward primer.",
                    type=str)
parser.add_argument("-r","--reverse",
                    help="Tag for the reverse primer.",
                    type=str)
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
    table1 = pd.read_table(args.file1, sep='\t', header=0)
    table2 = pd.read_table(args.file2, sep='\t', header=0)
    column_names = {
        "fwd_primer": "forward_primer",
        "rev_primer": "reverse_primer",
        "frequency": "count",
        "count(barcode)": "count"
    }
    table1.rename(columns=column_names, errors='ignore', inplace=True)
    table2.rename(columns=column_names, errors='ignore', inplace=True)
    if args.debug:
        table1.to_csv(sys.stdout, sep='\t')
        table2.to_csv(sys.stdout, sep='\t')
    
    merge_table = pd.merge(table1, table2,
                           on=["forward_primer", "reverse_primer", "barcode"],
                           how='outer',
                           suffixes=('_1', '_2'),
                           indicator=True,
                           left_index=False,
                           right_index=False).convert_dtypes()
    if args.debug:
        merge_table.to_csv("merged_table.temp.tsv", sep='\t')
    merge_table["max_count"] = merge_table[["count_1", "count_2"]].max(axis=1)
    filtered_table = merge_table[
        (merge_table["forward_primer"]==args.forward) &
        (merge_table["reverse_primer"]==args.reverse)] \
        .copy() \
        .sort_values(by='max_count', ascending=False)
    filtered_table[["forward_primer", "reverse_primer", "barcode", "count_1", "count_2"]]. \
        to_csv(args.outfile, sep='\t', index=False)
    args.outfile.close()

    
if __name__ == '__main__':
    main()
