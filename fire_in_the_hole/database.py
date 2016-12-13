# encoding: UTF-8
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


def get_predictions(rgb_key):
    def helper(_bad):
        return eval('u\'{}\''.format(_bad.replace('u', '\\u'))).encode('utf-8')

    def list_it(t):
        return list(map(list_it, t)) if isinstance(t, (list, tuple)) else t

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
