#! python3
from Bio import Seq, SeqIO, Align
import argparse, os
#import gzip
#import csv
import itertools
import regex
import importlib.util
import sys
import types

try:
    from icecream import ic
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

#Yeschoices = ["true","t","yes","y"]
#noChoices = ["false","f","no","n"]

parser = argparse.ArgumentParser(description='Count regex matches in a FASTQ file.')
parser.add_argument("pattern_file", help="Regex pattern strings in Python syntax.")
parser.add_argument("FASTQ_file", help="FASTQ file to read")
#parser.add_argument("primer_filename", help="Primers file.")
parser.add_argument("-l", "--limit", help="Stop after reading LIMIT pairs of reads", type=int, default=None)
#parser.add_argument("-r", "--rejected", help="Output read pairs that do not pass sanity checks (default no)", action="store_true")
#parser.add_argument("-u", "--unassigned", help="Output read pairs that are not assigned to a group (default no)", action="store_true")
parser.add_argument("-d", "--debug", help="Enable debugging output", action="store_true")
#parser.add_argument("-q", "--quality", help="Minimum base call quality for matching regions (default 0).", type=int, default=0)
#parser.add_argument("-r", "--rejected", help="Output read pairs that do not pass sanity checks (default no).", type=str.lower, choices=yesChoices + noChoices, default="no")
#parser.add_argument("-u", "--unassigned", help="Output read pairs that are not assigned to a group (default no).", type=str.lower, choices=yesChoices + noChoices, default="no")
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
    match_counts = {k:0 for k in sequences.patterns.keys() }

    ic(regexes)
    ic(match_counts)
    
    with open(args.FASTQ_file, "rt") as fq_file:
        reads1 = SeqIO.parse(fq_file, "fastq")
        for read in itertools.islice(reads1, args.limit):
            match_groups = {group_name:'' for r in regexes.values() for group_name in list(r.groupindex.keys())}
            seq = str(read.seq)
            # print(seq)
            for label, r in regexes.items():
                m = r.match(seq)
                if m:
                    match_counts[label] += 1
                    for group_name, group_value in m.groupdict().items():
                        match_groups[group_name] = group_value
                        # print(group_name + ": " + group_value)
            print(match_groups)
                

    print(match_counts)
            
if __name__ == '__main__':
    main()
