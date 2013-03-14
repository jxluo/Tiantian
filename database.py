import renrenagent
import MySQLdb as mdb
import log


class Status:
    """ The expand status of a person node.
    """
    (unrecorded, # There is no record in the database of the id.
     unexpanded, # The id has record in the database, but have not 
                 #   fetch it's connection's info from web.
     expanded # The id and it's connection's info are all in the database.
    ) = range(0, 3)


class Gender:
    """ gender enum."""
    (MALE, FEMALE) = range(0,2)

class Profile:
    """ The profile info for a person. 
    """
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
    """ The connection of a person.
    """
    def __init__(self):
        recentVisitorList = []
        homePageFriendList = []


class DataBase:
    """ The class handle the mysql operation, provide a data interface for
        Crawer and Indexer.
    """
    def init(self):
        """ Initialize the mysql connection.
            Reuturns:
                true if the action success.
                false if the action failed.
        """
        try:
            self.mdbConnection = mdb.connect('localhost', 'jxluo', 
                '1q2w3e', 'jxluodb');
            self.cursor = self.mdbConnection.cursor()
            sucess = true
        except mdb.Error, e:
            log.error("Can not establish connection to mysql: " + str(e))
            sucess = false
        return sucess

    def close(self):
        """ Close the connection."""
        if self.mdbConnection:    
            self.mdbConnection.close()

    def getStatus(self, id):
        """ Get the status for id.
            Returns: {Status} the status which is a integer.
        """
        command = "SELECT status FROM Persons WHERE id = %s;"
        self.cursor.execute(command, [id])
        rows = cur.fetchall()
        if len(rows):
            if len(rows) > 1:
                log.warning("Mutiple result for id: " + id)
            return rows[0][0]
        else:
            return Status.unrecorded

    def getProfile(self, id):
        """ Get the profile for id.
            Returns: {Profile} the profile, 
                None if there is no such person.
        """
        command = "SELECT name, gender, hometown, residence, birthday," +\
            "visitor_number, friend_number, recent_visitor_number," +\
            "home_page_friend_number " +\
            "FROM Persons WHERE id = %s;"
        self.cursor.execute(command, [id])
        rows = cur.fetchall()
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
            return profile
        else:
            return None

    def getConnection(self, id):
        """ Get the connection for id.
            Returns: {Connection} the connection, 
        """
        connection = Connection()
        visitorsCommand = "SELECT visitor FROM RecentVisitors WHERE id = %s;"
        self.cursor.execute(visitorsCommand, [id])
        rows = self.cursor.fetchall()
        for row in rows:
            connection.recentVisitorList.append(row[0])
        friendsCommand = "SELECT friend FROM HomePageFriends WHERE id = %s;"
        self.cursor.execute(friendsCommand, [id])
        rows = self.cursor.fetchall()
        for row in rows:
            connection.homePageFriendList.append(row[0])
        return connection

    def addRecord(self, id, userInfo):
        """ Insert a person into database, provided user id and userInfo
            from crawer.
            Reuturns:
                true if the action success.
                false if the action failed.   
        """
        personsCommand = "INSERT INTO Persons (" +\
            "id, status, " +\
            "name, gender, hometown" +\
            "residence, birthday" +\
            "visitor_number, friend_number, " +\
            "recent_visitor_number, home_page_friend_number) " +\
            "VALUES(%s, %d, " +\
            "%s, %d, %s, " +\
            "%s, %s" +\
            "%d, %d" +\
            "%d, %d);"
        visitorsCommand = "INSERT INTO RecentVisitors (" +\
            "id, visitor) VALUES(%s, %s);"
        friendsCommand = "INSERT INTO HomePageFriends (" +\
            "id, friend) VALUES(%s, %s);"
        try:
            connection, profile = convert(userInfo)
            self.cursor.execute(personsCommand, (
                id, Status.unexpanded,
                profile.name, profile.gender, profile.hometown,
                profile.residence, profile.birthday,
                profile.visitorNum, profile.friendNum,
                profile.recentVisitorNum, profile.homePageFriendNum))
            for visitor in connection.recentVisitorList:
                self.cursor.execute(visitorsCommand, (id, visitor))
            for friend in connection.homePageFriendList:
                self.cursor.execute(friendsCommand, (id, friend))
            self.mdbConnection.commit()
            sucess = true
        except Exception, e:
            log.warning("Add Record Failed! " + str(e))
            self.mdbConnection.rollback()
            sucess = false
        return sucess

    def setStatus(self, id, newStatus):
        """ Set the status for id.
            Reuturns:
                true if the action success.
                false if the action failed.
        """
        command =\
            "UPDATE Persons" +\
            "SET status = %d" +\
            "WHERE id = %s"
        try:
            self.cursor.execute(command, (newStatus, id))
            self.mdbConnection.commit()
            sucess = true
        except Exception, e:
            log.warning("Set Status Failed! " + str(e))
            self.mdbConnection.rollback()
            sucess = false
        return sucess


def convert(userInfo):
    """ Conver a UserInfo object to Profile and Connection.
        Returns: (Profile, Connection)
    """
    profile = Profile()
    connection = Connection()
    profile.name = userInfo.name
    profile.gender = (userInfo.gender == 'male' ? 1 : 0)
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
