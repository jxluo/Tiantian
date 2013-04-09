#!/usr/bin/python
# -*- coding: utf-8 -*-

import renrenagent
import MySQLdb as mdb
import log


class RenrenAccount:
    """A class represent a renren accout.

    Attributes:
        username: {string} the username.
        passworda: {string} the password.
        isLogin: {boolean} is the account login.
        requestCount: {number} the number of request this account has made.
        accountPool: {RenrenAccountPool} reference to the RenrenAccountPool.
    """
    username = None
    password = None
    isLogin = False
    requestCount = 0
    accountPool = None
    
    def finishUsing(self):
        """It will call finishUsing of RenrenAccountPool for updating info."""
        pass
    def reportInvalid(self):
        """It will call reportInvalidAccount of RenrenAccountPool for updating
        info.
        """
        pass

class RenrenAccountPool:
    """Resource pool for renren accounts."""

    def getAccounts(self, number):
        """Get a list of RenrenAccount."""
        pass

    def finishUsing(self, account):
        """Update database when a RenrenAccount is finished being using.
        """
        pass

    def reportInvalidAccount(self, account):
        """Update database when a RenrenAccoun become invalid.
        """
        pass
