#! python3
"""Count matches for a list of regular expressions in a FASTQ file.

count_regex.py takes as input a pattern_file, containing a python dict
of pattern names mapped to regular expressions, and a FASTQ file.
"""

import argparse
import sys
import csv
from itertools import count, islice
import types
import regex
from Bio import SeqIO

try:
    from icecream import ic
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("fastq_file", nargs='?',
                    help="FASTQ file to read, or stdin if not provided.",
                    type=argparse.FileType('r'), default=sys.stdin)
parser.add_argument("-p", "--patterns",
                    type=argparse.FileType('r'), default=None, action="append", required=True,
                    help="Regex pattern strings in Python syntax.  Multiple files can be specified.")
parser.add_argument("-l", "--limit", help="Stop after reading LIMIT pairs of reads",
                    type=int, default=None)
parser.add_argument("-d", "--debug", help="Enable debugging output", action="store_true")
parser.add_argument("-o", "--out",
                    help="Write a table (tsv) of the named groups matching each line.",
                    type=argparse.FileType('w'), default=None)
parser.add_argument("-f", "--fastq_out", help="Output FASTQ file with annotations.",
                    type=argparse.FileType('w'), default=None)
parser.add_argument("-s", "--stats", help="Output statistics including match counts.",
                    action="store_true")
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


def print_table(table, out_file=sys.stdout):
    """Print a simple dictionary with uniform column widths."""
    for k, v in table.items():
        table[k] = str(v)
    column_1_width = max(map(len, table.keys()))
    column_2_width = max(map(len, table.values()))
    for k, v in table.items():
        print('{key:<{padding_1}} {value:>{padding_2}}'.format(
            key=k,
            value=v,
            padding_1=column_1_width,
            padding_2=column_2_width
        ), file=out_file)


def import_patterns(pattern_file):
    """Read the file object passed and return the 'patterns' object.
    File should be valid python code.  Uses exec."""
    pattern_imports = {}
    exec(pattern_file.read(), pattern_imports, pattern_imports)
    return pattern_imports["patterns"]


def format_dict(d):
    """Format the dictionary of regex matches for writing to the
    FASTQ sequence identifier line."""
    return ":".join([k + '=' + d[k] for k in d if d[k] is not None])


def parse_fastq_id(s):
    """Parse the sequence identifier line from FASTQ reads.
    return as a dictionary.
    Illumina FASTQ id format:
    @<instrument>:<run number>:<flowcell ID>:<lane>:<tile>:<x-pos>:<y-pos> <read>:<is filtered>:<control number>:<sample number>"""
    instrument, runid, flowcellid, lane, tile, x, y = s.id.split(':')
    return {
        "instrument": instrument,
        "runid": runid,
        "flowcellid": flowcellid,
        "lane": lane,
        "tile": tile,
        "x": x,
        "y": y
    }

   
def main():
    """main
    Read the patterns file(s).  Loop throuth the FASTQ file
    and count matches for each regular expression in the patterns.
    """

    # read patterns file
    ic(args.patterns)
    patterns = {}
    for patterns_file in args.patterns:
        patterns.update(import_patterns(patterns_file))

    # compile regular expressions
    regexes = {k: regex.compile(v)
               for k, v in patterns.items()}
    match_counts = {k: 0 for k in patterns}
    column_names = [group_name for r in regexes.values()
                    for group_name in r.groupindex.keys()]

    # set up table writer for writing regex match groups
    if args.out is not None:
        ic('Write to the file {}'.format(args.out))
        table_writer = csv.DictWriter(
            args.out,
            fieldnames=column_names,
            delimiter='\t',
            restval='',
            extrasaction='ignore'
        )
        table_writer.writeheader()
    else:
        table_writer = lambda x: None

    ic(regexes)
    ic(match_counts)

    # read FASTQ file and attempt to match all regular expressions
    reads = SeqIO.parse(args.fastq_file, "fastq")
    for read, row_count in zip(islice(reads, args.limit), count(start=0)):
        match_groups = {name: None for name in column_names}
        seq = str(read.seq)
        for label, re in regexes.items():
            re_match = re.search(seq)
            if args.verbose:
                ic(re)
            if re_match:
                match_counts[label] += 1
                for group_name, group_value in re_match.groupdict().items():
                    match_groups[group_name] = group_value
                # ic(match_groups)
        if args.seq:
            print(seq)
            print(parse_fastq_id(read))
            print(format_dict(match_groups))
        if args.fastq_out:
            read.id = read.id + ":" + format_dict(match_groups)
            # read.description = format_dict(match_groups)
            read.description = ""
            args.fastq_out.write(read.format("fastq"))
        if args.out:
            table_writer.writerow(match_groups)

    if args.out is not None:
        args.out.close()

    if args.stats:
        print_table({'total rows': row_count, **match_counts})


if __name__ == '__main__':
    main()
