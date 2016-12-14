# encoding: UTF-8
import path_magic
from image_hash import calc_perceptual_hash
from cassandra.cluster import Cluster, Session

cluster = Cluster()
session = cluster.connect()
session.set_keyspace('capstone')


def get_rgb_key(rgb_hash):
    command = 'SELECT rgb_key FROM rgb_hash_2_key WHERE rgb_hash = \'{}\';'.format(rgb_hash)
    rows = session.execute(command)
    return next(iter(rows)).rgb_key


assert get_rgb_key('ffffc7c783e5cdaf000064ec96644020000024781c5c7020') == \
       'ffffc7c783e5cdaf000064ec96644020000024781c5c7020'


def get_closest_rgb_key(gray_hash, rgb_hash):
    command = 'SELECT rgb_keys FROM buckets WHERE gray_hash = \'{}\''.format(gray_hash)
    rows = session.execute(command)
    rgb_keys = eval(next(iter(rows)).rgb_keys)

    def hamming_dist(h1, h2):
        return bin(int(h1, base=16) ^ int(h2, base=16)).count('1')

    min_dist = float('inf')
    rgb_key = None
    for cur_key in rgb_keys:
        cur_dist = hamming_dist(rgb_hash, cur_key)
        if cur_dist < min_dist:
            cur_dist, rgb_key = min_dist, cur_key
    return rgb_key


def boom(image):
    gray_hash = calc_perceptual_hash(image, mode='GRAY', return_hex_str=True)
    rgb_hash = calc_perceptual_hash(image, mode='RGB', return_hex_str=True)

    try:
        rgb_key = get_rgb_key(rgb_hash)
        return rgb_key
    except StopIteration:
        try:
            rgb_key = get_closest_rgb_key(gray_hash, rgb_hash)
            return rgb_key
        except StopIteration:
            return None


def get_predictions(rgb_key):
    def helper(_bad):
        return eval('u\'{}\''.format(_bad.replace('u', '\\u'))).encode('utf-8')

    def list_it(t):
        return list(map(list_it, t)) if isinstance(t, (list, tuple)) else t

    if not rgb_key:
        return [(u"不存在".encode('utf-8'), 1.0)]

    command = 'SELECT predictions FROM rgb_key_2_predictions WHERE rgb_key = \'{}\';'.format(rgb_key)
    rows = session.execute(command)
    predictions = next(iter(rows)).predictions
    if not predictions:
        return None
    else:
        predictions = list_it(eval(predictions))
        for i in xrange(len(predictions)):
            predictions[i][0] = helper(predictions[i][0])
        return predictions


p = get_predictions('0b0b0f13375be75e0f0b0f13377be7028f5b5f33777be702')
assert p[0][0] == u'摩天轮'.encode('utf-8')
