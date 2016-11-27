from PIL import Image
import numpy as np
import os
import math


def calc_perceptual_hash(image_fname, shrunk_size=8, mode='RGB'):
    assert os.path.exists(image_fname)

    # open image
    img = Image.open(image_fname)
    img = img.resize((shrunk_size, shrunk_size))

    if mode == 'RGB':
        img_arr = np.asanyarray(img)
        r_channel, g_channel, b_channel = img_arr[:, :, 0], img_arr[:, :, 1], img_arr[:, :, 2]
        r_mean, g_mean, b_mean = r_channel.mean(), g_channel.mean(), b_channel.mean()
        r_filtered, g_filtered, b_filtered = 1 * (r_channel > r_mean), 1 * (g_channel > g_mean), 1 * (
            b_channel > b_mean)
        r_flatten, g_flatten, b_flatten = map(lambda arr: arr.flatten(), [r_filtered, g_filtered, b_filtered])

        p_hash = np.concatenate((r_flatten, g_flatten, b_flatten))

        return p_hash

    else:

        img_arr = np.asarray(img.convert('L'))
        img_mean = img_arr.mean()
        img_filtered = 1 * (img_arr > img_mean)

        p_hash = img_filtered.flatten()

        return p_hash


def image_diff(img_fname1, img_fname2):
    assert os.path.exists(img_fname1) and os.path.exists(img_fname2)

    phash1, phash2 = map(calc_perceptual_hash, (img_fname1, img_fname2))

    return np.sum(phash1 != phash2)


def calc_num_2_bin_one_count():
    with open('../data/num_2_bin_one_count.csv', 'w') as writer:
        cur_num = 0
        while cur_num < 2 ** 192:
            cur_one_count = sum(map(int, bin(cur_num)[2:]))
            writer.write('{},{}\n'.format(cur_num, cur_one_count))
            cur_num += 1
            if sum(map(int, str(cur_num))) == 1:
                print cur_num


def test():
    print image_diff('../data/bfzw.png', '../data/sxey.png')
    print image_diff('../data/mh.png', '../data/xf.png')
    print image_diff('../data/bfzw.png', '../data/xf.png')
    print image_diff('../data/bfzw.png', '../data/mh.png')
    print image_diff('../data/sxey.png', '../data/mh.png')
    print image_diff('../data/sxey.png', '../data/xf.png')


if __name__ == '__main__':
    test()
    # calc_num_2_bin_one_count()
