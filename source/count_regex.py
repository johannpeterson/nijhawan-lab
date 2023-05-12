#! python3
from Bio import Seq, SeqIO, Align
import argparse, os
#import gzip
import csv
import itertools
import regex
import importlib.util
import sys
import types

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
# main loop
# ----------------------------------------------------------
    
def main():

    ic(args.pattern_file)
    file_path = os.path.abspath(args.pattern_file)
    ic(file_path)
    (head, tail) = os.path.split(args.pattern_file)
    (module_name,_) = os.path.splitext(tail)
    ic(module_name)
    sequences_spec = importlib.util.spec_from_file_location(module_name, file_path)
    sequences_module = importlib.util.module_from_spec(sequences_spec)
    ic(dir(sequences_module))
    sequences_spec.loader.exec_module(sequences_module)
    sequences = importlib.import_module("sequences")
    ic(sequences.patterns)

    regexes = {k:regex.compile(sequences.patterns[k]) for k in sequences.patterns.keys()}
    match_counts = {k:0 for k in sequences.patterns.keys()}
    column_names = [group_name for r in regexes.values() for group_name in r.groupindex.keys()]
    row_count=0

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
            #ic(match_groups)
            if args.out:
                tableWriter.writerow(match_groups)
                
    if args.out is not None:
        args.out.close()

    if args.stats:
        column_width = max( map(len, match_counts.keys())) + 2
        print('{key:<{padding}}{value:>6}'.format(key='total rows', value=row_count, padding=column_width))
        for k,v in match_counts.items():
            print('{key:<{padding}}{value:>6}'.format(key=k, value=v, padding=column_width))
            
if __name__ == '__main__':
    main()
