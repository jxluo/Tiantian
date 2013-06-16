#!/usr/bin/python
# -*- coding: utf-8 -*-

from jx import log
from utils import globalconfig as GC
from analyse.result import MapValue
from analyse.result import Result

import random


fileForMapValueTest = 'tmp/mapvaluetest'
fileForResultTest = 'tmp/resulttest'
dirForResultTest = 'tmp'


def assertValueEqual(a, b):
    assert a.key == b.key
    assert a.code == b.code
    assert a.count == b.count
    assert a.maleCount == b.maleCount
    assert a.femaleCount == b.femaleCount
    assert a.rank == b.rank


def testMapValueSerialization():
    key = u'姓'
    value1 = MapValue(key, ord(key))
    value1.count = 21
    value1.maleCount = 12
    value1.femaleCount = 9
    value1.rank = 10
    
    key = u'名字'
    value2 = MapValue(key)
    value2.count = 13
    value2.maleCount = 1
    value2.femaleCount = 7
    value2.rank = 121

    f = open(fileForMapValueTest, 'w')
    value1.write(f)
    value2.write(f)
    f.close()

    f = open(fileForMapValueTest, 'r')
    value3 = MapValue()
    value4 = MapValue()
    value3.read(f)
    value4.read(f)
    f.close()

    assertValueEqual(value1, value3)
    assertValueEqual(value2, value4)

def assertMapEqual(a, b):
    assert len(a) == len(b)
    akeys = [item[0] for item in a.items()]
    bkeys = [item[0] for item in b.items()]
    assert len(akeys) == len(bkeys)
    for key in akeys:
        avalue = a.get(key)
        bvalue = b.get(key)
        assertValueEqual(avalue, bvalue)

def assertArrayEqual(a, b):
    assert len(a) == len(b)
    for i in range(0, len(a)):
        assert a[i] == b[i]

def assertResultEqual(a, b):
    # Global information:
    assert a.personCount == b.personCount
    assert a.globalMaleCount == b.globalMaleCount
    assert a.globalFemaleCount == b.globalFemaleCount

    # Map count
    assert a.allXingCharCount == b.allXingCharCount
    assert a.allXingCount == b.allXingCount
    assert a.allMingCharCount == b.allMingCharCount
    assert a.allMingCount == b.allMingCount

    # Map
    assertMapEqual(a.xingCharMap, b.xingCharMap)
    assertMapEqual(a.xingMap, b.xingMap)
    assertMapEqual(a.mingCharMap, b.mingCharMap)
    assertMapEqual(a.mingMap, b.mingMap)

    # Array
    assertArrayEqual(a.xingCharSortedArray, b.xingCharSortedArray)
    assertArrayEqual(a.xingSortedArray, b.xingSortedArray)
    assertArrayEqual(a.mingCharSortedArray, b.mingCharSortedArray)
    assertArrayEqual(a.mingSortedArray, b.mingSortedArray)

def getRadomMapValue():
    key = unichr(random.randint(0x4E00, 0x9FCC + 1))
    value = MapValue(key, ord(key))
    value.count = random.randint(0, 100)
    value.maleCount = random.randint(0, 100)
    value.femaleCount = random.randint(0, 100)
    value.rank = random.randint(0, 100)
    return value

def getRandomMap():
    length = random.randint(1000, 5000)
    m = {}
    for i in range(0, length):
        value = getRadomMapValue()
        m[value.key] = value
    return m

def getRandomArray():
    length = random.randint(1000, 5000)
    array = []
    for i in range(0, length):
        key = unichr(random.randint(0x4E00, 0x9FCC + 1))
        array.append(key)
    return array

def assertMapArrayMatch(m, a):
    for i in range(0, len(a)):
        if i > 0:
            key1 = a[i-1]
            key2 = a[i]
            value1 = m[key1]
            value2 = m[key2]
            assert value1.count >= value2.count

def testResultSerialization():
    result = Result()
    result.personCount = random.randint(100,1000)
    result.globalMaleCount = random.randint(100,1000)
    result.globalFemaleCount = random.randint(100,1000)

    result.allXingCharCount = random.randint(100,1000)
    result.allXingCount = random.randint(100,1000)
    result.allMingCharCount = random.randint(100,1000)
    result.allMingCount = random.randint(100,1000)

    result.xingCharMap = getRandomMap()
    result.xingMap = getRandomMap()
    result.mingCharMap = getRandomMap()
    result.mingMap = getRandomMap()

    result.caculate()
    assertMapArrayMatch(result.xingCharMap, result.xingCharSortedArray)
    assertMapArrayMatch(result.xingMap, result.xingSortedArray)
    assertMapArrayMatch(result.mingCharMap, result.mingCharSortedArray)
    assertMapArrayMatch(result.mingMap, result.mingSortedArray)

    result.writeToFile(fileForResultTest)

    newResult = Result()
    newResult.readFromFile(fileForResultTest)
    assertResultEqual(result, newResult)

    result.readableWriteToFile(dirForResultTest)


def main():
    log.config(GC.LOG_FILE_DIR + 'result_test', 'debug', 'debug')
    testMapValueSerialization()
    testResultSerialization()
    log.info("Pass the test!")

if __name__ == "__main__":
  main();





