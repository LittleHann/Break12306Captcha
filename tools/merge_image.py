import json
import sys
import argparse
from collections import defaultdict

def hamming_dist(x, y):
    a, b = int(x, base=16), int(y, base=16)
    return bin(a ^ b).count('1')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", action="store",
                        help="specify the file containing text_format CAPTCHAs")
    parser.add_argument("output", action="store",
                        help="specify the file containing buckets and mapping ")
    parser.add_argument("dist", type=int,
                        help="specify the maximum hamming distance")

    args = parser.parse_args()
    buckets = defaultdict(list)
    rgb2final = dict() #store the mapping of rgb_phash and final rgb_phash
    unique_count = 0
    with open (args.input) as f:
        for line in f:
            content = line.split('\t')
            for i in xrange(len(content) // 2):
                gray_phash, rgb_phash = content[i*2+1], content[i*2+2]
                if rgb_phash in rgb2final:
                    continue
                found_match = False
                for t in buckets[gray_phash]:
                    if hamming_dist(t, rgb_phash) <= args.dist:
                        found_match = True
                        rgb2final[rgb_phash] = t
                        break
                if not found_match:
                    buckets[gray_phash].append(rgb_phash)
                    unique_count += 1
    print unique_count
    with open (args.output, "w") as f:
        json.dump({'buckets': buckets,
                   'rgb2final':rgb2final,
                   'unique_count': unique_count,
                   'dist': args.dist}, f)
