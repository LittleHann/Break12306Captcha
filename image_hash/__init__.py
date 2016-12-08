from PIL import Image, ImageFilter
import numpy as np
import itertools


def calc_perceptual_hash(image, mode, return_hex_str=False, gray_size=6, rgb_size=8):
    """ Functions to calculate perceptual hashes of RGB or GRAY images
    :type image: Image.Image
    :type mode: str
    :type return_hex_str: bool
    :rtype: np.ndarray
    """

    def vec_to_hex(vec):
        """ len(vec) == 64 or 192, thus after packing bits, len(vec) == 8 or 24.
        format(255, '02x') == 'ff', thus for any integer `x` between 0 and 255 (1 byte == 8 bits),
        format(x, '02x').__len__() == 2

        Basically, a vec of bits (ones or zeroes) is shrunk to 1/4 of its original length"""
        vec = np.packbits(vec)
        return "".join(map(lambda x: format(x, '02x'), vec))

    def helper(_arr):
        """ A helper function to calculate perceptual hash for a single channel or gray scale"""
        assert isinstance(_arr, np.ndarray) # and （_arr.shape == (size, size)）
        _arr_mean = _arr.mean()
        _arr_filtered = 1 * (_arr > _arr_mean)  # change bool to 1s and 0s
        _arr_hash = _arr_filtered.flatten()
        return _arr_hash

    # Sanity check
    assert isinstance(image, Image.Image), 'Input param type is wrong!'
    assert mode in {'RGB', 'GRAY'}, '{} mode does not exist!'.format(mode)

    # Open a new image and resize it
    image = image.resize((rgb_size, rgb_size)) if mode == "RGB" \
                else image.resize((gray_size, gray_size))

    if mode == 'GRAY':
        # change RGB images to GRAY
        image_array = np.asarray(image.convert('L'))
        image_hash = helper(image_array)
        return vec_to_hex(image_hash) if return_hex_str else image_hash

    else:  # mode == "RGB":
        image_array = np.asanyarray(image)

        red_hash = helper(image_array[:, :, 0])
        green_hash = helper(image_array[:, :, 1])
        blue_hash = helper(image_array[:, :, 2])

        image_hash = np.concatenate((red_hash, green_hash, blue_hash))
        return vec_to_hex(image_hash) if return_hex_str else image_hash


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

        im = _captcha.crop((left, top, left + 67, top + 67))
        return im.filter(ImageFilter.MedianFilter(size=1))

    # >>> list(itertools.product(xrange(2), xrange(4)))
    # [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (1, 3)]
    return map(lambda (i, j): helper(captcha, i, j),
               itertools.product(xrange(2), xrange(4)))


if __name__ == '__main__':
    for img in get_sub_images(Image.open('../data/captcha_0.jpg')):
        # img.show()
        print np.packbits(calc_perceptual_hash(img, 'RGB')), np.packbits(calc_perceptual_hash(img, 'GRAY'))
