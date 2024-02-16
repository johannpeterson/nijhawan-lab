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
import itertools

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
parser.add_argument('--prefix', '-p', default=None,
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


def pad_primer(s, l, primer_name_regex):
    m = primer_name_regex.match(s)
    if m is not None:
      return m.group(1) + m.group(2).rjust(l, '0')
    else:
      return None

  
def all_equal(l):
    return all(i==l[0] for i in l)


def common_prefix(string_list):
    return ''.join(map(lambda l: l[0], itertools.takewhile(all_equal, zip(*string_list))))


def take_prefix(s):
    r=re.compile('^(.*?)[0-9]+$')
    m = r.match(s)
    if m:
        return m.group(1)
    else:
        return ''

    
def split_primer_name(s):
    r = re.compile('^(.*?)([0-9]+)$')
    m = r.match(s)
    if m:
        return (m.group(1), m.group(2))
    else:
        return ('','')


def infer_prefix(primer_list):
    return common_prefix(primer_list)


# ----------------------------------------------------------
# main
# ----------------------------------------------------------


def main():
    """main
    """
    csvraw = list(csv.reader(args.infile, delimiter='\t'))
    # ic(csvraw)
    col_headers = csvraw[0][1:]
    row_headers = [r[0] for r in csvraw[1:]]
    ic(col_headers, row_headers)
    split_list = list(map(split_primer_name, col_headers + row_headers))
    prefixes = [i[0] for i in split_list]
    suffixes = [i[1] for i in split_list]
    ic(prefixes, suffixes)
    suffix_length = max(map(len, suffixes))
    label_prefix = infer_prefix(prefixes)
    ic(suffix_length)
    ic(label_prefix)
    
    primer_name_regex_string = r"(" + label_prefix + ")(\d+)"
    primer_name_regex = re.compile(primer_name_regex_string)

    col_headers = [pad_primer(h, suffix_length, primer_name_regex) for h in col_headers]
    row_headers = [pad_primer(h, suffix_length, primer_name_regex) for h in row_headers]
    ic(col_headers, row_headers)
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
