import os
import logging

logging.basicConfig(level=logging.INFO)

# Ground Truth
ground_truth = {}
with open('ground_truth.number') as reader:
    for line in reader:
        rgb_hash, i_label = line.strip().split()
        ground_truth[rgb_hash] = int(i_label)

# Evaluation
prediction_path = 'head_2000.txt'
assert os.path.isfile(prediction_path)

with open(prediction_path) as reader:
    correct_counter = 0
    for i_line, line in enumerate(reader):
        rgb_hash, i_prediction = eval(line.strip())
        assert rgb_hash in ground_truth
        i_truth = ground_truth[rgb_hash]
        if i_prediction == i_truth:
            correct_counter += 1

logging.warn('Final result: {} / 200 = {}'.format(correct_counter, float(correct_counter) / 200))
