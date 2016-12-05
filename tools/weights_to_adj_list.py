from collections import defaultdict
import sys

if __name__ == "__main__":
    result = defaultdict(lambda : defaultdict(float))
    for line in sys.stdin:
        k1, k2, weight = eval(line)
        result[k1][k2] += weight
        result[k2][k1] += weight
    for k in result:
        adj_list = "\t".join(map(lambda x: "{}:{}".format(x[0], x[1]), 
                                    sorted(result[k].items(), 
                                        key=lambda x: -x[1])))
        print "{}\t{}".format(k, adj_list)


