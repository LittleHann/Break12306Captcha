import numpy as np
from PIL import Image

np.set_printoptions(threshold=np.nan)

PIXEL_DEPTH = 255

def load_chinese_phrases(path):
    chinese_phrases = []
    with open(path) as reader:
        for line in reader:
            # please decode with `utf8`
            chinese_phrases.append(line.strip().split()[0].decode("utf8"))
    print "%d Chinese phrases are loaded" % len(chinese_phrases)
    return chinese_phrases


phrase = load_chinese_phrases('../labelgenerator/labels.txt')
label = load_chinese_phrases('data/label.txt')
data_size = len(label)
vec = list()
matrix = np.zeros((data_size, 60**2))
label_vec = np.zeros(data_size)
for i in xrange(data_size):
    matrix[i, :] = np.array(Image.open("data/%d.jpg" % i) \
                        .convert("L") \
                        .resize((60, 60))) \
                        .reshape(60**2)

matrix = (matrix - PIXEL_DEPTH / 2.0) / PIXEL_DEPTH


p2i = {p:i for (i, p) in enumerate(phrase)}
for i, l in enumerate(label):
    label_vec[i] = p2i[l]

np.save('test_data.npy', matrix)
np.save('test_label.npy', label_vec)
