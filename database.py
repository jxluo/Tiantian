import renrenagent


class Status:
    """ The expand status of a person node.
    """
    (unrecorded, # There is no record in the database of the id.
     unexpanded, # The id has record in the database, but have not 
                 #   fetch it's connection's info from web.
     expanded # The id and it's connection's info are all in the database.
    ) = range(0, 3)

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
    
    recentVisitorListNum = None
    someFriendListNum = None

class Connection:
    """ The connection of a person.
    """
    def __init__(self):
        recentVisitorList = []
        someFriendList = []

def init():
    pass

def close():
    pass

def getStatus(id):
    pass

def getProfile(id):
    pass

def getConnection():
    pass

def addRecord(id, userInfo):
    pass

def setStatus(id, newStatus):
    pass
