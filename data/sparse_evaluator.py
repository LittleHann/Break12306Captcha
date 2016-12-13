from pyspark.mllib.linalg import SparseVector

import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('prediction')
args = parser.parse_args()

ground_truth = {}
with open('ground_truth.number') as reader:
    for line in reader:
        rgb_hash, label = line.strip().split()
        ground_truth[rgb_hash] = int(label)

with open('labels.txt') as reader:
    labels = map(lambda line: line.strip(), reader)

top1_count = top3_count = top5_count = top7_count = 0
count = 0
assert os.path.isfile(args.prediction)
with open(args.prediction) as reader:
    for i, line in enumerate(reader):
        rgb_hash, prob = eval(line.strip())

        if i == 200:
            break

        predictions = prob.toArray().argsort()[-10:]

        if rgb_hash in ground_truth:
            count += 1
            true_label = ground_truth[rgb_hash]
            if true_label in predictions[-7:]:
                top7_count += 1
            if true_label in predictions[-5:]:
                top5_count += 1
            if true_label in predictions[-3:]:
                top3_count += 1
            if true_label in predictions[-1:]:
                top1_count += 1

print 'Top 1: {} / {} = {}'.format(top1_count, count, top1_count / 200.0)
print 'Top 3: {} / {} = {}'.format(top3_count, count, top3_count / 200.0)
print 'Top 5: {} / {} = {}'.format(top5_count, count, top5_count / 200.0)
print 'Top 7: {} / {} = {}'.format(top7_count, count, top7_count / 200.0)
