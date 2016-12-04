import logging
from pyspark import SparkConf, SparkContext

from image_hash.multiprocess_fc7_extractor import load_precomputed_hashes, load_rgb_mappings

logging.basicConfig(level=logging.INFO)

conf = SparkConf().setAppName('12306').setMaster('local[*]')
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


def load_hash_2_sources():
    # TODO
    pass


if __name__ == '__main__':
    construct_hash_2_sources()
