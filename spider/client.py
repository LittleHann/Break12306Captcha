#!/usr/bin/python

# Heqing Ya modified from following file:
# #  FileName    : fuck12306.py
# #  Author      : MaoMaog Wang <andelf@gmail.com>
# #  Created     : Mon Mar 16 22:08:41 2015 by ShuYu Wang
# #  Copyright   : Feather (c) 2015
# #  Description : fuck fuck 12306
# #  Time-stamp: <2015-03-16 22:12:31 andelf>


#from PIL import Image
import urllib
import urllib2
import re
import json
import os
import datetime
import string
import random
# hack CERTIFICATE_VERIFY_FAILED
# https://github.com/mtschirs/quizduellapi/issues/2
import ssl
import threading
import time
import Queue
import traceback
import boto3
import settings

if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context


UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36"
pic_url = "https://kyfw.12306.cn/otn/passcodeNew/getPassCodeNew?module=login&rand=sjrand&0.%d"
messageQueue = Queue.Queue()
uploadQueue = Queue.Queue(maxsize=100)
removeQueue = Queue.Queue(maxsize=100)


def isValidImage(raw_data):
    return False if len(raw_data) < 1500 or "</html>" in raw_data else True


def getImage(dirname="download", filename="tmp.jpg"):
    resp = urllib2.urlopen(pic_url % (random.randrange(10**18, 10**19)), timeout=10)
    raw = resp.read()
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    messageQueue.put("image size:%d" % len(raw))
    if not isValidImage(raw):
        return ""
    path = os.path.join(dirname, filename)
    with open(path, 'wb') as fp:
        fp.write(raw)
    return path


def generateFileName():
    return datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S_") \
        + "".join([random.choice(string.uppercase + string.lowercase + string.digits)
                   for i in range(0, 5)]) + ".jpg"


def imageDownloader():
    sleepTime = 1
    while True:
        fname = generateFileName()
        path = getImage(filename=fname)
        if path:
            uploadQueue.put(path)
            sleepTime = 1
        else:
            sleepTime = sleepTime * 2 if sleepTime < 25200 else 25200  # 3600s/h * 7h
            messageQueue.put('Invalid Image, sleepping for %ds' % (sleepTime))
            time.sleep(sleepTime)


def messagePrinter():
    while True:
        print messageQueue.get(),
        print datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")


def imageUploader():
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(settings.bucketname)
    while True:
        path = uploadQueue.get()
        s3.meta.client.upload_file(path, settings.bucketname, os.path.basename(path))
        messageQueue.put("Uploaded successfully: %s." % path)
        if removeQueue.full():
            try:
                path = removeQueue.get()
                os.system("rm %s > /dev/null" % path)
            except:
                messageQueue.put(traceback.format_exc())
        removeQueue.put(path)


if __name__ == '__main__':
    image_count = 0
    downloader = threading.Thread(name='imageDownloader', target=imageDownloader)
    printer = threading.Thread(name='messagePrinter', target=messagePrinter)
    uploader = threading.Thread(name='imageUploader', target=imageUploader)
    downloader.start()
    printer.start()
    uploader.start()
    downloader.join()
    printer.join()
    uploader.join()
