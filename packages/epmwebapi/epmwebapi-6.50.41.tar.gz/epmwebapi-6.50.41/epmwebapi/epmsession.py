from requests import Session
from .authorizationservice import AuthorizationService
from requests.exceptions import ConnectionError

class EpmSession:

    def __init__(self, authService:AuthorizationService):
        self._authService = authService

    def post(self, url, json=None, headers=None, data=None, verify=None):
        session = self._prepareSession()
        try:
            return session.post(url=url, json=json, headers=headers, data=data, verify=verify)
        except ConnectionError:
            self._authService.logout()
            raise

    def get(self, url, verify=None):
        session = self._prepareSession()
        try:
            return session.get(url=url, verify=verify)
        except ConnectionError:
            self._authService.logout()
            raise


    def patch(self, url, headers=None, json=None, data=None, verify=None):
        session = self._prepareSession()
        try:
            return session.patch(url=url, headers=headers, json=json, data=data, verify=verify)
        except ConnectionError:
            self._authService.logout()
            raise

    def delete(self, url, json=None, verify=None):
        session = self._prepareSession()
        try:
            return session.delete(url=url, json=json,verify=verify)
        except ConnectionError:
            self._authService.logout()
            raise
       

    def _prepareSession(self):
        context = self._authService.getContext()
        if not context.isValidToken() or context.canRefreshToken():
            self._authService.reloadToken()
        return self._authService._getSession()
        
