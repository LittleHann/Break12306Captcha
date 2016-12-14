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
