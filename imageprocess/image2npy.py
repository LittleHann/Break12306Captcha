import numpy as np
from PIL import Image
import os

np.set_printoptions(threshold=np.nan)

PIXEL_DEPTH = 255
IMAGE_DIR = "../data/validation/"

def load_chinese_phrases(path):
    chinese_phrases = []
    with open(path) as reader:
        for line in reader:
            # please decode with `utf8`
            chinese_phrases.append(line.strip().split()[0].decode("utf8"))
    print "%d Chinese phrases are loaded" % len(chinese_phrases)
    return chinese_phrases


phrase = load_chinese_phrases('../labelgenerator/labels.txt')
lines = list()
with open (os.path.join(IMAGE_DIR, 'label.txt')) as f:
    lines = f.readlines()
lines = [line.decode('utf8') for line in lines if '\t' in line]

data_size = len(lines)
vec = list()
matrix = np.zeros((data_size, 60**2))
label_vec = np.zeros(data_size)
p2i = {p:i for (i, p) in enumerate(phrase)}
for i, line in enumerate(lines):
    file_path, label = line.split()
    file_name = os.path.basename(file_path)
    matrix[i, :] = np.array(Image.open(os.path.join(IMAGE_DIR, file_name)) \
                        .convert("L") \
                        .resize((60, 60))) \
                        .reshape(60**2)
    label_vec[i] = p2i[label]

matrix = (matrix - PIXEL_DEPTH / 2.0) / PIXEL_DEPTH


np.save('validation_data.npy', matrix)
np.save('validation_label.npy', label_vec)
