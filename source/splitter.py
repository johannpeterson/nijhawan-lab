#! python3
from Bio import Seq, SeqIO, Align
import argparse, os
import gzip
import csv
import itertools
import re
from tabulate import tabulate

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
# sequence matching
# ----------------------------------------------------------

def findSubsequence(subSeq, fullSeq, min_quality=30):
    pos = fullSeq.seq.find(subSeq)
    while (pos < len(subSeq)) & (pos > -1):
        qualities = fullSeq.letter_annotations['phred_quality'][pos:pos+len(subSeq)]
        if all([q >= min_quality for q in qualities]):
            return (pos, qualities)
        pos = fullSeq.seq.find(subSeq, pos+1)
    return None

def findAllSubsequences(subSeq, fullSeq, min_quality=30):
    matches = []
    start_pos = 0
    max_pos = len(fullSeq)
    while ((start_pos < max_pos) & (start_pos > -1)):
        start_pos = fullSeq.seq.find(subSeq, start_pos)
        if start_pos > -1:
            quality = min(fullSeq.letter_annotations['phred_quality'][start_pos:start_pos + len(subSeq)])
            if quality > min_quality:
                matches.append({'position':start_pos, 'quality':quality})
            start_pos += 1
    return matches

def findBestSubsequence(subSeq, fullSeq, min_quality=30):
    best_match = {'position':-1, 'quality':-1}
    start_pos = 0
    max_pos = len(fullSeq)
    while ((start_pos < max_pos) & (start_pos > -1)):
        start_pos = fullSeq.seq.find(subSeq, start_pos)
        if start_pos > -1:
            quality = min(fullSeq.letter_annotations['phred_quality'][start_pos:start_pos + len(subSeq)])
            if quality > best_match['quality']:
                best_match['position'] = start_pos
                best_match['quality'] = quality
            start_pos += 1
    if best_match['quality'] >= min_quality:
        return best_match
    else:
        return None

# ----------------------------------------------------------
# file access
# ----------------------------------------------------------

def outputFilename(tag, suffix):
    return tag + "_" + suffix + ".fastq"

def readPrimers(primer_file):
    read_groups = {}
    with open(primer_file, newline='') as primers_IO:
        primer_reader = csv.DictReader(primers_IO,
                                       delimiter='\t',
                                       fieldnames=['tag','forward_primer','reverse_primer'])
        for primer in primer_reader:
            read_groups[primer['tag']] = {
                'forward_primer':primer['forward_primer'].upper(),
                'reverse_primer':primer['reverse_primer'].upper(),
                'read_count':0,
                'output_files':{
                    'R1':outputFilename(primer['tag'], 'R1'),
                    'R2':outputFilename(primer['tag'], 'R2')
                }
            }
        read_groups['unassigned'] = {'read_count':0, 'output_files':{'R1':None, 'R2':None}}
        read_groups['rejected'] = {'read_count':0, 'output_files':{'R1':None, 'R2':None}}
    ic(read_groups)
    return read_groups

def openGroupFiles(read_groups):
    ic(read_groups)
    for k in read_groups:
        if read_groups[k]['output_files']['R1'] != None:
            read_groups[k]['output_files']['R1'] = open(read_groups[k]['output_files']['R1'], "w")
        if read_groups[k]['output_files']['R2'] != None:
            read_groups[k]['output_files']['R2'] = open(read_groups[k]['output_files']['R2'], "w")
        
def closeGroupFiles(read_groups):
    ic(read_groups)
    for k in read_groups:
        try:
            read_groups[k]['output_files']['R1'].close()
            read_groups[k]['output_files']['R2'].close()
        except:
            pass

# ----------------------------------------------------------
# read check functions
# ----------------------------------------------------------

def readCheckIDsMatch(read1, read2):
    return read1.id == read2.id
       
# ----------------------------------------------------------
# group assignment functions
# ----------------------------------------------------------
        
def assignReadsToGroupRandomly(read1, read2, read_groups):
    return random.choice( list(read_groups.keys()) )

def assignReadsToGroupByForwardPrimer(read1, read2, read_groups, quality=30):
    best_match = {'quality':0, 'group':''}
    for group in read_groups:
        m = findBestSubsequence(read_groups[group]['forward_primer'],
                                read1, min_quality=quality)
        if m != None:
            if m['quality'] > best_match['quality']:
                best_match['quality'] = m['quality']
                best_match['group'] = group
    for group in read_groups:
        m = findBestSubsequence(read_groups[group]['forward_primer'],
                                read2, min_quality=quality)
        if m != None:
            if m['quality'] > best_match['quality']:
                best_match['quality'] = m['quality']
                best_match['group'] = group
    if best_match['quality'] != 0:
        return best_match['group']
    else:
        return None
    
def assignReadsToGroupByReversePrimer(read1, read2, read_groups, quality=30):
    best_match = {'quality':0, 'group':''}
    for group in read_groups:
        m = findBestSubsequence(read_groups[group]['reverse_primer'],
                                read1, min_quality=quality)
        if m != None:
            if m['quality'] > best_match['quality']:
                best_match['quality'] = m['quality']
                best_match['group'] = group
    for group in read_groups:
        m = findBestSubsequence(read_groups[group]['reverse_primer'],
                                read2, min_quality=quality)
        if m != None:
            if m['quality'] > best_match['quality']:
                best_match['quality'] = m['quality']
                best_match['group'] = group
    if best_match['quality'] != 0:
        return best_match['group']
    else:
        return None

# ----------------------------------------------------------
# main logic
# ----------------------------------------------------------
    
def main():
    read_groups = readPrimers(args.primer_filename)
    if args.rejected:
        read_groups['rejected']['output_files']['R1'] = outputFilename('rejected', 'R1')
        read_groups['rejected']['output_files']['R2'] = outputFilename('rejected', 'R2')
    if args.unassigned:
        read_groups['unassigned']['output_files']['R1'] = outputFilename('unassigned', 'R1')
        read_groups['unassigned']['output_files']['R2'] = outputFilename('unassigned', 'R2')
    
    prechecks = [readCheckIDsMatch]
    assignmentFunction = assignReadsToGroupByReversePrimer

    openGroupFiles(read_groups)
    ic(read_groups)
    with gzip.open(args.R1_filename, "rt") as R1, gzip.open(args.R2_filename, "rt") as R2:
        reads1 = SeqIO.parse(R1, "fastq")
        reads2 = SeqIO.parse(R2, "fastq")
        for (read1, read2, readNumber) in itertools.islice( zip(reads1, reads2, itertools.count(1)), args.limit):
            group = None
            if any([check(read1, read2)==False for check in prechecks]):
                group = 'rejected'
            else:
                group = assignReadsToGroupByReversePrimer(read1, read2, read_groups, quality=10)
            if group == None:
                group = 'unassigned'

            read_groups[group]['read_count'] += 1
        
            # output reads by group
            R1_file = read_groups[group]['output_files']['R1']
            R2_file = read_groups[group]['output_files']['R2']
            if ((R1_file != None) & (R2_file != None)):
                SeqIO.write(read1, R1_file, "fastq") 
                SeqIO.write(read2, R2_file, "fastq") 
        
    closeGroupFiles(read_groups)
            
    t = [[k, read_groups[k]['read_count']] for k in read_groups]
    t.append(["limit", args.limit])
    t.append(["total pairs read", readNumber])
    print(tabulate.tabulate(t, headers=["sample","read count"]))

if __name__ == '__main__':
    main()
