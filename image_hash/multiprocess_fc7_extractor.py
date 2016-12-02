import json
import os
import sys
import itertools
import logging
import numpy as np

from multiprocessing import Process

# -------
# logging
# -------


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')


def get_sub_caffe_images(image):
    """ Get all 8 sub-arrays of a given CAPTCHA image(numpy array) which is loaded with caffe.io.load_image
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


def worker(i_worker, num_workers, rgb_mappings, precomputed_hashes):
    # -----
    # Caffe
    # -----

    # Load and set up caffe, BTW, please use caffe-latest environment
    caffe_root = '/home/haonans/software/caffe-latest/'
    sys.path.insert(0, caffe_root + 'python')

    import caffe

    # There are 4 GPUs in totoal
    caffe.set_device(i_worker % 4)
    caffe.set_mode_gpu()

    # Load CaffeNet model
    model_weights = caffe_root + 'models/bvlc_reference_caffenet/bvlc_reference_caffenet.caffemodel'
    model_def = caffe_root + 'models/bvlc_reference_caffenet/deploy.prototxt'

    assert os.path.isfile(model_weights), 'Model weights file is not found!'
    assert os.path.isfile(model_def), 'Model definition file is not found!'

    net = caffe.Net(model_def,  # defines the structure of the model
                    model_weights,  # contains the trained weights
                    caffe.TEST)  # use test mode (e.g., don't perform dropout)

    # -----------------
    # Image transformer
    # -----------------

    # load the mean ImageNet image (as distributed with Caffe) for subtraction
    mu = np.load(caffe_root + 'python/caffe/imagenet/ilsvrc_2012_mean.npy')
    mu = mu.mean(1).mean(1)  # average over pixels to obtain the mean (BGR) pixel values

    # create transformer for the input called 'data'
    transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})

    transformer.set_transpose('data', (2, 0, 1))  # move image channels to outermost dimension
    transformer.set_mean('data', mu)  # subtract the dataset-mean value in each channel
    transformer.set_raw_scale('data', 255)  # rescale from [0, 1] to [0, 255]
    transformer.set_channel_swap('data', (2, 1, 0))  # swap channels from RGB to BGR

    # -------------------
    # Config the CaffeNet
    # -------------------

    # set the batch size of the input
    batch_size = 100
    net.blobs['data'].reshape(batch_size,  # batch size, number of sub-images
                              3,  # 3-channel (BGR) images
                              227, 227)  # image size is 227x227

    # ----------------------
    # Fc7 feature extraction
    # ----------------------

    def calc_fc7_vectors(input_array):
        """ Run the forward algorithm and return computed fc7 feature vectors"""
        assert input_array.shape == (batch_size, 3, 227, 227)

        net.blobs['data'].data[...] = input_array
        net.forward()

        all_fc7_vectors = np.array(net.blobs['fc7'].data, copy=True)
        assert all_fc7_vectors.shape == (batch_size, 4096)

        return all_fc7_vectors

    # Destination file
    writer = open('/home/haonans/capstone/database/text_db_worker_{}.txt'.format(i_worker), 'w')

    # avoid processing duplicate rgb_keys
    processed_keys = set()

    captcha_dir = '/ssd/data/captchas'
    captcha_path_list = '/ssd/data/filelist.txt'

    with open(captcha_path_list) as reader:

        image_queue, rgb_queue = [], []

        def process_queue(_image_queue, _rgb_queue):
            assert len(_image_queue) == len(_rgb_queue)
            # padding to fit the batch size
            _transformed_queue = map(lambda img: transformer.preprocess('data', img), _image_queue)
            _image_batch_input = np.concatenate((np.array(_transformed_queue),
                                                 np.zeros((batch_size - len(_image_queue), 3, 227, 227))),
                                                axis=0)
            _fc7_vectors = calc_fc7_vectors(_image_batch_input)
            for _i in xrange(len(_image_queue)):
                writer.write(json.dumps({'rgb_key': _rgb_queue[_i], 'fc7': _fc7_vectors[_i, :].tolist()}) + '\n')

        for _, line in enumerate(reader):
            # each line -> a image source/filename

            # get rgb_hashes for the 8 images of the current captcha
            source = line.strip()
            try:
                rgb_hashes = precomputed_hashes[source]['rgb']
            except KeyError as e:
                logging.error(e)
                continue

            # get corresponding rgb_keys
            rgb_keys = map(rgb_mappings.__getitem__, rgb_hashes)

            # Load the current captcha using caffe
            path = os.path.join(captcha_dir, source)
            try:
                captcha = caffe.io.load_image(path)
            except IOError as e:
                logging.error(e)
                continue

            # segment the captcha into 8 sub-images
            sub_images = get_sub_caffe_images(captcha)
            # image transformation are going to be done before feeding data into CaffeNet

            for i in xrange(8):
                # Q1. should the current sub-image be processed by the current worker?
                # Q2. if so, has the current sub-image be processed by the current worker?
                cur_rgb_key = rgb_keys[i]
                cur_sub_image = sub_images[i]
                if hash(cur_rgb_key) % num_workers == i_worker and cur_rgb_key not in processed_keys:
                    processed_keys.add(cur_rgb_key)
                    rgb_queue.append(rgb_keys[i])
                    image_queue.append(cur_sub_image)

            assert len(rgb_queue) == len(image_queue)
            if len(image_queue) > batch_size - 8:
                process_queue(image_queue, rgb_queue)
                image_queue, rgb_queue = [], []

        if image_queue:
            process_queue(image_queue, rgb_queue)

    writer.close()


def load_precomputed_hashes(path='/ssd/data/txt_captchas.txt'):
    assert os.path.isfile(path)

    computed_hashes = {}
    with open(path) as f:
        for line in f:
            items = line.strip().split()

            source = items[0]
            gray_hashes = [items[1 + 2 * i] for i in xrange(8)]
            rgb_hashes = [items[2 + 2 * i] for i in xrange(8)]

            computed_hashes[source] = {'gray': gray_hashes, 'rgb': rgb_hashes}
    return computed_hashes


def load_rgb_mappings(path='/ssd/data/mapping.json'):
    assert os.path.isfile(path)

    with open(path) as f:
        rgb_mappings = json.load(f)['rgb2final']
    return rgb_mappings


def multi_process(num_workers, i_start, i_end):
    assert 0 <= i_start <= i_end <= num_workers - 1
    logging.info('Loading pre-computed RGB hashes')
    # Load pre-computed gray-scale and RGB hashes
    precomputed_hashes = load_precomputed_hashes()

    logging.info('Loading pre-compute RGB mappings')
    # Load RGB hash dictionary and define methods
    rgb_mappings = load_rgb_mappings()

    processes = []
    for i_worker in xrange(i_start, i_end + 1):
        processes.append(
            Process(target=worker, args=(i_worker, num_workers, rgb_mappings, precomputed_hashes)))

    for p in processes:
        p.start()
    for p in processes:
        p.join()


def main():
    """ Parse arguments and run processes """
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('num_workers', type=int, help='number of total workers')
    parser.add_argument('i_start', type=int, help='i_worker >= i_start')
    parser.add_argument('i_stop', type=int, help='i_worker <= i_end')

    args = parser.parse_args()
    num_workers = args.num_workers
    i_start = args.i_start
    i_stop = args.i_stop

    multi_process(num_workers, i_start, i_stop)


if __name__ == '__main__':
    main()
