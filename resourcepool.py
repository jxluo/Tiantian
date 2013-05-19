#!/usr/bin/python
# -*- coding: utf-8 -*-

import renrenagent
import confidential as CFD
import MySQLdb as mdb
import log
import threading

def createProdRenrenAccountPool():
    pool = RenrenAccountPool()
    pool.init(CFD.PROD_RESOURCE_HOST,
        CFD.PROD_RESOURCE_USERNAME,
        CFD.PROD_RESOURCE_PASSWORD,
        CFD.PROD_RESOURCE_DATABASE);
    return pool


def createTestRenrenAccountPool():
    pool = RenrenAccountPool()
    pool.init(CFD.TEST_HOST,
        CFD.TEST_USER_NAME,
        CFD.TEST_PWD,
        CFD.TEST_DATA_BASE);
    return pool


class RenrenAccount:
    """A class represent a renren account.
    Attributes:
        username: {string} the username.
        password: {string} the password.
        isLogin: {boolean} is the account login.
        requestCount: {number} the number of request this account has made.
        accountPool: {RenrenAccountPool} reference to the RenrenAccountPool.
    """
    username = None
    password = None
    isLogin = False
    requestCount = 0
    accountPool = None

    #dispose related
    needFinish = True

    def __init__(self, username, password, accountPool):
        self.username = username
        self.password = password
        self.accountPool = accountPool
    
    def finishUsing(self):
        """It will call finishUsing of RenrenAccountPool for updating info."""
        self.accountPool.finishUsing(self)
        self.needFinish = False

    def reportInvalidAccount(self, errorCode, errorInfo=None):
        """It will call reportInvalidAccount of RenrenAccountPool for updating
        info.
        """
        self.accountPool.reportInvalidAccount(self, errorCode, errorInfo)
        self.needFinish = False

    def dispose(self):
        if self.needFinish:
            self.finishUsing()


class RenrenAccountLogEvent:
    """RenrenAccountLogEvent Code."""
    (CREATE, # Create at table.
     USE, # Be used.
     FINISH_USE, # Finish used.
     BECOME_INVALID, # Become invalid.
     DELETE, # Delete from pool.
     SAVE_ACCOUNT_SUCCESS, # Save account success, become valid.
     SAVE_ACCOUNT_FAIL # Save account fail, still invalid.
    ) = range(0, 7)


class RenrenAccountErrorCode:
    """RenrenAccounts error code. Indecates why does it become invalid."""
    (ERROR_WHEN_LOGIN, # Get error when login.
     ERROR_WHEN_REQUEST, # Get error when making request.
    ) = range(0, 2)


class RenrenAccountPool:
    """Resource pool for renren accounts."""

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

    def getAccount(self):
        """Get one available account."""
        result = self.getAccounts(1)
        if len(result) < 1:
            return None
        else:
            return result[0]

    def getAccounts(self, number):
        """Get a list of RenrenAccount.

        Read some accounts from database, mark them as using and write to
        log table.
        """
        RenrenAccountPool.acquireLock()
        accounts = []
        try:
            selectCommand = """
                SELECT username, password FROM RenrenAccounts
                WHERE is_using = 0 AND
                    is_valid = 1 AND
                    last_used_time <= DATE_SUB(NOW(), INTERVAL 1 DAY)
                ORDER BY last_used_time ASC
                LIMIT %s;
            """
            self.cursor.execute(selectCommand, [number])
            rows = self.cursor.fetchall()
            for row in rows:
                accounts.append(RenrenAccount(row[0], row[1], self))

            updateCommand = """
                UPDATE RenrenAccounts
                SET is_using = 1
                WHERE username = %s AND password = %s;
            """
            insertCommand = """
                INSERT INTO RenrenAccountsLog (
                    username, password, event) VALUES(
                    %s, %s, %s);
            """
            for account in accounts:
                self.cursor.execute(
                    updateCommand, [account.username, account.password]);
                self.cursor.execute(
                    insertCommand, [
                        account.username,
                        account.password,
                        RenrenAccountLogEvent.USE]);
                self.mdbConnection.commit()
        except Exception, e:
            log.warning(
                "RenrenAccountPool: set is_using = True failed! " + str(e))
            self.mdbConnection.rollback()
        finally:
            RenrenAccountPool.releaseLock()
        return accounts


    def finishUsing(self, account):
        """Update database when a RenrenAccount is finished being using.

        Set is_using = false for the account, update account infomation and
        insert a log into log table.
        """
        RenrenAccountPool.acquireLock()
        try:
            updateCommand = """
                UPDATE RenrenAccounts
                SET is_using = 0,
                    login_count = %s + login_count,
                    request_count = %s + request_count,
                    last_used_time = NOW()
                WHERE username = %s AND password = %s;
            """
            updateCommandNoUse = """
                UPDATE RenrenAccounts
                SET is_using = 0
                WHERE username = %s AND password = %s;
            """
            insertCommand = """
                INSERT INTO RenrenAccountsLog (
                    username, password, event, is_login, request_count) VALUES(
                    %s, %s, %s, %s, %s);
            """
            loginCount = 1 if account.isLogin else 0
            if not account.isLogin and account.requestCount == 0:
                self.cursor.execute(
                    updateCommandNoUse, [
                        account.username,
                        account.password]);
            else:
                self.cursor.execute(
                    updateCommand, [
                        loginCount,
                        account.requestCount,
                        account.username,
                        account.password]);
            self.cursor.execute(
                insertCommand, [
                    account.username,
                    account.password,
                    RenrenAccountLogEvent.FINISH_USE,
                    loginCount,
                    account.requestCount]);
            self.mdbConnection.commit()
        except Exception, e:
            log.warning(
                "RenrenAccountPool: finish use failed! " +\
                "username: " + account.username + "  " +\
                "password: " + account.password + "  " + str(e))
            self.mdbConnection.rollback()
        finally:
            RenrenAccountPool.releaseLock()

    def reportInvalidAccount(self, account, errorCode, errorInfo=None):
        """Update database when a RenrenAccoun become invalid.
        
        Set is_using = false and is_valid = fale the account, update account
        infomation and insert a log into log table.
        """
        RenrenAccountPool.acquireLock()
        try:
            updateCommand = """
                UPDATE RenrenAccounts
                SET is_using = 0,
                    is_valid = 0,
                    login_count = %s + login_count,
                    request_count = %s + request_count,
                    last_used_time = NOW(),
                    become_invalid_time = NOW(),
                    error_code = %s,
                    error_info = %s
                WHERE username = %s AND password = %s;
            """
            insertCommand = """
                INSERT INTO RenrenAccountsLog (
                    username, password, event, is_login, request_count) VALUES(
                    %s, %s, %s, %s, %s);
            """
            loginCount = 1 if account.isLogin else 0
            if not errorInfo:
                if errorCode == RenrenAccountErrorCode.ERROR_WHEN_LOGIN:
                    errorInfo = "Get error when login."
                elif errorCode == RenrenAccountErrorCode.ERROR_WHEN_REQUEST: 
                    errorInfo = "Get error when making request."
                else:
                    errorInfo = "Unknown error."
            self.cursor.execute(
                updateCommand, [
                    loginCount,
                    account.requestCount,
                    errorCode,
                    errorInfo,
                    account.username,
                    account.password]);
            self.cursor.execute(
                insertCommand, [
                    account.username,
                    account.password,
                    RenrenAccountLogEvent.BECOME_INVALID,
                    loginCount,
                    account.requestCount]);
            self.mdbConnection.commit()
        except Exception, e:
            log.warning(
                "RenrenAccountPool: report invalid failed! " +\
                "username: " + account.username + "  " +\
                "password: " + account.password + "  " + str(e))
            self.mdbConnection.rollback()
        finally:
            RenrenAccountPool.releaseLock()

    def addAccount(self, username, password, comeFrom):
        """Add a new account to the pool."""
        RenrenAccountPool.acquireLock()
        try:
            accountCommand = """
                INSERT INTO RenrenAccounts (
                    username, password,
                    come_from,
                    is_using, is_valid,
                    last_used_time,
                    login_count, request_count
                ) VALUES (
                    %s, %s, %s,
                    0, 1,
                    '1971-1-1',
                    0, 0
                );
            """
            logCommand = """
                INSERT INTO RenrenAccountsLog (
                    username, password, event
                ) VALUES (%s, %s, %s);
            """
            self.cursor.execute(
                accountCommand, [
                    username,
                    password,
                    comeFrom]);
            self.cursor.execute(
                logCommand, [
                    username,
                    password,
                    RenrenAccountLogEvent.CREATE]);
            self.mdbConnection.commit()
            success = True
        except Exception, e:
            log.warning(
                "RenrenAccountPool: add account failed! " +\
                "username: " + username + "  " +\
                "password: " + password + "  " + str(e))
            self.mdbConnection.rollback()
            success = False
        finally:
            RenrenAccountPool.releaseLock()
        return success

    def saveAccount(self, username, password, successSave, time=None):
        """Set a account is_valid to valid."""
        RenrenAccountPool.acquireLock()
        try:
            accountCommandNoTime = """
                UPDATE RenrenAccounts
                SET is_using = 0,
                    is_valid = 1,
                    last_used_time = NOW()
                WHERE username = %s AND password = %s;
            """
            accountCommandWithTime = """
                UPDATE RenrenAccounts
                SET is_using = 0,
                    is_valid = 1,
                    last_used_time = %s
                WHERE username = %s AND password = %s;
            """
            logCommand = """
                INSERT INTO RenrenAccountsLog (
                    username, password, event
                ) VALUES (%s, %s, %s);
            """
            if successSave:
                if time:
                    self.cursor.execute(
                        accountCommandWithTime, [
                            time,
                            username,
                            password]);
                else:
                    self.cursor.execute(
                        accountCommandNoTime, [
                            username,
                            password]);

            event = RenrenAccountLogEvent.SAVE_ACCOUNT_SUCCESS if successSave\
                else RenrenAccountLogEvent.SAVE_ACCOUNT_FAIL
            self.cursor.execute(
                logCommand, [
                    username,
                    password,
                    event]);
            self.mdbConnection.commit()
            success = True
        except Exception, e:
            log.warning(
                "RenrenAccountPool: save account operation failed! " +\
                "username: " + username + "  " +\
                "password: " + password + "  " + str(e))
            self.mdbConnection.rollback()
            success = False
        finally:
            RenrenAccountPool.releaseLock()
        return success

    def onceSaveFail(self, username, password):
        """Return whether a account has once been saved but fail."""
        RenrenAccountPool.acquireLock()
        try:
            command = """
                SELECT * FROM RenrenAccountsLog
                WHERE username = %s AND password = %s AND event = %s;
            """
            self.cursor.execute(
                command, [
                    username,
                    password,
                    RenrenAccountLogEvent.SAVE_ACCOUNT_FAIL]);
            rows = self.cursor.fetchall()
            onceFail = len(rows) > 0
        except Exception, e:
            log.warning(
                "RenrenAccountPool: once save fail failed! " +\
                "username: " + username + "  " +\
                "password: " + password + "  " + str(e))
            self.mdbConnection.rollback()
            onceFail = False
        finally:
            RenrenAccountPool.releaseLock()
        return onceFail

    @staticmethod
    def acquireLock():
        RenrenAccountPool.LOCK.acquire()

    @staticmethod
    def releaseLock():
        RenrenAccountPool.LOCK.release()

