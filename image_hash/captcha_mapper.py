from PIL import Image
from image_hash import calc_perceptual_hash, get_sub_images
import os
import numpy as np
import argparse
from itertools import izip
import traceback
from multiprocessing import Process

np.set_printoptions(threshold=np.nan)


def captcha_mapper(file_path, separator='\t', gray_size=6, rgb_size=8):
    '''
    Convert captcha into a string in following order:
        filename,  gray_phash1, rgbphash1, gray_phash2, rgb_phash2, ...
        separated by '\t'
    '''
    result_list = [os.path.basename(file_path)]
    captcha = Image.open(file_path)

    for image in get_sub_images(captcha):
        phash_gray = calc_perceptual_hash(image, 
                                            'GRAY', 
                                            return_hex_str=True, 
                                            gray_size=6, 
                                            rgb_size=8)
        phash_rgb = calc_perceptual_hash(image, 
                                            'RGB', 
                                            return_hex_str=True, 
                                            gray_size=6, 
                                            rgb_size=8)
        result_list.append(phash_gray)
        result_list.append(phash_rgb)
    return separator.join(result_list)

def worker(file_list, output_dir, total_workers, worker_id, gray_size=6, rgb_size=8, debug=False):
    f = open(os.path.join(output_dir, "output_%d.txt" % worker_id), "w")
    for path in file_list:
        if hash(path) % total_workers == worker_id:
            if debug:
                print path
            try:
                result = captcha_mapper(path, gray_size, rgb_size)
            except:
                print path
                traceback.print_exc()
                continue
            f.write(result + '\n')
    f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", dest="debug", type=int, help="enable single group debug mode")
    parser.set_defaults(debug=False)
    parser.add_argument("--gray_size", type=int, default=6, help="the size for gray_size, 6 by default")
    parser.add_argument("--rgb_size", type=int, default=8, help="the size for rgb_size, 8 by default")
    parser.add_argument("file_list_path", action="store",
                        help="the file list of filenames")
    parser.add_argument("file_dir", action="store",
                        help="the path to CAPTCHA file directory")
    parser.add_argument("output_dir", action="store", help="the output directory")
    parser.add_argument("n", type=int,
                        help="the number of process to start")
    args = parser.parse_args()
    with open(args.file_list_path) as f:
        filenames = f.read().strip().split('\n')
    file_paths = map(lambda filename: os.path.join(args.file_dir, filename), filenames)
    worker_list = list()
    if args.debug is not False:
        print "in debug mode, group:", args.debug
        worker(file_paths, 
                args.output_dir, 
                args.n, 
                args.debug, 
                args.gray_size, 
                args.rgb_size, 
                debug=True)
    else:
        for i in xrange(args.n):
            worker_list.append(Process(target=worker, 
                                        args=(file_paths, 
                                                args.output_dir, 
                                                args.n, 
                                                i, 
                                                args.gray_size, 
                                                args.rgb_size)))
        for p in worker_list:
            p.start()
        for p in worker_list:
            p.join()
