import json


def foo():
    with open('../data/labels.txt') as reader:
        labels = map(lambda line: line.strip(), reader)

    with open('fake.txt', 'w') as writer:
        with open('capchat_class_predictions.txt') as lines:
            for line in lines:
                writer.write('{}\n'.format(labels[sorted(
                    map(lambda x: (int(x.split(':')[0]), float(x.split(':')[1])), line.split()[1:]), reverse=True,
                    key=lambda t: t[1])[0][0]]))

    truth = open('truth.txt').readlines()
    fake = open('fake.txt').readlines()

    for i in xrange(50):
        if truth[i] != fake[i]:
            print i + 1


"""
Generate Cassandra database data copy from `mapping.json`
"""

with open('../data/mapping.json') as f:
    mappings = json.load(f)

    with open('rgb_hash_2_key.txt', 'w') as writer:
        for k, v in mappings['rgb2final'].iteritems():
            writer.write('{}\t{}\n'.format(k, v))

    with open('buckets.txt', 'w') as writer:
        for k, v in mappings['buckets'].iteritems():
            writer.write('{}\t{}\n'.format(k, v))
