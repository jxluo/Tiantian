#!/usr/bin/python
#-*-coding:utf-8 -*-
import globalconfig as GC
import log


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

