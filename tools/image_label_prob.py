
import boto3
import sys
import json
import numpy as np
import argparse
import cPickle as pickle
from collections import defaultdict

BUCKET_NAME = '12306bucket'

def load_label_prob(label_prob_path):
    prob_dict = defaultdict(lambda : defaultdict(float))
    with open (label_prob_path) as f:
        for line in f:
            line = line.strip()
            if line:
                content = line.split('\t')
                filename = content[0]
                for t in content[1:]:
                    idx, v = t.split(":")
                    idx, v = int(idx), float(v)
                    prob_dict[filename][idx] = v
    return prob_dict

def calculate_image_prob(text_captcha_path, rgb2final, prob_dict):
    image_prob = defaultdict(lambda : defaultdict(float))
    with open (text_captcha_path) as f:
        for line in f:
            content = line.strip().split('\t')
            filename = content[0]
            for i in xrange(8):
                final_rgb = rgb2final[content[i*2+2]]
                for idx, v in image_prob[file_name].items():
                    image_prob[final_rgb][idx] += v
    for rgb in image_prob:
        s = np.sum(image_prob[rgb].values())
        for k in image_prob[rgb]:
            image_prob[rgb][k] /= s
    return image_prob


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("label_prob_path", action="store",
                        help="specify the file path for label prediction")
    parser.add_argument("text_captcha_path", action="store",
                        help="specify the file path for text format CAPTCHA")
    parser.add_argument("mapping_file", action="store",
                        help="specify the file path of mapping from rgb_phash to final rgb_phash")
    parser.add_argument("output", action="store",
                        help="specify the file path of image category probability")
    args = parser.parse_args()

    label_prob_dict = load_label_prob(args.label_prob_path)
    rgb2final = pickle.load(open(args.mapping_file))['rgb2final']
    image_prob = calculate_image_prob(args.text_captcha_path, rgb2final, load_label_prob)
    json.dump(open(args.output, "w"))
