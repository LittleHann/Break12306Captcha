import os
import sys
import json
import cPickle
import logging
import boto3
from PIL import Image
from flask import Flask, request, jsonify

app_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)) + '/../')
try:
    from image_hash import get_sub_images
except ImportError:
    sys.path.insert(0, app_dir)
    from image_hash import get_sub_images

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)


# ----------
# On startup
# ----------

def load_rgb_key_2_hashes(path='/home/haonans/capstone/data/rgb_key_2_hashes.pickle'):
    """ RGB key to a list of RGB hashes """
    assert os.path.exists(path), 'Cannot find file: {}'.format(os.path.abspath(path))
    with open(path) as reader:
        _rgb_key_2_hashes = cPickle.load(reader)
    return _rgb_key_2_hashes


logging.info('Loading rgb_key_2_hashes')
rgb_key_2_hashes = load_rgb_key_2_hashes()


def load_rgb_hash_2_sources(path='/home/haonans/capstone/data/hash_2_sources.pickle'):
    """ RGB hash to a list of sources ('filename:loc') """
    assert os.path.exists(path), 'Cannot find file: {}'.format(os.path.abspath(path))
    with open(path) as reader:
        _rgb_hash_2_sources = cPickle.load(reader)
    return _rgb_hash_2_sources


logging.info('Loading rgb_hash_2_sources')
rgb_hash_2_sources = load_rgb_hash_2_sources()


# --
# S3
# --

def get_bucket():
    with open('../aws/cred.json') as reader:
        cred = json.load(reader)
    _s3 = boto3.resource('s3', aws_access_key_id=cred['aws_access_key_id'],
                         aws_secret_access_key=cred['aws_secret_access_key'])
    _bucket = _s3.Bucket('12306captchas')
    return _bucket


logging.info('Establishing S3 connection')
bucket = get_bucket()


# ------
# Routes
# ------


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

    paths = []
    for i_source, cur_source in enumerate(sources):
        source_name, image_loc = cur_source.split(':')[0], int(cur_source.split(':')[1])
        # Download
        destination = os.path.join(app_dir, './static/' + source_name)
        bucket.download_file(source_name, destination)
        # Load, crop
        target_image = get_sub_images(Image.open(destination))[image_loc]
        cur_path = '{}.jpg'.format(cur_source)
        # Save
        target_image.save(cur_path)
        # return
        paths.append(cur_path)
    return jsonify(paths)


if __name__ == '__main__':
    app.run(debug=True)
