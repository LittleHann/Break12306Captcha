import os
import json
import cPickle
import logging
from pyspark import SparkConf, SparkContext

try:
    from image_hash.multiprocess_fc7_extractor import load_rgb_mappings, load_precomputed_hashes
    from image_hash import get_sub_images
except ImportError:
    from multiprocess_fc7_extractor import load_rgb_mappings, load_precomputed_hashes
    from __init__ import get_sub_images

logging.basicConfig(level=logging.INFO)

conf = SparkConf().setAppName('12306').setMaster('local[*]').set('spark.driver.maxResultSize', '2G')
sc = SparkContext(conf=conf)


def construct_hash_2_sources():
    def get_source_rgb_pairs(_kv):
        source, rgb_hashes = _kv[0], _kv[1]['rgb']
        return map(lambda i: (rgb_hashes[i], '{}:{}'.format(source, i)), xrange(8))

    source_2_hashes = load_precomputed_hashes()
    sc.parallelize(source_2_hashes.iteritems()) \
        .flatMap(get_source_rgb_pairs) \
        .groupByKey() \
        .mapValues(list) \
        .saveAsTextFile('/ssd/haonans/hash_2_sources')


def transform_hash_2_sources():
    hash_2_sources = sc.textFile('/ssd/haonans/hash_2_sources').map(eval).collectAsMap()
    with open('/ssd/haonans/hash_2_sources.pickle', 'w') as writer:
        cPickle.dump(hash_2_sources, writer, cPickle.HIGHEST_PROTOCOL)


def construct_rgb_key_2_hashes():
    rgb_mappings = load_rgb_mappings()
    sc.parallelize(rgb_mappings.iteritems()) \
        .map(lambda (key, val): (val, key)) \
        .groupByKey() \
        .mapValues(list) \
        .saveAsTextFile('/ssd/haonans/rgb_key_2_hashes')


def transform_rgb_key_2_hashes():
    rgb_key_2_hashes = sc.textFile('/ssd/haonans/rgb_key_2_hashes').map(eval).collectAsMap()
    with open('/ssd/haonans/rgb_key_2_hashes.pickle', 'w') as writer:
        cPickle.dump(rgb_key_2_hashes, writer, cPickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
    # construct_hash_2_sources()
    # construct_rgb_key_2_hashes()
    transform_hash_2_sources()
    transform_rgb_key_2_hashes()
