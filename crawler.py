#!/usr/bin/python
# -*- coding: utf-8 -*-

from renrenagent import UserInfo
from renrenagent import RenrenAgent
from database import UserNode
from database import DataBase
import database
import time
import threading
import log


class CrawlerException(Exception):
    """Crawler exception class.
    
    Attributes:
        errorCode: {CrawlerErrorCode} the error code.
    """
    errorCode = None
    def __init__(self, exceptionString, errorCode):
       Exception.__init__(self, exceptionString)
       self.errorCode = errorCode



class CrawlerErrorCode:
    """Enum of error code."""
    (OK,
     DETECT_STOP_SIGNAL, # Detect a stop signal.
     GET_EXPANDING_NODE_FAILED, # Failed to get a node to expand.
     EXPAND_EXPANDED_NODE, # Try to expand a expanded node.
     NO_NODE_TO_EXPAND, # No available node for next expand.
     AGENT_ERROR,
     DATABASE_ERROR,
     UNKNOWN 
     ) = range(0, 8)


class Crawler:
    """The class that crawl the info from renren.com.

    By calling crawl(id), crawling information from renren in one single
    thread. This func can be called multipule times.
    External call:
        crawl(id)
        setStopSignal()
    This class supportes:
    1) Save intermediate result in startlist at every expand round.
    2) The crawling process can be stop by stop signal and the signal can be
        set by another thread.
    3) Guarantee minimum time interval between two HTTP request.
    4) Raise CrawlerException when something wrong happen.

    Attributes:
        agent: {RenrenAgent} the renren agent.
        dataBase: {DataBase} the DataBase object.
        lastRequestTime: {number} the time last request happen.
        MIN_REQ_INTERVAL: {number} Minimum HTTP request interval.
        stopSignal: {boolean} stop signal.
        signalLock: {threading.RLock} Lock to set or get stop signal.
        expandingId: {string} the id that is expanding.
    """
    agent = None; # The renren agent.
    dataBase = None; # The database.
    lastRequestTime = None;
    MIN_REQ_INTERVAL = 2; # Default to 1 second.

    stopSignal = False
    signalLock = None

    expandingId = None

    def __init__(self, agent, dataBase):
        """Initialize the crawler, set the agent and database."""
        self.agent = agent
        assert self.agent.isLogin, "The crawler have a agent without login!"
        self.dataBase = dataBase

        self.stopSignal = False
        self.signalLock = threading.RLock()

    def crawl(self, id, opt_number=None):
        """Crawls from renren.com.

        Given a start node by id. Crwals the user information from renren.
        The crawling process would stop when:
            1) Have expanded opt_number(If have) nodes.
            2) When a stop signal is detected.
            3) When something wrong happen in agent or database.

        Args:
            id: the start node's id.
            opt_number: the number of nodes would be expanded.

        Raise:
            CrawlerException: happen when things are so bad that crawling
            process must be stop.
        """
        nextId = id
        self.expandingId = id
        connection = None
        i = 0
        try:
            while 1:
                node = self.expand(nextId, connection)
                nextId = node.id
                connection = node.connection
                self.saveIntermediateResult(nextId)
                self.detectStopSignal()
                i += 1
                if opt_number and i >= opt_number:
                    break
        except CrawlerException, e:
            if e.errorCode == CrawlerErrorCode.DETECT_STOP_SIGNAL:
                return
            else:
                raise e # Throws it to upper class.

    def expand(self, id, opt_connection=None):
        """Expand the node with given id.

        This function will:
        1) If not provided connection, means the status of the id may be
            unrecorded. We need to check the status and makeHTTPRequest if
            needed. Then get the connection of the node.
        2) If provided opt_connection, use the connection.
        3) With the connection, get the profile (and with connection if
            availabel) of it's home page friend and recent visitors.
        3) Calculates the connected upexpanded nodes' score.
        4) Picks the node with highest score and return it for next expand.

        Returns:
            UserNode: the node for next expand.
        
        Raise:
            CrawlerException: happen .
        """
        log.info("Expand node: " + id)
        # Get the connection of the node.
        if not opt_connection:
            # If opt_connection is not provided.
            # Check the status and get the connection.
            status = self.dataBase.getStatus(id)
            if status == database.Status.unrecorded:
                node = self.makeRequsetAndSave(id)
                if not node:
                    raise CrawlerException(
                        "Failed to get expanding node's user profile!",
                        CrawlerErrorCode.GET_EXPANDING_NODE_FAILED)
                connection = node.connection
            elif status == database.Status.unexpanded:
                connection = self.dataBase.getConnection(id)
            elif status == database.Status.expanded:
                raise CrawlerException(
                    "Try to expand expanded node.",
                    CrawlerErrorCode.EXPAND_EXPANDED_NODE)
            else:
                raise CrawlerException("WTF??", CrawlerErrorCode.UNKNOWN)
        else:
            connection = opt_connection

        # Get the profile of connected nodes.
        connectedUnexpandedNodes = []
        allConnection =\
            connection.recentVisitorList + connection.homePageFriendList
        for id in allConnection:
            status, profile = self.dataBase.getStatusAndProfile(id)
            if status == database.Status.unrecorded:
                node = self.makeRequsetAndSave(id)
                if node:
                    connectedUnexpandedNodes.append(node)
            elif status == database.Status.unexpanded:
                node = UserNode(id, status, profile)
                connectedUnexpandedNodes.append(node)

        # Raise exception
        if not len(connectedUnexpandedNodes):
            raise CrawlerException(
                "There is no availabel node to expand.",
                CrawlerErrorCode.NO_NODE_TO_EXPAND)

        # Calculate the score.
        results = [(self.calculateScore(node), node) \
            for node in connectedUnexpandedNodes]

        # Pick highest one and return
        highestScore = results[0][0]
        highestNode = results[0][1]
        for result in results:
            if result[0] > highestScore:
                highestScore = result[0]
                highestNode = result[1]
            
        return highestNode    
       
    def makeRequsetAndSave(self, id):
        """Make http request to get a user node and save in database.

        If the time between now and last request is less than MIN_REQ_INTERVAL
        second, it will sleep to make the interval become MIN_REQ_INTERVAL
        second.

        Returns:
            UserNode: the UserNode of the user with given id.
            None: if the request failed. 
        """
        now = time.time()
        if self.lastRequestTime:
            interval = now - self.lastRequestTime
            if interval  < self.MIN_REQ_INTERVAL:
                time.sleep(self.MIN_REQ_INTERVAL - interval)

        # TODO: Investigate the behavior of SIG_INT in single thread and multi
        # thread program, then determin if detectStopSignal after sleep is
        # necessary.
        self.detectStopSignal()
        userInfo, error = self.agent.getProfile(id)
        self.lastRequestTime = time.time()
        
        if error:
            # TODO: Need retry in the future?
            return None
        node = self.dataBase.addRecord(id, userInfo)
        return node

    def calculateScore(self, node):
        """Calculates a user node's expand score.

        More high the score is, more likely the node would be expand.

        Returns:
            number: the score number.
        """
        # TODO: Find a better score generation method.
        return node.profile.friendNum + node.profile.visitorNum / 10

    def saveIntermediateResult(self, nextId):
        """Save intermediate result to StartList."""
        # Bad things may happen between two database operation, so we firstly
        # insert and then delete.
        self.dataBase.insertIntoStartList(nextId)
        self.dataBase.setStatus(self.expandingId, database.Status.expanded)
        self.dataBase.deleteFromStartList(self.expandingId)
        self.expandingId = nextId

    def clearStopSignal(self):
        """Clear the stop signal. This function may be call in other thread."""
        self.signalLock.acquire()
        self.stopSignal = False
        self.signalLock.release()

    def setStopSignal(self):
        """Set a stop signal. This function may be call in other thread."""
        self.signalLock.acquire()
        self.stopSignal = True
        self.signalLock.release()

    def detectStopSignal(self):
        """Detect stop signal, if have, raise a CrawlerException."""
        self.signalLock.acquire()
        signal = self.stopSignal
        self.signalLock.release()
        if signal:
            raise CrawlerException(
                "Detect stop signal!", CrawlerErrorCode.DETECT_STOP_SIGNAL)
