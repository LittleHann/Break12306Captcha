# encoding: UTF-8

# config system path
import path_magic
from image_hash import calc_perceptual_hash
from cassandra.cluster import Cluster

# local cluster: brew install cassandra; brew services start cassandra
cluster = Cluster()
session = cluster.connect()
"""
CREATE KEYSPACE capstone WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '3'}
AND durable_writes = true;
"""
session.set_keyspace('capstone')


def _get_direct_rgb_key(rgb_hash):
    """
    If the rgb_hash doesn't exist in the database, `StopIteration` is thrown.
    """
    #
    command = 'SELECT rgb_key FROM rgb_hash_2_key WHERE rgb_hash = \'{}\';'.format(rgb_hash)
    rows = session.execute(command)
    return next(iter(rows)).rgb_key


assert _get_direct_rgb_key('ffffc7c783e5cdaf000064ec96644020000024781c5c7020') == \
       'ffffc7c783e5cdaf000064ec96644020000024781c5c7020'


def _get_closest_rgb_key(gray_hash, rgb_hash):
    """
    If the gray_hash doesn't exist in the database (the original image is assumed to be new),
    the function will return None
    """
    # CREATE TABLE buckets (gray_hash text PRIMARY KEY , rgb_keys text );
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


def get_rgb_key(image):
    gray_hash = calc_perceptual_hash(image, mode='GRAY', return_hex_str=True)
    rgb_hash = calc_perceptual_hash(image, mode='RGB', return_hex_str=True)

    try:
        rgb_key = _get_direct_rgb_key(rgb_hash)
        return rgb_key
    except StopIteration:
        try:
            rgb_key = _get_closest_rgb_key(gray_hash, rgb_hash)
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

    # CREATE TABLE rgb_key_2_predictions (rgb_key text PRIMARY KEY , predictions text );
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
