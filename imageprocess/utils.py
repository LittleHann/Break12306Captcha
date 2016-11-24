import numpy as np
from PIL import Image

def load_chinese_phrases(path):
    chinese_phrases = []
    with open(path) as reader:
        for line in reader:
            # please decode with `utf8`
            chinese_phrases.append(line.strip().split()[0].decode("utf8"))
    print "%d Chinese phrases are loaded" % len(chinese_phrases)
    return chinese_phrases

def minBoundingBox(img):
    matrix = np.array(img.convert("L"))
    threshold = 200
    matrix = np.where(matrix>threshold, 0, 1)
    col_hist = np.sum(matrix, 0)
    row_hist = np.sum(matrix, 1)
    left, right, top, bot = 0, len(col_hist)-1, 0, len(row_hist)-1
    while col_hist[left] == 0 and left < right: left += 1
    while col_hist[right] == 0 and left < right: right -= 1
    while row_hist[top] == 0 and top < bot: top += 1
    while row_hist[bot] == 0 and top < bot: bot -= 1
    img = img.crop((left, top, right, bot))
    return img

def trim_label(img, size=227):
    img = minBoundingBox(img)
    width, height = img.size
    new_height = size / max(width, height) * height
    img = img.resize((size, new_height))
    result = Image.new('L', (size, size), 255)
    result.paste(img, (0, (size - new_height)//2))
    return result


def crop_label(img):
    box = (118, 0, 218, 25)
    label = img.crop(box)
    label = minBoundingBox(label)
    return label
