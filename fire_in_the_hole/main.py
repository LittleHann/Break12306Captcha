# encoding: UTF-8

import os

from PIL import Image
import numpy as np

import path_magic
from image_hash import get_sub_images
from database import get_predictions, get_rgb_key

truths = map(lambda line: line.strip(), open('truth.txt'))
filenames = map(lambda line: line.strip().decode('utf-8'), open('filenames.txt'))

for i in xrange(70):
    print '--{}--'.format(i + 1)
    base_path, label = filenames[i], truths[i]
    full_path = '../data/download/{}'.format(base_path)
    assert os.path.isfile(full_path)

    sub_images = get_sub_images(Image.open(full_path))
    rgb_keys = map(get_rgb_key, sub_images)

    print base_path, label

    all_predictions = map(lambda k: get_predictions(k), rgb_keys)
    probabilities = []
    for i, predictions in enumerate(all_predictions):
        # print i
        # for k, v in predictions:
        #    print k + '\t%.3f' % v

        d = dict(predictions)
        probabilities.append(d.get(label, 0))
    prob_arr = np.array(probabilities)

    ind = prob_arr.argsort()[::-1]
    print ind[:4]
    print prob_arr[ind][:4]
    print

"""
for file in $(ls | grep .jpg | tail -n 40)
do
echo $file;
imgcat $file;
done
"""
