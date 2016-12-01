import json
import sys
import argparse
from collections import defaultdict
import itertools


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("captcha_path", action="store",
                        help="specify the txt file of CAPTCHAs")
    parser.add_argument("mapping_path", action="store",
                        help="specify the file containing mapping info")
    parser.add_argument("output", action="store",
                        help="specify the file path of edges")
    args = parser.parse_args()
    rgb2final = json.load(open(parser.mapping_path))['rgb2final']
    cooccur_count = defaultdict(int)
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
    print len(cooccur_count)
    json.dump(cooccur_count, open('cooccur_count.json', w))
