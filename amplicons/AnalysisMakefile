.PHONY: settings help clean cleanall merge matches
.ONESHELL:
SHELL=/bin/bash

# use the top N reads to make the bar charts
TOP_N=10

# input files
# Infer the paired read files based on filenames.
R1_FILE=$(firstword $(wildcard *_R1_*.fastq.gz))
R2_FILE=$(firstword $(wildcard *_R2_*.fastq.gz))
PREFIX=$(firstword $(subst _, ,$(R1_FILE)))

BARCODE_PATTERNS_FILE=./barcode_patterns.py
PRIMERS_FILE=./primers.txt
SAMPLES_FILE=./$(PREFIX)_samples.tsv

# executables
SOURCEDIR=~/bio/amplicons
DESTDIR=./aligned
GET_REGEXES=$(SOURCEDIR)/get_regexes.py
COUNT_REGEX=$(SOURCEDIR)/count_regex.py
JOIN_MATCHES=$(SOURCEDIR)/join_matches.sh # no longer used
SEPARATE_MATCHTABLE=$(SOURCEDIR)/separate_matchtable.awk
MERGE_NAMES=$(SOURCEDIR)/merge_names.awk
COUNT_BARCODES=$(SOURCEDIR)/count_barcodes.sh
FLATTEN_SAMPLES=$(SOURCEDIR)/flatten_samples.py
FLASH=flash2 -M 230
BARCHART_GRID=$(SOURCEDIR)/barchart_grid.py
MAKE_BARCHART=$(BARCHART_GRID) --top $(TOP_N) --experiment $(PREFIX) --control W1 --control W2 --control W3

# Intermediate and result files
MERGED_READS=$(DESTDIR)/$(PREFIX)_merged.fastq
PATTERNS=$(DESTDIR)/$(PREFIX)_patterns.py
SED_COMMANDS=$(DESTDIR)/$(PREFIX).sed
NEW_FASTQ=$(DESTDIR)/$(PREFIX)_annotated.fastq
MATCHES=$(DESTDIR)/$(PREFIX)_matches.tsv
BARCODE_TABLE=$(DESTDIR)/$(PREFIX)_barcode_table.tsv
BARCODE_COUNTS=$(DESTDIR)/$(PREFIX)_barcode_counts.tsv
COUNT_REGEX_OUTPUT=$(DESTDIR)/$(PREFIX)_count_regex_output.txt
BARCODE_COUNTS_SAMPLES=$(DESTDIR)/$(PREFIX)_barcode_counts_samples.tsv
FLAT_SAMPLES=$(DESTDIR)/$(PREFIX)_flat_samples.tsv
COUNTS=$(DESTDIR)/$(PREFIX)_totals_by_sample.tsv
FLASH_LOG=$(DESTDIR)/$(PREFIX)_flash.log
BARCHARTS=$(DESTDIR)/$(PREFIX)_barchart.png
LOGFILE=$(DESTDIR)/$(PREFIX).log
TOP_N_FILE=$(DESTDIR)/$(PREFIX)_top_$(TOP_N).tsv
TOP_N_XLSX=$(DESTDIR)/$(PREFIX)_top_$(TOP_N).xlsx

MATCHFILE_FWD=$(DESTDIR)/$(PREFIX)_matchfile_fwd.tsv
MATCHFILE_REV=$(DESTDIR)/$(PREFIX)_matchfile_rev.tsv
MATCHFILE_FWD_RC=$(DESTDIR)/$(PREFIX)_matchfile_fwd_rc.tsv
MATCHFILE_REV_RC=$(DESTDIR)/$(PREFIX)_matchfile_rev_rc.tsv

INTERMEDIATE_FILES=$(PATTERNS) $(MATCHES) $(BARCODE_TABLE) $(BARCODE_COUNTS) \
	$(BARCODE_COUNTS_SAMPLES) $(FLAT_SAMPLES) $(COUNTS) $(FLASH_LOG) \
	$(MATCHFILE_FWD) $(MATCHFILE_REV) $(MATCHFILE_FWD_RC) $(MATCHFILE_REV_RC) \
	$(COUNT_REGEX_OUTPUT) $(LOGFILE) $(SED_COMMANDS)
RESULT_FILES=$(MERGED_READS) $(BARCODE_COUNTS_SAMPLES) $(BARCHARTS) $(TOP_N_FILE) $(NEW_FASTQ) $(TOP_N_XLSX)

## all: run all steps necessary to produce the barchart grid (default action)
all : $(TOP_N_FILE) $(BARCHARTS)

## settings: show the values of variables
settings :
	@echo "PREFIX (experiment):" $(PREFIX)
	@echo SOURCEDIR: $(SOURCEDIR)
	@echo DESTDIR: $(DESTDIR)
	@echo TOP_N: $(TOP_N)
	@echo
	@echo Input
	@echo R1_FILE: $(R1_FILE)
	@echo R2_FILE: $(R2_FILE)
	@echo BARCODE_PATTERNS_FILE: $(BARCODE_PATTERNS_FILE)
	@echo PRIMERS_FILE: $(PRIMERS_FILE)
	@echo SAMPLES_FILE: $(SAMPLES_FILE)
	@echo
	@echo Executables
	@echo FLASH: $(FLASH)
	@echo GET_REGEXES: $(GET_REGEXES)
	@echo COUNT_REGEX: $(COUNT_REGEX)
	@echo SEPARATE_MATCHTABLE: $(SEPARATE_MATCHTABLE)
	@echo MERGE_NAMES: $(MERGE_NAMES)
	@echo COUNT_BARCODES: $(COUNT_BARCODES)
	@echo FLATTEN_SAMPLES: $(FLATTEN_SAMPLES)
	@echo MAKE_BARCHART: $(MAKE_BARCHART)
	@echo
	@echo Output
	@echo BARCHARTS: $(BARCHARTS)
	@echo MERGED_READS: $(MERGED_READS)
	@echo BARCODE_COUNTS_SAMPLES: $(BARCODE_COUNTS_SAMPLES)
	@echo TOP_N_FILE: $(TOP_N_FILE)
	@echo TOP_N_XLSX: $(TOP_N_XLSX)
	@echo NEW_FASTQ: $(NEW_FASTQ)
	@echo INTERMEDIATE_FILES: $(INTERMEDIATE_FILES)

## clean: remove intermediate files, leaving barchart.png and merged.fastq
clean :
	rm -f $(INTERMEDIATE_FILES)

## cleanall: remove intermediate and results files, incuding the barchart.png and merged.fastq
cleanall :
	rm -f $(INTERMEDIATE_FILES)
	rm -f $(RESULT_FILES)

## help: show this message
help :
	@grep '^##' ./Makefile

$(DESTDIR) :
	mkdir -p $(DESTDIR)

# merge two paired .fastq files into one file
$(MERGED_READS) : $(R1_FILE) $(R2_FILE) $(DESTDIR)
	$(FLASH) --to-stdout $(R1_FILE) $(R2_FILE) 2>$(FLASH_LOG) >$(MERGED_READS)

## merge: run flash2 to merge the paired reads (R1 & R2 files) into _merged.fastq
merge : $(MERGED_READS)

# obtain the barcode patterns from the source directory
$(BARCODE_PATTERNS_FILE) : $(SOURCEDIR)/barcode_patterns.py
	cp $(SOURCEDIR)/barcode_patterns.py ./$(BARCODE_PATTERNS_FILE)

$(MATCHFILE_FWD) $(MATCHFILE_REV) $(MATCHFILE_FWD_RC) $(MATCHFILE_REV_RC) $(PATTERNS) $(SED_COMMANDS) : \
	$(PRIMERS_FILE) $(GET_REGEXES) $(SEPARATE_MATCHTABLE)
	$(GET_REGEXES) $(PRIMERS_FILE) --patterns $(PATTERNS) --sed $(SED_COMMANDS) | \
	$(SEPARATE_MATCHTABLE) -v FILE_FWD=$(MATCHFILE_FWD) -v FILE_REV=$(MATCHFILE_REV) \
		-v FILE_FWD_RC=$(MATCHFILE_FWD_RC) -v FILE_REV_RC=$(MATCHFILE_REV_RC)

$(MATCHES) : $(MERGED_READS) $(PATTERNS) $(BARCODE_PATTERNS_FILE) $(COUNT_REGEX)
	$(COUNT_REGEX) $(MERGED_READS) -p $(PATTERNS) -p $(BARCODE_PATTERNS_FILE) \
		-s --out $(MATCHES) --fastq_out $(NEW_FASTQ) \
	> $(COUNT_REGEX_OUTPUT)

## matches: Compute regex matches using count_regex.py
matches : $(MATCHES)

$(BARCODE_TABLE) : $(MATCHES) $(JOIN_MATCHES) $(MERGE_NAMES)
# join_matches.sh is reproduced here so we can use our filename variables easily
# was: $(JOIN_MATCHES) < $(MATCHES) | $(MERGE_NAMES) -v FILTER=1 > $(BARCODE_TABLE)
	csvtk join --left-join -t --fields "seq_fwd_1;seq_fwd_1" $(MATCHES) $(MATCHFILE_FWD) | \
	csvtk join --left-join -t --fields "seq_rev_1;seq_rev_1" - $(MATCHFILE_REV) | \
	csvtk join --left-join -t --fields "seq_fwd_rc_1;seq_fwd_rc_1" - $(MATCHFILE_FWD_RC) | \
	csvtk join --left-join -t --fields "seq_rev_rc_1;seq_rev_rc_1" - $(MATCHFILE_REV_RC) | \
	$(MERGE_NAMES) -v FILTER=1 > $(BARCODE_TABLE)

$(BARCODE_COUNTS) : $(BARCODE_TABLE) $(COUNT_BARCODES)
	$(COUNT_BARCODES) < $(BARCODE_TABLE) > $(BARCODE_COUNTS)

$(FLAT_SAMPLES) : $(SAMPLES)
	$(FLATTEN_SAMPLES) $(SAMPLES_FILE) $(FLAT_SAMPLES)

$(BARCODE_COUNTS_SAMPLES) : $(BARCODE_COUNTS) $(FLAT_SAMPLES)
	csvtk join -t --left-join -f "fwd_primer,rev_primer" $(BARCODE_COUNTS) $(FLAT_SAMPLES) > $(BARCODE_COUNTS_SAMPLES)

$(COUNTS) : $(BARCODE_COUNTS_SAMPLES)
	csvtk summary -t -g sample,fwd_primer,rev_primer -f frequency:sum $(BARCODE_COUNTS_SAMPLES) > $(COUNTS)

$(BARCHARTS) $(TOP_N_FILE) : $(BARCODE_COUNTS_SAMPLES) $(BARCHART_GRID)
	$(MAKE_BARCHART) --png $(BARCHARTS) $(BARCODE_COUNTS_SAMPLES) $(TOP_N_FILE) 2>>$(LOGFILE)
# stderr redirected to a log mostly because there are some annoying layout warnings coming from barchart_grid.py

## excel: Write the .xlsx file with the top reads for each sample
excel : $(TOP_N_XLSX)

$(TOP_N_XLSX) : $(BARCODE_COUNTS_SAMPLES)
	csvtk sort -t -k sample -k frequency:nr $(BARCODE_COUNTS_SAMPLES) | \
	csvtk uniq -t -f sample -n 10 | \
	csvtk csv2xlsx -t --format-numbers -o $(TOP_N_XLSX)
