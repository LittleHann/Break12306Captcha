import cPickle as pickle
# import msgpack
import json
import sys
import argparse
from collections import defaultdict
import itertools
import time


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("captcha_path", action="store",
                        help="specify the txt file of CAPTCHAs")
    parser.add_argument("mapping_path", action="store",
                        help="specify the file containing mapping info")
    parser.add_argument("output", action="store",
                        help="specify the file path of cooccurrence list")
    args = parser.parse_args()

    print 'loading rgb2final...'
    start_time = time.time()
    rgb2final = json.load(open(args.mapping_path))['rgb2final']
    print 'loading done, used:', time.time() - start_time, "s"

    cooccur_count = defaultdict(int)

    print 'calculating...'
    start_time = time.time()
    with open (args.captcha_path) as f:
        for line in f:
            rgb_phash_list = map(lambda (i, p): rgb2final[p],
                              filter(lambda (i, p): i > 0 and i % 2 == 0,
                                     enumerate(line.strip().split('\t'))))
            combination_list = filter(lambda (a, b): a != b,
                                      itertools.combinations(rgb_phash_list, 2))
            for (a, b) in combination_list:
                if a > b:
                    a, b = b, a
                cooccur_count[a, b] += 1
    print 'calculation done, used', time.time() - start_time, "s"
    print 'edge number:', len(cooccur_count)

    print 'start saving...'
    start_time = time.time()
    pickle.dump(cooccur_count, open(args.output, 'w'), protocol=pickle.HIGHEST_PROTOCOL)
    # f = open(args.output, "wb")
    # msgpack.pack(cooccur_count, f)
    f.close()
    print 'saving done, used:', time.time() - start_time, "s"
