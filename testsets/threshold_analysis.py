def get_accuracy(threshold=0.1):
    correct_count = 0
    with open('test_set_final_prob.txt') as predictions, open('test_set_ground_truth.txt') as truths:
        for i in xrange(200):
            probabilities = map(float, predictions.readline().strip().split())
            cur_choices = set()
            for j in xrange(8):
                if probabilities[j] > threshold:
                    cur_choices.add(j)
            cur_truth = set(map(int, truths.readline().strip().split()))

            if cur_choices == cur_truth:
                correct_count += 1

    return correct_count / 200.0


if __name__ == '__main__':
    print get_accuracy(0.05)
    print get_accuracy(0.06)
    print get_accuracy(0.07)
    print get_accuracy(0.08)
    print get_accuracy(0.09)
    print get_accuracy(0.1)
    print get_accuracy(0.11)
    print get_accuracy(0.12)
