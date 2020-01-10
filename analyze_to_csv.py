import argparse
import bootstrapped.bootstrap as bs
import bootstrapped.stats_functions as bs_stats
from collections import defaultdict
import numpy as np
import os
import pandas as pd
import re
import sys


parser = argparse.ArgumentParser(description='Analyze directory of MTurk 2AFC study results')

# In a single HIT, how many comparisons did the Turker make?
parser.add_argument('--n-real-comparisons-per-hit', type=int, default=50)
# How many "vigilance tests" (i.e. 'obvious' comparisons to check if the Turker is paying attention) per HIT?
parser.add_argument('--n-vigilance-tests-per-hit', type=int, default=5)
# If a Turker gets below this percentage of vigilance tests correct, throw out their responses
parser.add_argument('--vigilance-threshold', type=float, default=0.0)
# Directory containing CSV files to analyze
parser.add_argument('--in-dir', type=str, required=True)
# Name of output file to write
parser.add_argument('--out-filename', type=str, default='analysis.csv')

args = parser.parse_args()


n_comparisons = args.n_real_comparisons_per_hit + args.n_vigilance_tests_per_hit
n_vigilance = args.n_vigilance_tests_per_hit
vigilance_threshold = args.vigilance_threshold
in_dir = args.in_dir
out_filename = args.out_filename


def analyze(loc, n_bootstrap_samples=10000, alpha=0.050):

	df = pd.read_csv(loc)

	# Figure out how many hits there are by looking at one of the fields
	n_hits = len(df['Input.gt_side1'])

	# Keep track of how each worker does on vigilance tests
	worker_vigilance = defaultdict(int)
	for i in range(n_comparisons):
		gt_sides = df['Input.gt_side' + str(i+1)]
		choice = df['Answer.selection' + str(i+1)]
		im_left = df['Input.images_left' + str(i+1)]
		im_right = df['Input.images_right' + str(i+1)]
		for j in range(n_hits):
			if ('vigilance' in im_left[j]) or ('vigilance' in im_right[j]):
				this_gt_side = gt_sides[j]
				this_choice = choice[j]
				worker_vigilance[j] += int(this_gt_side == this_choice)
	# Print worker accuracy on vigilance tests:
	num_workers_passed = 0
	for worker_id in worker_vigilance:
		worker_vigilance[worker_id] = float(worker_vigilance[worker_id])/n_vigilance
		print('Worker ID, vigilance: ', worker_id, worker_vigilance[worker_id])
		if worker_vigilance[worker_id] >= vigilance_threshold:
			num_workers_passed += 1
	print("Num workers passed vigilance threshold: " + str(num_workers_passed))

	# Now record actual comparison stats
	values = []
	for i in range(n_comparisons):
		gt_sides = df['Input.gt_side' + str(i+1)]
		choice = df['Answer.selection' + str(i+1)]
		im_left = df['Input.images_left' + str(i+1)]
		im_right = df['Input.images_right' + str(i+1)]
		for j in range(n_hits):
			# Skip workers that didn't pass enough vigilance tests
			if worker_vigilance[j] < vigilance_threshold:
				continue
			# Only record values that don't come from vigilance tests
			if ('vigilance' in im_left) or ('vigilance' in im_right):
				continue
			this_gt_side = gt_sides[j]
			this_choice = choice[j]
			values.append(int(this_gt_side == this_choice))

	# Convert to np array
	values = np.array(values)

	# Do bootstrap
	samples = []
	for _ in range(n_bootstrap_samples):
		# Sample values with replacement
		this_bs_sample = np.random.choice(values, replace=True, size=len(values))
		samples.append(np.mean(this_bs_sample))

	samples = np.array(samples)
	mean = np.mean(samples)
	stdev = np.std(samples)
	# Compute confidence intervals
	# https://en.wikipedia.org/wiki/Bootstrapping_(statistics)#Methods_for_bootstrap_confidence_intervals
	# Using the first one (basic bootstrap) in above link
	low = 2 * mean - np.percentile(samples, 100 * (1 - alpha / 2.))
	high = 2 * mean - np.percentile(samples, 100 * (alpha / 2.))

	print('mean, stdev, low, high: ', mean, stdev, low, high)

	# Compare with the package for sanity check
	print('mean, conf interval: ', bs.bootstrap(values, stat_func=bs_stats.mean, alpha=alpha, iteration_batch_size=values.size, num_iterations=n_bootstrap_samples))

	return mean, stdev, low, high, num_workers_passed


'''
Analyze a whole directory of batch result .csv's and write the results to another
   .csv (so we can put that into Tableau/whatever)
'''
def analyze_to_csv(in_dir, out_filename):
	outfile = open(out_filename, 'w')
	header = 'experiment_name,conditionA,conditionB,mean,stdev,ci_low,ci_high,num_workers,num_samples\n'
	outfile.write(header)

	files = [f for f in os.listdir(in_dir) if f.endswith('.csv')]
	for fname in files:
		m = re.search('(.*)_(.*)_vs_(.*).csv', fname)
		experiment_name = m.group(1)
		conditionA = m.group(2)
		conditionB = m.group(3)
		fpath = os.path.join(in_dir, fname)
		mean, stdev, low, high, num_workers_passed = analyze(fpath, n_comparisons, n_vigilance, vigilance_threshold)
		num_samples = num_workers_passed * (n_comparisons - n_vigilance)
		outfile.write(','.join([experiment_name, conditionA, conditionB, str(mean), str(stdev), str(low), str(high), str(num_workers_passed), str(num_samples) , '\n']))
	outfile.close()


analyze_to_csv(in_dir, out_filename)