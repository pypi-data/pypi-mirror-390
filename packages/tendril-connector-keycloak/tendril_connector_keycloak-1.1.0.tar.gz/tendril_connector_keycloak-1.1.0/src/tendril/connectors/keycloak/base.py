

class KeycloakClientBase(object):
    def __init__(self, server_url: str, realm: str, ssl_verify: bool = True):
        self._server_url: str = server_url.rstrip("/")
        self.realm = realm
        self.ssl_verify = ssl_verify

    @property
    def _realm_url(self):
        return f"{self._server_url}/realms/{self.realm}"

    @property
    def _protocol_url(self):
        return f"{self._realm_url}/protocol/openid-connect"
