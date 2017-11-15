import logging
from xml.etree import cElementTree
import time
import uuid
from user import User
from usergroup import UserGroup

log = logging.getLogger("psps-{0}".format(__name__))

class LoginManager(object):
    """Manages the login status of all users.
       Logins are identified against unique tokens.
    """
    
    def __init__(self):
        """Creates an empty dictionary where the keys are tokens and the values are the Users (identified by the username).
        """
        self.users = []
        self.tokens = {}
        log.info("Created LoginManager")
        self.xmlns = {"ns0": "http://www.iter.org/CODAC/PlantSystemConfig/2014"}

    def load(self, userXml):
        """Loads a list of users from an xml file.
           Args:
               userXml (string): path to the file which contains the user definitions.

           Returns:
               True if the file can be sucessfully loaded.
        """
        ok = True
        log.info("Loading xml: {0}".format(userXml))
        try:
            root = cElementTree.parse(userXml)
            #Get all users
            usersXml = root.findall(".//ns0:user", self.xmlns)
            for userXml in usersXml:
                groups = []
                #For each user load the groups
                groupsXml = userXml.findall(".//ns0:group", self.xmlns)
                for groupXml in groupsXml:
                    groupNameXml= groupXml.find("./ns0:name", self.xmlns)
                    groups.append(UserGroup(groupNameXml.text)) 

                usernameXml = userXml.find("./ns0:name", self.xmlns)
                user = User(usernameXml.text, groups) 
                self.users.append(user)
                log.info("Registered user: {0}".format(user))
        except Exception as e:
            log.critical("Error loading xml file {0} : {1}".format(userXml, str(e)))
            ok = False 

        return ok

    def isTokenValid(self, tokenId):
        """Returns true if the token is valid (i.e. if it was created against a valid login).
           If the token is valid the last time at which this token was checked is updated.

           Args:
               tokenId (str): the token to verify.           
 
           Returns:
               True if the token is valid.
        """
        ok = (tokenId in self.tokens)
        print self.tokens
        if (ok):
            self.tokens[tokenId]["lastInteraction"] = int(time.time())
        print self.tokens
        return ok
      
    def login(self, username):
        """Tries to log a new user into the system.
           If successful a token will be associated to this user and registered into the system, so a subsequent call to
           isTokenValid, with this token, will return True.

           Returns:
              A token described as a 32-character hexadecimal string or an empty string if the login fails.

           Todo:
              Implement a proper login mechanism (against a validation mechanism, e.g. password).
        """
        ok = (username in self.users)
        if (ok):
            log.info("{0} logged in successfully".format(username))
            loginToken = uuid.uuid4().hex
            self.tokens[loginToken] = {"user": username, "lastInteraction": int(time.time())}
        else:
            log.warning("{0} is not registered as a valid user".format(username))
            loginToken = ""
           
        return loginToken

    def logout(self, token):
        """Removes the current token from the list of valid tokens, which is equivalent to logging out the user from the system.
        """
        print "\n\n\n\n\n\n\n\n WHAT????\n\n\n\n"
        return self.tokens.pop(token, None)

    def getUser(self, token):
        """Gets the user associated to a given token

           Args:
               token (str): the token to query.

           Returns:
               The User or None if the token is not found.
        """
        user = None
        tokenInfo = self.tokens[token]
        if (tokenInfo is not None):
            tokenUsername = tokenInfo["user"]
            idx = self.users.index(tokenUsername)
            if (idx >= 0):
                user = self.users[idx]
        return user

    def getUsers(self):
        """ Gets all the available users.
       
        Returns:
            All the available users.
        """
        return self.users
 
    def __str__(self):
        """Returns a list of all the currently logged users and associated last interaction times for any given session (one token = one session).
        """
        return str(self.tokens.values())
