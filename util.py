#!/usr/bin/python
#-*-coding:utf-8 -*-
import globalconfig as GC
import log
import random

def weightPickInt(weights):
    """Random pick a number, the posibility is base on the weights.
    Arguments:
        weights: a list of weight, each of the element represent the weight
          of the index number. weight should be a integer.
    Reutrns:
        number: range from 0 to len(weights)-1
    """
    sum = 0
    for weight in weights:
        sum += weight
    result = random.randint(0, sum - 1)
    for i in range(0, len(weights)):
        weight = weights[i]
        if result < weight:
            return i
        else:
            result -= weight
    raise Exception('Shit happen')

def weightPickIntTest():
    testRound = 100000
    weights = [300, 200, 100]
    result = [0, 0, 0]
    for i in range(0, testRound):
        result[weightPickInt(weights)] += 1
    for i in range(0, 3):
        print str(i) + ': ' + str(float(result[i])/testRound*600)

#weightPickIntTest()

def randomTrue(p):
    return random.random() < p

def randomTrueTest():
    testRound = 1000000
    t = 0
    f = 0
    p = 1.0/1000
    for i in range(0, testRound):
        if randomTrue(p): t += 1
        else: f += 1
    print 'True:  ' + str(float(t)/testRound)
    print 'False:  ' + str(float(f)/testRound)

#randomTrueTest()

    

def saveTestPage(html, name):
  path = GC.TEST_PAGE_PATH + str(name) + '.html'
  file = open(path, 'w');
  file.write(html)
  file.close()
  return path

def savePage(html, name):
  file = open(GC.ALL_PAGE_PATH + str(name) + '.html', 'w');
  file.write(html)
  file.close()  


def saveErrorPage(html, name):
  file = open(GC.ERROR_PAGE_PATH + str(name) + '.html', 'w');
  file.write(html)
  file.close()



# 中日韩月统一表意文字
CJKV = (0x4E00, 0x9FCC + 1)

# 中日韩月统一表意文字 扩展A区
CJKV_A = (0x3400, 0x4DB5 + 1)

# 中日韩月统一表意文字 扩展B区
CJKV_B = (0x20000, 0x2A6D6 + 1)

# 中日韩月统一表意文字 扩展C区
CJKV_C = (0x2A700, 0x2B734 + 1)


def isHanChar(char):
    val = ord(char)
    if CJKV[0] <= val < CJKV[1] or\
        CJKV_A[0] <= val < CJKV_A[1] or\
        CJKV_B[0] <= val < CJKV_B[1] or\
        CJKV_C[0] <= val < CJKV_C[1]:
        return True
    else:
        return False

