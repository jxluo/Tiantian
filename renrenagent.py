#!/usr/bin/python
#-*-coding:utf-8 -*-
from urllib import urlencode
import urllib2
import re
from bs4 import BeautifulSoup
import bs4
import log
import globalconfig as GC
import util



class ErrorCode:
    """Error code enum"""
    (OK, # No error.
     NO_LOGIN, # Haven't login.
     URL_ERROR, # Can not get the page of the url.
     UNKNOWN_PAGE, # Do not know the page template.
     BANNED_ACCOUNT, # The account was banned.
     LACK_CRITICAL_INFO # Lack of critical infomation.
    ) = range(0, 6)


class PageType:
    """page type enum of profile page"""
    (TIME_LINE, # timeline page
     OLD_WITH_ACCESS, # old page with access
     OLD_WITHOUT_ACCESS, # Old page without access
    ) = range(0, 3)


class UserInfo:
    """A data struct to store user information.
    Attributes:
        @id {string} the id of user.
        @name {string} the name of the user.
        @gender {string} 'male' or 'female'.
        @hometown {string} the hometown of user.
        @residence {string} where is user living.
        @birthday {string} when do user born.
        @visitedNum {int} the number of people who have visited the user's
            profile page.
        @friendNum {int} the number of user's friend.
        @recentVisitedList {List<string>} the idf of recent visited user on
            the profile page.
        @friendList {List<string>} the id of friends on the profile page.

        @html {string} the html user's profile page.
        @pagetype {PageType} the type of the user's profile page.
    """
    id = None # Deprecated
    name = None
    gender = None
    hometown = None
    residence = None
    birthday = None
    visitedNum = None
    friendNum = None

    def __init__(self):
        self.recentVisitedList = []
        self.friendList = []


class RenrenAgent:
    """Agent to get information for renren.com"""

    loginUrl = 'http://www.renren.com/PLogin.do'
    renrenUrl = 'http://www.renren.com/'

    TIME_OUT = 30 # In seconds

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.isLogin = False
        cookieProcessor = urllib2.HTTPCookieProcessor()
        self.opener = urllib2.build_opener(cookieProcessor)

    def login(self):
        loginData={
                'email': self.username,
                'password': self.password,
                'originUrl': '',
                'formName': '',
                'method': '',
                'isplogin': 'true',
                'submit': '登陆'
        }
        postData = urlencode(loginData)
        req = urllib2.Request(self.loginUrl, postData)
        try:
            response = self.opener.open(req, timeout=self.TIME_OUT)
        except urllib2.URLError, e:
            #print 'Login error: ' + e.reason
            log.error('Login error: ' + e.reason)
            return ({}, ErrorCode.URL_ERROR)

        # Verify the login
        # The first login page may not directly go to guide page.
        # So we need to do a request again.
        try:
            response = self.opener.open(self.renrenUrl, timeout=self.TIME_OUT)
            html = response.read()
        except Exception, e:
            # TODO: use e.reason or other appropriate exceition if possible
            # The another possible exception is stock.timeout: time out
            log.error('Open guide error: ' + str(e))
            return ({}, ErrorCode.URL_ERROR)
        document = BeautifulSoup(html)
        info = {}
        error = 0;
        if document.find('div', class_='info'):
            link = document.find('div', class_='info').find('a')
            info['name'] = link.string
            info['href'] = link['href']
        else:
            log.error('Unknown login template')
            util.saveErrorPage(html, self.username + 'login')
            error = 1
            return ({}, ErrorCode.UNKNOWN_PAGE)

        self.isLogin = True
        log.info('Success login, name: ' + info['name'])
        return (info, ErrorCode.OK)

    def getProfile(self, id, saveAllPage = False):
        """Get profile of given user id, if the saveAllPage is true, this
            method will store the html page at the disk.
        Returns:
            {(UserInfo, ErrorCode)} the user information and errorcode
        """
        if not self.isLogin:
            return (None, ErrorCode.NO_LOGIN)
        url = RenrenAgent.getProfileUrl(id)
        try:
            response = self.opener.open(url, timeout=self.TIME_OUT)
            realUrl = response.geturl()
            html = response.read()
        except Exception, e:
            # TODO: use e.reason or other appropriate exceition if possible
            # The another possible exception is stock.timeout: time out
            log.warning('Get profile url error: ' + str(e) +\
                        '. Profile url: ' + url)
            return (None, ErrorCode.URL_ERROR)

        if re.match(r'.*page.renren.com.*', url):
            # It may be not a personal profile page
            log.warning('Not a personal profile page. Profile url' + url)
            return (None, ErrorCode.UNKNOWN_PAGE)

        if saveAllPage:
            util.savePage(html, id + '_profile')
        info, error = self.parseProfileHtml(html)
        if error:
            # Parse error
            log.warning('Profile parse error, url: ' + url)
            util.saveErrorPage(html, id + 'profile')
        return (info, error)

    def parseProfileHtml(self, html):
        """Returns: {(UserInfo, ErrorCode)} the user information and errorcode.
        """
        document = BeautifulSoup(html)
        errorCode = ErrorCode.LACK_CRITICAL_INFO
        pagetype = -1
        info = None
        if document.find('div', id = 'timeline'):
            # Timeline profile page
            log.debug('The page type is: Timeline')
            pagetype = PageType.TIME_LINE
            info = self.parseTimelineProfilePage(document)
        else:
            # Old profile page
            if document.find('div', id = 'visitors'):
                # With access permission
                log.debug('The page type is: old with access')
                pagetype = PageType.OLD_WITH_ACCESS
                info = self.parseOldProfilePageWithAccess(document)
            elif document.find('div', id = 'allFrdGallery'):
                # Without access permission
                log.debug('The page type is: old without access')
                pagetype = PageType.OLD_WITHOUT_ACCESS
                info = self.parseOldProfilePageWithoutAccess(document)
            else:
                # Unknown page tamplate
                errorCode = ErrorCode.UNKNOWN_PAGE
        if info:
            info.pagetype = pagetype
            info.html = html
            return (info, ErrorCode.OK)
        else:
            # Parse error
            return (None, errorCode)

    def parseTimelineProfilePage(self, document):
        """Returns: {UserInfo} the user information."""
        info = UserInfo()
        # Name & visitedNum
        nameNode = document.find('h1', class_='avatar_title')
        try:
            info.name = nameNode.stripped_strings.next()
            visitedString = nameNode.span.strings.next()
            pat = re.compile('[^\d]*(\d+)[^\d]*',)
            mat = pat.match(visitedString)
            info.visitedNum = int(mat.group(1))
        except Exception, e:
            log.warning('Shit happen in parse time line page: ' + str(e))
            return None  # Lack of critical information
        ul = document.find('ul', id='information-ul')
        # Gender, birthday
        try:
            birthdayNode = ul.find('li', class_='birthday')
            if birthdayNode:
                spanList = birthdayNode.find_all('span')
                for span in spanList:
                    if span.string == u'男生':
                        info.gender = 'male'
                    elif span.string == u'女生':
                        info.gender = 'female'
                    elif span.string:
                        if span.string[0] == u'，':
                            info.birthday = span.string[1:]
                        else:
                            info.birthday = span.string
        except:
            pass
        # Hometown
        try:
            hometownNode = ul.find('li', class_='hometown')
            hometownString = ''
            # TODO: Some times they don't user <a> to palce hometown string
            for aTag in hometownNode.find_all('a'):
                hometownString += aTag.string + ' '
            if not hometownNode.find_all('a'):
                # Use string to directly represent hometown
                pattern = re.compile('\S*\s(.*)')
                hometownString = pattern.match(hometownNode.string).group(1)
            info.hometown = hometownString
        except Exception, e:
            log.debug('Exception in hometown: ' + str(e))
            pass
        # Residence
        try:
            residenceNode = ul.find('li', class_='address')
            placeString = ''
            # TODO: Some times they don't user <a> to palce hometown string
            for aTag in residenceNode.find_all('a'):
                placeString += aTag.string + ' '
            if not residenceNode.find_all('a'):
                # Use string to directly represent hometown
                pattern = re.compile('\S*\s(.*)')
                placeString = pattern.match(residenceNode.string).group(1)
            info.residence = placeString
        except Exception, e:
            log.debug('Exception in Residence: ' + str(e))
            pass
        # FriendsList
        try:
            hasFriendNode = document.find('div', class_ = 'has-friend')
            info.friendNum = int(hasFriendNode.span.string)
            liNodes = hasFriendNode.find_all('li')
            for node in liNodes:
                if node.a and node.a['namecard']:
                    info.friendList.append(node.a['namecard'])
        except:
            pass
        return info

    def parseOldProfilePageWithAccess(self, document):
        """Returns: {UserInfo} the user information."""
        info = UserInfo()
        # Name & visitedNum
        try:
            holderNode = document.find('div', class_='status-holder')
            info.name = holderNode.find('h1', class_='username').string
            info.visitedNum = int(
                holderNode.find('span', class_='count')
                .find('span', class_='count').string)
        except:
            return None  # Lack of critical information
        summaryNode = document.find('div', class_='profile-summary')
        # Gender
        try:
            # sayHiText is something like: '向他打招呼'
            sayHiText = summaryNode.ul.find('a', stats='pf_poke').string
            if re.compile(u'.*他.*').match(sayHiText):
                info.gender = 'male'
            elif re.compile(u'.*她.*').match(sayHiText):
                info.gender = 'female'
        except Exception, e:
            log.debug('Exception in gender: ' + str(e))
            pass
        # Birthday
        try:
            divList = summaryNode.find_all('div', class_='clearfix')
            for divTag in divList:
                if divTag.dt and divTag.dt.string == u'生　　日:':
                    birthdayString = []
                    for a in divTag.find_all('a'):
                        birthdayString.append(a.string)
                    info.birthday = '-'.join(birthdayString)
        except Exception, e:
            log.debug('Exception in birthday: ' + str(e))
            pass
        # Hometown
        try:
            divList = summaryNode.find_all('div', class_='clearfix')
            for divTag in divList:
                if divTag.dt and divTag.dt.string == u'家　　乡:':
                    hometownString = []
                    for a in divTag.find_all('a'):
                        hometownString.append(a.string)
                    info.hometown = ' '.join(hometownString)
        except:
            pass
        # Friends list and friend number.
        # It seems that if you are not the user's friend, you can not see the
        # user id of his/her friend list. Even though you have the access
        # right of the profile page.
        # When you are the user's friend, the friend and friend number in
        # the friend list will appear as a <a xxx...> with the friend's id.
        # When you are not, they are just plain text like <li>xxx</li>
        friendCountNode = document.find(
            'a', stats='pf_allfriend', class_='count')
        if friendCountNode:
            # You can see the ids
            try:
                pat = re.compile('\((\d+)\)')
                numText = pat.match(friendCountNode.string).group(1)
                info.friendNum = int(numText)
                ulTag = document.find('div', id='friends').find(
                    'div', class_='mod-body-out').find('ul', 'people-list')
                for liTag in ulTag.find_all('li'):
                    href = liTag.find('a', class_='avatar')['href']
                    id = re.compile('.*id=(\d+)').match(href).group(1)
                    if id: info.friendList.append(id)
            except Exception, e:
                log.debug('Exception in with id friend list: ' + str(e))
                pass
        else:
            # You can not see the ids in friend list.
            try:
                headerDiv = document.find('div', id='friends').find(
                    'div', class_='mod-header').find(
                    'div', class_='mod-header-in')
                pat = re.compile('\((\d+)\)')
                for string in headerDiv.stripped_strings:
                    mat = pat.match(string)
                    if mat: info.friendNum = int(mat.group(1))
            except Exception, e:
                log.debug('Exception in no id friend list: ' + str(e))
                pass
        # Recent visitors
        try:
            recentVisitorsNode = document.find('div', id = 'visitors')
            liNodes = recentVisitorsNode.find_all('li')
            for node in liNodes:
                if node.a and node.a['namecard']:
                    info.recentVisitedList.append(node.a['namecard'])
        except:
            pass
        return info

    def parseOldProfilePageWithoutAccess(self, document):
        """Returns: {UserInfo} the user information."""
        info = UserInfo()
        # Name & visitedNum
        try:
            info.name = document.find('div', class_='add-guide').h3.string
            spanTag = document.find(
                'div', class_='status-holder').find(
                'span', class_='count').find('span', class_='count')
            info.visitedNum = int(spanTag.string)
        except Exception, e:
            log.warning('Shit happen in parse old without access: ' + str(e))
            return None  # Lack of critical information
        ulTag = document.find('ul', class_='user-info')
        # Gender
        try:
            genderText = ulTag.find('li', class_='gender').span.string
            if genderText == u'男生':
              info.gender = 'male'
            elif genderText == u'女生':
              info.gender = 'female'
        except Exception, e:
            log.debug('Exception in gender 1: ' + str(e))
            try:
                # It's possible that there is no gender info in user-info
                # So we find it's gender info from something link: '她/他xx'
                detailUlTag = document.find('ul', class_='detail')
                for liTag in detailUlTag.find('li'):
                    tagText = liTag.string
                    if re.compile(u'.*他.*').match(tagText):
                        info.gender = 'male'
                    elif re.compile(u'.*她.*').match(tagText):
                        info.gender = 'female'
            except Exception, e:
                log.debug('Exception in gender 2: ' + str(e))
        # Hometown
        try:
            liTag = ulTag.find('li', class_='hometown')
            placeList = []
            for spanTag in liTag.find_all('span'):
                placeList.append(spanTag.string)
            info.hometown = ' '.join(placeList)
        except:
            pass

        allFriNode = document.find('div', id = 'allFrdGallery')
        # FriendNum
        try:
            text = allFriNode.h3.string
            pat = re.compile('[^\d]*(\d+)[^\d]*')
            text = pat.match(text).group(1)
            info.friendNum = int(text)
        except Exception, e:
            log.debug('Exception in friend number: ' + str(e))
            pass
        # Friend list
        try:
            liNodes = allFriNode.find_all('li')
            for node in liNodes:
                if node.a and node.a['href']:
                    url = node.a['href']
                    pat = re.compile('.*profile\.do\?id=(\d+).*')
                    result = pat.match(url)
                    if result.group(1):
                        info.friendList.append(result.group(1))
        except:
            pass

        return info
    
    @staticmethod
    def getProfileUrl(id):
        return RenrenAgent.renrenUrl + str(id) + '/profile'
