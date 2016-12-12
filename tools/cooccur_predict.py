#!/usr/bin/env python
# encoding: utf-8

'''
Used to predict image with only image-label co-occurrence
'''


import sys
from pyspark import SparkConf, SparkContext
from pyspark.mllib.linalg import SparseVector
from scipy.spatial.distance import cosine
import numpy as np
import json
import argparse

NUMBER_OF_CATEGORY = 230
VEC_PERCENTILE = 95

def get_sparse_index(vec, percentile=VEC_PERCENTILE):
    vec = np.array(vec)
    threshold = np.percentile(vec, percentile)
    idx = np.where(vec > threshold)[0]
    return idx, vec[idx]


def parse_ori2final(line):
    '''
    generates (original, final)
    '''
    ori, final = line.strip().split('\t')
    return ori, final

def parse_txtcaptcha(line):
    '''
    generates [(filename, original_rgb_hash), ...]
    '''
    tokens = line.strip().split('\t')
    filename = tokens[0]
    return [(filename, phash) for i, phash in enumerate(tokens[1:]) if i % 2]

def parse_labelprob(line):
    '''
    generates (filename, label)
    '''
    tokens = line.strip().split('\t')
    filename = tokens[0]
    val_dict = dict()
    for t in tokens[1:]:
        idx, val = t.split(":")
        idx, val = int(idx), float(val)
        val_dict[idx] = val
    vec = SparseVector(NUMBER_OF_CATEGORY, val_dict)
    return filename, vec

def add_sparse_vector(vec1, vec2):
    t = vec1.toArray() + vec2.toArray()
    idx, val = get_sparse_index(t)
    return SparseVector(NUMBER_OF_CATEGORY, idx, val)

def normalize(t):
    final_phash, vec = t
    vec = vec.toArray()
    z = np.linalg.norm(vec, ord=2)
    if z:
        vec /= z
    idx, val = get_sparse_index(vec, percentile=50)
    return final_phash, SparseVector(NUMBER_OF_CATEGORY, idx, val)

def predict(t):
    final_phash, vec = t
    vec = vec.toArray()
    return (final_phash, np.argmax(vec))

def main(argv):
    # parse args

    parser = argparse.ArgumentParser()
    parser.add_argument("original_to_final", action="store",
                        help="specify the file path for original to final path")
    parser.add_argument("text_captcha", action="store",
                        help="specify the file path for text captcha")
    parser.add_argument("label_prob", action="store",
                    help="specify the ilfe path of label probability for captcha files")
    parser.add_argument("--predict", action="store_const", default=False, const=True,
                    help="output prediction, default setting outputs probability")
    parser.add_argument("--local", action="store_const", default=False, const=True,
                    help="run the program in local mode")
    parser.add_argument("--output", action="store", 
                    help="specify the output path")


    args = parser.parse_args()


    f_ori2final = args.original_to_final
    f_txtcaptcha = args.text_captcha
    f_labelprob = args.label_prob
    local_mode = args.local
    f_output = args.output

    """ configure pyspark """
    conf = SparkConf().setAppName("Calculate Similarity")
    if local_mode:
        conf = conf.setMaster('local[*]')
    sc = SparkContext(conf=conf)

    ori2final = sc.textFile(f_ori2final).map(parse_ori2final)
    txtcaptcha = sc.textFile(f_txtcaptcha).flatMap(parse_txtcaptcha)
    labelprob = sc.textFile(f_labelprob).map(parse_labelprob)
    labelprob.cache()

    result = txtcaptcha.join(labelprob) \
                        .map(lambda (filename, (ori, prob)): (ori, prob)) \
                        .reduceByKey(add_sparse_vector) \
                        .join(ori2final) \
                        .map(lambda (ori, (p, final)): (final, p)) \
                        .reduceByKey(add_sparse_vector) \
                        .map(normalize)
    if args.predict:
        result = result.map(predict)


    # print result.collect()
    if local_mode:
        ostream = sys.stdout if not args.output else open(args.output, "w")
        for i in result.collect():
            ostream.write("{}\n".format(i))
        ostream.close()
    else:
        result.saveAsTextFile(f_output)

    """ terminate """
    sc.stop()


if __name__ == '__main__':
    main(sys.argv)