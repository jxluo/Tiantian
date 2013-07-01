#!/usr/bin/python
# -*- coding: utf-8 -*-

from jx import log
from utils import confidential as CFD
from crawl import renrenagent
from analyse.result import Result
from analyse.result import MapValue

import MySQLdb as mdb
import threading

def createTestAnalysedDataBase():
    db = AnalysedDataBase()
    db.init(CFD.TEST_HOST,
        CFD.TEST_USER_NAME,
        CFD.TEST_PWD,
        CFD.TEST_DATA_BASE);
    return db


class AnalysedDataBase:
    """The class handle the mysql operation, provide a data interface of
        analysed data base.
    """
    allXingCharCount = None
    allXingCount = None
    allMingCharCount = None
    allMingCount = None
    personCount = None
    maleCount = None
    femaleCount = None

    LOCK = threading.RLock()

    XING_CHAR_MAP_NAME = 'XingCharMap'
    XING_MAP_NAME = 'XingMap'
    MING_CHAR_MAP_NAME = 'MingCharMap'
    MING_MAP_NAME = 'MingMap'

    XING_CHAR_RANK_NAME = 'XingCharRank'
    XING_RANK_NAME = 'XingRank'
    MING_CHAR_RANK_NAME = 'MingCharRank'
    MING_RANK_NAME = 'MingRank'

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
                password, database, charset='utf8');
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

    def getXingCharMap(self, key):
        return self._getMap(key, self.XING_CHAR_MAP_NAME)

    def getXingMap(self, key):
        return self._getMap(key, self.XING_MAP_NAME)

    def getMingCharMap(self, key):
        return self._getMap(key, self.MING_CHAR_MAP_NAME)

    def getMingMap(self, key):
        return self._getMap(key, self.MING_MAP_NAME)


    def getXingCharRankNeighbors(self, rank):
        return self._getRankNeighbors(rank, self.XING_CHAR_RANK_NAME)

    def getXingRankNeighbors(self, rank):
        return self._getRankNeighbors(rank, self.XING_RANK_NAME)

    def getMingCharRankNeighbors(self, rank):
        return self._getRankNeighbors(rank, self.MING_CHAR_RANK_NAME)

    def getMingRankNeighbors(self, rank):
        return self._getRankNeighbors(rank, self.MING_RANK_NAME)


    def _getMap(self, key, mapName):
        """Get the MapValue for the map the key.

        Returns: {MapValue} the value.
        """
        AnalysedDataBase._acquireLock()
        try:
            command = "SELECT value FROM %s WHERE s_key = %s;" % (mapName, '%s')
            self.cursor.execute(command, [key])
            rows = self.cursor.fetchall()
            if len(rows):
                if len(rows) > 1:
                    log.error("Mutiple result for key: " + key)
                valueString = rows[0][0]
                mapValue = MapValue()
                mapValue.unserialize(valueString)
                return mapValue
            else:
                return None
        finally:
            AnalysedDataBase._releaseLock()
    
    def _addMapRecord(self, key, value, mapName):
        """Add key-value pair record to database for specified map.

        Reuturns:
            True if the action success.
            False if the action failed.
        """
        AnalysedDataBase._acquireLock()
        try:
            command = 'INSERT INTO %s (s_key, value) VALUES (%s, %s);' %\
                (mapName, '%s', '%s')
            self.cursor.execute(command,\
                (key, value.serialize()))
            self.mdbConnection.commit()
            sucess = True
        except Exception, e:
            log.warning("Add map record failed! " + str(e))
            self.mdbConnection.rollback()
            sucess = False
        finally:
            AnalysedDataBase._releaseLock()
        return sucess
        
    def _getRankNeighbors(self, rank, arrayName):
        """Get the neighbor keys in rank array and for the rank and the array.

        Returns: {(key...)} A tuple contain neighbor keys.
        """
        NEIGHBOR_COUNT = 7
        AnalysedDataBase._acquireLock()
        try:
            # The result will contains the element which
            # rank is bottom and upper.
            command = """SELECT s_key FROM %s
                WHERE rank BETWEEN %s AND %s
                ORDER BY rank ASC;
            """ % (arrayName, '%s', '%s')
            bottom = rank - NEIGHBOR_COUNT / 2
            if bottom < 1: bottom = 1
            upper = rank + NEIGHBOR_COUNT / 2

            self.cursor.execute(command, [bottom, upper])
            rows = self.cursor.fetchall()
            array = [x[0] for x in rows]
            if not len(array) or len(array) > NEIGHBOR_COUNT:
                log.warning('Wrong result in rank neighbors, rank %s' % rank)
            return array
        finally:
            AnalysedDataBase._releaseLock()
    
    def _addRankArrayRecord(self, key, rank, arrayName):
        """Add key rank record to database for specified array.

        Reuturns:
            True if the action success.
            False if the action failed.
        """
        AnalysedDataBase._acquireLock()
        try:
            command = 'INSERT INTO %s (s_key, rank) VALUES (%s, %s);' %\
                (arrayName, '%s', '%s')
            self.cursor.execute(command,\
                (key, rank))
            self.mdbConnection.commit()
            sucess = True
        except Exception, e:
            log.warning("Add rank record failed! " + str(e))
            self.mdbConnection.rollback()
            sucess = False
        finally:
            AnalysedDataBase._releaseLock()
        return sucess
    
    def readGlobalInfo(self):
        """Get the global information."""
        AnalysedDataBase._acquireLock()
        try:
            command = """SELECT
                all_xing_char_count, all_xing_count,
                all_ming_char_count, all_ming_count,
                person_count, male_count, female_count
                FROM GlobalInfo
                WHERE id = 1;
            """
            self.cursor.execute(command)
            rows = self.cursor.fetchall()
            if not rows:
                log.error('Read gloabal information fail!')
            row = rows[0]
            self.allXingCharCount = row[0]
            self.allXingCount = row[1]
            self.allMingCharCount = row[2]
            self.allMingCount = row[3]
            self.personCount = row[4]
            self.maleCount = row[5]
            self.femaleCount = row[6]
        finally:
            AnalysedDataBase._releaseLock()


    def _addGlobalInfo(self, allXingCharCount, allXingCount,\
        allMingCharCount, allMingCount, personCount, maleCount, femaleCount):
        """Set the global information.

        Reuturns:
            True if the action success.
            False if the action failed.
        """
        AnalysedDataBase._acquireLock()
        try:
            command = """INSERT INTO GlobalInfo(
                id,
                all_xing_char_count, all_xing_count,
                all_ming_char_count, all_ming_count,
                person_count, male_count, female_count)
                VALUES (
                1, %s, %s, %s, %s, %s, %s, %s);"""
            self.cursor.execute(command,\
                (allXingCharCount, allXingCount,\
                 allMingCharCount, allMingCount,\
                 personCount, maleCount, femaleCount))
            self.mdbConnection.commit()
            sucess = True
        except Exception, e:
            log.warning("Set global infomation failed! " + str(e))
            self.mdbConnection.rollback()
            sucess = False
        finally:
            AnalysedDataBase._releaseLock()
        return sucess

    def _resetTable(self):
        with open('sitedata/schema.sql') as script:
            lines = script.readlines()
            command = ''
            for i in range(0, len(lines)):
                line = lines[i]
                command += line
                if line.find(';') != -1:
                    #print command
                    self.cursor.execute(command) 
                    self.mdbConnection.commit()
                    command = ''

    def _importMap(self, m, mapName):
        for item in m.items():
            key = item[0]
            value = item[1]
            self._addMapRecord(key, value, mapName)

    def _importRankArray(self, array, arrayName):
        for i in range(0, len(array)):
            key = array[i]
            rank = i + 1
            self._addRankArrayRecord(key, rank, arrayName)
        
    def importResult(self, result):
        """Import result to database. The new data will override old ones."""
        self._resetTable()
        self._addGlobalInfo(\
            result.allXingCharCount, result.allXingCount,\
            result.allMingCharCount, result.allMingCount,\
            result.personCount, result.globalMaleCount,\
            result.globalFemaleCount)

        self._importMap(result.xingCharMap, self.XING_CHAR_MAP_NAME)
        self._importMap(result.xingMap, self.XING_MAP_NAME)
        self._importMap(result.mingCharMap, self.MING_CHAR_MAP_NAME)
        self._importMap(result.mingMap, self.MING_MAP_NAME)
        
        self._importRankArray(\
            result.xingCharSortedArray, self.XING_CHAR_RANK_NAME)
        self._importRankArray(result.xingSortedArray, self.XING_RANK_NAME)
        self._importRankArray(\
            result.mingCharSortedArray, self.MING_CHAR_RANK_NAME)
        self._importRankArray(result.mingSortedArray, self.MING_RANK_NAME)

    @staticmethod
    def _acquireLock():
        AnalysedDataBase.LOCK.acquire()

    @staticmethod
    def _releaseLock():
        AnalysedDataBase.LOCK.release()
