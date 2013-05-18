#!/usr/bin/python
# -*- coding: utf-8 -*-

import confidential as CFD
import renrenagent
import MySQLdb as mdb
import log
import threading

def createTestDataBase():
    db = DataBase()
    db.init(CFD.TEST_HOST,
        CFD.TEST_USER_NAME,
        CFD.TEST_PWD,
        CFD.TEST_DATA_BASE);
    return db

def createProdDataBase():
    db = DataBase()
    db.init(CFD.PROD_TIANTIAN_DATA_HOST,
        CFD.PROD_TIANTIAN_DATA_USERNAME,
        CFD.PROD_TIANTIAN_DATA_PASSWORD,
        CFD.PROD_TIANTIAN_DATA_DATABASE);
    return db

class Status:
    """The expand status of a person node."""
    (unrecorded, # There is no record in the database of the id.
     unexpanded, # The id has record in the database, but have not 
                 #   fetch it's connection's info from web.
     expanded # The id and it's connection's info are all in the database.
    ) = range(0, 3)


class Gender:
    """Gender enum."""
    (MALE, FEMALE) = (1, 2)

class Profile:
    """The profile info for a person."""
    name = None
    gender = None
    hometown = None
    residence = None
    birthday = None
    visitorNum = None
    friendNum = None
    
    recentVisitorNum = None
    homePageFriendNum = None


class Connection:
    """The connection of a person."""
    def __init__(self):
        self.recentVisitorList = []
        self.homePageFriendList = []

class UserNode:
    """A node represent a user."""
    id = None
    status = None
    profile = None
    connection = None
    
    def __init__(self, id=None, status=None, profile=None, connection=None):
        self.id = id
        self.status = status
        self.profile = profile
        self.connection = connection


class DataBase:
    """The class handle the mysql operation, provide a data interface for
        Crawer and Indexer.
    """

    LOCK = threading.RLock()

    def init(self, host, username, password, database):
        """Initialize the mysql connection.
            
        Args:
            @host {string} the name of the host, e.g. 'localhost'.
            @username {string} the user name of the database account.
            @password {string} the password.
            @database {string} the name of the database.

        Reuturns:
            True if the action success.
            False if the action failed.
        """
        try:
            self.mdbConnection = mdb.connect(host, username, 
                password, database);
            self.cursor = self.mdbConnection.cursor()
            sucess = True
        except mdb.Error, e:
            log.error("Can not establish connection to mysql: " + str(e))
            sucess = False
        return sucess

    def close(self):
        """Close the connection."""
        if self.mdbConnection:    
            self.mdbConnection.close()

    def getStatusAndProfile(self, id):
        """Get status and profile.

        Returns:
            (Status, Profile) a tuple with status and profile.
        """
        return (self.getStatus(id), self.getProfile(id))
        

    def getStatus(self, id):
        """Get the status for id.

        Returns: {Status} the status which is a integer.
        """
        DataBase.acquireLock()
        try:
            command = "SELECT status FROM Persons WHERE id = %s;"
            self.cursor.execute(command, [id.encode('utf-8')])
            rows = self.cursor.fetchall()
            if len(rows):
                if len(rows) > 1:
                    log.warning("Mutiple result for id: " + id)
                return rows[0][0]
            else:
                return Status.unrecorded
        finally:
            DataBase.releaseLock()

    def getProfile(self, id):
        """Get the profile for id.

        Returns: 
            Profile: the profile, 
            None: if there is no such person.
        """
        DataBase.acquireLock()
        try:
            command = "SELECT name, gender, hometown, residence, birthday," +\
                "visitor_number, friend_number, recent_visitor_number," +\
                "home_page_friend_number " +\
                "FROM Persons WHERE id = %s;"
            self.cursor.execute(command, [id.encode('utf-8')])
            rows = self.cursor.fetchall()
            if len(rows):
                if len(rows) > 1:
                    log.warning("Mutiple result for id: " + id)
                profile = Profile()
                profile.name,\
                profile.gender,\
                profile.hometown,\
                profile.residence,\
                profile.birthday,\
                profile.visitorNum,\
                profile.friendNum,\
                profile.recentVisitorNum,\
                profile.homePageFriendNum = rows[0]
                # Decode the string
                if profile.name:
                    profile.name = profile.name.decode('utf-8')
                if profile.hometown:
                    profile.hometown = profile.hometown.decode('utf-8')
                if profile.residence:
                    profile.residence = profile.residence.decode('utf-8')
                if profile.birthday:
                    profile.birthday = profile.birthday.decode('utf-8')
                return profile
            else:
                return None
        finally:
            DataBase.releaseLock()

    def getConnection(self, id):
        """Get the connection for id.

        Returns: {Connection} the connection, 
        """
        DataBase.acquireLock()
        try:
            connection = Connection()
            visitorsCommand = "SELECT visitor FROM RecentVisitors WHERE id = %s;"
            self.cursor.execute(visitorsCommand, [id.encode('utf-8')])
            rows = self.cursor.fetchall()
            for row in rows:
                connection.recentVisitorList.append(row[0])
            friendsCommand = "SELECT friend FROM HomePageFriends WHERE id = %s;"
            self.cursor.execute(friendsCommand, [id.encode('utf-8')])
            rows = self.cursor.fetchall()
            for row in rows:
                connection.homePageFriendList.append(row[0])
            return connection
        finally:
            DataBase.releaseLock()

    def addRecord(self, id, userInfo, opt_referenceId=None):
        """Insert a person into database, provided user id and userInfo
            from crawer.

        Reuturns:
            UserNode: the user node convert from the userInfo.
            None: if the operation failed.
        """
        DataBase.acquireLock()
        try:
            personsCommand = "INSERT INTO Persons (" +\
                "id, status, " +\
                "name, gender, hometown, " +\
                "residence, birthday, " +\
                "visitor_number, friend_number, " +\
                "recent_visitor_number, home_page_friend_number, " +\
                "create_time, reference_id) " +\
                "VALUES(%s, %s, " +\
                "%s, %s, %s, " +\
                "%s, %s, " +\
                "%s, %s, " +\
                "%s, %s, NOW(), %s);"
            visitorsCommand = "INSERT INTO RecentVisitors (" +\
                "id, visitor) VALUES(%s, %s);"
            friendsCommand = "INSERT INTO HomePageFriends (" +\
                "id, friend) VALUES(%s, %s);"
            profile, connection = convert(userInfo)
            self.cursor.execute(personsCommand, (
                id.encode('utf-8'), Status.unexpanded,
                profile.name.encode('utf-8'),
                profile.gender if profile.gender else None,
                profile.hometown.encode('utf-8') \
                    if profile.hometown else None,
                profile.residence.encode('utf-8') \
                    if profile.residence else None,
                profile.birthday.encode('utf-8') \
                    if profile.birthday else None,
                profile.visitorNum, profile.friendNum,
                profile.recentVisitorNum, profile.homePageFriendNum,
                opt_referenceId.encode('utf-8') if opt_referenceId else None))
            for visitor in connection.recentVisitorList:
                self.cursor.execute(visitorsCommand, (id, visitor))
            for friend in connection.homePageFriendList:
                self.cursor.execute(friendsCommand, (id, friend))
            self.mdbConnection.commit()
            sucess = True
        except Exception, e:
            log.warning("Add Record Failed! ("+ str(id) + ") " + str(e))
            self.mdbConnection.rollback()
            sucess = False
        finally:
            DataBase.releaseLock()
        if sucess:
            return UserNode(id, Status.unexpanded, profile, connection)
        else:
            return None

    def setStatus(self, id, newStatus):
        """Set the status for id.

        Reuturns:
            True if the action success.
            False if the action failed.
        """
        DataBase.acquireLock()
        try:
            command =\
                "UPDATE Persons " +\
                "SET status = %s " +\
                "WHERE id = %s"
            self.cursor.execute(command, (newStatus, id.encode('utf-8')))
            self.mdbConnection.commit()
            sucess = True
        except Exception, e:
            log.warning("Set Status Failed! " + str(e))
            self.mdbConnection.rollback()
            sucess = False
        finally:
            DataBase.releaseLock()
        return sucess

    def insertIntoStartList(self, id, opt_lastModified=None):
        """Insert a node into start list."""
        DataBase.acquireLock()
        try:
            command = \
                "INSERT INTO StartList (id, last_modified) VALUES(%s, %s);"
            self.cursor.execute(command, [id.encode('utf-8'), opt_lastModified])
            self.mdbConnection.commit()
            sucess = True
        except Exception, e:
            log.warning("Insert into start list failed!" + str(e))
            self.mdbConnection.rollback()
            sucess = False
        finally:
            DataBase.releaseLock()
        return sucess

    def deleteFromStartList(self, id):
        """Delete a node from start list."""
        DataBase.acquireLock()
        try:
            command = "DELETE FROM StartList WHERE id = %s;"
            self.cursor.execute(command, [id.encode('utf-8')])
            self.mdbConnection.commit()
            sucess = True
        except Exception, e:
            log.warning("Delete from start list failed!" + str(e))
            self.mdbConnection.rollback()
            sucess = False
        finally:
            DataBase.releaseLock()
        return sucess

    def getStartNode(self):
        """Get one start node.

        Returns:
            (tableId, id) the start node.
        """
        ids = self.getStartNodes(1)
        if len(ids) < 1:
            return None, None
        else:
            return ids[0]

    def getStartNodes(self, number=1):
        """Get start nodes for start one or several crawl thread.
        
        Args:
            number: the number of nodes you would like to get.

        Returns:
            ((tableId, id)): A tuple that contains nodes.
        """
        DataBase.acquireLock()
        try:
            selectCommand = """
                SELECT id, table_id FROM StartList
                WHERE is_using = 0
                ORDER BY last_modified ASC
                LIMIT %s;
            """
            self.cursor.execute(selectCommand, [number])
            rows = self.cursor.fetchall()

            updateCommand = """
                UPDATE StartList SET is_using = 1
                WHERE table_id = %s;
            """
            for row in rows:
                self.cursor.execute(updateCommand, [row[1]])
            self.mdbConnection.commit()
            return rows
        except Exception, e:
            log.warning("Get start node failed!" + str(e))
            self.mdbConnection.rollback()
            return ()
        finally:
            DataBase.releaseLock()

    def releaseStartNode(self, tableId):
        """Release a startNode by a table id.

        Args:
            tableId: the id of the table row.
        """
        DataBase.acquireLock()
        try:
            command = """
                UPDATE StartList SET is_using = 0 WHERE table_id = %s;
            """
            self.cursor.execute(command, [tableId])
            self.mdbConnection.commit()
        except Exception, e:
            log.warning("Release start list node failed!" + str(e))
            self.mdbConnection.rollback()
        finally:
            DataBase.releaseLock()

    def releaseAllStartNode(self):
        """Release all startNode."""
        DataBase.acquireLock()
        try:
            command = """
                UPDATE StartList SET is_using = 0;
            """
            self.cursor.execute(command)
            self.mdbConnection.commit()
        except Exception, e:
            log.warning("Release all start list node failed!" + str(e))
            self.mdbConnection.rollback()
        finally:
            DataBase.releaseLock()

    def replaceStartNode(self, originId, newId):
        """Replace a old node with new id."""
        DataBase.acquireLock()
        try:
            command = "UPDATE StartList SET id = %s WHERE id = %s;"
            self.cursor.execute(command, [
                newId.encode('utf-8'),
                originId.encode('utf-8')])
            self.mdbConnection.commit()
            sucess = True
        except Exception, e:
            log.warning("Replace start list node failed!" + str(e))
            self.mdbConnection.rollback()
            sucess = False
        finally:
            DataBase.releaseLock()
        return sucess

    @staticmethod
    def acquireLock():
        DataBase.LOCK.acquire()

    @staticmethod
    def releaseLock():
        DataBase.LOCK.release()

def convert(userInfo):
    """Conver a UserInfo object to Profile and Connection.

    Returns: (Profile, Connection)
    """
    profile = Profile()
    connection = Connection()
    profile.name = userInfo.name
    gender = None
    if userInfo.gender == u'male': gender = Gender.MALE
    if userInfo.gender == u'female': gender = Gender.FEMALE
    profile.gender = gender
    profile.hometown = userInfo.hometown
    profile.residence = userInfo.residence
    profile.birthday = userInfo.birthday
    profile.visitorNum = userInfo.visitedNum
    profile.friendNum = userInfo.friendNum
    profile.recentVisitorNum = len(userInfo.recentVisitedList)
    profile.homePageFriendNum = len(userInfo.friendList)
    connection.recentVisitorList = userInfo.recentVisitedList
    connection.homePageFriendList = userInfo.friendList
    return profile, connection
