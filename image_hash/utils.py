import os
import json
import logging
from pyspark import SparkConf, SparkContext

logging.basicConfig(level=logging.INFO)

conf = SparkConf().setAppName('12306').setMaster('local[*]')
sc = SparkContext(conf=conf)


def load_precomputed_hashes(path='/ssd/data/txt_captchas.txt'):
    """ Attention please, this function is exactly the same as that in fc7_extractor.
    The reason why I don't import it from fc_extractor is because I don't know how to in shell mode. :D"""
    assert os.path.isfile(path)

    computed_hashes = {}
    with open(path) as f:
        for line in f:
            items = line.strip().split()

            source = items[0]
            gray_hashes = [items[1 + 2 * i] for i in xrange(8)]
            rgb_hashes = [items[2 + 2 * i] for i in xrange(8)]

            computed_hashes[source] = {'gray': gray_hashes, 'rgb': rgb_hashes}
    return computed_hashes


def load_rgb_mappings(path='/ssd/data/mapping.json'):
    """ Yeah, I did the same thing as above again, :D"""
    assert os.path.isfile(path)

    with open(path) as f:
        rgb_mappings = json.load(f)['rgb2final']
    return rgb_mappings


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


def load_hash_2_sources():
    # TODO
    pass


def construct_rgb_key_2_hashes():
    rgb_mappings = load_rgb_mappings()
    sc.parallelize(rgb_mappings.iteritems()) \
        .map(lambda (key, val): (val, key)) \
        .groupByKey() \
        .mapValues(list) \
        .saveAsTextFile('/ssd/haonans/rgb_key_2_hashes')


def load_rgb_key_2_hashes():
    # TODO
    pass


if __name__ == '__main__':
    # construct_hash_2_sources()
    construct_rgb_key_2_hashes()
