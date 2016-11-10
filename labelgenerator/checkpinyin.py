from text_2_image import load_chinese_phrases
from pypinyin import lazy_pinyin
from collections import defaultdict

phrases = load_chinese_phrases()
pinyin_dict = defaultdict(list)

for p in phrases:
    pinyin = tuple(lazy_pinyin(p))
    if pinyin in pinyin_dict:
        print u"duplicate pinyin:", pinyin, pinyin_dict[pinyin]
    pinyin_dict[pinyin].append(p)
