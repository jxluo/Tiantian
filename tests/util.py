#!/usr/bin/python
# -*- coding: utf-8 -*-

from jx import log
from utils import globalconfig as GC
from analyse.result import MapValue
from analyse.result import Result

import random

def assertValueEqual(a, b):
    assert a
    assert b
    assert a.key == b.key
    assert a.code == b.code
    assert a.count == b.count
    assert a.maleCount == b.maleCount
    assert a.femaleCount == b.femaleCount
    assert a.rank == b.rank

def getRadomMapValue():
    key = unichr(random.randint(0x4E00, 0x9FCC + 1))
    haveCode = random.randint(0, 1)
    if haveCode:
        value = MapValue(key, ord(key))
    else:
        value = MapValue(key)
    value.count = random.randint(0, 100)
    value.maleCount = random.randint(0, 100)
    value.femaleCount = random.randint(0, 100)
    value.rank = random.randint(0, 100)
    return value

def getRandomMap(length):
    length = random.randint(length, length * 5)
    m = {}
    for i in range(0, length):
        value = getRadomMapValue()
        m[value.key] = value

    # Assert 
    m1 = {}
    m2 = {}
    items = m.items()
    for item in items:
        key1 = item[0]
        key2 = item[1].key
        assert key1 == key2
        assert key1.encode('utf-8') == key2.encode('utf-8')
        assert m1.get(key1) == None
        m1[key1] = 1
        assert m2.get(key1.encode('utf-8')) == None
        m2[key1.encode('utf-8')] = 2

    return m

def getRandomResult(length=1000):
    result = Result()
    result.personCount = random.randint(100,1000)
    result.globalMaleCount = random.randint(100,1000)
    result.globalFemaleCount = random.randint(100,1000)

    result.allXingCharCount = random.randint(100,1000)
    result.allXingCount = random.randint(100,1000)
    result.allMingCharCount = random.randint(100,1000)
    result.allMingCount = random.randint(100,1000)

    result.xingCharMap = getRandomMap(length)
    result.xingMap = getRandomMap(length)
    result.mingCharMap = getRandomMap(length)
    result.mingMap = getRandomMap(length)

    result.caculate()
    
    return result

