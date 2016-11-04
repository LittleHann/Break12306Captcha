from PIL import Image
from PIL.ImageOps import grayscale
from utils import chopLabel, resize
import numpy as np
import matplotlib.pyplot as plt


np.set_printoptions(threshold=np.nan)


print "Demo for chopping generated label"
im = Image.open("data/mh.png")
label = resize(im)
label.show()
raw_input("Press Enter to Continue")


print "Demo for chopping real label"
im = Image.open("data/captcha_0.jpg")
label = chopLabel(im)
label.show()
raw_input("Press Enter to Quit")

# to save the file
# execute image.save(filename, format)
# e.g: label.save("label.jpeg", "JPEG")

