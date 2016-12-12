import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('prediction')
args = parser.parse_args()

ground_truth = {}
with open('ground_truth.number') as reader:
    for line in reader:
        rgb_hash, label = line.strip().split()
        ground_truth[rgb_hash] = label

with open('labels.txt') as reader:
    labels = map(lambda line: line.strip(), reader)

top1_count = top3_count = top5_count = 0

assert os.path.isfile(args.prediction)
with open(args.prediction) as reader:
    for i, line in enumerate(reader):
        rgb_hash, _predictions = line.split('\t')
        predictions = map(lambda t: labels.index(t[0]), eval(_predictions))
        print predictions
        if rgb_hash in ground_truth:
            true_label = ground_truth[rgb_hash]
            if true_label in predictions[:5]:
                top5_count += 1
            if true_label in predictions[:3]:
                top3_count += 1
            if true_label in predictions[:1]:
                top1_count += 1
            print rgb_hash, true_label, " ".join(predictions[:5])
print 'Top 1: {} / 200 = {}'.format(top1_count, top1_count / 200.0)
print 'Top 3: {} / 200 = {}'.format(top3_count, top3_count / 200.0)
print 'Top 5: {} / 200 = {}'.format(top5_count, top5_count / 200.0)
