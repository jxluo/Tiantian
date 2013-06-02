#!/usr/bin/python
# -*- coding: utf-8 -*-

from jx import log
from resource.proxy import Proxy
from utils import confidential as CFD
from crawl import renrenagent

import MySQLdb as mdb
import threading


def createProdProxyPool():
    pool = ProxyPool()
    pool.init(CFD.PROD_RESOURCE_HOST,
        CFD.PROD_RESOURCE_USERNAME,
        CFD.PROD_RESOURCE_PASSWORD,
        CFD.PROD_RESOURCE_DATABASE);
    return pool


def createTestProxyPool():
    pool = ProxyPool()
    pool.init(CFD.TEST_HOST,
        CFD.TEST_USER_NAME,
        CFD.TEST_PWD,
        CFD.TEST_DATA_BASE);
    return pool


class ProxyPool:
    """Resource pool for proxy."""

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

    def insertProxy(self, proxy):
        """Insert a proxy to database. """
        ProxyPool.acquireLock()
        try:
            command = """
                INSERT INTO Proxies (
                    address, port, protocol,
                    info, source,
                    test_count, success_count, average_time
                ) VALUES (
                    %s, %s, %s,
                    %s, %s,
                    %s, %s, %s
                );
            """
            address = proxy.addr.encode('utf-8')
            port = proxy.port.encode('utf-8')
            protocol = proxy.protocol.encode('utf-8') if proxy.protocol\
                else u'http'

            info = proxy.info.encode('utf-8') if proxy.info else None
            source = proxy.source.encode('utf-8') if proxy.source else None

            self.cursor.execute(command, (
                address, port, protocol,
                info, source,
                proxy.testCount, proxy.successCount, proxy.averageTime))
            
            self.mdbConnection.commit()
            success = True
        except Exception, e:
            log.warning('Proxy pool insert fail >>>>> ' + str(e))
            self.mdbConnection.rollback()
            success = False
        finally:
            ProxyPool.releaseLock()
        return success

    def updateProxy(self, proxy):
        """Update a proxy's test info in database."""
        ProxyPool.acquireLock()
        try:
            command = """
                UPDATE Proxies 
                SET test_count = %s,
                    success_count = %s,
                    average_time = %s
                WHERE address = %s AND
                    port = %s;
            """
            address = proxy.addr.encode('utf-8')
            port = proxy.port.encode('utf-8')
            self.cursor.execute(command, (
                proxy.testCount, proxy.successCount, proxy.averageTime,
                address, port))
            self.mdbConnection.commit()
            success = True
        except Exception, e:
            log.warning('Proxies update fail >>>>> ' + str(e))
            self.mdbConnection.rollback()
            success = False
        finally:
            ProxyPool.releaseLock()
        return success
    
    def convertToProxy(self, row): 
        proxy = Proxy()
        proxy.addr = row[0].decode('utf-8')
        proxy.port = row[1].decode('utf-8')
        proxy.protocol = row[2].decode('utf-8').lower()
        
        proxy.info = row[3].decode('utf-8') if row[3] else None
        proxy.source = row[4].decode('utf-8') if row[4] else None

        proxy.testCount = row[5]
        proxy.successCount = row[6]
        proxy.averageTime = row[7]
        return proxy

    def getProxies(self, number, protocol='http'):
        """Get some proxies from database."""
        ProxyPool.acquireLock()
        proxies = []
        try:
            command = """
                SELECT address, port, protocol,
                    info, source,
                    test_count, success_count, average_time
                FROM Proxies
                WHERE average_time < 20000 AND
                    protocol = %s
                ORDER BY average_time ASC
                LIMIT %s;
            """
            self.cursor.execute(command, [protocol, number])
            rows = self.cursor.fetchall()
            for row in rows:
                proxies.append(self.convertToProxy(row))
        except Exception, e:
            log.warning('Proxy pool get warning >>>>> ' + str(e))
        finally:
            ProxyPool.releaseLock()
        return proxies

    def getAllProxies(self):
        """Get all the proxy from database."""
        ProxyPool.acquireLock()
        proxies = []
        try:
            command = """
                SELECT address, port, protocol,
                    info, source,
                    test_count, success_count, average_time
                FROM Proxies
                ORDER BY average_time ASC
            """
            self.cursor.execute(command)
            rows = self.cursor.fetchall()
            for row in rows:
                proxies.append(self.convertToProxy(row))
        except Exception, e:
            log.warning('Proxy pool get all warning >>>>> ' + str(e))
        finally:
            ProxyPool.releaseLock()
        return proxies

    def deleteProxy(self, proxy):
        """Delete a proxy from database."""
        ProxyPool.acquireLock()
        try:
            command = """
                DELETE FROM Proxies 
                WHERE address = %s AND
                    port = %s;
            """
            address = proxy.addr.encode('utf-8')
            port = proxy.port.encode('utf-8')
            self.cursor.execute(command, (address, port))
            self.mdbConnection.commit()
            success = True
        except Exception, e:
            log.warning('Proxies pool delete fail >>>>> ' + str(e))
            self.mdbConnection.rollback()
            success = False
        finally:
            ProxyPool.releaseLock()
        return success

    def deleteAllProxies(self):
        """Delete all proxy from database."""
        ProxyPool.acquireLock()
        try:
            command = """
                DELETE FROM Proxies;
            """
            self.cursor.execute(command)
            self.mdbConnection.commit()
            success = True
        except Exception, e:
            log.warning('Proxies pool delete all fail >>>>> ' + str(e))
            self.mdbConnection.rollback()
            success = False
        finally:
            ProxyPool.releaseLock()
        return success
    
    @staticmethod
    def acquireLock():
        ProxyPool.LOCK.acquire()

    @staticmethod
    def releaseLock():
        ProxyPool.LOCK.release()
