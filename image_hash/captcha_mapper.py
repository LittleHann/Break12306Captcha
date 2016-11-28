from PIL import Image
from image_hash import calc_perceptual_hash, get_sub_images
import os
import numpy as np
import argparse
from itertools import izip

from multiprocessing import Process


def captcha_mapper(file_path, separator='\t'):
    '''
    Convert captcha into a string in following order:
        filename,  gray_phash1, rgbphash1, gray_phash2, rgb_phash2, ...
        separated by '\t'
    '''
    result_list = [os.path.basename(file_path)]
    captcha = Image.open(file_path)
    for image in get_sub_images(captcha):
        phash_gray = np.packbits(calc_perceptual_hash(image, 'GRAY'))
        phash_rgb = np.packbits(calc_perceptual_hash(image, 'RGB'))
        result_list.append(np.array_str(phash_gray, max_line_width=1000))
        result_list.append(np.array_str(phash_rgb, max_line_width=1000))
    return separator.join(result_list)

def worker(file_list, output_dir, total_workers, worker_id):
    f = open(os.path.join(output_dir, "output_%d.txt" % worker_id), "w")
    for path in file_list:
        if hash(path) % total_workers == worker_id:
            f.write(captcha_mapper(path) + '\n')
    f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

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
    for i in xrange(args.n):
        worker_list.append(Process(target=worker, args=(file_paths, args.output_dir, args.n, i)))
    for p in worker_list:
        p.start()
    for p in worker_list:
        p.join()
