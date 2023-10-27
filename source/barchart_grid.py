#! python3
"""barchart_grid

A stand-alone script to generate the grid of bar charts for amplicon barcodes.
Input should be in TSV format with fields fwd_primer, rev_primer, count, barcode.

"""

import types
import sys
import argparse
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

try:
    from icecream import ic
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("-d", "--debug",
                    help="Enable debugging output", action="store_true")
parser.add_argument("infile", nargs='?',
                    help="File to read from;  stdin if not provided.",
                    type=argparse.FileType('r'), default=sys.stdin)
parser.add_argument("outfile", nargs='?',
                    help="File to write to;  stdout if not provided.",
                    type=argparse.FileType('w'), default=sys.stdout)
parser.add_argument("--top", type=int, default=10,
                    help="Number of barcodes to keep from each sample.")
parser.add_argument("-e", "--experiment",
                    type=str, default="",
                    help="Name of the experiment for plot title.")
parser.add_argument("--control",
                    type=str, action="append", default=["water"],
                    help="Sample names for the control samples.")
# parser.add_argument...

args = parser.parse_args()

if not isinstance(ic, types.FunctionType):
    if args.debug:
        ic.enable()
        ic.configureOutput(includeContext=True)
    else:
        ic.disable()
ic(args)


# ----------------------------------------------------------
# plotting functions
# ----------------------------------------------------------


def annotate(data, **kwargs):
    ic(kwargs)
    f = data.iloc[0]['forward_primer']
    r = data.iloc[0]['reverse_primer']
    n = data[(data['forward_primer'] == f) & (data['reverse_primer'] == r)].iloc[0]['count']

    sample_dict = kwargs.get('sample_dict')
    if sample_dict is not None:
        sample = sample_dict.get((f,r), "???")
    else:
        sample = ""
    ic(sample)
        
    ax = plt.gca()
    if sample in args.control:
        ax.set_facecolor('lightgrey')

    ax.text(.9, .1, f"{sample}\ncount:{n}",
            fontsize=14,
            horizontalalignment='right',
            verticalalignment='bottom',
            transform=ax.transAxes)


def make_plot_grid(data, sample_dict, expname="experiment"):
    sns.set_style()
    sns.set_style("dark")
    sns.set_context("paper")
    hist_grid = sns.FacetGrid(
        data,
        row="forward_primer",
        col="reverse_primer",
        height=2.5, aspect=1,
        margin_titles=True,
        sharex=False,
        sharey=False
    )
    hist_grid.fig.set_constrained_layout(True)
    hist_grid.map_dataframe(
        sns.barplot,
        x="count",
        y="barcode",
        # order = data['count'], #counts_table['count'].value_counts().iloc[:5].index,
        # errorbar=None,
        orient='h'
    )

    hist_grid.map_dataframe(annotate,
                            sample_dict = sample_dict)
    hist_grid.set_yticklabels([])
    hist_grid.set_xticklabels([])
    hist_grid.fig.suptitle(expname, fontsize=24)
    hist_grid.set_titles(col_template="{col_name}", row_template="{row_name}", size=18)
    plt.subplots_adjust(top=0.85)
    return hist_grid


def compute_sample_dict(data):
    full_sample_dict =  data.groupby(by=['forward_primer','reverse_primer']) \
                       .first() \
                       .reset_index() \
                       .set_index(['forward_primer','reverse_primer']) \
                       .to_dict('index')
    ic(full_sample_dict)
    ic(full_sample_dict.items())
    if ('sample' in data.columns):
        sample_dict = {k:full_sample_dict[k].get('sample')
                       for k in full_sample_dict
                       if full_sample_dict[k].get('sample') is not None}
    else:
        sample_dict = {k:'' for k in full_sample_dict}
    ic(sample_dict)
    return sample_dict

    
# ----------------------------------------------------------
# main
# ----------------------------------------------------------


def main():
    """main
    """
    ic(args.control)
    df = pd.read_csv(args.infile, sep='\t', header=0)
    ic(df.head)
    sorted_counts = df.sort_values(['forward_primer','reverse_primer','count'], ascending=[True,True,False])
    ic(sorted_counts.head)
    top_n = sorted_counts.groupby(by=['forward_primer','reverse_primer']) \
                         .nth(list(range(args.top))) \
                         .reset_index() \
                         .astype({'barcode':'str', 'forward_primer':'category', 'reverse_primer':'category'})
    top_n.to_csv(args.outfile, sep='\t', header=True, index=False)
    sample_dict = compute_sample_dict(sorted_counts)
    figure = make_plot_grid(top_n, sample_dict, expname=args.experiment)
    figure.savefig("barchart.png")


if __name__ == '__main__':
    main()
