# encoding: UTF-8

import os
import numpy as np
from PIL import Image

import path_magic
from image_hash import get_sub_images
from database import get_predictions, get_rgb_key

truths = map(lambda line: line.strip(), open('test_set_1_label_truth.txt'))
filenames = map(lambda line: line.strip().decode('utf-8'), open('test_set_1_filenames.txt'))

for i in xrange(163):

    print '###########'
    print '### {} ###'.format(i + 1)
    print '###########'

    base_path, label = filenames[i], truths[i]
    full_path = 'test_set_1/{}'.format(base_path)
    assert os.path.isfile(full_path)

    print base_path, label

    sub_images = get_sub_images(Image.open(full_path))
    rgb_keys = map(get_rgb_key, sub_images)
    all_predictions = map(lambda k: get_predictions(k), rgb_keys)

    probabilities = []
    for j, predictions in enumerate(all_predictions):
        d = dict(predictions)
        probabilities.append(d.get(label, 0))

        # print j
        # for k, v in predictions:
        #    print k + '\t%.3f' % v

    prob_arr = np.array(probabilities)

    ind = prob_arr.argsort()[::-1]
    for k in xrange(4):
        print ind[k], '\t', prob_arr[ind][k]

    # print ind[:4]
    # print prob_arr[ind][:4]
    # print

"""
for file in $(ls | grep .jpg | tail -n 40)
do
echo $file;
imgcat $file;
done
"""
