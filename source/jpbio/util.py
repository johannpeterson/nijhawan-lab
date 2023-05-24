# jpbio/util.py

import regex

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

def sequence_to_regex(seq):
    # Return a regular expression string to match a DNA sequence.
    # 'N' is changed to '(.)', and a series of consecutive 'N' is changed
    # to '(.{k})', where k is the number of Ns.
    nRegex=regex.compile('N{2,}')
    matches=nRegex.finditer(seq)
    marker = 0
    newSeq = ""
    for m in matches:
        newSeq += seq[marker:m.span()[0]] + "(.{{{}}})".format(m.span()[1]-m.span()[0])
        marker = m.span()[1]
        newSeq += seq[marker:]
    return newSeq.replace("N","(.)")

def common_sequence(seqs):
    # Return a string representing the common sequence of a list of sequences.
    # Letters in the returned string are either A, C, T or G if the letter in that
    # position is the same in all sequences, or N if not.
    # Sequences must be the same length.

    def elements_equal(l):
        if all([x==l[0] for x in l]):
            return l[0]
        else:
            return 'N'

    N = max(map(len, seqs))
        
    return ''.join(list( map(elements_equal, [[l[i] for l in seqs] for i in range(N)]) ))
