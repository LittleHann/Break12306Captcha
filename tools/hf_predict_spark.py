#!/usr/bin/env python
# encoding: utf-8

'''
Predict with harmonic field
'''


import sys
import cPickle as pickle
from pyspark import SparkConf, SparkContext
from pyspark.mllib.linalg import SparseVector
import numpy as np
import json
import argparse
from collections import defaultdict
import time
import pyspark

DEFAULT_ITER = 5
N_CATEGORY = 230


# dicitonaries to be broadcast
label_prob = None
phash_count = None


# possible options to G:
# lambda x: np.log(x + b)
# lambda x: x
# lambda x: x ** 2
# lambda x: sqrt(x)
G = lambda x: x**2

W = lambda (phash, similarity, cooccur): (phash, similarity * G(cooccur))

chinese_labels = [u"床", u"桥", u"油", u"狗", u"猫", u"葱", u"锣", u"鹰", u"乌云", u"胶卷", u"人参", u"企鹅", u"光盘", u"兔子", u"公路", u"冰箱", u"刺猬", u"剪纸", u"南瓜", u"印章", u"卷尺", u"哑铃", u"啤酒", u"喷泉", u"围巾", u"土豆", u"墨镜", u"天线", u"天鹅", u"奖状", u"奶瓶", u"山楂", u"帐篷", u"干冰", u"年画", u"恐龙", u"戒指", u"手套", u"手机", u"扫把", u"扳手", u"报纸", u"披萨", u"拉链", u"数字", u"斑马", u"星星", u"月亮", u"本子", u"杏仁", u"枕头", u"树叶", u"核桃", u"梳子", u"椰子", u"楼梯", u"樱桃", u"毛巾", u"毛线", u"气球", u"水管", u"沙拉", u"沙漠", u"油条", u"洋葱", u"海滩", u"海豚", u"海豹", u"海鸥", u"游艇", u"漏斗", u"灯笼", u"烤鸭", u"熨斗", u"牙刷", u"牙膏", u"狮子", u"玛瑙", u"球拍", u"生姜", u"电线", u"白菜", u"皮球", u"盒子", u"盘子", u"砚台", u"磁铁", u"秋千", u"章鱼", u"竹席", u"算盘", u"箭头", u"箱子", u"篮球", u"粽子", u"红枣", u"红豆", u"红酒", u"纸牌", u"纽扣", u"经筒", u"绿豆", u"翅膀", u"翡翠", u"老虎", u"脸谱", u"舞狮", u"航母", u"芒果", u"花瓶", u"花生", u"花轿", u"茶几", u"药片", u"荷叶", u"菠萝", u"萝卜", u"蒸笼", u"薯条", u"蚂蚁", u"蚊子", u"蚊香", u"蛋挞", u"蜂蜜", u"蜗牛", u"蜜蜂", u"蜡烛", u"蜥蜴", u"蜻蜓", u"蝌蚪", u"蝴蝶", u"螃蟹", u"衣架", u"袋鼠", u"被子", u"裙子", u"西装", u"试管", u"话梅", u"贝壳", u"路灯", u"轮胎", u"钟表", u"钻石", u"铁轨", u"铁锹", u"铃铛", u"键盘", u"雕像", u"雨靴", u"青椒", u"青蛙", u"鞋刷", u"鞭炮", u"韭菜", u"风筝", u"飞机", u"饭盒", u"馄饨", u"骆驼", u"鱼缸", u"鱿鱼", u"鲨鱼", u"鸭蛋", u"龙舟", u"三明治", u"中国结", u"人民币", u"仙人球", u"仪表盘", u"传真机", u"保温杯", u"保龄球", u"创可贴", u"加湿器", u"发电机", u"喷雾器", u"图书馆", u"垃圾桶", u"塑料杯", u"塑料瓶", u"太阳能", u"安全帽", u"手掌印", u"手电筒", u"打字机", u"投影仪", u"报刊亭", u"排风机", u"摩天轮", u"收纳箱", u"收音机", u"文件夹", u"档案袋", u"榨汁机", u"油纸伞", u"游泳圈", u"游泳池", u"灭火器", u"热水器", u"热水瓶", u"热水袋", u"煤油灯", u"猫头鹰", u"电子秤", u"电热壶", u"电视机", u"电话亭", u"电话机", u"电饭煲", u"矿泉水", u"糖葫芦", u"紫砂壶", u"红绿灯", u"缝纫机", u"肥皂盒", u"自行车", u"苍蝇拍", u"蒙古包", u"西红柿", u"警示牌", u"订书机", u"调色板", u"辣椒酱", u"金字塔", u"钥匙圈", u"青花瓷", u"食用油", u"高压锅", u"七星瓢虫"]


class TicTock:
    def __init__(self):
        self._timer = time.time()
    
    def tick(self):
        self._timer = time.time()

    def tock(self):
        sys.stderr.write("Used Time: {}s\n".format(time.time() - self._timer)) 

def get_sparse_index(vec):
    vec = np.array(vec)
    threshold = 0
    idx = np.where(vec > threshold)[0]
    return idx, vec[idx]

def load_label_prob(path):
    sys.stderr.write("loading {}\n".format(path))
    result = dict()
    if path.endswith(".pickle"):
        result = pickle.load(open(path, "rb"))
    else:
        with open(path) as f:
            for line in f:
                if line.strip():
                    phash, prob = eval(line)
                    prob = prob.toArray()
                    result[phash] = prob
    sys.stderr.write("loading done.\n".format(path))
    return result


def load_phash_count(path):
    sys.stderr.write("loading {}\n".format(path))
    t = json.load(open(path))
    sys.stderr.write("loading done.\n".format(path))
    return t['image_occurrence']


def load_adjcent_list(path):
    sys.stderr.write("loading {}\n".format(path))
    result = dict()
    with open(path) as f:
        for line in f:
            if line.strip():
                phash, adjlist = eval(line)
                result[phash] = adjlist
    sys.stderr.write("loading done.\n".format(path))
    return result

def calc_weight(t):
    '''
    Input:
        t: an adjcent list for phash_i:
            [(phash_j1, fc7_sim_j1, coocur_count_j1), ...]
    Output:
        result: a list of weights for phash_i:
            [(phash_j1, wij), ...]
    '''
    
    k, v = t
    return (k, list(map(W, v)))


def append_vec(t):
    phash_i, adj_list = t
    new_list = list()
    for phash_j, weight_ij in adj_list:
        v = label_prob[phash_j]
        new_list.append((phash_j, weight_ij, label_prob[phash_j]))
    return phash_i, label_prob[phash_i].toArray(), label_prob[phash_i], new_list


def sparcify_vec(vec, threshold = 1e-3, top_k=None, sort=True):
    # remove zeros and specify
    # z = np.linalg.norm(vec, ord=2)
    z = np.sum(vec)
    if z:
        vec /= z
    result = filter(lambda x: x[1] > threshold, enumerate(vec))
    if sort:
        result.sort(key = lambda x: -x[1])
    result = result[:top_k]
    return result

def flat_adj_weight(t):
    phash_i, weight_list = t
    for phash_j, w_ij in weight_list:
        yield (phash_j, (phash_i, w_ij)) #swap i, j for join


def transform_chinese(t):
    phash, prob_list = t
    prob_list = list(map(lambda x: (chinese_labels[x[0]], x[1]), prob_list))
    return (phash, prob_list)



def main(argv):
    # parse args

    parser = argparse.ArgumentParser()
    parser.add_argument("rgb_label_prob", action="store",
                        help="specify the file path for label_prob of each RGB PHash")
    
    # TODO: refactor the pipeline to separate the image_occurrence dict from mapping.json
    parser.add_argument("mapping", action="store",
                        help="specify the file path for mapping.json, \
                            containing count of each RGB PHash")

    parser.add_argument("adjcent_list", action="store",
                    help="specify the file path for adjcent_list for each phash, in the format of \
                        [(phash_i, [(phash_j1, fc7_sim_j1, coocur_count_j1), ...])] ")
    parser.add_argument("--iter", type=int, default=5, 
                    help="specify the number of iteration, default {}".format(DEFAULT_ITER))
    parser.add_argument("--cn", action="store_const", default=False, const=True,
                    help="output Chinese Label")
    parser.add_argument("--output", action="store", default=None,
                    help="the path for output")
    parser.add_argument("--local", action="store_const", default=False, const=True,
                help="run the program in local mode")


    args = parser.parse_args()


    """ configure pyspark """
    conf = SparkConf().setAppName("Calculate Similarity")
    if args.local:
        conf = conf.setMaster('local[*]')
    sc = SparkContext(conf=conf)

    max_iter = args.iter if args.iter else DEFAULT_ITER
    timer = TicTock()

    timer.tick()
    label_prob = load_label_prob(args.rgb_label_prob)
    old_prob = sc.parallelize(label_prob.items())

    # global label_prob
    # label_prob = sc.broadcast(_label_prob)
    timer.tock()
    
    # TODO: refactor the pipeline to separate the image_occurrence dict from mapping.json
    timer.tick()
    phash_count = load_phash_count(args.mapping)
    # global phash_count
    # phash_count = sc.broadcast(_phash_count)
    # old_prob = sc.parallelize(_phash_count.items())

    timer.tock()


    timer.tick()
    sys.stderr.write("Start loading {}\n".format(args.adjcent_list))
    weight_list = sc.textFile(args.adjcent_list) \
                     .map(lambda x: eval(x)) \
                     .map(calc_weight)
                     # .flatMap(flat_adj_weight)

    sys.stderr.write("Done.\n")
    timer.tock()



    vec_add = lambda a, b: a + b
    def update_weight(phash_i, weight_list):
        w_sum =np.sum(map(lambda (phash, w): w, weight_list)) + G(phash_count[phash_i])
        result = np.zeros(N_CATEGORY)
        for phash_j, w_ij in weight_list:
            result += w_ij / w_sum * old_prob.lookup(phash_j)
        result += 0.5 * G(phash_count[phash_i]) * label_prob[phash_i]
        return (phash_i, result)

    for _iter in range(max_iter):
        sys.stderr.write("Iter: {}\n".format(_iter))
        timer.tick()
        new_prob = old_prob.map(update_weight)
        old_prob = new_prob
        sys.stderr.write("Iter: {} Done.\n".format(_iter))
        timer.tock()
    final_prob = old_prob.map(lambda x: (x[0], sparcify_vec(x[1])))
    if args.cn:
        final_prob = final_prob.map(transform_chinese)
    
    ostream = sys.stdout if not args.output else open(args.output, "w")
    if args.local:
        for k in final_prob.collect():
            ostream.write("{}\t{}\n".format(k[0], k[1]))
        ostream.close()
    else:
        final_prob.saveAsTextFile(args.output)
    sc.stop()

if __name__ == '__main__':
    main(sys.argv)