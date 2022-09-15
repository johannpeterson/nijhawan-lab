# jpbio/util.py

basePair = {'A':'T','T':'A','G':'C','C':'G'}
basePairTrans = str.maketrans(basePair)

def rcDNA(seq):
    return seq.translate(basePairTrans) [::-1]

def cDNA(seq):
   return seq.translate(basePairTrans)

def pad_list(l, length, element):
    if len(l) < length:
        l.extend( [element for _ in range(length - len(l))] )
        return l
    else:
        return l

# It is necessary to create lists of dictionaries differently from lists of integers,
# because if you use the strategy above you get a list where every element is the same dict.
def pad_dict_list(l, length):
    if len(l) < length:
        l.extend( [dict() for _ in range(length - len(l))] )
        return l
    else:
        return l

def export_figure(fig, title, metadata={}):
    fig_metadata = {
        "Comment" : "experiment:" + experiment
    }
    fig_metadata.update(metadata)
    filename = data_directory + experiment + "_" + title + ".png"
    fig.savefig(filename, metadata = fig_metadata)