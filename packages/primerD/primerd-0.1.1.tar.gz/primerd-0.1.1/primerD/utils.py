# utils.py
def GC_content(seq):
    return (seq.count("G")+seq.count("C"))/len(seq)*100 if len(seq)>0 else 0

def Tm(seq):
    return 4*(seq.count("G")+seq.count("C")) + 2*(seq.count("A")+seq.count("T"))

def reverse_complement(seq):
    complement = {'A':'T','T':'A','G':'C','C':'G'}
    return ''.join(complement.get(base,base) for base in seq[::-1])
