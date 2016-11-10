#!/usr/bin/env python
# coding:utf-8

import requests
from hashlib import md5
import json
import argparse
import traceback
import glob
import os



class RClient(object):

    def __init__(self, username, password, soft_id, soft_key):
        self.username = username
        self.password = md5(password).hexdigest()
        self.soft_id = soft_id
        self.soft_key = soft_key
        self.base_params = {
            'username': self.username,
            'password': self.password,
            'softid': self.soft_id,
            'softkey': self.soft_key,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'Expect': '100-continue',
            'User-Agent': 'ben',
        }

    def rk_create(self, im, im_type, timeout=60):
        """
        im: 图片字节
        im_type: 题目类型
        """
        params = {
            'typeid': im_type,
            'timeout': timeout,
        }
        params.update(self.base_params)
        files = {'image': ('a.jpg', im)}
        r = requests.post('http://api.ruokuai.com/create.json', data=params, files=files, headers=self.headers)
        return r.text

    def rk_report_error(self, im_id):
        """
        im_id:报错题目的ID
        """
        params = {
            'id': im_id,
        }
        params.update(self.base_params)
        r = requests.post('http://api.ruokuai.com/reporterror.json', data=params, headers=self.headers)
        return r.text


if __name__ == '__main__':
    rc = RClient('aynamron', 'whoisnamron', '70573', '25719211ab1e43e285946732200d6f36')
    parser = argparse.ArgumentParser()
    parser.add_argument("path", action="store",
                        help="specify the directory of labeled image")
    parser.add_argument("group", type=int,
                        help="number of total grouops")
    parser.add_argument("i", type=int,
                        help="the group of image to process")
    args = parser.parse_args()
    filenames = sorted(glob.glob(os.path.join(args.path, "*.jpg")))
    with open("%d.txt" % args.i, "w" ) as output:
        for f in filenames:
            if abs(hash(f)) % args.group != args.i:
                continue
            print "opening file", f
            im = open(f, 'rb').read()
            try:
                ret_str = rc.rk_create(im, 4000)
            except:
                traceback.print_exc()
                continue
            print ret_str
            output.write((u"%s %s\n" % (f, ret_str)).encode('utf-8'))
