# encoding: UTF-8
from __future__ import unicode_literals


def load_chinese_phrases(path="./phrases/chinese_phrases.txt"):
    chinese_phrases = []
    with open(path) as reader:
        for line in reader:
            # please decode with `utf8`
            chinese_phrases.append(line.strip().split()[0].decode("utf8"))

    print "%s Chinese phrases are loaded" % len(chinese_phrases)
    return chinese_phrases


def text_2_image(text,
                 image_dir_path="./images",
                 font_size=40,
                 left_right_padding=10,
                 up_down_padding=5,
                 does_show=False,
                 does_save=False):
    """ Units are all pixels"""
    import os
    import StringIO
    from PIL import Image  # pip install pillow
    import pygame

    pygame.init()

    if isinstance(text, str):
        text = text.decode("utf8")

    num_characters = len(text)
    width = left_right_padding * 2 + num_characters * font_size
    height = up_down_padding * 2 + font_size  # just one line

    image = Image.new(mode="RGB", size=(width, height), color=(255, 255, 255))

    font_list = ["simsun.ttc", "black.ttf", "youyuan.TTF"]
    font = pygame.font.Font(os.path.join("fonts", font_list[0]), font_size)
    rendered_text = font.render(text, True, (0, 0, 0), (255, 255, 255))

    string_io = StringIO.StringIO()
    pygame.image.save(rendered_text, string_io)
    string_io.seek(0)

    line = Image.open(string_io)
    image.paste(line, (left_right_padding, up_down_padding))

    if does_show:
        image.show()

    if does_save:
        image.save(os.path.join(image_dir_path, "%s.png" % text))


def distort_image(image_dir, image_filename, does_show=False, does_save=False):
    from PIL import Image
    import numpy as np
    import os

    image_path = os.path.join(image_dir, image_filename)
    if not isinstance(image_path, unicode):
        image_path = image_path.decode("utf8")

    image_arr = np.array(Image.open(image_path))

    height, width, _ = image_arr.shape

    # - Vertical shift
    sin_amplitude = height / 3.5
    sin_frequency = 3.0 / width

    def sin_shift(x):
        return sin_amplitude * np.sin(2.0 * np.pi * x * sin_frequency)

    for i in xrange(width):
        image_arr[:, i] = np.roll(image_arr[:, i], int(sin_shift(i)))

    image = Image.fromarray(image_arr)

    if does_show:
        image.show()

    if does_save:
        image.save()


if __name__ == '__main__':
    # phrases = load_chinese_phrases()
    # text_2_image(text="电话机", does_show=True, does_save=True)
    distort_image('./images', '电话机.png', does_show=True)
