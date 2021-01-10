#!python

import vcf
import argparse, sys, os

parser = argparse.ArgumentParser(description='Convert a .vcf file into a flat table of variants.')
parser.add_argument("infile",help="Input VCF file.")
parser.add_argument("--header", help="Write a header row at the beginning of the output.", action="store_true")
parser.add_argument("-o", "--outfile", help="Write output to file OUTFILE.")
parser.add_argument("-l", "--limit", help="Stop after reading LIMIT lines.", type=int, default=-1)
parser.add_argument("-d", "--delimiter", help="Column delimiter in output table.  Default=\\t", default='\t')
args = parser.parse_args()

infoFields = {
    'geneName':'Annomen.geneName',
    'transcriptID':'Annomen.transcriptId',
    'nucleotideVariationNomenclature':'Annomen.nucleotideVariationNomenclature',
    }

VCFColumns = ['chr',
              'pos',
              'reference_allele',
              'alternate_allele',
              'sample',
              'sample_depth',
              'quality',
              'alternate_allele_depth',
]
VCFColumns.extend( list( infoFields.keys() ) )

# https://pcingola.github.io/SnpEff/adds/VCFannotationformat_v1.0.pdf
ANNFields = ['allele',
             'annotation',
             'putative_impact',
             'gene_name',
             'gene_id',
             'feature_type',
             'feature_id',
             'transcript_biotype',
             'rank',
             'HGVS.c',
             'GHVS.p',
             'cDNA_position',
             'cds_position',
             'protein_position',
             'distance_to_feature',
             'messages'
             ]
VCFColumns.extend(ANNFields)

def writeVCFRecord(variant, outfile_object):

    def variant_item(i):
        if i in variant:
            return str(variant[i])
        else:
            return ''
    
    output_line = args.delimiter.join(
        [variant_item(i) for i in VCFColumns]
        )
    if ( output_line != '' ) & ( not output_line.isspace() ):
        print(output_line, file=outfile_object)
        return 1
    else:
        return 0

def writeVCFHeader(outfile_object):
    print(args.delimiter.join(VCFColumns), file=outfile_object)
    return

def parseAnnFields(a):
    return dict( zip(ANNFields, a.split('|') ) )

def read_vcf(input_file, output_file, maxRecords=-1):
    vcfReader = vcf.Reader(input_file)
    currentRecord = 1
    variantList = []
    for record in vcfReader:
        if (maxRecords < 0) | (currentRecord <= maxRecords):
            varFields={
                'chr':record.CHROM,
                'pos':record.POS,
                'reference_allele':record.REF,
            }
            for k,v in infoFields.items():
                try:
                    varFields[k] = record.INFO[v][0]
                except KeyError:
                    pass
            try:
                annotations = record.INFO['ANN']
                annotation_dict = parseAnnFields(annotations[0])
                varFields.update(annotation_dict)
            except KeyError:
                pass
            for s in record.samples:
                call = record.genotype(s.sample)
                callAlleles = call.data.GT.replace('|','/').split('/')
                sampleFields={
                    'sample':s.sample,
                    'sample_depth':call.data.DP,
                    'quality':call.data.GQ
                }
                sampleFields.update(varFields)
                allAlleles = [record.REF] + record.ALT
                for alleleNum, depth in zip(callAlleles, call.data.AD):
                    sampleFields['alternate_allele'] = allAlleles[int(alleleNum)]
                    sampleFields['alternate_allele_depth'] = depth
                    writeVCFRecord(sampleFields, output_file)
            currentRecord += 1
        else:
            return currentRecord
    return currentRecord

def main():
    linesWritten = 0
    variantsRead = 0
    try:
        infile_object = open(args.infile, 'r')
    except OSError as err:
        print('Unable to open input file {0} for reading. ({1})'.format(args.infile, err), file=sys.stderr)
        sys.exit()
    if args.outfile:
        try:
            outfile_object = open(args.outfile, 'w')
        except OSError as err:
            print('Unable to open output file {0} for writing. ({1})'.format(args.outfile, err), file=sys.stderr)
            sys.exit()
    else:
        outfile_object = sys.stdout
    if args.header:
        writeVCFHeader(outfile_object)
    try:
        read_vcf(input_file=infile_object, output_file=outfile_object, maxRecords=args.limit)
    except BrokenPipeError:
        # https://stackoverflow.com/questions/26692284/how-to-prevent-brokenpipeerror-when-doing-a-flush-in-python
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(1)

if __name__ == '__main__':
   main()
