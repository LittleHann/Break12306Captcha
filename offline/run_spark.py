import os
import json
from redis import Redis

from pyspark import SparkConf, SparkContext

conf = SparkConf().setAppName('12306').setMaster('local[*]').set('spark.driver.maxResultSize', '20G')
sc = SparkContext(conf=conf)

REDIS_URL = 'redis://localhost:6379'


# ---------------------
# Load precomputed data
# ---------------------

def load_precomputed_hashes(path='/data2/heqingy/txt_captchas.txt'):
    assert os.path.isfile(path)

    _precomputed_hashes = {}
    with open(path) as f:
        for line in f:
            items = line.strip().split()

            source = items[0]
            gray_hashes = [items[1 + 2 * i] for i in xrange(8)]
            rgb_hashes = [items[2 + 2 * i] for i in xrange(8)]

            _precomputed_hashes[source] = rgb_hashes
    return _precomputed_hashes


def load_rgb_mappings(path='/data2/heqingy/mapping.json'):
    assert os.path.isfile(path)

    with open(path) as f:
        _rgb_mappings = json.load(f)['rgb2final']

    return _rgb_mappings


def gen_rgb_key_2_rgb_hashes():
    rgb_mappings = load_rgb_mappings()
    sc.parallelize(rgb_mappings.iteritems()) \
        .map(lambda (key, val): (val, key)) \
        .groupByKey() \
        .mapValues(lambda it: str(list(it))) \
        .map(lambda (key, val): '{}\t{}'.format(key, val)) \
        .saveAsTextFile('/home/haonans/capstone/mysql/rgb_key_2_hashes.csv')


def gen_rgb_key_2_filenames():
    rgb_mappings = load_rgb_mappings()
    pre_computed_hashes = load_precomputed_hashes()

    def helper1(filename, rgb_hashes):
        return [(rgb_hashes[i], '{}:{}'.format(filename, i)) for i in xrange(8)]

    def helper2(_partition):
        redis = Redis.from_url(REDIS_URL)
        for k, v in _partition:
            redis.set(k, v)

    sc.parallelize(pre_computed_hashes.iteritems()) \
        .flatMap(lambda (key, val): helper1(key, val)) \
        .groupByKey() \
        .mapValues(lambda i: str(list(i))) \
        .foreachPartition(helper2)

    def helper3(_rgb_hashes):
        redis = Redis.from_url(REDIS_URL)
        sources = reduce(lambda l1, l2: l1 + l2, map(lambda rgb_hash: eval(redis.get(rgb_hash)), _rgb_hashes))
        return sources

    sc.parallelize(rgb_mappings.iteritems()) \
        .map(lambda (key, val): (val, key)) \
        .groupByKey() \
        .mapValues(helper3) \
        .map(lambda (key, val): '{}\t{}'.format(key, val)) \
        .saveAsTextFile('/home/haonans/capstone/mysql/rgb_key_2_sources.csv')


def gen_phash_2_count():
    rgb_mappings = load_rgb_mappings()
    pre_computed_hashes = load_precomputed_hashes()

    sc.parallelize(pre_computed_hashes.values()) \
        .flatMap(lambda x: list(x)) \
        .map(lambda rgb_hash: rgb_mappings[rgb_hash]) \
        .map(lambda x: (x, 1)) \
        .reduceByKey(lambda x, y: x + y) \
        .map(lambda (key, val): '{}\t{}'.format(key, val)) \
        .saveAsTextFile('/home/haonans/capstone/mysql/rgb_key_2_count.csv')


if __name__ == '__main__':
    gen_rgb_key_2_rgb_hashes()
    gen_rgb_key_2_filenames()
    gen_phash_2_count()
