import os
import sys
import logging

logging.basicConfig(level=logging.INFO)

# All labels

labels_path = 'labels.txt'
assert os.path.isfile(labels_path)
with open(labels_path) as reader:
    labels = map(lambda l: l.strip(), reader)

logging.info('First 5 labels: {}'.format(', '.join(labels[:5])))

# Ground Truth


# Evaluation

prediction_path = 'head_2000.txt'
assert os.path.isfile(prediction_path)

with open(prediction_path) as reader:
    for i_line, line in enumerate(reader):
        rgb_hash, i_prediction = eval(line.strip())
        label_prediction = labels[i_prediction]
