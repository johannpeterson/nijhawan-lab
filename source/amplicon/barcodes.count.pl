#!/bin/env perl
# Author: Jiwoong Kim (jiwoongbio@gmail.com)
use strict;
use warnings;
local $SIG{__WARN__} = sub { die $_[0] };

use Getopt::Long qw(:config no_ignore_case);

GetOptions(
	'e' => \(my $exact = ''),
);
my ($samFile) = @ARGV;
my %barcodesCountHash = ();
open(my $reader, ($samFile =~ /\.gz$/ ? "gzip -dc $samFile |" : $samFile));
my @tokenListList = ();
while(my $line = <$reader>) {
	chomp($line);
	next if($line =~ /^@/);
	my @tokenList = split(/\t/, $line, -1);
	if(@tokenListList && $tokenListList[0]->[0] ne $tokenList[0]) {
		$barcodesCountHash{join(',', getBarcodeList(@tokenListList))} += 1;
		@tokenListList = ();
	}
	push(@tokenListList, \@tokenList);
}
if(@tokenListList) {
	$barcodesCountHash{join(',', getBarcodeList(@tokenListList))} += 1;
	@tokenListList = ();
}
close($reader);

foreach my $barcodes (sort {$barcodesCountHash{$b} <=> $barcodesCountHash{$a} || $a cmp $b} keys %barcodesCountHash) {
	print join("\t", $barcodes, $barcodesCountHash{$barcodes}), "\n";
}

sub getBarcodeList {
	my @tokenListList = @_;
	my %barcodeNumberHash = ();
	foreach(@tokenListList) {
		my %tokenHash = ();
		(@tokenHash{'qname', 'flag', 'rname', 'pos', 'mapq', 'cigar', 'rnext', 'pnext', 'tlen', 'seq', 'qual'}, my @tagTypeValueList) = @$_;
		$tokenHash{"$_->[0]:$_->[1]"} = $_->[2] foreach(map {[split(/:/, $_, 3)]} @tagTypeValueList);
		next if($tokenHash{'flag'} & 4);
		next if($exact && scalar(grep {/^MD:Z:[0-9]+$/} @tagTypeValueList) == 0);
		$barcodeNumberHash{$tokenHash{'rname'}}->{($tokenHash{'flag'} & 192) / 64} = 1;
	}
	my @barcodeList = ();
	foreach my $barcode (sort keys %barcodeNumberHash) {
		push(@barcodeList, $barcode) if($barcodeNumberHash{$barcode}->{0});
		push(@barcodeList, $barcode) if($barcodeNumberHash{$barcode}->{1} && $barcodeNumberHash{$barcode}->{2});
	}
	return @barcodeList;
}
