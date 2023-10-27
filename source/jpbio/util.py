# jpbio/util.py

import regex

basePair = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G'}
basePairTrans = str.maketrans(basePair)


def rcDNA(seq):
    return seq.translate(basePairTrans)[::-1]


def cDNA(seq):
    return seq.translate(basePairTrans)


def pad_list(item_list, length, element):
    if len(item_list) < length:
        item_list.extend([element for _ in range(length - len(item_list))])
        return item_list
    else:
        return item_list


# It is necessary to create lists of dictionaries differently
# from lists of integers,
# because if you use the strategy above you get a list where
# every element is the same dict.
def pad_dict_list(item_list, length):
    if len(item_list) < length:
        item_list.extend([dict() for _ in range(length - len(item_list))])
        return item_list
    else:
        return item_list


def export_figure(fig, title, data_directory, experiment, metadata={}):
    fig_metadata = {
        "Comment": "experiment:" + experiment
    }
    fig_metadata.update(metadata)
    filename = data_directory + experiment + "_" + title + ".png"
    fig.savefig(filename, metadata=fig_metadata)


def sequence_to_regex(seq, group=True, name=None):
    # Return a regular expression string to match a DNA sequence.
    # 'N' is changed to '(.)', and a series of consecutive 'N' is changed
    # to '(.{k})', where k is the number of Ns.
    nRegex = regex.compile('N{2,}')
    matches = nRegex.finditer(seq)
    marker = 0
    newSeq = ""
    group_num = 1
    for m in matches:
        group_length = m.span()[1] - m.span()[0]
        if name:
            group_string = "(?P<{name}{num}>.{{{len}}})".format(
                name=name,
                num=group_num,
                len=group_length)
        elif group:
            group_string = "(.{{{len}}})".format(len=group_length)
        else:
            group_string = ".{{{len}}}".format(len=group_length)
        newSeq += seq[marker:m.span()[0]] + group_string
        marker = m.span()[1]
        group_num += 1
        newSeq += seq[marker:]
    return newSeq.replace("N", "(.)")


def common_sequence(seqs):
    # Return a string representing the common sequence of a list of sequences.
    # Letters in the returned string are either A, C, T or G
    # if the letter in that position is the same in all sequences,
    # or N if not.  Sequences must be the same length.

    def elements_equal(element_list):
        if all([x == element_list[0] for x in element_list]):
            return element_list[0]
        else:
            return 'N'

    N = max(map(len, seqs))

    return ''.join(list(map(elements_equal,
                            [[l[i] for l in seqs] for i in range(N)])))


def hamming_distance(s1, s2):
    if len(s1) != len(s2):
        raise ValueError("hamming_distance: string arguments must have the same length")
    return [s1[i] != s2[i] for i in range(len(s1))]
