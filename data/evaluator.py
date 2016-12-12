import os
import logging
import argparse

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument('prediction', help='path to prediction file')
parser.add_argument('truth', help='path to ground truth number file')

args = parser.parse_args()

# Ground Truth
ground_truth = {}
with open(args.truth) as reader:
    for line in reader:
        rgb_hash, i_label = line.strip().split()
        ground_truth[rgb_hash] = int(i_label)

# Evaluation

with open(args.prediction) as reader:
    correct_counter = 0
    for i_line, line in enumerate(reader):
        if i_line == 200:
            break
        rgb_hash, i_prediction = eval(line.strip())
        assert rgb_hash in ground_truth
        i_truth = ground_truth[rgb_hash]
        if i_prediction == i_truth:
            correct_counter += 1

logging.warn('Final result: {} / 200 = {}'.format(correct_counter, float(correct_counter) / 200))
