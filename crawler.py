#!/usr/bin/python
# -*- coding: utf-8 -*-

from renrenagent import UserInfo
from renrenagent import RenrenAgent

class Crawler:
    """ The class that crawl the info from renren.com
        Use single renren user to make http request.
        Between every two http request there will be at less one
            second time interval.
        Run in one single thread.
    """
    agent = None; # The renren agent.
    database = None; # The database.

    def __init__(self, agent, database):
        """ Initialize the crawler, set the agent and database."""
        self.agent = agent
        assert self.agent.isLogin, "The crawler have a agent without login!"
        self.database = database

    def expand(self, id, opt_profile=None):
        """ Expand the node with given id.
            This function will:
            1) Get the profile of given id.
            2) Get the profile of it's home page friend and
                recent visitors.
            3) Rank them, pick one for next expand.
            4) Return the picked one.

        Returns:
            {String} the id for next expand.
        """
        pass

    def getUserInfo(self, id):
        """ Make http request with agent to get a id's user info.
            If the time between now and last request is less than 1 second,
                it will sleep to make the interval become 1 second.
        """
        pass

    def crawl(self, id):
        pass
