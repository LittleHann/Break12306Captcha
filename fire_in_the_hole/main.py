# encoding: UTF-8

import os
import json

import sys
from PIL import Image
import numpy as np

import path_magic
from image_hash import get_sub_images, calc_perceptual_hash
from database import get_predictions, get_rgb_key, boom

labor = sorted([['2016_03_27_15_14_45_57YiC.jpg', u'核桃'.encode('utf-8')],
                ['2016_03_28_12_15_10_DBFb1.jpg', u'荷叶'.encode('utf-8')],
                ['2016_11_28_06_08_21_qGb2A.jpg', u'肥皂盒'.encode('utf-8')],
                ['2016_11_28_04_57_50_2cjET.jpg', u'绿豆'.encode('utf-8')],
                ['2016_11_28_04_26_20_hY6Ux.jpg', u'绿豆'.encode('utf-8')],
                ['2016_11_28_03_53_34_K69pF.jpg', u'蚊香'.encode('utf-8')],
                ['2016_11_27_21_25_32_IVV1x.jpg', u'骆驼'.encode('utf-8')],
                ['2016_11_27_14_48_50_E0hyz.jpg', u'菠萝'.encode('utf-8')],
                ['2016_11_28_03_05_24_l3ETv.jpg', u'萝卜'.encode('utf-8')],
                ['2016_11_25_04_11_05_YgbuM.jpg', u'鲨鱼'.encode('utf-8')],
                ['2016_11_24_18_26_29_NKuDe.jpg', u'油'.encode('utf-8')],
                ['2016_11_25_07_24_45_9ip9p.jpg', u'核桃'.encode('utf-8')],
                ['2016_11_25_03_03_27_wBfHA.jpg', u'楼梯'.encode('utf-8')],
                ['2016_11_27_15_41_17_7YseP.jpg', u'煤油灯'.encode('utf-8')],
                ['2016_11_27_16_20_04_58BBT.jpg', u'风筝'.encode('utf-8')],
                ['2016_11_27_16_42_53_Mr56e.jpg', u'贝壳'.encode('utf-8')],
                ['2016_11_27_16_50_08_9C62x.jpg', u'保温杯'.encode('utf-8')],
                ['2016_11_27_17_23_57_THrIz.jpg', u'馄饨'.encode('utf-8')],
                ['2016_11_27_19_04_08_7yPbV.jpg', u'鱼缸'.encode('utf-8')],
                ['2016_11_27_19_15_04_1Q4P5.jpg', u'绿豆'.encode('utf-8')],
                ['2016_11_27_20_34_37_FdDK6.jpg', u'仙人球'.encode('utf-8')],
                ['2016_11_27_21_06_17_VyBP3.jpg', u'蒸笼'.encode('utf-8')],
                ['2016_11_27_21_44_41_Y9ccD.jpg', u'风筝'.encode('utf-8')],
                ['2016_11_27_22_26_03_CG4p6.jpg', u'手套'.encode('utf-8')],
                ['2016_11_27_23_39_40_qorAu.jpg', u'太阳能'.encode('utf-8')],
                ['2016_11_28_00_15_15_CV2jH.jpg', u'箱子'.encode('utf-8')],
                ['2016_11_28_01_02_20_npHJR.jpg', u'电饭煲'.encode('utf-8')],
                ['2016_11_27_15_30_43_WThkw.jpg', u'塑料杯'.encode('utf-8')],
                ['2016_11_27_14_41_46_12tn6.jpg', u'花瓶'.encode('utf-8')],
                ['2016_11_27_14_26_04_z2Jvm.jpg', u'树叶'.encode('utf-8')],
                ['2016_11_27_12_16_27_yvLEY.jpg', u'药片'.encode('utf-8')],
                ['2016_11_27_12_14_08_cXW8P.jpg', u'拉链'.encode('utf-8')],
                ['2016_11_27_11_18_00_vScd5.jpg', u'海鸥'.encode('utf-8')],
                ['2016_11_27_10_52_17_G0BxA.jpg', u'游泳池'.encode('utf-8')],
                ['2016_11_27_10_15_01_OjPBb.jpg', u'毛线'.encode('utf-8')],
                ['2016_11_27_10_13_32_PkagS.jpg', u'袋鼠'.encode('utf-8')],
                ['2016_11_27_10_06_35_ODM9c.jpg', u'游泳池'.encode('utf-8')],
                ['2016_11_27_09_59_54_6zsLt.jpg', u'篮球'.encode('utf-8')],
                ['2016_11_27_09_08_59_z6HEN.jpg', u'印章'.encode('utf-8')],
                ['2016_11_27_07_38_21_KMjrh.jpg', u'仪表盘'.encode('utf-8')],
                ['2016_11_27_06_10_07_hi5uH.jpg', u'披萨'.encode('utf-8')],
                ['2016_11_27_05_55_47_SZ2d4.jpg', u'电线'.encode('utf-8')],
                ['2016_11_27_04_39_25_oZlG9.jpg', u'人参'.encode('utf-8')],
                ['2016_11_27_04_01_40_IvWqp.jpg', u'楼梯'.encode('utf-8')],
                ['2016_11_27_03_25_32_hoiXy.jpg', u'电子秤'.encode('utf-8')],
                ['2016_05_13_20_10_04_uCHRQ.jpg', u'西红柿'.encode('utf-8')],
                ['2016_05_13_10_18_07_xOE3Y.jpg', u'煤油灯'.encode('utf-8')],
                ['2016_05_11_23_25_23_IxTzI.jpg', u'排风机'.encode('utf-8')],
                ['2016_05_08_20_53_48_MXt9e.jpg', u'星星'.encode('utf-8')],
                ['2016_11_23_12_00_26_7xqRu.jpg', u'轮胎'.encode('utf-8')]
                ], key=lambda t: t[0])

truths = map(lambda line: line.strip(), open('truth.txt'))
# truths = map(lambda line: line.strip(), open('fake.txt'))
filenames = map(lambda line: line.strip().decode('utf-8'), open('filenames.txt'))

# for base_path, label in labor:
for i in xrange(50):
    print '--{}--'.format(i + 1)
    base_path, label = filenames[i], truths[i]
    # full_path = '../data/captchas/{}'.format(base_path)
    full_path = '../data/download/{}'.format(base_path)
    assert os.path.isfile(full_path)

    sub_images = get_sub_images(Image.open(full_path))
    rgb_keys = map(boom, sub_images)
    # assert all(rgb_keys)

    print base_path, label

    all_predictions = map(lambda k: get_predictions(k), rgb_keys)
    probabilities = []
    for i, predictions in enumerate(all_predictions):

        # print i
        # for k, v in predictions:
        #    print k + '\t%.3f' % v

        d = dict(predictions)
        probabilities.append(d.get(label, 0))
    prob_arr = np.array(probabilities)

    ind = prob_arr.argsort()[::-1]
    print ind[:4]
    print prob_arr[ind][:4]
    print

"""
for file in $(ls | grep .jpg | tail -n 40)
do
echo $file;
imgcat $file;
done
"""

"""

当前策略, 如果有比0.1大的, 那么全部选择
如果没有, 只选择一个最大的

32 / 50
"""
