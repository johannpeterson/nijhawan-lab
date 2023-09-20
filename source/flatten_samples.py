#! python3
"""flatten_samples.py
Script to take a 2-dimensional samples.tsv table and convert to
a table with columns fwd_primer, rev_primer, sample.

"""

import types
import sys
import argparse
import re
import csv

try:
    from icecream import ic
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("-d", "--debug",
                    help="Enable debugging output",
                    action="store_true", default=False)
parser.add_argument("infile", nargs='?',
                    help="File to read from;  stdin if not provided.",
                    type=argparse.FileType('r'), default=sys.stdin)
parser.add_argument("outfile", nargs='?',
                    help="File to write to;  stdout if not provided.",
                    type=argparse.FileType('w'), default=sys.stdout)
parser.add_argument('--prefix', '-p', default='oVK',
                    help="Primer name prefix, e.g. oVK.")
parser.add_argument('--all', '-a', action='store_true', default=False,
                    help="Write a row for every pair of primers, even if the name is blank.")
parser.add_argument('--noheader', action='store_true', default=False,
                    help="Write a header row.")
# parser.add_argument...

args = parser.parse_args()

if not isinstance(ic, types.FunctionType):
    if args.debug:
        ic.enable()
        ic.configureOutput(includeContext=True)
    else:
        ic.disable()
ic(args)

label_prefix = args.prefix
primer_name_regex_string = r"(" + label_prefix + ")(\d{1,3})"
primer_name_regex = re.compile(primer_name_regex_string)

def pad_primer(s):
    m = primer_name_regex.match(s)
    if m is not None:
      return m.group(1) + m.group(2).rjust(3, '0')
    else:
      return None

  
# ----------------------------------------------------------
# main
# ----------------------------------------------------------


def main():
    """main
    """
    csvraw = list(csv.reader(args.infile, delimiter='\t'))
    col_headers = [pad_primer(h) for h in csvraw[0][1:]]
    row_headers = [pad_primer(row[0]) for row in csvraw[1:]]
    data = [row[1:] for row in csvraw[1:]]
    sample_list = [s for sublist in data for s in sublist if s != '']

    sample_dict = {row_headers[r]:{col_headers[c]:'' for c in range(len(col_headers))}
                   for r in range(0, len(row_headers))}
        
    for r in range(len(row_headers)):
        for c in range(0,len(col_headers)):
            try:
                sample_dict[row_headers[r]][col_headers[c]]=data[r][c]
            except:
                pass
                
    writer = csv.writer(args.outfile, delimiter='\t', lineterminator='\n')
    if not args.noheader:
        writer.writerow(['fwd_primer','rev_primer','sample'])
    for fwd_primer in sample_dict:
        for rev_primer in sample_dict[fwd_primer]:
            row=[fwd_primer,rev_primer,sample_dict[fwd_primer][rev_primer]]
            if ((sample_dict[fwd_primer][rev_primer] != '') | args.all):
                ic(row)
                writer.writerow(row)
    args.outfile.close()
                
if __name__ == '__main__':
    main()
