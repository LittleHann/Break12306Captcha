import sys
import cPickle as pickle
# import msgpack
import argparse
import numpy as np

def get_weight(similarity, co_occur, b):
    return np.log(co_occur + b) * similarity

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("cosine_similarity_path", action="store",
                        help="specify the file path for cosine similarity")
    parser.add_argument("co_occur_path", action="store",
                        help="specify the file path for co_occur count dictionary")
    parser.add_argument("b", type=float,
                        help="specify the smooth factor b for Log(cooccur_ij + b)")
    parser.add_argument("output", action="store",
                        help="specify the file path for weights")
    args = parser.parse_args()

    co_occur = pickle.load(open(args.co_occur_path))
    # f = open(args.co_occur_path, "rb")
    # co_occur = msgpack.unpack(f)
    # f.close()

    fin = open (args.cosine_similarity_path)
    fout = open (args.output, "w")
    for line in fin:
        if not line.strip():
            continue
        k1, k2, sim = eval(line)
        weight = get_weight(sim, co_occur[k1, k2], args.b)
        fout.write("{}\t{}\t{}\n".format(k1, k2, weight))



