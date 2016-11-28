from image_hash import *
import os
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

image_dir = '../../../Downloads/subimages/'
assert os.path.exists(image_dir)
image_paths = os.listdir(image_dir)


# there are 4312 sub-images from 539 CAPTCHAs in total.

def hamming_dist(hash1, hash2):
    assert isinstance(hash1, np.ndarray) and isinstance(hash2, np.ndarray)
    return np.sum(hash1 != hash2)


def test1():
    gray_hash_buckets = defaultdict(list)
    for cur_path in image_paths:
        # The gray_hash needs to be hashable
        gray_hash = ''.join(map(str, calc_perceptual_hash(os.path.join(image_dir, cur_path), mode='GRAY')))
        rgb_hash = calc_perceptual_hash(os.path.join(image_dir, cur_path), mode='RGB')

        for _rgb_hash in gray_hash_buckets[gray_hash]:
            if hamming_dist(rgb_hash, _rgb_hash) < 10:
                break
        else:
            # If we cannot find any "similar" images inside
            gray_hash_buckets[gray_hash].append(rgb_hash)

    print sum(map(len, gray_hash_buckets.values())) / float(len(image_paths))
    # 0.849953617811


def test2():
    gray_hash_path_buckets = defaultdict(list)
    for cur_path in image_paths:
        # The gray_hash needs to be hashable
        gray_hash = ''.join(map(str, calc_perceptual_hash(os.path.join(image_dir, cur_path), mode='GRAY')))
        rgb_hash = calc_perceptual_hash(os.path.join(image_dir, cur_path), mode='RGB')

        for prev_path in gray_hash_path_buckets[gray_hash]:
            _rgb_hash = calc_perceptual_hash(os.path.join(image_dir, prev_path))
            if hamming_dist(rgb_hash, _rgb_hash) < 10:
                # print cur_path, prev_path
                cur_image = Image.open(os.path.join(image_dir, cur_path))
                prev_image = Image.open(os.path.join(image_dir, prev_path))
                # plt.figure()
                plt.subplot(1, 2, 1)
                plt.imshow(cur_image)
                plt.subplot(1, 2, 2)
                plt.imshow(prev_image)
        else:
            # If we cannot find any "similar" images inside
            gray_hash_path_buckets[gray_hash].append(cur_path)

    print sum(map(len, gray_hash_path_buckets.values())) / float(len(image_paths))
    # 0.849953617811


test2()
