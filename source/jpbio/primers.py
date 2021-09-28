# jpbio/primers.py

from jpbio.util import rcDNA
import csv

try:
    from icecream import ic
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)

# PrimerTable (specifically readPrimersFile)
# expects a table of primers in this format:
# oVK025	GCTACCTTGGATATTGCTGAAGAGCTTG	ACCTTG 	F
# oVK031	GCTGCCGAAGATATTGCTGAAGAGCTTG	GCCGAA	F
# oVK032	GCTACTGCTGATATTGCTGAAGAGCTTG	TACTGC	F
# ...

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
            } for p in self.primers}

    def getForwardPrimers(self):
        """Return a list of all primers with forward (F) direction."""
        return [p['OriginalSeq'] for p in self.primers if p['direction']=='F']

    def getReversePrimers(self):
        """Return a list of all primers with reverse (R) direction."""
        return [p['OriginalSeq'] for p in self.primers if p['direction']=='R']

    def lookupPrimer(self, primer_name):
        try:
            p = self.primer_lookup[primer_name]
            p['name'] = primer_name
            return p
        except KeyError:
            return None

    def lookupPrimerDirection(self, primer_name):
        try:
            p = self.primer_lookup[primer_name]
            return p['direction']
        except KeyError:
            return None

    def idPrimers(self, seq):
        """Search the provided seq and return the first matching forward & reverse primers."""
        found_primers = {
            'fwd_primer':None,
            'fwd_primer_loc':None, 
            'rc_primer':None, 
            'rc_primer_loc':None, 
            'fwd_direction':None,
            'rc_direction':None
        }
        ic(seq)
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
