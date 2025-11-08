# core.py
import primer3
from .utils import GC_content, Tm, reverse_complement

def evaluate_primer(GC, Tm_val):
    return 40 <= GC <= 60 and 55 <= Tm_val <= 65

def check_hairpin_dimer(seq):
    hairpin = primer3.calcHairpin(seq)
    dimer = primer3.calcHomodimer(seq)
    if hairpin.structure_found and hairpin.dg < -5:
        return False
    if dimer.structure_found and dimer.dg < -5:
        return False
    return True

def generate_primers(dna_seq, primer_length=18):
    primers = []
    dna_seq = dna_seq.upper()
    for i in range(len(dna_seq)-primer_length+1):
        forward = dna_seq[i:i+primer_length]
        reverse = reverse_complement(forward)
        GC_f, Tm_f = GC_content(forward), Tm(forward)
        GC_r, Tm_r = GC_content(reverse), Tm(reverse)
        good_basic = evaluate_primer(GC_f, Tm_f) and evaluate_primer(GC_r, Tm_r)
        good_struct = check_hairpin_dimer(forward) and check_hairpin_dimer(reverse)
        quality = "Good" if good_basic and good_struct else "Bad"
        primers.append({
            "Forward": forward, "GC_F": GC_f, "Tm_F": Tm_f,
            "Reverse": reverse, "GC_R": GC_r, "Tm_R": Tm_r,
            "Quality": quality
        })
    return primers
