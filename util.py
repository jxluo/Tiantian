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
