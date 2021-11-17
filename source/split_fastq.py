#! python3
from Bio import Seq, SeqIO, Align
import argparse, os
import gzip
import csv
import itertools

from jpbio import primers
from jpbio import MultiStream

try:
    from icecream import ic
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

#yesChoices = ["true","t","yes","y"]
#noChoices = ["false","f","no","n"]

parser = argparse.ArgumentParser(description='Split paired FASTQ files by primers.')
parser.add_argument("R1_filename", help="FASTQ file 1")
parser.add_argument("R2_filename", help="FASTQ file 2")
parser.add_argument("primer_filename", help="Primers file.")
parser.add_argument("-l", "--limit", help="Stop after reading LIMIT pairs of reads", type=int, default=None)
parser.add_argument("-r", "--rejected", help="Output read pairs that do not pass sanity checks (default no)", action="store_true")
parser.add_argument("-u", "--unassigned", help="Output read pairs that are not assigned to a group (default no)", action="store_true")
parser.add_argument("-d", "--debug", help="Enable debugging output", action="store_true")
parser.add_argument("-q", "--quality", help="Minimum base call quality for matching regions (default 0).", type=int, default=0)
#parser.add_argument("-r", "--rejected", help="Output read pairs that do not pass sanity checks (default no).", type=str.lower, choices=yesChoices + noChoices, default="no")
#parser.add_argument("-u", "--unassigned", help="Output read pairs that are not assigned to a group (default no).", type=str.lower, choices=yesChoices + noChoices, default="no")
args = parser.parse_args()

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
    primer_table = primers.PrimerTable(args.primer_filename)
    base_tags = ["A", "B", "C"]
    tags = [b + "_" + d for b in base_tags for d in ["R1", "R2"]]
    streams = MultiStream.MultiStream(
        tags=tags,
        prefix="test",
        extension="fastq",
        directory="temp"
        )
    streams.open()
    base_tags = itertools.cycle(base_tags)

    with open(args.R1_filename, "rt") as R1, open(args.R2_filename, "rt") as R2: # need to accomodate gzip or regular files
        reads1 = SeqIO.parse(R1, "fastq")
        reads2 = SeqIO.parse(R2, "fastq")
        for (read1, read2, readNumber) in itertools.islice( zip(reads1, reads2, itertools.count(1)), args.limit):
            tag = next(base_tags)
            R1_out = tag + "_" + "R1"
            R2_out = tag + "_" + "R2"
            R1_stream = streams.getStream(R1_out)
            R2_stream = streams.getStream(R2_out)
            SeqIO.write(read1, R1_stream, "fastq")
            SeqIO.write(read2, R2_stream, "fastq")
            # print(read1)
            # print(read2)

    streams.close()

if __name__ == '__main__':
    main()
