from PIL import Image
from PIL.ImageOps import grayscale
from utils import cropLabel, resize
import numpy as np
import matplotlib.pyplot as plt


np.set_printoptions(threshold=np.nan)


print "Demo for cropping generated label"
im = Image.open("data/mh.png")
label = resize(im, size=100)
label.show()
raw_input("Press Enter to Continue")


print "Demo for cropping real label"
im = Image.open("data/captcha_1.jpg")
label = cropLabel(im)
label = resize(label, size=100)
label.show()
raw_input("Press Enter to Quit")

# to save the file
# execute image.save(filename, format)
# e.g: label.save("label.jpeg", "JPEG")
