import pandas as pd
import numpy as np
import bootstrapped.bootstrap as bs
import bootstrapped.stats_functions as bs_stats
from collections import defaultdict

n_comparisons = 55
# n_vigilance = 5
# vigilance_threshold = 1.0 # If worker vigilance below this, filter out
n_vigilance = 0
vigilance_threshold = 0.0

'''
'''
def analyze(loc, n_comparisons, n_vigilance, vigilance_threshold, n_bootstrap_samples=10000, alpha=0.050):

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



if __name__ == '__main__':

	# loc = 'results_bedroom.csv'
	# loc = 'results_kitchen.csv'
	# loc = 'results_office.csv'
	# loc = 'results_living.csv'
	loc = 'pilot2/results_toilet.csv'

	analyze(loc, n_comparisons, n_vigilance, vigilance_threshold)