#!/usr/bin/python
#-*-coding:utf-8 -*-

from jx import log
from utils import globalconfig as GC
from utils import util
from crawl.renrenagent import RenrenAgent, ErrorCode
from resource.renrenaccount import RenrenAccount

from urllib import urlencode
import urllib2
import re
from bs4 import BeautifulSoup
import bs4
import time


class SharePageInfo:
    commentUserList = None
    popularShareList = None

class ShareAgent(RenrenAgent):

    def __init__(self, account):
        RenrenAgent.__init__(self, account)

    def getSharePageInfoById(self, userId, postId):
        url = 'http://blog.renren.com/share/%s/%s' % (userId, postId)
        return self.getSharePageInfo(url)

    def getSharePageInfo(self, url):
        """Get share page info.
        Returns:
            None if error happen.
            SharePageInfo
        """
        if not self.isLogin:
            raise Exception('Account is not login')
        try:
            response = self.opener.open(url, timeout=self.TIME_OUT)
            realUrl = response.geturl()
            html = response.read()
        except Exception, e:
            log.warning('Get share url error: ' + str(e) +\
                        '. Share url: ' + url)
            return None
        finally:
            self.account.requestCount += 1

        try:
            info = self.parseSharePage(html)
            return info
        except Exception, e:
            log.warning('Parse share page error: %s' % e)
            return None

    def parseSharePage(self, html):
        info = SharePageInfo()
        document = BeautifulSoup(html)
        
        cmtsNode = document.find('div', id='allCmts_comment_list')
        aList = cmtsNode.find_all('a', class_='minfriendpic')
        userList = []
        hrefPattern = re.compile('[^\d]+(\d+)$')
        for aTag in aList:
            href = aTag['href']
            #print aTag['href']
            res = hrefPattern.match(href)
            #print res.group(1)
            userId = res.group(1)
            if userId not in userList:
                userList.append(userId)
        info.commentUserList = userList

        shareList1 = document.find('div', id='hotsharelist')
        info.popularShareList = self.parseShareList(shareList1)

        return info

    def parseShareList(self, node):
        urlList = []
        ulTags = node.find_all('ul', class_='blog-list')
        for tag in ulTags:
            aTags = tag.find_all('a')
            for a in aTags:
                url = a['href']
                urlList.append(url)
        return urlList
        







def test():
    account = RenrenAccount('', '', None)
    agent = ShareAgent(account)
    info = agent.parseSharePage(open('tmp/share.html').read())

    print '===========Share Info==========='
    for id in info.commentUserList:
        print id
    for url in info.popularShareList:
        print url


if __name__ == "__main__":
  test();
