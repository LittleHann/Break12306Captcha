import os
import json

from pyspark import SparkConf, SparkContext

conf = SparkConf().setAppName('12306').setMaster('local[*]').set('spark.driver.maxResultSize', '2G')
sc = SparkContext(conf=conf)


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
        .map(lambda t: ','.join(t)) \
        .saveAsTextFile('/home/haonans/capstone/mysql/rgb_key_2_hashes.csv')


def gen_rgb_key_2_filenames():
    rgb_mappings = load_rgb_mappings()
    pre_computed_hashes = load_precomputed_hashes()

    def helper1(filename, rgb_hashes):
        return [(rgb_hashes[i], '{}:{}'.format(filename, i)) for i in xrange(8)]

    rgb_hash_2_sources = sc.parallelize(pre_computed_hashes.iteritems()) \
        .flatMap(lambda (key, val): helper1(key, val)) \
        .groupByKey() \
        .mapValues(list) \
        .collectAsMap()

    sc.parallelize(rgb_mappings.iteritems()) \
        .map(lambda (key, val): (val, key)) \
        .mapValues(lambda rgb_hash: rgb_hash_2_sources.get(rgb_hash, [])) \
        .groupByKey() \
        .mapValues(lambda it: str(list(it))) \
        .map(lambda t: ','.join(t)) \
        .saveAsTextFile('/home/haonans/capstone/mysql/rgb_key_2_sources.csv')


def gen_phash_2_count():
    rgb_mappings = load_rgb_mappings()
    pre_computed_hashes = load_precomputed_hashes()

    sc.parallelize(pre_computed_hashes.values()) \
        .flatMapValues(lambda x: x) \
        .map(rgb_mappings.__getitem__) \
        .map(lambda x: (x, 1)) \
        .reduceByKey(lambda x, y: x + y) \
        .map(lambda t: ','.join(t)) \
        .saveAsTextFile('/home/haonans/capstone/mysql/rgb_key_2_count.csv')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('n', 'job number')
    args = parser.parse_args()

    n = args.n
    if n == 1:
        gen_rgb_key_2_rgb_hashes()
    elif n == 2:
        gen_rgb_key_2_filenames()
    elif n == 3:
        gen_phash_2_count()
