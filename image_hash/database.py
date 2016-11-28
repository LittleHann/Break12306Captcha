import numpy as np
from PIL import Image

from redis import Redis
import boto3
from botocore.exceptions import ClientError

import os
import time
import decimal

from image_hash import calc_perceptual_hash, get_sub_images


# -----
# Redis
# -----

def get_redis(_host='localhost', _port=6379):
    # TODO: Redis eviction strategy
    # TODO: mark image as processed to async
    _redis = Redis(host=_host, port=_port)
    assert _redis.ping(), 'Redis server cannot be found!'
    return _redis


"""
Each grey hash is mapped to a list of Image IDs (uuid.uuid4()).

Each uuid is mapped to its rgb_hash and its source.
Each rgb_hash is mapped to its uuid
"""


# TODO: concurrency

class DatabaseOp(object):
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

    def clean(self):
        self.gray_table.delete()
        self.rgb_table.delete()

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
                print
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
                print
            assert rgb_2_details_table.table_status == 'ACTIVE'

        except ClientError:
            rgb_2_details_table = self.dynamodb.Table(_table_name)

        return rgb_2_details_table

    def store_captcha(self, captcha_path):
        # TODO: constants
        # TODO: celery async support

        captcha = Image.open(captcha_path)
        sub_images = get_sub_images(captcha)

        # store each sub-image
        for loc, cur_image in enumerate(sub_images):

            cur_gray_hash = calc_perceptual_hash(cur_image, mode='GRAY')
            cur_rgb_hash = calc_perceptual_hash(cur_image, mode='RGB')

            cur_gray_str = ''.join(map(str, cur_gray_hash))
            cur_rgb_str = ''.join(map(str, cur_rgb_hash))

            response = self.rgb_table.get_item(Key={'rgb_hash': cur_rgb_str})
            if 'Item' in response:
                # Find the same sub-image in the database
                self.gray_table.update_item(
                    Key={'gray_hash': cur_gray_str},
                    UpdateExpression='set rgb_hash_list = list_append(rgb_hash_list, :v)',
                    ExpressionAttributeValues={':v': [cur_rgb_str]},
                    ReturnValues='NONE'
                )

                self.rgb_table.update_item(
                    Key={'rgb_hash': cur_rgb_str},
                    UpdateExpression='set sources = list_append(sources, :v)',
                    ExpressionAttributeValues={':v': [{'path': captcha_path, 'location': loc}]},
                    ReturnValues='NONE'
                )
            else:
                response = self.gray_table.get_item(Key={'gray_hash': cur_gray_str})
                if 'Item' in response:

                    # scan the bucket
                    for prev_rgb_str in response['Item']['rgb_hash_list']:
                        prev_rgb_hash = np.array(map(int, prev_rgb_str))
                        hamming_dist = np.sum(cur_rgb_hash != prev_rgb_hash)
                        if hamming_dist < 15:
                            self.rgb_table.update_item(
                                Key={'rgb_hash': prev_rgb_str},  # IMPORTANT! here we use prev_rgb_str as its id
                                UpdateExpression='set sources = list_append(sources, :v)',
                                ExpressionAttributeValues={':v': [{'path': captcha_path, 'location': loc}]},
                                ReturnValues='NONE'
                            )
                            break  # IMPORTANT!
                    else:
                        self.rgb_table.put_item(
                            Item={
                                'rgb_hash': cur_rgb_str,
                                'gray_hash': cur_gray_str,
                                'sources': [{'path': captcha_path, 'location': loc}]
                            }
                        )

                    # update the bucket in the end
                    self.gray_table.update_item(
                        Key={'gray_hash': cur_gray_str},
                        UpdateExpression='set rgb_hash_list = list_append(rgb_hash_list, :v)',
                        ExpressionAttributeValues={':v': [cur_rgb_str]},
                        ReturnValues='NONE'
                    )
                else:
                    # Cannot find same images from the database
                    # Put the current images into the two tables
                    self.gray_table.put_item(
                        Item={
                            'gray_hash': cur_gray_str,
                            'rgb_hash_bucket': [cur_rgb_str]
                        }
                    )
                    self.rgb_table.put_item(
                        Item={
                            'rgb_hash': cur_rgb_str,
                            'gray_hash': cur_gray_str,
                            'sources': [{'path': captcha_path, 'location': loc}]
                        }
                    )


def get_captcha_paths(_captcha_dir):
    assert os.path.exists(_captcha_dir)
    return map(lambda p: os.path.join(_captcha_dir, p), os.listdir(_captcha_dir))


if __name__ == '__main__':
    import time

    start_time = time.time()

    db = DatabaseOp()
    captcha_paths = get_captcha_paths('/Users/haonans/Downloads/CAPTCHAs')
    for path in captcha_paths:
        db.store_captcha(path)
        print path

    print time.time() - start_time
