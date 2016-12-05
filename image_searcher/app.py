import os
import sys
import json
import cPickle
import logging
import boto3
from multiprocessing import Pool
from PIL import Image, ImageDraw
from flask import Flask, request, jsonify

# try:
from image_hash import get_sub_images
# except ImportError:

# TODO: get rid of this shit

app_dir = os.path.dirname(os.path.realpath(__file__))
    # sys.path.insert(0, app_dir + '/../')
#     from image_hash import get_sub_images

logging.basicConfig(level=logging.INFO)
logging.warn('APP_DIR={}'.format(app_dir))
app = Flask(__name__)


# ----------
# On startup
# ----------

def load_rgb_key_2_hashes(path='/data2/haonans/rgb_key_2_hashes.pickle'):
    """ RGB key to a list of RGB hashes """
    assert os.path.exists(path), 'Cannot find file: {}'.format(os.path.abspath(path))
    with open(path) as reader:
        _rgb_key_2_hashes = cPickle.load(reader)
    return _rgb_key_2_hashes


def load_rgb_hash_2_sources(path='/data2/haonans/hash_2_sources.pickle'):
    """ RGB hash to a list of sources ('filename:loc') """
    assert os.path.exists(path), 'Cannot find file: {}'.format(os.path.abspath(path))
    with open(path) as reader:
        _rgb_hash_2_sources = cPickle.load(reader)
    return _rgb_hash_2_sources


# --
# S3
# --

def get_bucket():
    with open(app_dir + '/../aws/cred.json') as reader:
        cred = json.load(reader)
    _s3 = boto3.resource('s3', aws_access_key_id=cred['aws_access_key_id'],
                         aws_secret_access_key=cred['aws_secret_access_key'])
    _bucket = _s3.Bucket('12306captchas')
    return _bucket


logging.info('Establishing S3 connection')
bucket = get_bucket()


def download_mark_save_source(source):
    captcha_name, image_loc = source.split(':')[0], int(source.split(':')[1])
    # Download
    captcha_path = os.path.join(app_dir, './static/' + captcha_name)
    logging.warn('captcha path:{}'.format(captcha_path))
    bucket.download_file(captcha_name, captcha_path)
    # Load and mark
    captcha = Image.open(captcha_path)
    marked_captcha = mark_on_captcha(captcha, image_loc)
    marked_captcha.save('./static/' + source + '.jpg')


def mark_on_captcha(captcha, image_loc):
    row, col = image_loc // 4, image_loc % 4

    top = 41 + (67 + 5) * row
    left = 5 + (67 + 5) * col

    draw = ImageDraw.Draw(captcha)
    corner_size = 10
    draw.rectangle(((left, top), (left + 67, top + 67)), outline='red')
    draw.rectangle(((left, top), (left + corner_size, top + corner_size)), fill='red')
    draw.rectangle(((left, top + 67 - corner_size), (left + corner_size, top + 67)), fill='red')
    draw.rectangle(((left + 67 - corner_size, top + 67 - corner_size), (left + 67, top + 67)), fill='red')
    draw.rectangle(((left + 67 - corner_size, top), (left + 67, top + corner_size)), fill='red')

    return captcha


# ------
# Routes
# ------

@app.route('/ping')
def ping():
    return jsonify('Pong')


@app.route('/getImage')
def get_image():
    """ This function returns a list of static urls

     Example request url: GET http://127.0.0.1/getImage?rgb_hash=1&max_query=2
    """
    # parse
    rgb_hash = request.args.get('rgb_hash')
    max_query = int(request.args.get('max_query'))
    # query
    sources = rgb_hash_2_sources.get(rgb_hash, [])[:max_query]
    # Multi-processing
    pool = Pool(len(sources))
    pool.map(download_mark_save_source, sources)
    return jsonify(map(lambda src: src + '.jpg', sources))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('p1', help='abs_path to rgb_key_2_hashes')
    parser.add_argument('p2', help='abs_path to rgb_hash_2_sources')
    parser.add_argument('--debug', action='store_true', help='flask debug configuration')
    parser.add_argument('--port', action='store', help='specify the port')
    parser.add_argument('--host', action='store', help='specify the host')
    args = parser.parse_args()

    logging.info('Loading rgb_key_2_hashes')
    rgb_key_2_hashes = load_rgb_key_2_hashes(args.p1)

    logging.info('Loading rgb_hash_2_sources')
    rgb_hash_2_sources = load_rgb_hash_2_sources(args.p2)

    app.run(host=args.host, port=args.port, debug=args.debug)
