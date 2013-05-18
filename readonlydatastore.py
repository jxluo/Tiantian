#!/usr/bin/python
# -*- coding: utf-8 -*-

import globalconfig as GC
import confidential as CFD
import MySQLdb as mdb
import log
import threading
import util
from database import Profile
from database import Gender

def createProdReadOnlyDataStore():
    ds = ReadOnlyDataStore()
    ds.init(CFD.PROD_ANALYSIS_DATA_HOST,
        CFD.PROD_ANALYSIS_DATA_USERNAME,
        CFD.PROD_ANALYSIS_DATA_PASSWORD,
        CFD.PROD_TIANTIAN_DATA_DATABASE);
    return ds


class ReadOnlyDataStore:
    """The class handle the read only database operation.
    Provide a read only data interface for Profile analyser.
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
    
    def getAllProfiles(self):
        """Returns all the profiles in the data store.

        Returns: [Profile] The profile list.
        """
        ReadOnlyDataStore.acquireLock()
        profiles = []
        try:
            command = """
                SELECT id, name, gender, hometown,
                   residence, birthday,
                   visitor_number, friend_number,
                   recent_visitor_number, home_page_friend_number
                FROM Persons;
                """
            self.cursor.execute(command)
            rows = self.cursor.fetchall()
            for row in rows:
                profiles.append(self.convertToProfile(row))
        except Exception, e:
            log.warning("Get all profiles failed!" + str(e))
        finally:
            ReadOnlyDataStore.releaseLock()
        return profiles;

    def getAThousandProfiles(self):
        """Returns 1000 prifles, next call will return next 1000 profiles. 
        If there is no more profiles, it will return a empty list.

        Returns: [Profile] The profile list.
        """
        pass
    
    def getAllCreatedTime(self):
        """Returns all the create_time in the data store.

        Returns: [time] The profile list.
        """
        ReadOnlyDataStore.acquireLock()
        times = []
        try:
            command = """
                SELECT create_time
                FROM Persons;
                """
            self.cursor.execute(command)
            rows = self.cursor.fetchall()
            for row in rows:
                times.append(row[0])
        except Exception, e:
            log.warning("Get all profiles failed!" + str(e))
        finally:
            ReadOnlyDataStore.releaseLock()
        return times

    def convertToProfile(self, row):
        """Convert a row of record to profile"""
        profile = Profile()
        profile.id = row[0].decode('utf-8')
        profile.name = row[1].decode('utf-8')
        profile.gender = row[2]
        return profile

    @staticmethod
    def hasValidName(profile):
        name = profile.name
        if len(name) > 4 or len(name) < 2:
            return False
        for char in name:
            if not util.isHanChar(char):
                return False
        return True


    @staticmethod
    def acquireLock():
        ReadOnlyDataStore.LOCK.acquire()

    @staticmethod
    def releaseLock():
        ReadOnlyDataStore.LOCK.release()
