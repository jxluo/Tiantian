#!/usr/bin/python
# -*- coding: utf-8 -*-

from jx import log
from utils import globalconfig as GC
from utils import confidential as CFD
from data.database import Status
from data.database import Profile
from data.database import Connection
from data.database import DataBase
from crawl.renrenagent import UserInfo


def assertUserInfoProfile(userInfo, profile):
    assert userInfo.name == profile.name
    if profile.gender == 1:
        gender = 'male'
    elif profile.gender == 2:
        gender = 'female'
    else:
        gender = None
    assert userInfo.gender == gender,\
        "Reason: %s %s" % (str(userInfo.gender), str(gender))
    assert userInfo.hometown == profile.hometown
    assert userInfo.residence == profile.residence
    assert userInfo.birthday == profile.birthday
    assert userInfo.visitedNum == profile.visitorNum,\
        "Reason: " + str(userInfo.visitedNum) + " " + str(profile.visitorNum)
    assert userInfo.friendNum == profile.friendNum
    assert len(userInfo.recentVisitedList) == profile.recentVisitorNum 
    assert len(userInfo.friendList) == profile.homePageFriendNum 

def assertUserInfoConnection(userInfo, connection):
    assert len(connection.recentVisitorList) == len(userInfo.recentVisitedList)
    assert len(connection.homePageFriendList) == len(userInfo.friendList)
    connection.recentVisitorList.sort()
    connection.homePageFriendList.sort()
    userInfo.recentVisitedList.sort()
    userInfo.friendList.sort()
    for i in range(0, len(connection.recentVisitorList)):
        assert connection.recentVisitorList[i] ==\
            userInfo.recentVisitedList[i], "Reason: " +\
            str(connection.recentVisitorList[i]) + '  ' +\
            str(userInfo.recentVisitedList[i])
    for i in range(0, len(connection.homePageFriendList)):
        assert connection.homePageFriendList[i] ==\
            userInfo.friendList[i]

def createConnection():
    db = DataBase()
    db.init(CFD.TEST_HOST,
        CFD.TEST_USER_NAME,
        CFD.TEST_PWD,
        CFD.TEST_DATA_BASE);
    return db

def createTables(db):
    with open('schema/data.sql') as script:
        lines = script.readlines()
        command = ''
        for i in range(0, len(lines)):
            line = lines[i]
            command += line
            #print line
            if line.find(';') != -1:
                #print "================="
                db.cursor.execute(command) 
                db.mdbConnection.commit()
                command = ''

def dropTables(db):
    script = "DROP TABLE Persons;"
    db.cursor.execute(script) 
    db.mdbConnection.commit()
    script = "DROP TABLE RecentVisitors;"
    db.cursor.execute(script) 
    db.mdbConnection.commit()
    script = "DROP TABLE HomePageFriends;"
    db.cursor.execute(script) 
    db.mdbConnection.commit()
    script = "DROP TABLE StartList;"
    db.cursor.execute(script) 
    db.mdbConnection.commit()

def test(db):
    xiaomingID = 'xiaomingID'
    xiaoming = UserInfo()
    xiaoming.name = u'小明'
    xiaoming.gender = u'male'
    xiaoming.hometown = u'广东'
    xiaoming.residence = u'珠海'
    xiaoming.birthday = u'1985-11-18'
    xiaoming.visitedNum = 1234
    xiaoming.friendNum = 21
    xiaoming.recentVisitedList = ['123e', '1233', '333']
    xiaoming.friendList = ['3124', '1222', 'dd33']

    qiangziID = u'123456777'
    qiangzi = UserInfo()
    qiangzi.name = u'强子'
    qiangzi.gender = 'male'
    qiangzi.hometown = u'荷兰'
    qiangzi.residence = u'驻马店'
    qiangzi.birthday = u'1989-11-18'
    qiangzi.visitedNum = 1234
    qiangzi.friendNum = 21
    qiangzi.recentVisitedList = ['123e', '1233', '333']
    qiangzi.friendList = ['3124', '1222', 'dd33']

    achaoID = 'achaoddd33333'
    achao = UserInfo()
    achao.name = u'阿超'
    achao.birthday = u'1987-11-18'
    achao.visitedNum = 1234
    achao.friendNum = 21
    achao.recentVisitedList = ['123e', '1233', '333']
    achao.friendList = ['3124', '1222', 'dd33']

    zhaoshufenID = '234123zhaoshufen'
    zhaoshufen = UserInfo()
    zhaoshufen.name = u'赵淑芬'
    zhaoshufen.gender = u'female'
    zhaoshufen.hometown = u'山西'
    zhaoshufen.residence = u'shanghai'
    zhaoshufen.visitedNum = 1234
    zhaoshufen.friendNum = 21
    zhaoshufen.recentVisitedList = ['123e', '1233', '333']
    zhaoshufen.friendList = ['3124', '1222', 'dd33']

    inexistentID = '8877654321'

    # Test add Record
    node =  db.addRecord(xiaomingID, xiaoming) # Add normal
    assert node
    assertUserInfoProfile(xiaoming, node.profile)
    node =  db.addRecord(qiangziID, qiangzi) # Add normal
    assert node
    assertUserInfoProfile(qiangzi, node.profile)
    node =  db.addRecord(achaoID, achao, xiaomingID) # Add normal
    assert node
    assertUserInfoProfile(achao, node.profile)
    node =  db.addRecord(zhaoshufenID, zhaoshufen, xiaomingID) # Add normal
    assert node
    assertUserInfoProfile(zhaoshufen, node.profile)

    assert not db.addRecord(zhaoshufenID, zhaoshufen) # Add duplicate
    assert not db.addRecord(qiangziID, qiangzi)

    # Test get/set Status
    assert Status.unexpanded == db.getStatus(xiaomingID) # Get existent
    assert Status.unexpanded == db.getStatus(qiangziID)
    assert Status.unexpanded == db.getStatus(achaoID)
    assert Status.unexpanded == db.getStatus(zhaoshufenID)
    assert Status.unrecorded == db.getStatus(inexistentID) # Get inexistent

    assert db.setStatus(xiaomingID, Status.expanded) # Set existent
    assert db.setStatus(achaoID, Status.expanded)
    # Still true
    assert db.setStatus(inexistentID, Status.expanded) # Set inexistent
    
    assert Status.expanded == db.getStatus(xiaomingID) # Get modified
    assert Status.expanded == db.getStatus(achaoID)
    assert Status.unexpanded == db.getStatus(zhaoshufenID) # Get unmodified

    # Test get Profile
    xiaomingProfile = db.getProfile(xiaomingID)
    assert xiaomingProfile
    assertUserInfoProfile(xiaoming, xiaomingProfile)
    qiangziProfile = db.getProfile(qiangziID)
    assert qiangziProfile
    assertUserInfoProfile(qiangzi, qiangziProfile)
    achaoProfile = db.getProfile(achaoID)
    assert achaoProfile
    assertUserInfoProfile(achao, achaoProfile)
    zhaoshufenProfile = db.getProfile(zhaoshufenID)
    assert zhaoshufenProfile
    assertUserInfoProfile(zhaoshufen, zhaoshufenProfile)
    assert not db.getProfile(inexistentID) # Get inexistent

    # Test get Status and Profile
    xiaomingStatus, xiaomingProfile = db.getStatusAndProfile(xiaomingID)
    assert xiaomingStatus == Status.expanded
    assert xiaomingProfile
    assertUserInfoProfile(xiaoming, xiaomingProfile)
    qiangziStatus, qiangziProfile = db.getStatusAndProfile(qiangziID)
    assert qiangziStatus == Status.unexpanded
    assert qiangziProfile
    assertUserInfoProfile(qiangzi, qiangziProfile)
    achaoStatus, achaoProfile = db.getStatusAndProfile(achaoID)
    assert achaoStatus == Status.expanded
    assert achaoProfile
    assertUserInfoProfile(achao, achaoProfile)
    zhaoshufenStatus, zhaoshufenProfile = db.getStatusAndProfile(zhaoshufenID)
    assert zhaoshufenStatus == Status.unexpanded
    assert zhaoshufenProfile
    assertUserInfoProfile(zhaoshufen, zhaoshufenProfile)
    inexistentStatus, inexistentProfile = db.getStatusAndProfile(inexistentID)
    assert inexistentStatus == Status.unrecorded
    assert not inexistentProfile

    # Test get Connection
    connection = db.getConnection(xiaomingID)
    assertUserInfoConnection(xiaoming, connection)
    connection = db.getConnection(qiangziID)
    assertUserInfoConnection(qiangzi, connection)
    connection = db.getConnection(achaoID)
    assertUserInfoConnection(achao, connection)
    connection = db.getConnection(zhaoshufenID)
    assertUserInfoConnection(zhaoshufen, connection)
    connection = db.getConnection(inexistentID)
    assert 0 == len(connection.recentVisitorList) # Get inexistent
    assert 0 == len(connection.homePageFriendList)

def testStartList(db):
    id1 = "start list id 111"
    time1 = "2012-4-1 15:21:29"
    id2 = "start list id 222"
    time2 = "2012-5-1 15:21:29"
    id3 = "id3333"
    newId = 'new_id'

    db.insertIntoStartList(id2, time2)
    db.insertIntoStartList(id1, time1)

    db.MIN_START_NODE_COUNT = 2
    assert not db.needMoreStartNode()
    db.MIN_START_NODE_COUNT = 3
    assert db.needMoreStartNode()

    result1 = db.getStartNodes(2)
    db.MIN_START_NODE_COUNT = 2
    assert db.needMoreStartNode()
    assert len(result1) == 2 , "len = " + str(len(result))
    assert result1[0][0] == id1
    assert result1[1][0] == id2

    # It's 2013 now.
    db.insertIntoStartList(id3)
    result2 = db.getStartNode()
    assert result2[1] != None
    assert result2[0] == id3

    result3 = db.getStartNode()
    assert result3[0] == None
    assert result3[1] == None
    result4 = db.getStartNodes(2)
    assert len(result4) == 0
    
    db.releaseStartNode(result2[1])

    id, tableId = db.getStartNode()
    db.replaceStartNode(id, newId) 
    db.releaseStartNode(tableId)
    id, tableId = db.getStartNode()
    assert id == newId
    
    db.releaseStartNode(result1[0][1])
    db.releaseStartNode(result1[1][1])
    db.releaseStartNode(tableId)
    result5 = db.getStartNodes(5)
    assert len(result5) == 3
    db.releaseStartNode(result5[0][1])
    db.releaseStartNode(result5[1][1])
    db.releaseStartNode(result5[2][1])

    db.deleteFromStartList(result5[0][0])
    db.deleteFromStartList(result5[1][0])
    result6 = db.getStartNodes(5)
    assert len(result6) == 1

    db.releaseAllStartNode()
    db.insertIntoStartList('id4')
    db.insertIntoStartList('id5')
    db.insertIntoStartList('id6')
    assert len(db.getStartNodes(5)) == 4
    db.releaseAllStartNode()
    db.clearAllStartNode()
    assert len(db.getStartNodes(5)) == 0


def main():
    log.config(GC.LOG_FILE_DIR + 'database_test', 'debug', 'debug')
    db = createConnection()
    createTables(db)
    dropTables(db)
    createTables(db)
    test(db)
    testStartList(db)
    dropTables(db)
    db.close()
    log.info("Pass the test!")

if __name__ == "__main__":
  main();
