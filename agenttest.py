#!/usr/bin/python
#-*-coding:utf-8 -*-
from renrenagent import RenrenAgent
from renrenagent import ErrorCode
import time
import log
import globalconfig as GC
import util
import sys
import os


def recursiveTestGenerator(
    username, password, testInterval, totalCount, startList):
    """A recursive test generator.
   
    Start from a list of user id, and get all the profile of these id and
    their friends and friend of the friends.
    Every time it gets a user profile, it will yield the
    (id, UserInfo, ErrorCode)
    
    Args:
        @username {string} the user name of the agent.
        @password {string} the password of the agent.
        @testInterval {float} the interval time between every request.
        @totalCount {integer} total number of profile to get.
        @startList {List} a list of user id to start test.
    """
    agent = RenrenAgent(username, password)
    info, error = agent.login()
    if not error:
        log.info(info['name'])
        log.info(info['href'])
    else:
        log.error('Login error(username, password): ' +\
                username + ', ' + password)
    count = 1
    visitList = []
    for elem in startList:
        visitList.append((elem, None))
    while visitList:
        # Get the element to do requet.
        elem = visitList[0]
        id = elem[0]
        log.info('processing(' + str(count) + '): ' + id)
        visitList = visitList[1:]
        info, errorCode = agent.getProfile(id)
        # Error handle
        if errorCode:
            if elem[1]:
                log.warning('Error happen when getProfile. Refer id: ' +\
                            str(elem[1]) + '. Refer page url: ' +\
                            agent.getProfileUrl(str(elem[1])))
            else:
                log.warning('Error happen when getProfile, no refer id.')
            continue
        # Yield result
        yield (id, info, errorCode)
        # Result handle
        if len(visitList) < totalCount - count:
            newList = []
            if info.friendList:
                for ele in info.friendList:
                    newList += [(ele, id)]
            if info.recentVisitedList:
                for ele in info.recentVisitedList:
                    newList += [(ele, id)]
            visitList += newList
        # Acc
        count += 1
        if count > totalCount:
            return
        time.sleep(testInterval)


def runTest(username, password, testInterval, totalCount, startList):
    """Run a recursive test."""
    generator = recursiveTestGenerator(
        username, password, testInterval, totalCount, startList)
    list(generator)

def recursiveProfileTest(
    username, password, testInterval, totalCount, startList):
    """Run a recursive get profile test."""
    generator = recursiveTestGenerator(
        username, password, testInterval, totalCount, startList)
    while True:
        try:
            id, info, errorCode = generator.next()
            if not errorCode:
                log.info('Profile url: ' + RenrenAgent.getProfileUrl(id))
                path = util.saveTestPage(info.html, id)
                log.info('Profile local path: file://'+path)
                printInfo(info)
        except Exception, e:
            log.error('Error happen or end: ' + str(e))
            break

def printInfo(info):
    log.info('Parsed user info:\n' +\
        'name: ' + str(info.name) + '\n'\
        'gender: ' + str(info.gender) + '\n'\
        'hometown: ' + str(info.hometown) + '\n'\
        'residence: ' + str(info.residence) + '\n'\
        'birthday: ' + str(info.birthday) + '\n'\
        'visitedNum: ' + str(info.visitedNum) + '\n'\
        'friendNum: ' + str(info.friendNum) + '\n'\
        'vistorListNum: ' + str(len(info.recentVisitedList)) + '\n'\
        'vistorList: ' + str(info.recentVisitedList) + '\n'\
        'friendListNum: ' + str(len(info.friendList)) + '\n'\
        'friendList: ' + str(info.friendList))

def getProfileTest(agent, id, filePath=''):
    if filePath:
        log.info('================= Get Profile test (Local Html) ======' +\
            '=======================')
        log.info('Local Profile path: file://' + filePath)
        html = open(filePath).read()
        info, errorCode = agent.parseProfileHtml(html)
        if errorCode:
            log.error('Error happen in parse local html, path: ' + filePath)
            return
    else:
        log.info('================= Get Profile test (Online Html) =====' +\
            '=======================')
        log.info('Profile url: ' + agent.getProfileUrl(id))
        info, errorCode = agent.getProfile(id)
        if errorCode:
            log.error('Error happen in get profile, id: ' + id)
            return
        if not info.html:
            log.warning('No html')
            return
        path = util.saveTestPage(info.html, id)
        log.info('Online Profile path: file://'+path)
    printInfo(info)

def main():
    #log.config(GC.LOG_FILE_DIR + 'agent_test', 'info', 'info')
    log.config(GC.LOG_FILE_DIR + 'agent_test', 'debug', 'debug')
    startList = [
        '255617816',
        '45516',
        '200656024',
        '601630763']
    #runTest('zhanglini.ok@163.com', '12345678', 1, 200, startList)
    recursiveProfileTest('zhanglini.ok@163.com', '12345678', 1, 20, startList)


reload(sys)
sys.setdefaultencoding( "utf-8" )
main()


def getTestAgent():
    return RenrenAgent('zhanglini.ok@163.com', '12345678')


def mainProfileTest():
    log.config(GC.LOG_FILE_DIR + 'agent_test', 'debug', 'debug')
    ids = ['67922197', '172442794', '344429329']
    agent = getTestAgent()
    agent.login()
    for root, dirs, files in os.walk(GC.TEST_STATIC_PAGE_PATH):
      for file in files:
        filePath = os.path.join(root, file)
        getProfileTest(agent, None, filePath)
    for id in ids:
        getProfileTest(agent, id)

reload(sys)
sys.setdefaultencoding( "utf-8" )
#mainProfileTest()
