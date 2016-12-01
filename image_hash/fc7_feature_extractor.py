import os
import sys
import json
import itertools
import logging

from unqlite import UnQLite
from celery import Celery
from redis import Redis
from PIL import Image
import numpy as np

try:
    from image_hash import calc_perceptual_hash, get_sub_images as get_sub_pillow_images
except ImportError:
    from __init__ import calc_perceptual_hash, get_sub_images as get_sub_pillow_images

# Config logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

db = UnQLite('/data2/haonans/rgb_2_fc7')

# Load RGB hash dictionary and define methods

rgb_mappings_path = '/data2/heqingy/mapping.json'
assert os.path.isfile(rgb_mappings_path)

logging.info('Loading RGB mappings')

with open(rgb_mappings_path) as f:
    rgb_mappings = json.load(f)

logging.info('Complete!')


def get_rgb_key(_org_rgb_hash):
    assert _org_rgb_hash in rgb_mappings['rgb2final'], "[HASH] {} is not found".format(_org_rgb_hash)
    return rgb_mappings['rgb2final'].get(_org_rgb_hash)


# Celery async support

# redis_url = 'redis://localhost:6379'
# assert Redis.from_url(redis_url).ping(), 'Redis server cannot be found'

# app = Celery(broker=redis_url)

# Load and config caffe

caffe_root = '/home/haonans/software/caffe-latest/'
sys.path.insert(0, caffe_root + 'python')

import caffe

caffe.set_device(0)
caffe.set_mode_gpu()

# Load model

model_weights = caffe_root + 'models/bvlc_reference_caffenet/bvlc_reference_caffenet.caffemodel'
model_def = caffe_root + 'models/bvlc_reference_caffenet/deploy.prototxt'

assert os.path.isfile(model_weights), 'Model weights file is not found!'
assert os.path.isfile(model_def), 'Model definition file is not found!'

net = caffe.Net(model_def,  # defines the structure of the model
                model_weights,  # contains the trained weights
                caffe.TEST)  # use test mode (e.g., don't perform dropout)

# Prepare image transformer

# load the mean ImageNet image (as distributed with Caffe) for subtraction
mu = np.load(caffe_root + 'python/caffe/imagenet/ilsvrc_2012_mean.npy')
mu = mu.mean(1).mean(1)  # average over pixels to obtain the mean (BGR) pixel values

# create transformer for the input called 'data'
transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})

transformer.set_transpose('data', (2, 0, 1))  # move image channels to outermost dimension
transformer.set_mean('data', mu)  # subtract the dataset-mean value in each channel
transformer.set_raw_scale('data', 255)  # rescale from [0, 1] to [0, 255]
transformer.set_channel_swap('data', (2, 1, 0))  # swap channels from RGB to BGR

# Prepare for image feature extraction

# set the batch size of the input
net.blobs['data'].reshape(8,  # batch size, number of sub-images
                          3,  # 3-channel (BGR) images
                          227, 227)  # image size is 227x227


# helper function
def get_sub_caffe_images(image):
    """ Get all 8 sub-arrays of a given CAPTCHA image which is loaded with caffe.io.load_image
    :type image: np.ndarray
    :rtype: list (np.ndarray)
    """
    assert isinstance(image, np.ndarray)

    def helper(_image, _i, _j):
        """ Each CAPTCHA array has 8 (2 * 4) sub-arrays,
        this function returns one of the eight at a given location. shape is (67, 67)
        """
        assert 0 <= _i <= 1 and 0 <= _j <= 3

        top = 41 + (67 + 5) * _i
        left = 5 + (67 + 5) * _j
        return _image[top: top + 67, left: left + 67, :]

    return map(lambda (i, j): helper(image, i, j), itertools.product(xrange(2), xrange(4)))


# Main function
# @app.task
def process_captcha(captcha_path):
    """ Given a CAPTCHA path, generate a formatted dict which contains the original path,
    (8, 4096) fc7 features vectors and then the dict is dumpped into a json line and
    appended to a file"""
    assert os.path.exists(captcha_path), '{} does not exist!'.format(captcha_path)
    logging.info('{} is being processed'.format(captcha_path))

    caffe_captcha = caffe.io.load_image(captcha_path)

    sub_caffe_images = get_sub_caffe_images(caffe_captcha)
    transformed_sub_caffe_images = map(lambda img: transformer.preprocess('data', img), sub_caffe_images)

    input_array = np.array(transformed_sub_caffe_images)
    assert input_array.shape == (8, 3, 227, 227)

    net.blobs['data'].data[...] = input_array
    net.forward()

    all_fc7_vectors = np.array(net.blobs['fc7'].data, copy=True)
    assert all_fc7_vectors.shape == (8, 4096)

    # Please use PIL.Image.Image to calc perceptual hash
    pillow_captcha = Image.open(captcha_path)
    sub_pillow_images = get_sub_pillow_images(pillow_captcha)
    all_rgb_hashes = map(lambda img: calc_perceptual_hash(img, 'RGB', True), sub_pillow_images)

    for i, org_rgb_hash in enumerate(all_rgb_hashes):
        rgb_key = get_rgb_key(org_rgb_hash)
        if rgb_key:
            db[rgb_key] = all_fc7_vectors[i, :]
        else:
            logging.error('[LOC] {} [HASH] {} is not found!'.format(i, org_rgb_hash))


def main():
    captcha_dir = '/data2/heqingy/captchas'
    captcha_path_list = '/data2/haonans/captcha_path_list.txt'

    with open(captcha_path_list) as reader:
        for line in reader:
            path = os.path.join(captcha_dir, line.strip())
            # process_captcha.delay(path)
            process_captcha(path)


if __name__ == '__main__':
    main()
