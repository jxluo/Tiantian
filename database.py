#!/usr/bin/python
# -*- coding: utf-8 -*-

import renrenagent
import MySQLdb as mdb
import log


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
        command = "SELECT status FROM Persons WHERE id = %s;"
        self.cursor.execute(command, [id.encode('utf-8')])
        rows = self.cursor.fetchall()
        if len(rows):
            if len(rows) > 1:
                log.warning("Mutiple result for id: " + id)
            return rows[0][0]
        else:
            return Status.unrecorded

    def getProfile(self, id):
        """Get the profile for id.

        Returns: 
            Profile: the profile, 
            None: if there is no such person.
        """
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

    def getConnection(self, id):
        """Get the connection for id.

        Returns: {Connection} the connection, 
        """
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

    def addRecord(self, id, userInfo):
        """Insert a person into database, provided user id and userInfo
            from crawer.

        Reuturns:
            UserNode: the user node convert from the userInfo.
            None: if the operation failed.
        """
        personsCommand = "INSERT INTO Persons (" +\
            "id, status, " +\
            "name, gender, hometown, " +\
            "residence, birthday, " +\
            "visitor_number, friend_number, " +\
            "recent_visitor_number, home_page_friend_number) " +\
            "VALUES(%s, %s, " +\
            "%s, %s, %s, " +\
            "%s, %s, " +\
            "%s, %s, " +\
            "%s, %s);"
        visitorsCommand = "INSERT INTO RecentVisitors (" +\
            "id, visitor) VALUES(%s, %s);"
        friendsCommand = "INSERT INTO HomePageFriends (" +\
            "id, friend) VALUES(%s, %s);"
        try:
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
                profile.recentVisitorNum, profile.homePageFriendNum))
            for visitor in connection.recentVisitorList:
                self.cursor.execute(visitorsCommand, (id, visitor))
            for friend in connection.homePageFriendList:
                self.cursor.execute(friendsCommand, (id, friend))
            self.mdbConnection.commit()
            sucess = True
        except Exception, e:
            log.warning("Add Record Failed! " + str(e))
            self.mdbConnection.rollback()
            sucess = False
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
        command =\
            "UPDATE Persons " +\
            "SET status = %s " +\
            "WHERE id = %s"
        try:
            self.cursor.execute(command, (newStatus, id.encode('utf-8')))
            self.mdbConnection.commit()
            sucess = True
        except Exception, e:
            log.warning("Set Status Failed! " + str(e))
            self.mdbConnection.rollback()
            sucess = False
        return sucess

    def insertIntoStartList(self, id, opt_createdTime=None):
        """Insert a node into start list."""
        command = \
            "INSERT INTO StartList (id, created_time) VALUES(%s, %s);"
        try:
            self.cursor.execute(command, [id.encode('utf-8'), opt_createdTime])
            self.mdbConnection.commit()
            sucess = True
        except Exception, e:
            log.warning("Insert into start list failed!" + str(e))
            self.mdbConnection.rollback()
            sucess = False
        return sucess

    def deleteFromStartList(self, id):
        """Delete a node from start list."""
        command = "DELETE FROM StartList WHERE id = %s;"
        try:
            self.cursor.execute(command, [id.encode('utf-8')])
            self.mdbConnection.commit()
            sucess = True
        except Exception, e:
            log.warning("Delete from start list failed!" + str(e))
            self.mdbConnection.rollback()
            sucess = False
        return sucess

    def getStartNodes(self, number=1):
        """Get start nodes for start one or several crawl thread.
        
        Args:
            number: the number of nodes you would like to get.

        Returns:
            (): A tuple that contains nodes.
        """
        command =\
            " SELECT id FROM StartList " +\
            " ORDER BY created_time ASC " +\
            " LIMIT %s; "
        self.cursor.execute(command, [number])
        rows = self.cursor.fetchall()
        allNodes = [row[0] for row in rows]
        return allNodes


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
