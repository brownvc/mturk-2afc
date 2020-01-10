import argparse
import csv
import numpy as np
import os
from random import shuffle
from random import randint


parser = argparse.ArgumentParser(description='Generate input CSV for MTurk 2AFC study')

# In a single HIT, how many comparisons will the Turker make?
parser.add_argument('--n-real-comparisons-per-hit', type=int, default=50)
# How many "vigilance tests" (i.e. 'obvious' comparisons to check if the Turker is paying attention) per HIT?
parser.add_argument('--n-vigilance-tests-per-hit', type=int, default=5)
# How many HITs?
parser.add_argument('--n-hits', type=int, default=10)
# Unique ID so that Turkers can only work on one HIT for any given experiment
# See http://uniqueturker.myleott.com/ for more information about how this works
parser.add_argument('--unique-id', type=str, required=True)
# The name of the experiment
parser.add_argument('--experiment-name', type=str, required=True)
# The name of condition A
parser.add_argument('--conditionA', type=str, required=True)
# The name of condition B
parser.add_argument('--conditionB', type=str, required=True)

args = parser.parse_args()



n_real_comparisons_per_hit = args.n_real_comparisons_per_hit
n_vigilance_tests_per_hit = args.n_vigilance_tests_per_hit
n_comparisons_per_hit = n_real_comparisons_per_hit + n_vigilance_tests_per_hit
n_hits = args.n_hits
experiment_name = args.experiment_name
unique_id = args.unique_ids
conditionA = args.conditionA
conditionB = args.conditionB
# Compute the name of the output csv file
output_loc = '{}_{}-vs-{}.csv'.format(experiment_name, conditionA, conditionB)


#########################################################################################


f = open(output_loc,'w')

first_row = ''

first_row += 'unique_id,'

for comp_idx in range(n_comparisons_per_hit):
	first_row += 'gt_side' + str(comp_idx+1) + ','
	first_row += 'images_left' + str(comp_idx+1) + ','
	first_row += 'images_right' + str(comp_idx+1) + ','	

first_row = first_row[:-1]
first_row += '\n'

f.write(first_row)


conditionA_dir = '{}/{}'.format(experiment_name, conditionA)
conditionB_dir = '{}/{}'.format(experiment_name, conditionB)
vigilance_true_dir = '{}/vigilance_true'.format(experiment_name)
vigilance_random_dir = '{}/vigilance_random'.format(experiment_name)

for hit_idx in range(n_hits):
	row = ''
	row += unique_id + ','
	# Build the list of images for each condition
	images_a = ['{}/{}'.format(conditionA_dir, i) for i in range(1, n_real_comparisons_per_hit+1)]
	images_b = ['{}/{}'.format(conditionB_dir, i) for i in range(1, n_real_comparisons_per_hit+1)]
	# # Randomize order (this randomizes the pairing)
	# shuffle(images_a)
	# shuffle(images_b)
	# Randomize order, but keep pairs intact (so we compare against different conditions of the same item (e.g. mesh, scene, etc.))
	indices = list(range(0, len(images_a)))
	shuffle(indices)
	images_a = [images_a[i] for i in indices]
	images_b = [images_b[i] for i in indices]
	# Pick random indices at which to insert vigilance tests
	# (Insert the true image into images_a, and the false/random image into images_b)
	for v in range(0, n_vigilance_tests_per_hit):
		insert_idx = randint(0, len(images_a)-1)
		vigilance_true_img = '{}/{}'.format(vigilance_true_dir, v+1)
		images_a.insert(insert_idx, vigilance_true_img)
		vigilance_random_img = '{}/{}'.format(vigilance_random_dir, v+1)
		images_b.insert(insert_idx, vigilance_random_img)
	# Add columns for each comparison
	for comp_idx in range(n_comparisons_per_hit):
		image_a = images_a[comp_idx]
		image_b = images_b[comp_idx]
		# Choose whether to put A on the left or on the right
		a_on_left = np.random.choice([0,1])
		if a_on_left:
			# Add gt_side
			row += 'left,'
			# Add images_left
			row += image_a + ','
			# Add images_right
			row += image_b + ','
		else:
			# Add gt_side
			row += 'right,'
			# Add images_left
			row += image_b + ','
			# Add images_right
			row += image_a + ','
	# Write row to file
	row = row[:-1]
	row += '\n'
	f.write(row)

f.close()