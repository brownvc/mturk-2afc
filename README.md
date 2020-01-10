# mturk-2afc
Rudimentary framework for running two-alternative forced choice (2AFC) perceptual studies on Mechanical Turk

## The Mechanical Turk Process

If you've never used Mechanical Turk (MTurk) before, the procedure goes something like this:
1. Go to [https://www.mturk.com](https://www.mturk.com) and sign in as a requester
2. Create a "human intelligence task," or "HIT." MTurk's web interface has utilities for setting these up. Part of the process involves deciding how much money you'll pay each worker for completing each task.
3. Make sure you've got enough money in your account to pay for the HITs you are planning to deploy.
4. Design the web layout for your HIT. MTurk has some rudimentary WYSIWYG tools for this, and you can also edit raw HTML.
5. Pass input data (e.g. the set of images that workers should look at) into your HIT via a CSV file that you upload via the MTurk web interface
6. Launch your HITs and wait for workers to complete them.
7. Approve the completed HITs (which releases funds to the workers)
8. Download the results and analyze them

This repository contains utilities that help you create the layout and input files, and to analyze the results, of HITs that involve performing 2AFC perceptual studies.

## Setup

Check out the repo. Make sure you are in an environment with Python 3 (not Python 2), and install the dependencies by running `pip install -r requirements.txt`.

## Contents of this Repository

This repository contains the following scripts (read the `argparse` blocks at the top of the respective files to get a sense for the input arguments they expect):
* `generate_hit_html.py`: creates the HTML that you can paste into the MTurk web interface to create the layout of your HIT. We need to generate it, rather than just provide static HTML, because MTurk passes input data to the HTML via a special templating system (i.e. we need to write certain string literals into the HTML that MTurk expects).
* `generate_amt_input.py`: creates the CSV file that you upload to MTurk before deploying a group of HITs. This CSV contains the data needed for all of the comparisons you want workers to perform (e.g. which pairs of images to show)
* `analyze_to_csv.py`: takes a directory of CSV results files from MTurk HITs and analyzes them, returning the mean, standard deviation, and upper and lower 95% confidence intervals for "How often is condition A chosen over condition B?" Writes its results to a CSV file to make it easy to plug directly into plots, etc.
* `rank_comparisons.py`: takes a single MTurk results CSV file and returns a list of (comparison_image_name, frequency_with_which_conditionA_was_chosen), sorted by decreasing order of frequency. This is useful if you want to inspect which images a particular condition are doing well/poorly at "fooling" people.

## Suggested Workflow

One way to use the scripts above:
1. Use `generate_hit_html.py` to generate the layout HTML for your HIT.
2. Generate/gather the images you'll be asking workers to look at. You'll need to put these somewhere on the web (so that the HIT HTML can access them). An Amazon S3 bucket is one option (make sure that the bucket contents are set to be publicly visible). Note that the scripts here expect the images to be named according to the following convention: `image_root_url/experiment_name/condition_name/<1-based_index>.png`.
3. For each experiment you want to run, use `generate_amt_input.py` to create the CSV file that lists the image pairs to be shown.
4. Log into MTurk (you can use the lab account; see below) and design a HIT for the experiment you want to run. Paste your generated HTML in to the layout.
5. Ensure that you have enough money for your HITs (see below)
6. Upload your input data CSV and launch the HITs.
7. Periodically check progress on your HITs. When they're all done, download the results summary CSV for each.
8. Use `analyze_to_csv.py` to spit out summary statistics of all the experiments

## Credentials and Funding

Daniel has an MTurk requester account that you can use; ask him for the credentials.

If you need to add more funds to the account to run new experiments, ask Daniel and he will do that for you.

If you're wondering what settings to use for your HIT, especially how much to pay workers, these are the settings that Daniel has used for past 2AFC studies:

![HIT settings screenshot](https://raw.githubusercontent.com/brownvc/mturk-2afc/master/hit_settings.png?token=AARAMRTRNRSEISR6Q3X67B26EIUPG)

## Acknowledgments

The HTML template used here is based on one created by Phillip Isola (original can be found in [this repo](https://github.com/phillipi/AMT_Real_vs_Fake))
