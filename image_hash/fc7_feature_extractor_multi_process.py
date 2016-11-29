import os
import sys
import json
import itertools
import logging

import numpy as np

# Config logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

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
def get_sub_images(image):
    """ Get all 8 sub-arrays of a given CAPTCHA image which is loaded with caffe.io.load_image
    :type arr: np.ndarray
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
def process_captcha(captcha_path, writer):
    """ Given a CAPTCHA path, generate a formatted dict which contains the original path,
    (8, 4096) fc7 features vectors and then the dict is dumpped into a json line and
    appended to a file"""
    assert os.path.exists(captcha_path), '{} does not exist!'.format(captcha_path)
    captcha = caffe.io.load_image(captcha_path)

    sub_images = get_sub_images(captcha)
    transformed_sub_images = map(lambda img: transformer.preprocess('data', img), sub_images)

    input_array = np.array(transformed_sub_images)
    assert input_array.shape == (8, 3, 227, 227)

    net.blobs['data'].data[...] = input_array
    output = net.forward()

    all_fc7_vectors = np.array(net.blobs['fc7'].data, copy=True)
    assert all_fc7_vectors.shape == (8, 4096)

    data = dict()
    data['path'] = captcha_path
    data['fc7'] = all_fc7_vectors.tolist()

    writer.write(json.dumps(data) + '\n')


def worker(i_worker):
    assert 0 <= i_worker < 4

    captcha_dir = '/data2/heqingy/captchas'
    captcha_path_list = '/data2/haonans/captcha_path_list.txt'

    output_path = '/data2/haonans/worker_{}.json'.format(i_worker)

    with open(captcha_path_list) as reader:
        with open(output_path, 'w') as writer:
            for i_line, line in enumerate(reader):
                if i_line % i_worker == 0:
                    path = os.path.join(captcha_dir, line.strip())
                    process_captcha(path, writer)
                    logging.info('{} is done'.format(path))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('i_worker', type=int, help='GPU ID')

    args = parser.parse_args()

    worker(args.i_worker)
