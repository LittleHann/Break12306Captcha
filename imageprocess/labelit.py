# Only for mac

import argparse
from PIL import Image
import os
import time
import glob
from subprocess import call
import utils



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", action="store",
                        help="specify the directory of labeled image and \
                        label.txt")
    parser.add_argument("-b", "--binary", action="store",
                        help="generate binary labeled data")
    parser.add_argument("-o", "--output", action="store",
                        help="specify the path to output")
    # parser.add_argument("n", type=int, help="number of samples")


    args = parser.parse_args()
    if not args.path:
        parser.print_help()
    else:
        try:
            os.makedirs(args.output)
        except:
            pass
        instances = list()
        labels = list()
        phrases = utils.load_chinese_phrases("../labelgenerator/labels.txt")
        filenames = glob.glob(os.path.join(args.path, "*.jpg"))
        # filenames.sort()
        for i, filename in enumerate(filenames):
            path = os.path.join(filename)
            img = utils.cropLabel(Image.open(path))
            # img = utils.trimLabel(img).resize((60, 60))
            # img.show()
            img.save(os.path.join(args.output, "%d.jpg" % i))
            # os.system('cp %s ./data/' % path)
