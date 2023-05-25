#! python3

import argparse
import os
import csv
import types
from jpbio.util import rcDNA, common_sequence, sequence_to_regex

try:
    from icecream import ic
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

parser = argparse.ArgumentParser(
    description='Generate regular expressions for the forward & reverse primer sequences.')
parser.add_argument("primer_file", help="Table of primer sequences.")
parser.add_argument("-d", "--debug",
                    help="Enable debugging output", action="store_true")
parser.add_argument("-o", "--out",
                    help="Write a table (tsv) of the named groups matching each line.",
                    type=argparse.FileType('w'),
                    default=None)
parser.add_argument("-v", "--verbose", help="Verbose - very.",
                    action="store_true")

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

    # read patterns file

    ic(args.primer_file)
    file_path = os.path.abspath(args.primer_file)
    ic(file_path)

    primers = []
    with open(args.primer_file, newline='') as primers_IO:
        primer_reader = csv.DictReader(
            primers_IO,
            delimiter='\t',
            fieldnames=['OriginalSeq', 'sequence', 'barcode', 'direction'])
        for primer in primer_reader:
            primers.append(dict(primer))

    # forward_primers = [p['OriginalSeq'] for p in primers if p['direction'] == 'F']
    # reverse_primers = [p['OriginalSeq'] for p in primers if p['direction'] == 'R']

    primer_lookup = {p['OriginalSeq']:
                     {'len': len(p['sequence']),
                      'sequence': p['sequence'],
                      'direction': p['direction']
                      } for p in primers}

    forward_primer_sequences = [primer_lookup[K]['sequence']
                                for K in primer_lookup
                                if primer_lookup[K]['direction'] == 'F']
    reverse_primer_sequences = [primer_lookup[K]['sequence']
                                for K in primer_lookup
                                if primer_lookup[K]['direction'] == 'R']

    patterns = {}
    patterns['SEQ_FWD'] = sequence_to_regex(
        common_sequence(forward_primer_sequences))
    patterns['SEQ_REV'] = sequence_to_regex(
        common_sequence(reverse_primer_sequences))
    patterns['SEQ_FWD_RC'] = sequence_to_regex(
        rcDNA(common_sequence(forward_primer_sequences)))
    patterns['SEQ_REV_RC'] = sequence_to_regex(
        rcDNA(common_sequence(reverse_primer_sequences)))

    print(patterns)


if __name__ == '__main__':
    main()
