#!/usr/bin/python
# -*- coding: utf-8 -*-

import log
import globalconfig as GC
from database import Status
from database import Profile
from database import Connection
from database import DataBase
from renrenagent import UserInfo



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
    db.init('localhost', 'jxluo', '1q2w3e', 'jxluodb');
    return db

def createTables(db):
    with open('schema.sql') as script:
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

    qiangziID = '123456777'
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
    assert db.addRecord(xiaomingID, xiaoming) # Add normal
    assert db.addRecord(qiangziID, qiangzi)
    assert db.addRecord(achaoID, achao)
    assert db.addRecord(zhaoshufenID, zhaoshufen)

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

def main():
    log.config(GC.LOG_FILE_DIR + 'database_test', 'debug', 'debug')
    db = createConnection()
    createTables(db)
    dropTables(db)
    createTables(db)
    test(db)
    dropTables(db)
    db.close()
    log.info("Pass the test!")

if __name__ == "__main__":
  main();
