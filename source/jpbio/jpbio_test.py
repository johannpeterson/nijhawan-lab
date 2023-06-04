# jpbio test
import sys, os
sys.path.insert(0, '/home/johann/bio/nijhawanlab/source')

import jpbio.primers
import jpbio.pairedreads
import jpbio.MultiStream

from Bio import Seq, SeqIO
import gzip
import csv
import itertools
import re
# import xlwt, openpyxl
from tqdm import tqdm
from io import StringIO
import locale

try:
    from icecream import ic
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

R1_file = "VK008_R1_001.fastq.gz"
R2_file = "VK008_R2_001.fastq.gz"
primer_file = "primers.txt"
samples_file = "VK008_samples.tsv"
experiment = "VK008"
working_directory = "/data/nijhawanlab/amplicons/" + experiment
os.chdir(working_directory)

primers_table = jpbio.primers.PrimerTable()
primers_table.readPrimersFile(primer_file)
tags_list = [f+"_"+r+"_"+d for f in primers_table.getForwardPrimers() for r in primers_table.getReversePrimers() for d in ["R1", "R2"]]

pair_analyzer = jpbio.pairedreads.PairAnalyzer(primers_table)
checker = jpbio.pairedreads.SanityChecker(checkBarcodes=False)
ic.disable()
check.resetStatistics()

streams = jpbio.MultiStream.MultiStream(
    tags = tags_list,
    prefix = experiment + "_",
    extension = ".fastq"
)
streams.open()

with gzip.open(R1_file, "rt") as R1, gzip.open(R2_file, "rt") as R2:
    reads1 = SeqIO.parse(R1, "fastq")
    reads2 = SeqIO.parse(R2, "fastq")
    maxReads = 10
    readNumber = 1
    reads_list = []
    
    progress_bar = tqdm(total=maxReads)
    for (read1, read2) in zip(reads1, reads2):
        pair_analyzer.analyzeReads(read1, read2)
        pair_analyzer.findBarcodes()
        checks_passed = checker.checkPair(pair_analyzer)
        
        if checks_passed:
            F_primer = pair_analyzer.forward_read_forward_primer
            R_primer = pair_analyzer.forward_read_rc_primer
            ic(F_primer, R_primer)
            outfile_R1 = streams.getStream(F_primer+"_"+R_primer+"_"+"R1")
            outfile_R2 = streams.getStream(F_primer+"_"+R_primer+"_"+"R2")
            if (outfile_R1 is not None and outfile_R2 is not None):
                SeqIO.write(read1, outfile_R1, "fastq")
                SeqIO.write(read2, outfile_R2, "fastq")
        
        progress_bar.update(1)
        if readNumber == maxReads:
            break
        readNumber += 1

    progress_bar.close()
ic.enable()
print("maxReads: {}\nTotal reads: {}".format(maxReads,readNumber))
ic(checker.sanity_failures)