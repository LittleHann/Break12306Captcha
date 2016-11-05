# encoding: UTF-8
from __future__ import unicode_literals
import random
import string


def get_random_string(length=5):
    return unicode("".join([random.choice(string.uppercase \
                                          + string.lowercase \
                                          + string.digits)
                            for i in range(length)]))


def add_noise_to_phrase(phrase):
    """
    Args
        phrase: Chinese phrase encoded in UTF8
    Return
        A Chinese phrase added with noise
    """
    prob_noise = 0.2
    if random.random() > prob_noise:
        return phrase
    noise_char = list(u'''~·^*-_" `',."''')
    phrase = list(phrase)
    length = len(phrase)
    pos = random.randint(0, length)  # [0, length] inclusive
    # print "before", phrase
    phrase.insert(pos, random.sample(noise_char, 1)[0])
    # print "after", phrase
    return unicode(u"".join(phrase))


def load_chinese_phrases(path="./labels.txt"):
    chinese_phrases = []
    with open(path) as reader:
        for line in reader:
            # please decode with `utf8`
            chinese_phrases.append(line.strip().split()[0].decode("utf8"))
    print "%s Chinese phrases are loaded" % len(chinese_phrases)
    return chinese_phrases


def text_2_distorted_image(text,
                           image_dir_path="./images",
                           font_size=20,
                           left_right_padding=10,
                           up_down_padding=5,
                           noise_char=True,
                           show=False,
                           save=False):
    """ Units are all pixels"""
    import os
    import StringIO
    from PIL import Image  # pip install pillow
    import pygame
    import numpy as np
    pygame.init()

    if isinstance(text, str):
        text = text.decode("utf8")

    original_text = text
    text = add_noise_to_phrase(text)
    num_characters = len(text)

    width = left_right_padding * 2 + num_characters * font_size
    height = up_down_padding * 2 + font_size  # just one line

    image = Image.new(mode="RGB", size=(width, height), color=(255, 255, 255))

    def letter_2_string_io(letter):
        font_list = ["simsun.ttc", "black.ttf", "youyuan.TTF"]
        selected_font = font_list[random.randint(0, len(font_list) - 1)]

        font = pygame.font.Font(os.path.join("fonts", selected_font), font_size)
        rendered_letter = font.render(letter, True, (0, 0, 0), (255, 255, 255))

        letter_string_io = StringIO.StringIO()
        pygame.image.save(rendered_letter, letter_string_io)
        return letter_string_io

    for i in xrange(len(text)):
        letter_io = letter_2_string_io(text[i])
        letter_io.seek(0)
        line = Image.open(letter_io)
        image.paste(line, (left_right_padding + i * font_size, up_down_padding))

    image_arr = np.array(image)

    height, width, _ = image_arr.shape

    # this is a decorator
    def get_sin_shift(amplitude, frequency, phrase=None):
        if phrase is None:
            phrase = random.random() * np.pi

        def sin_shift(x):
            return amplitude * np.sin(2.0 * np.pi * x * frequency + phrase)

        return sin_shift

    # TODO: 随机相位
    # TODO: 字体大小随机
    # TODO: 噪斑
    # - Vertical shift

    sin_amplitude = height / 3.5
    sin_frequency = float(len(text)) / width

    vertical_shift = get_sin_shift(sin_amplitude, sin_frequency)

    for i in xrange(width):
        image_arr[:, i] = np.roll(image_arr[:, i], int(vertical_shift(i)))

    # - Horizontal shift

    sin_amplitude = width / 20.0
    sin_frequency = 1.0 / height

    horizontal_shift = get_sin_shift(sin_amplitude, sin_frequency)
    for j in xrange(height):
        image_arr[j, :] = np.roll(image_arr[j, :], int(horizontal_shift(j)))

    image = Image.fromarray(image_arr).convert("L")

    if show:
        image.show()

    if save:
        image.save(os.path.join(image_dir_path, \
                                u"%s_%s.png" % (original_text, \
                                                get_random_string())))


if __name__ == '__main__':
    import random

    phrases = load_chinese_phrases()
    generate_number = 1000
    for i in range(generate_number):
        cur_phrase = random.sample(phrases, 1)[0]
        display_phrase = add_noise_to_phrase(cur_phrase)
        text_2_distorted_image(text=cur_phrase, show=False, save=True)
        print cur_phrase
