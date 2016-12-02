import cPickle as pickle
import argparse
import time
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', "--output", action="store",
                        help="specify the file path for queries")

    parser.add_argument("occurrence_dict", action="store",
                        help="specify the pickle file path of cooccurrence dict")
    args = parser.parse_args()

    print 'loading co-occur dictionary...'
    start_time = time.time()
    co_occur = pickle.load(open(args.occurrence_dict))
    print 'loading done, used:', time.time() - start_time, "s"


    print 'Generating queries...'
    start_time = time.time()
    total_count = len(co_occur)
    if args.output:
        f = open(args.output, "w")
    for i, k in enumerate(co_occur):
        v = co_occur[k]
        if i % (total_count // 100) == 0:
            sys.stderr.write("{} / {} = {:.2f}%% is done, time used: {}s.\n"\
                             .format(i,
                                     total_count,
                                     i * 100. / total_count,
                                     time.time()-start_time))

        if args.output:
            f.write("{}\t{}\n".format(k, v))
        else:
            print "{}\t{}".format(k, v)
