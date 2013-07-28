#!/usr/bin/python
# -*- coding: utf-8 -*-

from jx import log
from utils import globalconfig as GC
from analyse.result import Result
from entities.name_pb2 import RawNameItemInfo, GlobalNameInfo

import random

def getRadomRawNameItemInfo():
    info = RawNameItemInfo()
    info.text = unichr(random.randint(0x4E00, 0x9FCC + 1))
    info.count = random.randint(0, 100)
    info.male_count = random.randint(0, 100)
    info.female_count = random.randint(0, 100)
    info.rank = random.randint(0, 100)
    info.sum_count = random.randint(0, 10000)
    return info

def getRandomResultMap(length):
    length = random.randint(length, length * 5)
    m = {}
    for i in range(0, length):
        info = getRadomRawNameItemInfo()
        m[info.text] = info
    return m


def getRandomGlobalNameInfo():
    info = GlobalNameInfo()
    info.person_count = random.randint(100,1000)
    info.male_count = random.randint(100,1000)
    info.female_count = random.randint(100,1000)

    info.xing_char_count = random.randint(100,1000)
    info.xing_count = random.randint(100,1000)
    info.ming_char_count = random.randint(100,1000)
    info.ming_count = random.randint(100,1000)
    info.xing_ming_count = random.randint(100,1000)


def getRandomResult(length=1000):
    result = Result()

    result.glbalInfo = getRandomGlobalNameInfo()
    result.xingCharMap = getRandomResultMap(length)
    result.xingMap = getRandomResultMap(length)
    result.mingCharMap = getRandomResultMap(length)
    result.mingMap = getRandomResultMap(length)
    result.xingMingMap = getRandomResultMap(length)

    result.caculate()
    
    return result

