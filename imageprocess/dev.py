from PIL import Image
from PIL.ImageOps import grayscale
import numpy as np
import matplotlib.pyplot as plt

from imageprocess.utils import trim_label, crop_label

np.set_printoptions(threshold=np.nan)

print "Demo for cropping generated label"
im = Image.open("../data/mh.png")
label = trim_label(im, size=100)
label = label.resize((60, 60))
label.show()
raw_input("Press Enter to Continue")

print "Demo for cropping real label"
im = Image.open("../data/captcha_0.jpg")
label = crop_label(im)
label = trim_label(label, size=100)
label = label.resize((60, 60))
label.show()
raw_input("Press Enter to Quit")

# to save the file
# execute image.save(filename, format)
# e.g: label.save("label.jpeg", "JPEG")
