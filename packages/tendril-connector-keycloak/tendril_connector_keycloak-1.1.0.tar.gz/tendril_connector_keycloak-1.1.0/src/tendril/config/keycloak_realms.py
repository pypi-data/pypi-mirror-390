

from tendril.utils.config import ConfigOption
from tendril.utils.config import ConfigOptionConstruct
from tendril.utils import log
logger = log.get_logger(__name__, log.DEFAULT)

depends = ['tendril.config.core',
           'tendril.config.auth',
           'tendril.config.keycloak',]


class KeycloakRealmAdminParameters(ConfigOptionConstruct):
    @property
    def value(self):
        return {
            'server_url': self.ctx["KEYCLOAK_{}_SERVER_URL".format(self._parameters)],
            'realm': self.ctx["KEYCLOAK_{}_REALM".format(self._parameters)],
            'admin_client_id': self.ctx["KEYCLOAK_{}_ADMIN_CLIENT_ID".format(self._parameters)],
            'admin_client_secret': self.ctx["KEYCLOAK_{}_ADMIN_CLIENT_SECRET".format(self._parameters)],
            'ssl_verify': self.ctx["KEYCLOAK_{}_SSL_VERIFICATION".format(self._parameters)],
        }


def _keycloak_realm_config_template(realm):
    return [
        ConfigOption(
            'KEYCLOAK_{}_SERVER_URL'.format(realm.upper()),
            "KEYCLOAK_SERVER_URL",
            "URL of the Keycloak Server with provides the {} Authn Realm".format(realm)
        ),
        ConfigOption(
            'KEYCLOAK_{}_REALM'.format(realm.upper()),
            f"KEYCLOAK_REALM + '-{realm}'",
            "Keycloak realm name for the {} Authn Realm".format(realm)
        ),
        ConfigOption(
            'KEYCLOAK_{}_AUDIENCE'.format(realm.upper()),
            f"AUTH_AUDIENCE_BASE + '{realm}'",
            f"Audience to expect in Keycloak Tokens provided by the {realm} Authn Realm."
            f" Expect Deprecation of this unused configuration item."
        ),
        ConfigOption(
            'KEYCLOAK_{}_ADMIN_CLIENT_ID'.format(realm.upper()),
            "None",
            f"Client ID for the admin client of the {realm} Authn Realm."
        ),
        ConfigOption(
            'KEYCLOAK_{}_ADMIN_CLIENT_SECRET'.format(realm.upper()),
            "None",
            f"Client Secret for the admin client of the {realm} Authn Realm.",
            masked=True
        ),
        ConfigOption(
            'KEYCLOAK_{}_SSL_VERIFICATION'.format(realm.upper()),
            "KEYCLOAK_SSL_VERIFICATION",
            f"Whether SSL needs to be verified for the {realm} Authn Realm."
        ),
        KeycloakRealmAdminParameters(
            'KEYCLOAK_{}_ADMIN_PARAMETERS'.format(realm.upper()),
            realm.upper(),
            f"Constructed Keycloak Realm Admin parameters instance for the "
            f"{realm} realm. This option is created by the code, and should not "
            f"be set directly in any config file."
        )
    ]


def load(manager):
    logger.debug("Loading {0}".format(__name__))
    config_elements_keycloak_realms = []
    for realm in manager.KEYCLOAK_REALMS:
        config_elements_keycloak_realms += _keycloak_realm_config_template(realm)
    manager.load_elements(config_elements_keycloak_realms,
                          doc="Administrable Keycloak Realms Configuration")
