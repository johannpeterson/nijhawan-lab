# jpbio/pairedreads.py

import jpbio.primers
from jpbio.util import rcDNA
import re

class PairAnalyzer:
    """A class to analyze pairs of paired-end reads."""

    def __init__(self, primers):
        self.primers = primers
        self.reference_sequence_pre = 'TTCTTGACGAGTTCTTCTGA'
        self.reference_sequence_post = 'ACGCGTCTGGAACAATCAAC'

    def findBarcode(self, read, rc=False):
        if rc:
            pre_loc = read.seq.find( rcDNA( self.reference_sequence_pre ) ) 
            post_loc = read.seq.find( rcDNA( self.reference_sequence_post ) ) 
            barcode_loc = [post_loc + len( self.reference_sequence_post ), pre_loc]
            barcode = rcDNA( str(read.seq)[ barcode_loc[0] : barcode_loc[1] ] )
        else:
            pre_loc = read.seq.find( self.reference_sequence_pre )
            post_loc = read.seq.find( self.reference_sequence_post )
            barcode_loc = [pre_loc + len( self.reference_sequence_pre ), post_loc]
            barcode = str(read.seq)[ barcode_loc[0] : barcode_loc[1] ]
        return barcode, barcode_loc

    def findBarcodes(self):
        """Find barcode sequences in the forward & rc reads.
        Execute after analyzeReads."""
        
        self.forward_read_barcode, self.forward_read_barcode_loc = self.findBarcode(
            self.forward_read, rc=False)
        self.rc_read_barcode, self.rc_read_barcode_loc = self.findBarcode(
            self.rc_read, rc=True)
        
        self.forward_read_barcode_quality = self.forward_read.letter_annotations["phred_quality"][ self.forward_read_barcode_loc[0]:self.forward_read_barcode_loc[1] ]
        self.rc_read_barcode_quality = self.rc_read.letter_annotations["phred_quality"][ self.rc_read_barcode_loc[0]:self.rc_read_barcode_loc[1] ]
    
    def analyzeReads(self, read1, read2):
        primers1 = self.primers.idPrimers(read1.seq)
        primers2 = self.primers.idPrimers(read2.seq)

        # implement error checking here
        if primers1["fwd_direction"] == 'R':
            self.forward_read = read1
            self.rc_read = read2
            self.forward_read_primers = primers1
            self.rc_read_primers = primers2
        else:
            self.forward_read = read2
            self.rc_read = read1
            self.forward_read_primers = primers2
            self.rc_read_primers = primers1

        self.forward_id = self.forward_read.id
        self.rc_id = self.rc_read.id
        self.forward_read_forward_primer = self.forward_read_primers['fwd_primer']
        self.forward_read_rc_primer = self.forward_read_primers['rc_primer']
        self.rc_read_forward_primer = self.rc_read_primers['fwd_primer']
        self.rc_read_rc_primer = self.rc_read_primers['rc_primer']

class SanityChecker:
    def sanity_id_match(r):
        return r.forward_id == r.rc_id

    def sanity_primer_match(r):
        return (
            (r.forward_read_forward_primer == r.rc_read_rc_primer) &
            (r.forward_read_rc_primer == r.rc_read_forward_primer)
        )

    def sanity_all_primers_found(r):
        return (
            (r.forward_read_forward_primer != None) &
            (r.forward_read_rc_primer != None) &
            (r.rc_read_forward_primer != None) & 
            (r.rc_read_rc_primer != None)
        )

    def sanity_barcodes_match(r):
        return (r.forward_read_barcode == r.rc_read_barcode)

    def sanity_barcodes_length(r):
        lF = len(r.forward_read_barcode)
        lR = len(r.rc_read_barcode) 
        return (
            (lF <= self.maximum_barcode_length) &
            (lF >= self.minimum_barcode_length) &
            (lR <= self.maximum_barcode_length) &
            (lR >= self.minimum_barcode_length)
        )

    def sanity_barcode_pattern(r):
        if self.barcode_regex.fullmatch(r.forward_read_barcode):
            return True
        else:
            return False

    def sanity_barcodes_quality(r):
        return (
            (min(r.forward_read_barcode_quality) >= self.minimum_read_quality) &
            (min(r.rc_read_barcode_quality) >= self.minimum_read_quality)
        )

    basic_sanity_checks = [
        {
            'id':'any',
            'label':'Any Check',
            'description':'Read pairs failing any sanity check.',
            'function':(lambda _: True)
        },
        {
            'id':'id_match',
            'label':'IDs Match',
            'description':'R1 & R2 read IDs match.',
            'function':sanity_id_match},
        {
            'id':'primer_match',
            'label':'Primers Match',
            'description':'Forward & reverse primers for R1 & R2 match.',
            'function':sanity_primer_match
        },
        {
            'id':'primers_found',
            'label':'Primers Found',
            'description':'Forward & reverse primers identified in both reads.',
            'function':sanity_all_primers_found
        }
    ]
    barcode_sanity_checks = [
        {
            'id':'barcodes_match',
            'label':'Barcodes Match',
            'description':'Barcodes from R1 & R2 reads match exactly.',
            'function':sanity_barcodes_match
        },
        {
            'id':'barcode_length',
            'label':'Barcode Length',
            'description':'Barcode lengths are within the required range.',
            'function':sanity_barcodes_length
        },
        {
            'id':'barcode_pattern',
            'label':'Barcode Pattern',
            'description':'The R1 barcode matches the specified pattern (SWSW...).',
            'function':sanity_barcode_pattern
        },
        {
            'id':'barcodes_quality',
            'label':'Barcode Read Quality',
            'description':'The minimum read quality (PHRED score) for both barcodes is at least the minumum specified.',
            'function':sanity_barcodes_quality
        }
    ]

    def __init__(self):
        self.maximum_barcode_length = 30
        self.minimum_barcode_length = 14
        self.minimum_barcode_quality = 20
        self.barcode_regex = re.compile('([GC][AT])+[GC]?')
        self.sanity_checks = self.basic_sanity_checks + self.barcode_sanity_checks
        self.resetStatistics()

    def resetStatistics(self):
        self.sanity_failures = {c['id']:0 for c in self.sanity_checks}
        
    def checkPair(self, pair_analyzer):
        any_failure = False
        for check in self.sanity_checks:
            try:
                test_passes = check['function'](pair_analyzer)
            except ValueError:
                test_passes = False
            if not test_passes:
                self.sanity_failures[check['id']] += 1
                any_failure = True
        if any_failure:
            self.sanity_failures['any'] += 1
        return not any_failure
