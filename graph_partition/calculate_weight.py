#!/usr/bin/env python
# encoding: utf-8

import sys
from pyspark import SparkConf, SparkContext
import scipy
import numpy as np
import json

ALPHA = 0.01

def parse_query(line):
    # ensure rgb_phash1 < rgb_phash2 and co_occur > 0 in input
    rgb_phash1, rgb_phash2, co_occur = line.split('\t')
    return (rgb_phash1, rgb_phash2, int(co_occur))

def parse_fc7(line):
    t = json.loads(line)
    return ((t['rgb_key'],), t['fc7'])

def get_similarity(values):
    p_i, p_j, c_ij, fc7_i, fc7_j = values
    fc7_i, fc7_j = np.array(fc7_i), np.array(fc7_j)
    weight = (1 - scipy.spatial.distance.cosine(fc7_i, fc7_j) * np.log(c_ij + ALPHA))
    return (p_i, p_j, weight)


def main(argv):
    # parse args
    f_query = argv[1]
    f_fc7 = argv[2]
    n_outputs = argv[3]
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
