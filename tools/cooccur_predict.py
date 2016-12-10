#!/usr/bin/env python
# encoding: utf-8

import sys
from pyspark import SparkConf, SparkContext
from pyspark.mllib.linalg import SparseVector
from scipy.spatial.distance import cosine
import numpy as np
import json

NUMBER_OF_CATEGORY = 230
PERCENTILE = 95

def get_sparse_index(vec):
    vec = np.array(vec)
    threshold = np.percentile(vec, PERCENTILE)
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

def predict(t):
    final_phash, vec = t
    vec = vec.toArray()
    return (final_phash, np.argmax(vec))

def main(argv):
    # parse args
    f_ori2final = argv[1]
    f_txtcaptcha = argv[2]
    f_labelprob = argv[3]
    local_mode = len(argv) > 4 and argv[4] == 'local'

    """ configure pyspark """
    conf = SparkConf().setAppName("Calculate Similarity")
    if local_mode:
        conf = conf.setMaster('local[*]')
    sc = SparkContext(conf=conf)

    ori2final = sc.textFile(f_ori2final).map(parse_ori2final)
    txtcaptcha = sc.textFile(f_txtcaptcha).flatMap(parse_txtcaptcha)
    labelprob = sc.textFile(f_labelprob).map(parse_labelprob)

    result = txtcaptcha.join(labelprob) \
                        .map(lambda (filename, (ori, prob)): (ori, prob)) \
                        .reduceByKey(add_sparse_vector) \
                        .join(ori2final) \
                        .map(lambda (ori, (p, final)): (final, p)) \
                        .reduceByKey(add_sparse_vector) \
                        .map(predict)


    # print result.collect()
    if local_mode:
        for i in result.collect():
            print i
    else:
        result.saveAsTextFile(f_output)

    """ terminate """
    sc.stop()


if __name__ == '__main__':
    main(sys.argv)