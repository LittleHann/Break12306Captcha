from __future__ import unicode_literals
import os
import shutil
from pypinyin import lazy_pinyin
try:
    from labelgenerator.text_2_image import load_chinese_phrases
except:
    from text_2_image import load_chinese_phrases

phrase_2_code = {}


def get_code(phrase):
    if phrase not in phrase_2_code:
        phrase_2_code[phrase] = '{}_{:04d}'.format('_'.join(lazy_pinyin(phrase)), len(phrase_2_code) + 1)
    return phrase_2_code[phrase]


def main():
    phrases = load_chinese_phrases()
    images = os.listdir('/tmp/12306/images')

    for cur_img in images:
        print cur_img
        cur_phrase, cur_id = cur_img.split('_')
        cur_code = get_code(cur_phrase)
        shutil.copy(os.path.join('/Downloads/12306/images', cur_img),
                    os.path.join('/Downloads/12306/training/data', '-'.join([cur_code, cur_id])))


if __name__ == '__main__':
    main()
