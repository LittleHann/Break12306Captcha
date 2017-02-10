import json

"""
Generate Cassandra database data copy from `mapping.json`
"""

with open('../data/mapping.json') as f:
    mappings = json.load(f)

    with open('rgb_hash_2_key.txt', 'w') as writer:
        for k, v in mappings['rgb2final'].iteritems():
            writer.write('{}\t{}\n'.format(k, v))

    with open('buckets.txt', 'w') as writer:
        for k, v in mappings['buckets'].iteritems():
            writer.write('{}\t{}\n'.format(k, v))
