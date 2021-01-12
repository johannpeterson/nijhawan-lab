#!/bin/env perl
# Author: Jiwoong Kim (jiwoongbio@gmail.com)
use strict;
use warnings;
local $SIG{__WARN__} = sub { die $_[0] };

use List::Util qw(sum);
use Getopt::Long qw(:config no_ignore_case);

GetOptions(
	'e' => \(my $exact = ''),
);
my ($samFile) = @ARGV;
my %barcodePairSequenceCountHash = ();
my %barcodeLengthHash = ();
open(my $reader, ($samFile =~ /\.gz$/ ? "gzip -dc $samFile |" : $samFile));
my @tokenListList = ();
while(my $line = <$reader>) {
	chomp($line);
	my @tokenList = split(/\t/, $line, -1);
	if($tokenList[0] eq '@SQ') {
		my %tokenHash = map {$_->[0] => $_->[1]} map {[split(/:/, $_, 2)]} @tokenList[1 .. $#tokenList];
		$barcodeLengthHash{$tokenHash{'SN'}} = $tokenHash{'LN'};
	}
	next if($line =~ /^@/);
	if(@tokenListList && $tokenListList[0]->[0] ne $tokenList[0]) {
		foreach my $barcodePairSequence (getBarcodePairSequenceList(@tokenListList)) {
			my ($barcode1, $barcode2, $sequence) = split(/\t/, $barcodePairSequence, 3);
			$barcodePairSequenceCountHash{join("\t", $barcode1, $barcode2)}->{$sequence} += 1;
		}
		@tokenListList = ();
	}
	push(@tokenListList, \@tokenList);
}
if(@tokenListList) {
	foreach my $barcodePairSequence (getBarcodePairSequenceList(@tokenListList)) {
		my ($barcode1, $barcode2, $sequence) = split(/\t/, $barcodePairSequence, 3);
		$barcodePairSequenceCountHash{join("\t", $barcode1, $barcode2)}->{$sequence} += 1;
	}
	@tokenListList = ();
}
close($reader);

foreach my $barcodePair (sort keys %barcodePairSequenceCountHash) {
	my %sequenceCountHash = %{$barcodePairSequenceCountHash{$barcodePair}};
	my $count = sum(values %sequenceCountHash);
	foreach my $sequence (sort {$sequenceCountHash{$b} <=> $sequenceCountHash{$a} || $a cmp $b} keys %sequenceCountHash) {
		print join("\t", $barcodePair, $sequence, $sequenceCountHash{$sequence}, $sequenceCountHash{$sequence} / $count), "\n";
	}
}

sub getBarcodePairSequenceList {
	my @tokenListList = @_;
	my %numberBarcodeLengthSequenceStrandListHash = ();
	foreach(@tokenListList) {
		my %tokenHash = ();
		(@tokenHash{'qname', 'flag', 'rname', 'pos', 'mapq', 'cigar', 'rnext', 'pnext', 'tlen', 'seq', 'qual'}, my @tagTypeValueList) = @$_;
		$tokenHash{"$_->[0]:$_->[1]"} = $_->[2] foreach(map {[split(/:/, $_, 3)]} @tagTypeValueList);
		next if($tokenHash{'flag'} & 4);
		my $barcodeLength = $barcodeLengthHash{$tokenHash{'rname'}};
		next if(getEnd(@tokenHash{'pos', 'cigar'}) != $barcodeLength);
		next if($exact && scalar(grep {/^MD:Z:$barcodeLength/} @tagTypeValueList) == 0);
		my $number = ($tokenHash{'flag'} & 192) / 64;
		my $barcode = $tokenHash{'rname'};
		my $length = length(my $sequence = $tokenHash{'seq'});
		$length -= $1 if($tokenHash{'cigar'} =~ /([0-9]+)[IS]$/);
		my $strand = ($tokenHash{'flag'} & 16) == 0 ? '+' : '-';
		push(@{$numberBarcodeLengthSequenceStrandListHash{$number}}, [$barcode, $length, $sequence, $strand]);
	}
	my %barcodePairSequenceNumberHash = ();
	foreach my $number (keys %numberBarcodeLengthSequenceStrandListHash) {
		my @barcodeLengthSequenceStrandList = @{$numberBarcodeLengthSequenceStrandListHash{$number}};
		next if(scalar(@barcodeLengthSequenceStrandList) != 2);
		@barcodeLengthSequenceStrandList = sort {$a->[0] cmp $b->[0]} @barcodeLengthSequenceStrandList;
		my ($barcode1, $length1, $sequence1, $strand1) = @{$barcodeLengthSequenceStrandList[0]};
		my ($barcode2, $length2, $sequence2, $strand2) = @{$barcodeLengthSequenceStrandList[1]};
		next if($strand1 eq $strand2);
		my $sequence = substr($sequence1, $length1, length($sequence1) - ($length1 + $length2));
		$barcodePairSequenceNumberHash{join("\t", $barcode1, $barcode2, $sequence)}->{$number} = 1;
	}
	my @barcodePairSequenceList = ();
	foreach my $barcodePairSequence (keys %barcodePairSequenceNumberHash) {
		push(@barcodePairSequenceList, $barcodePairSequence) if($barcodePairSequenceNumberHash{$barcodePairSequence}->{0});
		push(@barcodePairSequenceList, $barcodePairSequence) if($barcodePairSequenceNumberHash{$barcodePairSequence}->{1} && $barcodePairSequenceNumberHash{$barcodePairSequence}->{2});
	}
	return @barcodePairSequenceList
}

sub getEnd {
	my ($position, $cigar) = @_;
	while($cigar =~ s/^([0-9]+)([MIDNSHP=X])//) {
		my ($length, $operation) = ($1, $2);
		if($operation eq 'M') {
			$position += $length;
		} elsif($operation eq 'D') {
			$position += $length;
		} elsif($operation eq 'N') {
			$position += $length;
		}
	}
	return $position - 1;
}

sub getReverseComplementarySequence {
	my ($sequence) = @_;
	($sequence = reverse($sequence)) =~ tr/ACGT/TGCA/;
	return $sequence;
}
