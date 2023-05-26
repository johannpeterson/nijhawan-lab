#! python3

import argparse
import os
import csv
import itertools
import types
import regex
import importlib.util
from Bio import SeqIO

try:
    from icecream import ic
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

parser = argparse.ArgumentParser(description='Count regex matches in a FASTQ file.')
parser.add_argument("pattern_file", help="Regex pattern strings in Python syntax.")
parser.add_argument("FASTQ_file", help="FASTQ file to read")
parser.add_argument("-l", "--limit", help="Stop after reading LIMIT pairs of reads", type=int, default=None)
parser.add_argument("-d", "--debug", help="Enable debugging output", action="store_true")
parser.add_argument("-o", "--out", help="Write a table (tsv) of the named groups matching each line.", type=argparse.FileType('w'), default=None)
parser.add_argument("-s", "--stats", help="Output statistics including match counts.", action="store_true")
parser.add_argument("--seq", help="Write the sequences to stdout.", action="store_true")
parser.add_argument("-v", "--verbose", help="Verbose - very.", action="store_true")

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

    ic(args.pattern_file)
    file_path = os.path.abspath(args.pattern_file)
    ic(file_path)
    (_, tail) = os.path.split(args.pattern_file)
    (module_name, _) = os.path.splitext(tail)
    ic(module_name)
    sequences_spec = importlib.util.spec_from_file_location(
        module_name,
        file_path)
    sequences_module = importlib.util.module_from_spec(sequences_spec)
    ic(dir(sequences_module))
    sequences_spec.loader.exec_module(sequences_module)
    sequences = importlib.import_module("sequences")
    ic(sequences.patterns)

    # compile regular expressions
    regexes = {k: regex.compile(sequences.patterns[k])
               for k in sequences.patterns.keys()}
    match_counts = {k: 0 for k in sequences.patterns.keys()}
    column_names = [group_name for r in regexes.values()
                    for group_name in r.groupindex.keys()]
    row_count = 0

    # set up table writer for writing regex match groups
    if args.out is not None:
        ic('Write to the file {}'.format(args.out))
        tableWriter = csv.DictWriter(
            args.out,
            fieldnames=column_names,
            delimiter='\t',
            restval='',
            extrasaction='ignore'
        )
        tableWriter.writeheader()
    else:
        tableWriter = lambda x: None

    ic(regexes)
    ic(match_counts)

    # read FASTQ file and attempt to match all regular expressions
    with open(args.FASTQ_file, "rt") as fq_file:
        reads1 = SeqIO.parse(fq_file, "fastq")
        for read in itertools.islice(reads1, args.limit):
            match_groups = {name:None for name in column_names}
            seq = str(read.seq)
            if args.seq:
                print(seq)
            row_count += 1
            for label, r in regexes.items():
                m = r.search(seq)
                if args.verbose:
                    ic(r)
                if m:
                    match_counts[label] += 1
                    for group_name, group_value in m.groupdict().items():
                        match_groups[group_name] = group_value
            # ic(match_groups)
            if args.out:
                tableWriter.writerow(match_groups)

    if args.out is not None:
        args.out.close()

    if args.stats:
        stats_table = {'total rows': row_count, **match_counts}
        for k, v in stats_table.items():
            stats_table[k] = str(v)
        column_1_width = max(map(len, stats_table.keys()))
        column_2_width = max(map(len, stats_table.values()))
        for k, v in stats_table.items():
            print('{key:<{padding_1}} {value:>{padding_2}}'.format(
                key=k,
                value=v,
                padding_1=column_1_width,
                padding_2=column_2_width
            ))


if __name__ == '__main__':
    main()
