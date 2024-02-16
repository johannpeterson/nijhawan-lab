#! python3
"""Extract regular expressions from a primers file.

The primers file should contain four columns in tab-separated
format.  The first column should be the label for the primer,
the second the full DNA sequence.  The fourth column should
contain the character 'F' or 'R' for foward or reverse.
"""

import argparse
import os
import sys
import csv
import types
import regex
from jpbio.util import rcDNA, common_sequence, sequence_to_regex

try:
    from icecream import ic
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("primer_file", help="Table of primer sequences.")
parser.add_argument("-d", "--debug",
                    help="Enable debugging output", action="store_true")
parser.add_argument("-p", "--patterns",
                    help="Write patterns to the output file instead of to stderr.",
                    type=argparse.FileType('w'), nargs='?',
                    default=sys.stderr)
parser.add_argument("-m", "--matches",
                    help="Specify a file to write a table of matching groups.",
                    type=argparse.FileType('w'), nargs='?',
                    default=sys.stdout)
parser.add_argument("-s", "--sed",
                    help="Specify a file to write sed commands to, for replacing tags in FASTQ files.",
                    type=argparse.FileType('w'), default=None)
parser.add_argument("--distances",
                    help="(not functioning) Write a table of Hamming distances between unique matching groups.",
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


def dict_to_regex(d):
    """Return a regex for replacing the tag in modified FASTQ file
    written by count_regex.py.  E.g. seq_fwd_1=TACCTTG -> oVK790.
    The dictionary passed in should have a 'name' key and one other
    key named, for example, 'seq_fwd_1'."""
    d_copy = d.copy()
    d_copy.pop('pattern', None)
    replacement_str = d_copy.pop('name')
    search_list = [k + '=' + v for k, v in d_copy.items() if k != 'pattern']
    search_str = ':'.join(search_list)
    return "s/{}/{}/".format(search_str, replacement_str)


def primer_matches(primer_regex, primer_seq, primer_label='', pattern_label=''):
    """Return a dict of the name for the primer (e.g. oVK043)
    along with the specific strings matching the groups in
    the regex.
    """
    matches = {'pattern': pattern_label, 'name': primer_label}
    re_match = regex.match(primer_regex, primer_seq)
    if re_match:
        matches.update(re_match.groupdict())
        return matches
    return None


def main():
    """Main script function.
    Read the table of primers, compute the consensus sequence and
    matching regex.
    """
    # read primers file
    ic(args.primer_file)
    file_path = os.path.abspath(args.primer_file)
    ic(file_path)

    primers = []
    with open(args.primer_file, newline='') as primers_io:
        primer_reader = csv.DictReader(
            primers_io,
            delimiter='\t',
            fieldnames=['OriginalSeq', 'sequence', 'barcode', 'direction'])
        for primer in primer_reader:
            primers.append(dict(primer))

    primer_lookup = {p['OriginalSeq']:
                     {'len': len(p['sequence']),
                      'sequence': p['sequence'],
                      'direction': p['direction']
                      } for p in primers}
    ic(primer_lookup)

    forward_primer_sequences = [primer_lookup[K]['sequence']
                                for K in primer_lookup
                                if primer_lookup[K]['direction'] == 'F']
    reverse_primer_sequences = [primer_lookup[K]['sequence']
                                for K in primer_lookup
                                if primer_lookup[K]['direction'] == 'R']

    patterns = {}
    patterns['SEQ_FWD'] = sequence_to_regex(
        common_sequence(forward_primer_sequences),
        name="seq_fwd_"
    )
    patterns['SEQ_REV'] = sequence_to_regex(
        common_sequence(reverse_primer_sequences),
        name="seq_rev_"
    )
    patterns['SEQ_FWD_RC'] = sequence_to_regex(
        rcDNA(common_sequence(forward_primer_sequences)),
        name="seq_fwd_rc_"
    )
    patterns['SEQ_REV_RC'] = sequence_to_regex(
        rcDNA(common_sequence(reverse_primer_sequences)),
        name="seq_rev_rc_"
    )

    # Write the list of patterns matching each set of primers.
    pattern_list = ["\t\'{}\': \"{}\"".format(k, v) for k, v in patterns.items()]
    print("patterns = {", file=args.patterns)
    print(",\n".join(pattern_list), file=args.patterns)
    print("}", file=args.patterns)
    # if args.out:
    #     args.out.close()

    # Compile the table of strings matching each group in the regexes
    # for every primer.
    if args.matches:
        matches = []
        for pattern in ['SEQ_FWD', 'SEQ_REV', 'SEQ_FWD_RC', 'SEQ_REV_RC']:
            matches.extend([primer_matches(patterns[pattern],
                                           primer_lookup[K]['sequence'],
                                           K, pattern_label=pattern)
                            for K in primer_lookup]
                           )
            matches.extend([primer_matches(patterns[pattern],
                                           rcDNA(primer_lookup[K]['sequence']),
                                           K, pattern_label=pattern)
                            for K in primer_lookup]
                           )
            match_table = [i for i in matches if i is not None]
            field_names = ['name', 'pattern']
            for m in match_table:
                for k in m.keys():
                    if k not in field_names:
                        field_names.append(k)
                        ic(match_table)
                        ic(field_names)

        match_writer = csv.DictWriter(args.matches, field_names, dialect="excel-tab")
        match_writer.writeheader()
        match_writer.writerows(match_table)

        for d in match_table:
            ic(dict_to_regex(d))
        # args.matches.close()
        if args.sed:
            for d in match_table:
                args.sed.write(dict_to_regex(d) + '\n')
            args.sed.close()

    if args.distances:
        fwd_matches = []
        rev_matches = []
        fwd_matches.extend([primer_matches(patterns['SEQ_FWD'],
                                           primer_lookup[K]['sequence'],
                                           K, pattern_label='SEQ_FWD')
                            for K in primer_lookup if primer_lookup[K]['direction'] == 'F'])
        rev_matches.extend([primer_matches(patterns['SEQ_REV'],
                                           primer_lookup[K]['sequence'],
                                           K, pattern_label='SEQ_REV')
                            for K in primer_lookup if primer_lookup[K]['direction'] == 'R'])
        ic(fwd_matches, rev_matches)
        fwd_match_dict = {}
        rev_match_dict = {}
        for e in fwd_matches:
            if e is not None:
                fwd_match_dict[e['name']] = ''.join([e[k] for k in e if k not in ['name', 'pattern']])
        for e in rev_matches:
            if e is not None:
                rev_match_dict[e['name']] = ''.join([e[k] for k in e if k not in ['name', 'pattern']])
        ic(fwd_match_dict, rev_match_dict)


if __name__ == '__main__':
    main()
