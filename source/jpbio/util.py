# jpbio/util.py

basePair = {'A':'T','T':'A','G':'C','C':'G'}
basePairTrans = str.maketrans(basePair)

def rcDNA(seq):
    return seq.translate(basePairTrans) [::-1]

def cDNA(seq):
   return seq.translate(basePairTrans)

