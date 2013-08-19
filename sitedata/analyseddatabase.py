#!/usr/bin/python
# -*- coding: utf-8 -*-

from jx import log
from utils import confidential as CFD
from analyse.result import Result
from entities.name_pb2 import GlobalNameInfo, RawNameItemInfo

import MySQLdb as mdb
import threading

def createTestAnalysedDataBase():
    db = AnalysedDataBase()
    db.init(CFD.TEST_HOST, CFD.TEST_USER_NAME,
        CFD.TEST_PWD,
        CFD.TEST_DATA_BASE);
    return db

def createProdAnalysedDataBase():
    db = AnalysedDataBase()
    db.init(CFD.PROD_SITE_DATA_HOST, CFD.PROD_SITE_DATA_USERNAME,
        CFD.PROD_SITE_DATA_PASSWORD,
        CFD.PROD_SITE_DATA_DATABASE);
    return db


class AnalysedDataBase:
    """The class handle the mysql operation, provide a data interface of
        analysed data base.
    """

    LOCK = threading.RLock()

    XING_CHAR_MAP_NAME = 'XingCharInfos'
    XING_MAP_NAME = 'XingInfos'
    MING_CHAR_MAP_NAME = 'MingCharInfos'
    MING_MAP_NAME = 'MingInfos'
    XING_MING_MAP_NAME = 'XingMingInfos'

    XING_CHAR_RANK_NAME = 'XingCharRank'
    XING_RANK_NAME = 'XingRank'
    MING_CHAR_RANK_NAME = 'MingCharRank'
    MING_RANK_NAME = 'MingRank'
    XING_MING_RANK_NAME = 'XingMingRank'

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

    def getXingCharInfo(self, key):
        return self._getInfo(key, self.XING_CHAR_MAP_NAME)

    def getXingInfo(self, key):
        return self._getInfo(key, self.XING_MAP_NAME)

    def getMingCharInfo(self, key):
        return self._getInfo(key, self.MING_CHAR_MAP_NAME)

    def getMingInfo(self, key):
        return self._getInfo(key, self.MING_MAP_NAME)
    
    def getXingMingInfo(self, key):
        return self._getInfo(key, self.XING_MING_MAP_NAME)


    def getXingCharRankNeighbors(self, rank):
        return self._getRankNeighbors(rank, self.XING_CHAR_RANK_NAME)

    def getXingRankNeighbors(self, rank):
        return self._getRankNeighbors(rank, self.XING_RANK_NAME)

    def getMingCharRankNeighbors(self, rank):
        return self._getRankNeighbors(rank, self.MING_CHAR_RANK_NAME)

    def getMingRankNeighbors(self, rank):
        return self._getRankNeighbors(rank, self.MING_RANK_NAME)

    def getXingMingRankNeighbors(self, rank):
        return self._getRankNeighbors(rank, self.XING_MING_RANK_NAME)


    def _getInfo(self, key, tableName):
        """Get the RawInfo for the map the key.

        Returns: {RawNameItemInfo} the raw info.
        """
        AnalysedDataBase._acquireLock()
        try:
            command = "SELECT info FROM %s WHERE s_key = %s;" % (tableName, '%s')
            self.cursor.execute(command, [key])
            rows = self.cursor.fetchall()
            if len(rows):
                if len(rows) > 1:
                    log.error("Mutiple result for key: " + key)
                infoString = rows[0][0]
                info = RawNameItemInfo.FromString(infoString)
                return info
            else:
                return None
        finally:
            AnalysedDataBase._releaseLock()
    
    def _addInfoRecord(self, key, info, tableName):
        """Add key-info pair record to database for specified map.

        Reuturns:
            True if the action success.
            False if the action failed.
        """
        AnalysedDataBase._acquireLock()
        try:
            command = 'INSERT INTO %s (s_key, info) VALUES (%s, %s);' %\
                (tableName, '%s', '%s')
            self.cursor.execute(command,\
                (key, info.SerializeToString()))
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
    
    def getGlobalInfo(self):
        """Get the global information."""
        AnalysedDataBase._acquireLock()
        try:
            command = """SELECT info
                FROM GlobalNameInfo
                WHERE id = 1;
            """
            self.cursor.execute(command)
            rows = self.cursor.fetchall()
            if not rows:
                log.error('Read gloabal information fail!')
            string = rows[0][0]
            globalInfo = GlobalNameInfo.FromString(string)
            return globalInfo
        except Exception, e:
            log.warning("Get global info failed! " + str(e))
            self.mdbConnection.rollback()
            return None
        finally:
            AnalysedDataBase._releaseLock()


    def _addGlobalInfo(self, globalInfo):
        """Set the global information.

        Reuturns:
            True if the action success.
            False if the action failed.
        """
        AnalysedDataBase._acquireLock()
        try:
            command = """INSERT INTO GlobalNameInfo(
                id, info)
                VALUES (
                1, %s);"""
            self.cursor.execute(command, (globalInfo.SerializeToString(),))
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

    def _importInfos(self, m, tableName):
        for item in m.items():
            key = item[0]
            value = item[1]
            self._addInfoRecord(key, value, tableName)

    def _importRankArray(self, array, arrayName):
        for i in range(0, len(array)):
            key = array[i]
            rank = i + 1
            self._addRankArrayRecord(key, rank, arrayName)
        
    def importResult(self, result):
        """Import result to database. The new data will override old ones."""
        self._resetTable()
        self._addGlobalInfo(result.globalInfo)

        self._importInfos(result.xingCharMap, self.XING_CHAR_MAP_NAME)
        log.info('XingCharMap imported...')
        self._importInfos(result.xingMap, self.XING_MAP_NAME)
        log.info('XingMap imported...')
        self._importInfos(result.mingCharMap, self.MING_CHAR_MAP_NAME)
        log.info('MingCharMap imported...')
        self._importInfos(result.mingMap, self.MING_MAP_NAME)
        log.info('MingMap imported...')
        self._importInfos(result.xingMingMap, self.XING_MING_MAP_NAME)
        log.info('XingMingMap imported...')
        
        self._importRankArray(\
            result.xingCharSortedArray, self.XING_CHAR_RANK_NAME)
        log.info('XingCharArray imported...')
        self._importRankArray(result.xingSortedArray, self.XING_RANK_NAME)
        log.info('XingArray imported...')
        self._importRankArray(\
            result.mingCharSortedArray, self.MING_CHAR_RANK_NAME)
        log.info('MingCharArray imported...')
        self._importRankArray(result.mingSortedArray, self.MING_RANK_NAME)
        log.info('MingArray imported...')
        self._importRankArray(result.xingMingSortedArray, self.XING_MING_RANK_NAME)
        log.info('XingMingArray imported...')

    @staticmethod
    def _acquireLock():
        AnalysedDataBase.LOCK.acquire()

    @staticmethod
    def _releaseLock():
        AnalysedDataBase.LOCK.release()
