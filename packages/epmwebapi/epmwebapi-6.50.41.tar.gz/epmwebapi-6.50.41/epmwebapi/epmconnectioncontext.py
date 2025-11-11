class EpmConnectionContext(object):
    """description of class"""
    def __init__(self, authServer, webapi, clientId, programId, userName, password, token = None, refreshToken = None, expiration = None, changedTokenDatetime = None):
      self._authServer = authServer
      self._webapi = webapi
      self._clientId = clientId
      self._programId = programId
      self._userName = userName
      self._password = password
      self._token = token
      self._refreshToken = refreshToken
      self._expiration = expiration
      self._changedTokenDatetime = changedTokenDatetime

    def __deepcopy__(self, memodict={}):
        cpyobj = EpmConnectionContext(self._authServer, self._webapi, self._clientId, self._programId, self._userName, 
                                      self._password, self._token, self._refreshToken, self._expiration, self._changedTokenDatetime) # shallow copy of whole object 
        return cpyobj

    def set(self, authServer, webapi, clientId, programId, userName, password, token, refreshToken, expiration, changedTokenDatetime):
      self._authServer = authServer
      self._webapi = webapi
      self._clientId = clientId
      self._programId = programId
      self._userName = userName
      self._password = password
      self._token = token
      self._refreshToken = refreshToken
      self._expiration = expiration
      self._changedTokenDatetime = changedTokenDatetime

    def reset(self):
      self._authServer = None
      self._webapi = None
      self._clientId = None
      self._programId = None
      self._userName = None
      self._password = None
      self._token = None
      self._refreshToken = None
      self._expiration = None
      self._changedTokenDatetime = None

    def canRefreshToken(self):
      from datetime import datetime, timedelta
      return self._hasChangedTime() and (datetime.utcnow() - self._changedTokenDatetime) > timedelta(seconds=60)

    def isValidToken(self):
      if self.hasToken() and self.hasExpiration():
        from datetime import datetime, timedelta
        return self._expiration > datetime.utcnow() + timedelta(seconds=30) 
      return False

    def hasToken(self):
      return self._token != None

    def hasRefreshToken(self):
      return self._refreshToken != None

    def hasExpiration(self):
      return self._expiration != None

    def getAuthServer(self):
      return self._authServer

    def setAuthServer(self, authServer):
      self._authServer = authServer

    def getWebApi(self):
      return self._webapi

    def setWebApi(self, webapi):
      self._webapi = webapi


    def getClientId(self):
      return self._clientId

    def setClientId(self, clientId):
      self._clientId = clientId

    def getProgramId(self):
      return self._programId

    def setProgramId(self, programId):
      self._programId = programId

    def getUserName(self):
      return self._userName

    def setUserName(self, userName):
      self._userName = userName

    def getPassword(self):
      return self._password

    def setPassword(self, password):
      self._password = password

    def getToken(self):
      return self._token

    def setToken(self, token):
      self._token = token
      self._updateChangedTokenDatetime()

    def getRefreshToken(self):
      return self._refreshToken

    def setRefreshToken(self, refreshToken):
      self._refreshToken = refreshToken

    def getExpiration(self):
      return self._expiration

    def setExpiration(self, expiration):
      self._expiration = expiration

    def _updateChangedTokenDatetime(self):
      from datetime import datetime
      self._changedTokenDatetime = datetime.utcnow()
      
    def _hasChangedTime(self):
        return self._changedTokenDatetime != None



