#!/bin/bash

mkdir -p tmp
export TMPDIR=`readlink -f tmp`

home=/work/archive/PCDC/shared/jkim23
reference=/work/archive/PCDC/shared/jkim23/data/igenomes/Homo_sapiens/UCSC/hg38/Sequence/BWAIndex/genome.fa

time fastq.read_length.read_count.pl 11_1.1.fastq.gz 11_1.2.fastq.gz > 11_1.read_length.read_count.txt

module load trimgalore/0.6.4
trim_galore --illumina --cores 8 --paired 11_1.1.fastq.gz 11_1.2.fastq.gz
module unload trimgalore/0.6.4

time fastq.read_length.read_count.pl 11_1.1_val_1.fq.gz 11_1.2_val_2.fq.gz > 11_1.trimgalore.read_length.read_count.txt

# BWA: mapping to reference genome
time bwa mem -t 8 $reference 11_1.1_val_1.fq.gz 11_1.2_val_2.fq.gz | gzip > 11_1.sam.gz

# Picard: add read group information
time java -Djava.io.tmpdir=$TMPDIR -Xmx16g -jar $home/src/picard/2.21.3/picard.jar AddOrReplaceReadGroups INPUT=11_1.sam.gz OUTPUT=11_1.rgAdded.bam SORT_ORDER=coordinate RGID=11_1 RGLB=11_1 RGPL=illumina RGPU=11_1 RGSM=11_1 VERBOSITY=ERROR QUIET=true VALIDATION_STRINGENCY=LENIENT CREATE_INDEX=true && rm 11_1.sam.gz

# Picard: mark PCR duplicates
time java -Djava.io.tmpdir=$TMPDIR -Xmx16g -jar $home/src/picard/2.21.3/picard.jar MarkDuplicates INPUT=11_1.rgAdded.bam OUTPUT=11_1.dupMarked.bam METRICS_FILE=11_1.dupMarked.metrics ASSUME_SORTED=true VERBOSITY=ERROR QUIET=true VALIDATION_STRINGENCY=LENIENT CREATE_INDEX=true && rm 11_1.rgAdded.{bam,bai}

# GATK: base quality score recalibration (BQSR)
time $home/src/gatk-4.1.4.0/gatk --java-options "-Djava.io.tmpdir=$TMPDIR -Xmx16g" BaseRecalibrator -R $reference -I 11_1.dupMarked.bam --use-original-qualities -O 11_1.recal_data.table --known-sites $home/data/gatk_resource_bundle/hg38/dbsnp_146.hg38.vcf.gz --known-sites $home/data/gatk_resource_bundle/hg38/Mills_and_1000G_gold_standard.indels.hg38.vcf.gz --verbosity ERROR
time $home/src/gatk-4.1.4.0/gatk --java-options "-Djava.io.tmpdir=$TMPDIR -Xmx16g" ApplyBQSR -R $reference -I 11_1.dupMarked.bam --use-original-qualities --bqsr-recal-file 11_1.recal_data.table -O 11_1.recal_reads.bam --verbosity ERROR && rm 11_1.dupMarked.{bam,bai}

# GATK: call variants with HaplotypeCaller
time $home/src/gatk-4.1.4.0/gatk --java-options "-Djava.io.tmpdir=$TMPDIR -Xmx16g" HaplotypeCaller -R $reference -I 11_1.recal_reads.bam -O 11_1.raw.snps.indels.g.vcf.gz -ERC GVCF -G StandardAnnotation -G AS_StandardAnnotation
time $home/src/gatk-4.1.4.0/gatk --java-options "-Djava.io.tmpdir=$TMPDIR -Xmx16g" GenotypeGVCFs -R $reference -V 11_1.raw.snps.indels.g.vcf.gz -O 11_1.raw.snps.indels.vcf.gz

# Custom Perl script: variant filtering with cutoffs (QD < 2, FS > 60, MQ < 40, DP < 3, GQ < 7)
time perl $home/projects/Annomen.hg38/vcf.filter.pl 11_1.raw.snps.indels.vcf.gz QD 'QD < 2' \
	| perl $home/projects/Annomen.hg38/vcf.filter.pl - FS 'FS > 60' \
	| perl $home/projects/Annomen.hg38/vcf.filter.pl - MQ 'MQ < 40' \
	| perl $home/projects/Annomen.hg38/vcf.filter.pl -g - DP 'DP < 3' \
	| perl $home/projects/Annomen.hg38/vcf.filter.pl -g - GQ 'GQ < 7' \
	> 11_1.filtered.vcf

# Custom Perl script: variant annotation (RefSeq genes, dbSNP, COSMIC Coding, ClinVar, gnomAD, CADD, tandem repeat)
time perl $home/projects/Annomen.hg38/leftalignIndel.pl 11_1.filtered.vcf $reference | perl $home/projects/Annomen.hg38/sort_by_reference.pl - $reference 0 1 \
	| perl $home/projects/Annomen.hg38/Annomen.pl - $reference $home/projects/Annomen.hg38/Annomen_table.hg38.txt $home/projects/Annomen.hg38/human.rna.fna $home/projects/Annomen.hg38/human.protein.faa \
	| perl $home/projects/Annomen.hg38/Annotate.pl - $reference $home/projects/Annomen.hg38/snp151_allele.txt snp151 name subset alleleN alleleFreq \
	| perl $home/projects/Annomen.hg38/Annotate.pl - $reference $home/projects/Annomen.hg38/cosmic_coding.txt cosmic_coding mutationID primary occurrence \
	| perl $home/projects/Annomen.hg38/Annotate.pl - $reference $home/projects/Annomen.hg38/clinvar_20191231.txt clinvar disease significance \
	| perl $home/projects/Annomen.hg38/Annotate.pl - $reference $home/projects/Annomen.hg38/gnomAD_r3.0.txt gnomAD AF nhomalt \
	| perl $home/projects/Annomen.hg38/Annotate.pl - $reference $home/projects/Annomen.hg38/CADD_v1.5.txt CADD RawScore PHRED \
	| perl $home/projects/Annomen.hg38/tandemRepeat.pl - $reference \
	> 11_1.annotated.vcf

# Custom Perl script: generate variant tables
time perl $home/projects/Annomen.hg38/vcf.table.pl -c $home/projects/Annomen.hg38/column.name.hg38.txt 11_1.annotated.vcf > 11_1.table.variant.txt

awk -F'\t' '(NR == 1 || $17 !~ /Common/)' 11_1.table.variant.txt > 11_1.table.variant.not_Common.txt
awk -F'\t' '(NR == 1 || $16 == "")' 11_1.table.variant.txt > 11_1.table.variant.not_dbSNP.txt
table.variant_count.pl 11_1.table.variant.txt > 11_1.table.variant_count.txt
table.variant_count.pl 11_1.table.variant.not_Common.txt > 11_1.table.variant_count.not_Common.txt
table.variant_count.pl 11_1.table.variant.not_dbSNP.txt > 11_1.table.variant_count.not_dbSNP.txt

cut -f1,2,3,4,`awk -F'\t' '($1 == "tandemRepeat") {print NR}' $home/projects/Annomen.hg38/column.name.hg38.txt` 11_1.table.variant.txt | awk -F'\t' '(NR > 1 && $5 != "")' | sort -u | wc -l > 11_1.tandemRepeat.count.txt

