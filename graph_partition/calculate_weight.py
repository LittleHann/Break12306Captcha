#!/usr/bin/env python
# encoding: utf-8

import sys
from pyspark import SparkConf, SparkContext
from pyspark.mllib.linalg import SparseVector
import scipy
import numpy as np
import json

ALPHA = 0.01
VEC_SIZE = 4096

def get_sparse_index(vec):
    vec = np.array(vec)
    threshold = np.mean(vec) + np.std(vec) * 2
    idx = np.where(vec > threshold)[0]
    return idx, vec[idx]

def parse_query(line):
    # ensure rgb_phash1 < rgb_phash2 and co_occur > 0 in input
    key, co_occur = line.split('\t')
    rgb_phash1, rgb_phash2 = eval(key)
    return (rgb_phash1, rgb_phash2, int(co_occur))


def parse_fc7(line):
    t = json.loads(line)
    idx, vec = get_sparse_index(t['fc7'])
    #sys.stderr.write("{}, {}\n".format(len(idx), len(vec)))
    return ((t['rgb_key'],), SparseVector(VEC_SIZE, idx, vec))


def get_similarity(values):
    p_i, p_j, c_ij, fc7_i, fc7_j = values
    fc7_i, fc7_j = fc7_i.toArray(), fc7_j.toArray()
    weight = (1 - scipy.spatial.distance.cosine(fc7_i, fc7_j) * np.log(c_ij + ALPHA))
    return (p_i, p_j, weight)


def main(argv):
    # parse args
    f_query = argv[1]
    f_fc7 = argv[2]
    f_output = argv[3]
    local_mode = len(argv) > 4 and argv[4] == 'local'

    """ configure pyspark """
    conf = SparkConf().setAppName("Calculate Similarity")
    if local_mode:
        conf = conf.setMaster('local[*]')
    sc = SparkContext(conf=conf)

    queries = sc.textFile(f_query).map(parse_query)
    fc7 = sc.textFile(f_fc7).map(parse_fc7)

    result = queries.map(lambda (p_i, p_j, c_ij): ((p_i,), (p_i, p_j, c_ij)))\
                .join(fc7) \
                .map(lambda ((p_i, ), ((_, p_j, c_ij), fc7_i)): ((p_j,), (p_i, c_ij, fc7_i))) \
                .join(fc7) \
                .map(lambda ((p_j, ), ((p_i, c_ij, fc7_i), fc7_j)): (p_i, p_j, c_ij, fc7_i, fc7_j)) \
                .map(get_similarity)
    if local_mode:
        for i in result.collect():
            print i
    else:
        result.saveAsTextFile(f_output)

    """ terminate """
    sc.stop()


if __name__ == '__main__':
    main(sys.argv)
