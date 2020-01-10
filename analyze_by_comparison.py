import argparse
from collections import Counter
import numpy as np
import os
import pandas as pd

parser = argparse.ArgumentParser(description='Rank-order each comparison by how frequently turkers chose the "ground truth" condition')

# In a single HIT, how many comparisons did the Turker make?
parser.add_argument('--n-real-comparisons-per-hit', type=int, default=50)
# How many "vigilance tests" (i.e. 'obvious' comparisons to check if the Turker is paying attention) per HIT?
parser.add_argument('--n-vigilance-tests-per-hit', type=int, default=5)
# How many HITs?
parser.add_argument('--n-hits', type=int, default=10)
# Name of CSV file to analyze
parser.add_argument('--in-filename', type=str, required=True)
# Name of output file to write
parser.add_argument('--out-filename', type=str, default='comparison_ranking.txt')

args = parser.parse_args()


n_comparisons = args.n_real_comparisons_per_hit + args.n_vigilance_tests_per_hit
n_hits = args.n_hits
loc = args.in_filename

df = pd.read_csv(loc)

# Comparisons are identifed by the image name of the our method image
comparison_to_freq = Counter()
for i in range(n_comparisons):
	gt_sides = df['Input.gt_side' + str(i+1)]
	choice = df['Answer.selection' + str(i+1)]
	im_left = df['Input.images_left' + str(i+1)]
	im_right = df['Input.images_right' + str(i+1)]
	for j in range(n_hits):
		# Skip vigilance tests, if there are any
		if ('vigilance' in im_left) or ('vigilance' in im_right):
			continue
		comparison_name = im_left[j] if gt_sides[j] == 'left' else im_right[j]
		if choice[j] == gt_sides[j]:
			comparison_to_freq[comparison_name] = comparison_to_freq[comparison_name] + 1
		else:
			# Do '+ 0' to make sure that the counter has an entry for things that are never chosen
			comparison_to_freq[comparison_name] = comparison_to_freq[comparison_name] + 0

ordered_pairs = comparison_to_freq.most_common()
f = open(args.out_filename, 'w')
for pair in ordered_pairs:
	line = '{}: {}'.format(pair[0], pair[1]/float(n_hits))
	print(line)
	f.write(line + '\n')
f.close()