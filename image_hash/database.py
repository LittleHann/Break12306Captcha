# coding: UTF-8
import numpy as np
from PIL import Image
import sys
import logging

from redis import Redis
import boto3
from botocore.exceptions import ClientError

import os
import time
import decimal

try:
    from image_hash import calc_perceptual_hash, get_sub_images
except ImportError:
    from __init__ import calc_perceptual_hash, get_sub_images

# -------
# Logging
# -------

logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s %(levelname)s %(message)s')


# -----
# Redis
# -----

def get_redis(_host='localhost', _port=6379):
    _redis = Redis(host=_host, port=_port)
    assert _redis.ping(), 'Redis server cannot be found!'
    return _redis


"""
Each grey hash is mapped to a list of Image IDs (uuid.uuid4()).

Each uuid is mapped to its rgb_hash and its source.
Each rgb_hash is mapped to its uuid
"""


class DatabaseOp():
    """ Database operations
    Here we use RGB hashes of each image as its id.

    There are several tables:

    1. A gray-scale hash to a bucket of RGB hashes. This is the gray-scale bucket.
        Key: gray-scale hash (str)
        Val: list of RGB hashes (str)
    2. A RGB hash to to its gray-scale hash, a list of all sources and corresponding locations.
        Key: RGB hash (str)
        Value: dict/object
    """

    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')

        self.gray_2_rgb_buckets_table = self.__get_gray_2_rgb_buckets_table()
        self.rgb_2_details_table = self.__get_rgb_2_details_table()

        # Aliases
        self.gray_table = self.gray_2_rgb_buckets_table
        self.rgb_table = self.rgb_2_details_table

        self.db_time = 0

    def clean(self):
        for item in self.gray_table.scan()['Items']:
            self.gray_table.delete_item(Key={'gray_hash': item['gray_hash']})

        for item in self.rgb_table.scan()['Items']:
            self.rgb_table.delete_item(Key={'rgb_hash': item['rgb_hash']})

    def __get_gray_2_rgb_buckets_table(self):
        """ Please refer to table(1) in class doc."""
        _table_name = 'gray_2_rgb_buckets'
        try:
            gray_2_rgb_buckets_table = self.dynamodb.create_table(
                TableName=_table_name,
                KeySchema=[
                    {
                        'AttributeName': 'gray_hash',
                        'KeyType': 'HASH'
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'gray_hash',
                        'AttributeType': 'S'
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 10000,
                    'WriteCapacityUnits': 10000
                }
            )
            print "Creating table {}".format(_table_name),
            # It might take some time to create table
            while gray_2_rgb_buckets_table.table_status == 'CREATING':
                print '.',
                time.sleep(1)
                gray_2_rgb_buckets_table = self.dynamodb.Table(_table_name)
            else:
                print >> sys.stdout
            assert gray_2_rgb_buckets_table.table_status == 'ACTIVE'
        except ClientError as e:
            gray_2_rgb_buckets_table = self.dynamodb.Table(_table_name)

        return gray_2_rgb_buckets_table

    def __get_rgb_2_details_table(self):
        """ Please refer to table(2) in class doc """
        _table_name = 'rgb_2_details'
        try:
            rgb_2_details_table = self.dynamodb.create_table(
                TableName=_table_name,
                KeySchema=[
                    {
                        'AttributeName': 'rgb_hash',
                        'KeyType': 'HASH'
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'rgb_hash',
                        'AttributeType': 'S'

                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 10000,
                    'WriteCapacityUnits': 10000
                }
            )

            print "Creating table {}".format(_table_name),
            while rgb_2_details_table.table_status == 'CREATING':
                print '.',
                time.sleep(1)
                rgb_2_details_table = self.dynamodb.Table(_table_name)
            else:
                print >> sys.stdout
            assert rgb_2_details_table.table_status == 'ACTIVE'

        except ClientError:
            rgb_2_details_table = self.dynamodb.Table(_table_name)

        return rgb_2_details_table

    def store_captcha(self, captcha_path):
        # TODO: constants
        # TODO: celery async support

        try:
            captcha = Image.open(captcha_path)
        except IOError as e:
            print e
            return

        sub_images = get_sub_images(captcha)

        # store each sub-image
        for loc, cur_image in enumerate(sub_images):

            cur_gray_hash = calc_perceptual_hash(cur_image, mode='GRAY')
            cur_rgb_hash = calc_perceptual_hash(cur_image, mode='RGB')

            cur_gray_str = ''.join(map(str, cur_gray_hash))
            cur_rgb_str = ''.join(map(str, cur_rgb_hash))

            _start = time.time()

            response = self.rgb_table.get_item(Key={'rgb_hash': cur_rgb_str})
            if 'Item' in response:
                # current image already exists in the database, we should just enrich the source in the rgb_table

                self.rgb_table.update_item(
                    Key={'rgb_hash': cur_rgb_str},
                    UpdateExpression='set sources = list_append(sources, :v)',
                    ExpressionAttributeValues={':v': [{'path': captcha_path, 'location': loc}]},
                    ReturnValues='NONE'
                )

            else:
                # Because now we don't if the current image is in the database, we check the bucket of grah_hash
                response = self.gray_table.get_item(Key={'gray_hash': cur_gray_str})
                if 'Item' in response:
                    # We can find its bucket
                    for prev_rgb_str in response['Item']['rgb_hash_list']:
                        prev_rgb_hash = np.array(map(int, prev_rgb_str))
                        hamming_dist = np.sum(cur_rgb_hash != prev_rgb_hash)
                        if hamming_dist < 15:
                            # we find it, enrich the source
                            self.rgb_table.update_item(
                                Key={'rgb_hash': prev_rgb_str},  # IMPORTANT! here we use prev_rgb_str as its id
                                UpdateExpression='set sources = list_append(sources, :v)',
                                ExpressionAttributeValues={':v': [{'path': captcha_path, 'location': loc}]},
                                ReturnValues='NONE'
                            )
                            break  # IMPORTANT!
                    else:
                        # It is a new image, but we already have its bucket
                        self.rgb_table.put_item(
                            Item={
                                'rgb_hash': cur_rgb_str,
                                'gray_hash': cur_gray_str,
                                'sources': [{'path': captcha_path, 'location': loc}]
                            }
                        )

                        self.gray_table.update_item(
                            Key={'gray_hash': cur_gray_str},
                            UpdateExpression='set rgb_hash_list = list_append(rgb_hash_list, :v)',
                            ExpressionAttributeValues={':v': [cur_rgb_str]},
                            ReturnValues='NONE'
                        )
                else:
                    # It is a totally new image!
                    # TODO: celery need to catch exception
                    self.gray_table.put_item(
                        Item={
                            'gray_hash': cur_gray_str,
                            'rgb_hash_list': [cur_rgb_str]
                        }
                    )
                    self.rgb_table.put_item(
                        Item={
                            'rgb_hash': cur_rgb_str,
                            'gray_hash': cur_gray_str,
                            'sources': [{'path': captcha_path, 'location': loc}]
                        }
                    )
            self.db_time += time.time() - _start


def get_captcha_paths(_captcha_dir):
    assert os.path.exists(_captcha_dir)
    return map(lambda p: os.path.join(_captcha_dir, p), os.listdir(_captcha_dir))


def build_database():
    import time

    start_time = time.time()

    db = DatabaseOp()
    # db.clean()
    logging.warning("Database is cleaned")
    # captcha_dir = '/Users/haonans/Downloads/CAPTCHAs'
    captcha_dir = '/data2/heqingy/captchas'

    captcha_path_list = '/data2/haonans/captcha_path_list.txt'
    with open(captcha_path_list) as reader:
        for line in reader:
            path = os.path.join(captcha_dir, line.strip())
            db.store_captcha(path)
            logging.warning('{} is processed'.format(path))

    print time.time() - start_time
    print db.db_time
    # 490.036904097
    # 391.408583403


build_database()


def inspect_database():
    db = DatabaseOp()
    all_items = db.rgb_table.scan()['Items']
    for cur_item in all_items:
        if len(cur_item['sources']) > 1:
            # Concatenate all same images into one landscape
            same_images = []
            for source in cur_item['sources']:
                same_images.append(get_sub_images(Image.open(source['path']))[int(source['location'])])

            widths, heights = zip(*(i.size for i in same_images))
            total_width = sum(widths)
            max_height = max(heights)
            landscape = Image.new('RGB', (total_width, max_height))
            x_offset = 0
            for image in same_images:
                landscape.paste(image, (x_offset, 0))
                x_offset += image.size[0]

            landscape.show()
