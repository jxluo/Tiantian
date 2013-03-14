from database import Status
from database import Profile
from database import Connection
from database import DataBase
from renrenagent import UserInfo


xiaomingID
xiaoming

qiangziID
qiangzi

achaoID
achao

zhaoshufenID
zhaoshufen

inexistentID

def assertUserInfoProfile(userInfo, profile):
    assert userInfo.name == profile.name
    assert userInfo.gender == (profile.gender ? 'male' : 'female')
    assert userInfo.hometown == profile.hometown
    assert userInfo.residence == profile.residence
    assert userInfo.birthday == profile.birthday
    assert userInfo.visitedNum == profile.visitorNum
    assert userInfo.friendNum == profile.friendNum
    assert len(userInfo.recentVisitedList) == profile.recentVisitorNum 
    assert len(userInfo.friendList) == profile.homePageFriendNum 

def assertUserInfoConnection(userInfo, connection):
    assert len(connection.recentVisitorList) == len(userInfo.recentVisitedList)
    assert len(connection.homePageFriendList) == len(userInfo.friendList)
    for i in range(0, len(connection.recentVisitorList)):
        assert connection.recentVisitorList[i] ==\
            userInfo.recentVisitedList[i]
    for i in range(0, len(connection.homePageFriendList)):
        assert connection.homePageFriendList[i] ==\
            userInfo.friendList[i]


def test():
    db = DataBase()
    assert db.init()
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
    assert not db.setStatus(inexistentID, Status.expanded) # Set inexistent
    
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

    db.close()


