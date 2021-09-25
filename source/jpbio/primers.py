# jpbio/primers.py

from jpbio.util import rcDNA

# PrimerTable (specifically readPrimersFile)
# expects a table of primers in this format:
# oVK025	GCTACCTTGGATATTGCTGAAGAGCTTG	ACCTTG 	F
# oVK031	GCTGCCGAAGATATTGCTGAAGAGCTTG	GCCGAA	F
# oVK032	GCTACTGCTGATATTGCTGAAGAGCTTG	TACTGC	F
# oVK033	GCTGAACGTGATATTGCTGAAGAGCTTG	GAACGT	F
# oVK034	GCTATCCATGATATTGCTGAAGAGCTTG	TATCCA	F
# oVK035	GCCTCCGGTGATATTGCTGAAGAGCTTG	CTCCGG	F
# oVK036	GCTACCACCGATATTGCTGAAGAGCTTG	ACCACC	F
# oVK037	GCTACCGAGGATATTGCTGAAGAGCTTG	ACCGAG	F
# oVK026	TTTTGTCACCCAGAGGTTGATTGTTCCAGA	TGTCAC 	R
# oVK038	TTTGTTAATCCAGAGGTTGATTGTTCCAGA	GTTAAT	R
# oVK039	TTTTATGGTCCAGAGGTTGATTGTTCCAGA	TATGGT	R
# oVK040	TTTTGAGATACAGAGGTTGATTGTTCCAGA	GAGATA	R
# oVK041	TTATGCACTCCAGAGGTTGATTGTTCCAGA	ATGCAC	R
# oVK042	TTTAGTCAGCCAGAGGTTGATTGTTCCAGA	AGTCAG	R
# oVK043	TTTTCCATTCCAGAGGTTGATTGTTCCAGA	TCCATT	R
# oVK044	TTTTGTGGTTCAGAGGTTGATTGTTCCAGA	GTGGTT	R
# oVK045	TTTTCTCTACCAGAGGTTGATTGTTCCAGA	TCTCTA	R
# oVK046	TTTTTACATCCAGAGGTTGATTGTTCCAGA	TACATC	R
# oVK047	TTTGGTAGACCAGAGGTTGATTGTTCCAGA	GGTAGA	R
# oVK048	TTTTACGATCCAGAGGTTGATTGTTCCAGA	TTTACG	R

class PrimerTable:
    """Class for storing and managing a table of primers."""
    
    def __init__(self, filename=None):
        self.primers = []
        if filename is not None:
            self.readPrimersFile(filename)

    def readPrimersFile(self, filename):
        """Read a tab-separated file with 4 columns into the PrimerTable object."""        
        with open(filename, newline='') as primers_IO:
            primer_reader = csv.DictReader(
                primers_IO, 
                delimiter='\t', 
                fieldnames=['OriginalSeq','sequence','barcode','direction'])
        for primer in primer_reader:
            self.primers.append(dict(primer))
        self.primer_lookup = {
            p['OriginalSeq']: {
                'len':len(p['sequence']), 
                'sequence':p['sequence'],
                'direction':p['direction']
            } for p in primers}

    def getForwardPrimers(self):
    """Return a list of all primers with forward (F) direction."""
        return [p['OriginalSeq'] for p in self.primers if p['direction']=='F']

    def getReversePrimers(self):
    """Return a list of all primers with reverse (R) direction."""
    return [p['OriginalSeq'] for p in self.primers if p['direction']=='R']

    def idPrimers(seq):
        """Search the provided seq and return the first matching forward & reverse primers."""
        found_primers = {
            'fwd_primer':None,
            'fwd_primer_loc':None, 
            'rc_primer':None, 
            'rc_primer_loc':None, 
            'fwd_direction':None,
            'rc_direction':None
        }
        for p in self.primers:
            p1 = seq.find(p['sequence'])
        if p1 != -1:
            found_primers['fwd_primer'] = p['OriginalSeq']
            found_primers['fwd_primer_loc'] = p1
            found_primers['fwd_direction'] = p['direction']
            p2 = seq.rfind( rcDNA( p['sequence'] ))
        if p2 != -1:
            found_primers['rc_primer'] = p['OriginalSeq']
            found_primers['rc_primer_loc'] = p2
            found_primers['rc_direction'] = p['direction']
        return found_primers
