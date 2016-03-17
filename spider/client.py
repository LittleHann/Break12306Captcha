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
from PIL import Image

if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context


UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36"
pic_url = "https://kyfw.12306.cn/otn/passcodeNew/getPassCodeNew?module=login&rand=sjrand&0.%d"
messageQueue = Queue.Queue()
uploadQueue = Queue.Queue(maxsize=100)
removeQueue = Queue.Queue(maxsize=100)


def isValidImage(path):
    try:
        im = Image.open(path)
    except:
        traceback.print_exc()
        return False
    if os.path.getsize(path) < 1500:
        print os.path.getsize(path)
        return False
    return True


def getImage(dirname="download", filename="tmp.jpg"):
    try:
        resp = urllib2.urlopen(pic_url % (random.randrange(10**18, 10**19)), timeout=10)
    except:
        messageQueue.put(traceback.format_exc())
        return ""
    raw = resp.read()
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    messageQueue.put("image size:%d" % len(raw))
    path = os.path.join(dirname, filename)
    with open(path, 'wb') as fp:
        fp.write(raw)
    if not isValidImage(path):
        return ""
    return path


def generateFileName():
    return datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S_") \
        + "".join([random.choice(string.uppercase + string.lowercase + string.digits)
                   for i in range(0, 5)]) + ".jpg"


def imageDownloader(terminate):
    sleepTime = 1
    while not terminate.isSet():
        fname = generateFileName()
        path = getImage(filename=fname)
        if path:
            uploadQueue.put(path)
            sleepTime = random.randint(2, 5)
        else:
            sleepTime = sleepTime * 2 if sleepTime < 3600 else 3600  # 3600s
            messageQueue.put('Invalid Image, sleeping for %ds' % (sleepTime))
        time.sleep(sleepTime)


def messagePrinter(terminate):
    while not terminate.isSet() or not messageQueue.empty():
        try:
            print messageQueue.get(timeout=1),
            print datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")
        except Queue.Empty:
            pass


def imageUploader(terminate):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(settings.bucketname)
    while not terminate.isSet() or not uploadQueue.empty():
        try:
            path = uploadQueue.get(timeout=1)
        except Queue.Empty:
            continue
        s3.meta.client.upload_file(
            path, settings.bucketname, os.path.basename(path))
        messageQueue.put("Uploaded successfully: %s." % path)
        if removeQueue.full():
            try:
                t_path = removeQueue.get()
                messageQueue.put("removing file %s" % t_path)
                os.system("rm %s > /dev/null" % t_path)
            except:
                messageQueue.put(traceback.format_exc())
        removeQueue.put(path)
    while not removeQueue.empty():
        try:
            t_path = removeQueue.get()
            messageQueue.put("removing file %s" % t_path)
            os.system("rm %s > /dev/null" % t_path)
        except:
            messageQueue.put(traceback.format_exc())


if __name__ == '__main__':
    image_count = 0
    terminateEvent = threading.Event()
    downloader = threading.Thread(
        name='imageDownloader', target=imageDownloader, args=(terminateEvent,))
    printer = threading.Thread(name='messagePrinter',
                               target=messagePrinter, args=(terminateEvent,))
    uploader = threading.Thread(
        name='imageUploader', target=imageUploader, args=(terminateEvent,))
    downloader.start()
    printer.start()
    uploader.start()
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        terminateEvent.set()
    downloader.join()
    print "downloader exited..."
    uploader.join()
    print "uploader exited..."
    printer.join()
    print "printer exited..."
