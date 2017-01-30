import os, json
import numpy as np
from PIL import Image

import path_magic
from image_hash import get_sub_images
from database import get_predictions, get_rgb_key

label_truths = map(lambda line: line.strip(), open('test_set_1_label_truth.txt'))
label_predictions = map(lambda line: line.strip(), open('test_set_1_label_predictions.txt'))
filenames = map(lambda line: line.strip().decode('utf-8'), open('test_set_1_filenames.txt'))

all_obj = []

for i in xrange(163):

    cur_obj = {}

    print '###########'
    print '### {} ###'.format(i + 1)
    print '###########'
    cur_obj['index'] = i + 1

    base_path, label, label_prediction = filenames[i], label_truths[i], label_predictions[i]
    full_path = 'test_set_1/{}'.format(base_path)
    assert os.path.isfile(full_path)

    print base_path, label, label_prediction
    cur_obj['filename'] = base_path
    cur_obj['label truth'] = label_truths[i]
    cur_obj['label prediction'] = label_predictions[i]

    sub_images = get_sub_images(Image.open(full_path))
    rgb_keys = map(get_rgb_key, sub_images)
    all_predictions = map(lambda _k: get_predictions(_k), rgb_keys)
    cur_obj['all predictions'] = all_predictions

    probabilities = []
    for j, predictions in enumerate(all_predictions):
        d = dict(predictions)
        probabilities.append(d.get(label, 0))

        # print j
        # for k, v in predictions:
        #     print k + '\t%.3f' % v

    prob_arr = np.array(probabilities)
    ind = prob_arr.argsort()[::-1]
    cur_obj['final choices'] = []
    for k in xrange(8):
        print ind[k], '\t', prob_arr[ind][k]
        if k == 0 or prob_arr[ind][k] > 0.1:
            cur_obj['final choices'].append([ind[k], prob_arr[ind][k]])

    all_obj.append(cur_obj)

with open('analysis.json', 'wb') as writer:
    json.dump({'analysis': all_obj}, writer, indent=2)

"""
for file in $(ls | grep .jpg | tail -n 40)
do
echo $file;
imgcat $file;
done
"""
