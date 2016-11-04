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

#label.show()
# a = label.convert('L')
# a.show()
# a.show()
# print len(a.histogram())
# matrix = np.array(a)
# print matrix
# Image.fromarray(matrix, 'L').show()

# matrix = np.where(matrix>200, 0, 255)
# print matrix
# v_histogram = np.sum(matrix, 0)
# h_histogram = np.sum(matrix, 1)
# Image.fromarray(matrix, 'L').show()
# print v_histogram
# print h_histogram
