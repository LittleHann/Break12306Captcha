#!/usr/bin/env python
# coding:utf-8

import requests
from hashlib import md5
import json
import argparse
import traceback
import glob
import os

PHRASE_FILE_PATH = '../labelgenerator/labels.txt'
MAX_RETRY = 2

def load_chinese_phrases(path):
    chinese_phrases = []
    with open(path) as reader:
        for line in reader:
            # please decode with `utf8`
            chinese_phrases.append(line.strip().split()[0].decode("utf8"))
    print "%d Chinese phrases are loaded" % len(chinese_phrases)
    return chinese_phrases

def parse_result(line):
    image_path, json_str = line.split("\t")
    data = json.loads(json_str)
    data[u'path'] = image_path
    return data

def handle_frequent_mistake(word):
    replace_list = [(u"一", u""),
                    (u"魔", u"鹰"),
                    (u"加温器", u"加湿器"),
                    (u"榨汗机", u"榨汁机"),
                    (u"收间机", u"收音机"),
                    (u"萝卡", u"萝卜")]
    for w1, w2 in replace_list:
        word = word.replace(w1, w2)
    return word

def submit_err(sess, id):
    data = sess.rk_report_error(id)
    return data



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
    rc = RClient('username', 'password', 'softwareID', 'sessionID')
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("-p", "--path", action="store",
                        help="specify the directory of labeled image")
    mode.add_argument("-f", "--file", action="store",
                        help="specify a file containing a image file path in each row")

    parser.add_argument("group", type=int,
                        help="number of total grouops")
    parser.add_argument("i", type=int,
                        help="the group of image to process")
    args = parser.parse_args()
    filenames = list()
    if args.path:
        filenames = sorted(glob.glob(os.path.join(args.path, "*.jpg")))
    elif args.file:
        with open(args.file) as f:
            filenames = f.readlines()
        filenames = [name.strip() for name in filenames]
    retry = 0
    output = open("%d.txt" % args.i, "w")
    phrases = set(load_chinese_phrases(PHRASE_FILE_PATH))
    i = 0
    while i < len(filenames):
        if retry >= MAX_RETRY:
            i += 1
            retry = 0

        f = filenames[i]
        if abs(hash(f)) % args.group != args.i:
            i += 1
            retry = 0
            continue
        print "opening file", f
        im = open(f, 'rb').read()
        try:
            ret_str = rc.rk_create(im, 4000)
        except:
            traceback.print_exc()
            continue

        data = json.loads(ret_str)
        if u'Result' not in data:
            retry += 1
            continue
        elif handle_frequent_mistake(data[u'Result']) not in phrases:
            retry += 1
            print submit_err(rc, data[u'Id'])
            continue
        print ret_str
        output.write((u"%s\t%s\n" % (f, \
                                     handle_frequent_mistake(data[u'Result'])))\
                                     .encode('utf-8'))
        i += 1
        retry = 0
