#!/usr/bin/env python3
import argparse
import random
from pathlib import Path

"""
split_bed.py needs number of kmers (int) contained in a bed file (--file-length)
it randomises kmers number and split this random list into several sub-lists
each list will be used to run a PCA using only kmers selected in output list
used for iKISS pipeline
"""
parser = argparse.ArgumentParser(description='Partition a genome into a set of overlapping segments')
parser.add_argument('--list_length', type=int, default=10000)
parser.add_argument('--file_length', type=int, default=10000000)
parser.add_argument('--min_length', type=int, default=5000)
parser.add_argument('--output-name', help="output name")
parser.add_argument('--output-dir', help="output dir")
args = parser.parse_args()

SEGMENT_LENGTH = args.list_length
FILE_LENGTH = args.file_length
MIN_LIST_LENGTH = args.min_length
OUTPUT_NAME = args.output_name
DIR = args.output_dir

# doing a list with random numbers, with duplicates!
#res = [random.randrange(1, FILE_LENGTH, 1) for i in range(FILE_LENGTH)]
res = random.sample(range(1, FILE_LENGTH+1), FILE_LENGTH)

n = SEGMENT_LENGTH

# splitting res in segments. Each element will be used to PCA independently
final = [res[i * n:(i + 1) * n] for i in range((len(res) + n - 1) // n)]

# if last element is less that MIN_LIST_LENGTH, joining two last list and remove last element
if (len(final[-1]) < MIN_LIST_LENGTH) and (len(final) > 1) and (MIN_LIST_LENGTH < SEGMENT_LENGTH):
    #print (len(final[-2]), len(final[-1]), MIN_LIST_LENGTH)
    final[-2] = list(final[-2] + final[-1])
    del final[-1]
    #print (len(final[-1]), MIN_LIST_LENGTH)


# writing each list in a new output txt file (nb files = nb element) compatible with R
i = 0
for elem in final:
    i = i + 1
    Path(DIR).mkdir(parents=True, exist_ok=True)
    with open(f"{DIR}/{i}.txt", "w") as segment:
        vec = []
        for v in elem:
            vec.append(int(v))
        segment.write((str(vec).replace('[', '')).replace(']','').replace("\'",'').replace(',',''))

