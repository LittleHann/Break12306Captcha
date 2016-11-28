from PIL import Image
import numpy as np
import os
import itertools


def calc_perceptual_hash(image, mode):
    """ Functions to calculate perceptual hashes of RGB or GRAY images
    :type image: Image.Image
    :type mode: str
    :rtype: np.ndarray
    """

    def helper(_arr):
        """ A helper function to calculate perceptual hash for a single channel or gray scale"""
        assert isinstance(_arr, np.ndarray) and _arr.shape == (8, 8)
        _arr_mean = _arr.mean()
        _arr_filtered = 1 * (_arr > _arr_mean)  # change bool to 1s and 0s
        _arr_hash = _arr_filtered.flatten()
        return _arr_hash

    # Sanity check
    assert isinstance(image, Image.Image), 'Input param type is wrong!'
    assert mode in {'RGB', 'GRAY'}, '{} mode does not exist!'.format(mode)

    # Open a new image and resize it
    image = image.resize((8, 8))

    if mode == 'GRAY':
        # change RGB images to GRAY
        image_array = np.asarray(image.convert('L'))
        image_hash = helper(image_array)
        return image_hash

    else:  # 'RGB'
        image_array = np.asanyarray(image)

        red_hash = helper(image_array[:, :, 0])
        green_hash = helper(image_array[:, :, 1])
        blue_hash = helper(image_array[:, :, 2])

        image_hash = np.concatenate((red_hash, green_hash, blue_hash))

        return image_hash


def get_sub_images(captcha):
    """ Get all 8 sub-images of a given CAPTCHA
    :type captcha: Image.Image
    :rtype: list (Image.Image)
    """

    # Sanity check
    assert isinstance(captcha, Image.Image)

    def helper(_captcha, _i, _j):
        """ Each CAPTCHA has 8 (2 * 4) sub-images, this function returns one of the eight at a given location"""
        assert 0 <= _i <= 1 and 0 <= _j <= 3

        top = 41 + (67 + 5) * _i
        left = 5 + (67 + 5) * _j

        return _captcha.crop((left, top, left + 67, top + 67))

    return map(lambda (i, j): helper(captcha, i, j), itertools.product(xrange(2), xrange(4)))


def image_diff(img_fname1, img_fname2):
    assert os.path.exists(img_fname1) and os.path.exists(img_fname2)

    phash1, phash2 = map(calc_perceptual_hash, (img_fname1, img_fname2))

    return np.sum(phash1 != phash2)


if __name__ == '__main__':
    # print image_diff('../data/bfzw.png', '../data/sxey.png')
    # print image_diff('../data/mh.png', '../data/xf.png')
    # print image_diff('../data/bfzw.png', '../data/xf.png')
    # print image_diff('../data/bfzw.png', '../data/mh.png')
    # print image_diff('../data/sxey.png', '../data/mh.png')
    # print image_diff('../data/sxey.png', '../data/xf.png')
    # calc_num_2_bin_one_count()
    for image in get_sub_images(Image.open('../data/captcha_0.jpg')):
        # image.show()
        print np.packbits(calc_perceptual_hash(image, 'RGB')), np.packbits(calc_perceptual_hash(image, 'GRAY'))
