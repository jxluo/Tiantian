#!/usr/bin/python
#-*-coding:utf-8 -*-

import urllib2
import re
import time
from bs4 import BeautifulSoup
import base64
import urllib
import confidential as con

site = 'http://192.168.1.1'

def getOpener():
    opener = urllib2.build_opener()
    user = con.ROUTER_USERNAME
    password = con.ROUTER_PASSWORD
    auth = 'Basic ' + base64.b64encode(user + ':' + password)
    opener.addheaders = [
        ('Authorization', auth),
        ('User-agent', 'Mozilla/5.0')
    ]
    return opener

def disconnectPPPoE():
    query = urllib.urlencode({'Disconnect': '断 线'})
    uri = '/userRpm/StatusRpm.htm?' + query + '&wan=1'
    url = site + uri
    getOpener().open(url).read()


def connectPPPoE():
    query = urllib.urlencode({'Connect': '连 接'})
    uri = '/userRpm/StatusRpm.htm?' + query + '&wan=1'
    url = site + uri
    getOpener().open(url).read()


def test():
    response = getOpener().open(site)
    html = response.read()
    document = BeautifulSoup(html)
    for string in document.stripped_strings:
        print string
