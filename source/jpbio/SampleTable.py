# jpbio.SampleTable

import re
import csv

class SampleTable:
    """Class to read and manage tables of samples, and map from primer pairs to sample names."""

    primer_name_regex = re.compile(r"(oVK)(\d{1,3})")

    def pad_primer_name(s):
        m = SampleTable.primer_name_regex.match(s)
        return m.group(1) + m.group(2).rjust(3, '0')

    def __init__(self):
        self.sample_dict = {}

    def readSampleFile(self, filename):
        with open(filename, "r") as f:
            csvraw = list(csv.reader(f, delimiter='\t'))
        col_headers = [SampleTable.pad_primer_name(h) for h in csvraw[0][1:]]
        row_headers = [SampleTable.pad_primer_name(row[0]) for row in csvraw[1:]]
        data = [row[1:] for row in csvraw[1:]]
        # sample_list = [s for sublist in data for s in sublist if s != '']
        self.sample_dict = {row_headers[r]:{col_headers[c]:data[r][c] for c in range(len(col_headers))} for r in range(0, len(row_headers))}

    def lookupSampleByPrimers(self, fwd, rev):
        try:
            sample = self.sample_dict[fwd][rev]
        except KeyError:
            sample = None
        return sample

