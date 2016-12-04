from PIL import Image
import os
import cPickle
from flask import Flask, request, jsonify

app = Flask(__name__)


# ----------
# On startup
# ----------

def load_rgb_key_2_hashes(path='/home/haonans/capstone/data/rgb_key_2_hashes.pickle'):
    """ RGB key to a list of RGB hashes """
    assert os.path.exists(path), 'Cannot find file: {}'.format(os.path.abspath(path))
    with open(path) as reader:
        rgb_key_2_hashes = cPickle.load(reader)
    return rgb_key_2_hashes


def load_hash_2_sources(path):
    """ RGB hash to a list of sources ('filename:loc') """
    assert os.path.exists(path), 'Cannot find file: {}'.format(os.path.abspath(path))
    with open(path) as reader:
        hash_2_sources = cPickle.load(reader)
    return hash_2_sources


# ------
# Routes
# ------


@app.route('/getImage')
def get_image():
    """ This function returns a list of static urls

     Example request url: GET http://127.0.0.1/getImage?rgb_hash=1&max_query=2
    """
    rgb_hash = request.args.get('rgb_hash')
    max_query = request.args.get('max_query')
    # TODO: query
    # TODO: download and save, get sub_image, refer to tools/get_image
    # TODO: return
    return jsonify('Successful')


if __name__ == '__main__':
    # TODO: ssh` tunneling
    # TODO: Gunicorn
    app.run(debug=True)
