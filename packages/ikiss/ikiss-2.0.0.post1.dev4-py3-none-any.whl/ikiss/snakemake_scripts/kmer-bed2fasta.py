#!/usr/bin/env python
# coding: utf-8
#from pandas_plink import read_plink1_bin
import argparse
from pathlib import Path, PurePosixPath
import subprocess
from subprocess import PIPE

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
parser.add_argument("-b", "--bed", help="give bed file", type=str)

args = parser.parse_args()
bed = args.bed

bed = Path(bed).resolve()

name = PurePosixPath(bed).stem
dir = PurePosixPath(bed).parent
bed = f"{dir}/{name}.bed"
fam = f"{dir}/{name}.fam"
bim = f"{dir}/{name}.bim"
fasta = f"{dir}/{name}.fasta"

command = ["wc", "-l", f"{bim}"]
shape = subprocess.run(command, stdout=PIPE, stderr=PIPE)
shape = int(str(shape.stdout).strip().split(' ')[0].split('\'')[1])

with open(bim, 'r') as b, open(fasta, 'w') as f:
    for i in range(0, int(shape)):
        kmer = b.readline().rstrip()
        kmer = kmer.split('\t')[1]
        f.write(f">{name}_{i+1}_{kmer}\n{kmer}\n")
