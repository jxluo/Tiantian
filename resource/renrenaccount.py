#!/usr/bin/python
# -*- coding: utf-8 -*-


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
