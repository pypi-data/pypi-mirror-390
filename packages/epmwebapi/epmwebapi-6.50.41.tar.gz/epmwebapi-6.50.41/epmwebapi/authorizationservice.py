import datetime as dt
import requests
import json

from .autostarttimer import AutoStartTimer

from .epmconnectioncontext import EpmConnectionContext

class AuthorizationService(object):

  def __init__(self, connectionContext:EpmConnectionContext, forceConnection = True):
    import copy
    self._context = copy.deepcopy(connectionContext)
    self._error = ''
    self._expireIn = 0
    self._session = None
    if self._context.hasToken():
      self.changedToken(self._context.getToken())  

  def reloadToken(self):
    try:
      token = self.renewToken()
      self._context.setToken(token)
      self.changedToken(token)      
      self._error = ''
    except Exception as ex:
      self._context.setToken(None)
      self._error = str(ex)
      raise
    
  def renewToken(self):
    from datetime import datetime, timedelta

    import logging
    try:
      if (self._context.hasToken()):
       return self.refreshToken()
    except TokenOldException:
      logging.info('The token is old and were closed! Trying to create a new one.')
    except Exception as ex:
      import traceback
      details = traceback.format_exc()
      logging.error('Refresh failed! Trying to connect again. Error: ' + str(ex) + '. Details: ' + details)

    client_auth = requests.auth.HTTPBasicAuth(self._context.getClientId(), self._context.getProgramId())
    post_data = {"grant_type": "password", 
                  "username": self._context.getUserName(),
                  "password": self._context.getPassword(),
                  "scope": "offline_access openid profile email opcua_browse opcua_read opcua_write opcua_subscription opcua_history EpmWebApi portal_files portal_upload"} 
    auth_url = self._context.getAuthServer() + '/connect/token'

    session = self._getSession()
    response = session.post(auth_url,
                             auth=client_auth,
                             data=post_data, verify=False)
    respose_json = response.json()

    if response.status_code != 200:
        raise Exception("GetToken() call http error '" +  str(response.status_code) + "'. Reason: " + respose_json["error"])
    
    expireIn = respose_json["expires_in"]
    if expireIn is None or expireIn < 60 or expireIn > 180:
      expireIn = 180

    self._expireIn = expireIn

    from datetime import datetime, timedelta
    self._context.setExpiration(datetime.utcnow() + timedelta(seconds=self._expireIn))
    self._context.setRefreshToken(respose_json["refresh_token"])

    return respose_json["access_token"]

  def changedToken(self, token):
    session = self._getSession()
    if token != None:
      header = {'Authorization': 'Bearer {}'.format(token)}
      session.headers.update(header)
    else:
      header = {}
      session.headers.update(header)

  def getContext(self) -> EpmConnectionContext:
    return self._context

  def getToken(self):
    if self._error == '':
      return self._context.getToken()
    else:
      raise Exception(self._error)

  def getEpmSession(self):
    from .epmsession import EpmSession
    return EpmSession(self)

  def _getSession(self):
    if self._session == None:
      self._session = requests.session()
    return self._session


  def refreshToken(self):

    import logging
    from datetime import datetime, timedelta
    # agora sempre faz um refresh pra verificar a conexão
    #if (self._tokenExpiration != None and self._tokenExpiration  > (datetime.utcnow() + timedelta(seconds=60))):
    #  return self._token
    if (self._context.hasExpiration() and self._context.getExpiration() < (datetime.utcnow() + timedelta(seconds=30))):
      # tenta fechar o token
      logging.debug('Token is old. Logging out to create a new one.')
      self.logout()
      raise TokenOldException()

    client_auth = requests.auth.HTTPBasicAuth(self._context.getClientId(), self._context.getProgramId())
    post_data = {"grant_type": "refresh_token", 
                 "refresh_token": "%s"%(str(self._context.getRefreshToken())) }
    auth_url = self._context.getAuthServer() + '/connect/token'

    session = self._getSession()
    response = session.post(auth_url,
                              auth=client_auth,
                              data=post_data, verify=False) 
    respose_json = response.json()

    if response.status_code != 200:
      raise Exception("RefreshToken() call http error '" +  str(response.status_code) + "'.")

    from datetime import datetime, timedelta

    expireIn = self._expireIn
    if expireIn is None or expireIn < 60 or expireIn > 180:
      expireIn = 180

    self._context.setRefreshToken(respose_json["refresh_token"])
    self._context.setExpiration(datetime.utcnow() + timedelta(seconds=expireIn))

    return respose_json["access_token"]

  def logout(self):
    if (not self._context.hasToken()):
      return
    
    try:
      post_data = { "token" : self._context.getToken() }
      client_auth = requests.auth.HTTPBasicAuth(self._context.getClientId(), self._context.getProgramId())
      auth_url = self._context.getAuthServer() + '/connect/revocation'
      session = self._getSession()
      try:
        response = session.post(auth_url,
                                  auth=client_auth,
                                  data=post_data, verify=False)
      except Exception as ex:
        import traceback
        details = traceback.format_exc()
        import logging
        logging.error('Trying to revoke token failed! Error: ' + str(ex) + '. Details: ' + details)

      if (not self._context.hasRefreshToken()):
        return
      post_data = { "token" : self._context.getRefreshToken(), "token_type_hint" : "refresh_token" }
      client_auth = requests.auth.HTTPBasicAuth(self._context.getClientId(), self._context.getProgramId())
      auth_url = self._context.getAuthServer() + '/connect/revocation'
      session = self._getSession()

      try:
        response = session.post(auth_url,
                                  auth=client_auth,
                                  data=post_data, verify=False)
      except Exception as ex:
        import traceback
        details = traceback.format_exc()
        import logging
        logging.error('Trying to revoke refreshToken failed! Error: ' + str(ex) + '. Details: ' + details)

    finally:
      self._context.setRefreshToken(None)
      self._context.setExpiration(None)
      self._context.setToken(None)


  def detach(self):
    import copy
    context = copy.deepcopy(self._context)
    self._context.reset()
    return context

  def close(self):
    self.logout()

  def restart(self):
    self._context.setRefreshToken(None)
    self._context.setExpiration(None)
    self._context.setToken(None)
    self._context.setToken(self.renewToken())



class TokenOldException(Exception):
    def __init__(self):
        msg = 'The token is old.'
        super().__init__(msg)
