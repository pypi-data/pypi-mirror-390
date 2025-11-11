from tendril.utils.config import ConfigOption
from tendril.utils import log
logger = log.get_logger(__name__, log.DEFAULT)

depends = ['tendril.config.core',
           'tendril.config.auth']


config_elements_keycloak = [
    ConfigOption(
        'KEYCLOAK_SERVER_URL',
        "None",
        "URL of the Keycloak Server"
    ),
    ConfigOption(
        'KEYCLOAK_REALM',
        "AUTH_REALM",
        "Keycloak Realm to Use for this application."
    ),
    ConfigOption(
        'KEYCLOAK_AUDIENCE',
        "AUTH_AUDIENCE",
        "Audience to expect in the Keycloak Token."
    ),
    ConfigOption(
        "KEYCLOAK_CLIENT_ID",
        "None",
        "Client ID to use for the Keycloak Connection for this Application"
    ),
    ConfigOption(
        "KEYCLOAK_CLIENT_SECRET",
        "None",
        "Client Secret to use for the Keycloak Connection for this Application"
    ),
    ConfigOption(
        "KEYCLOAK_CALLBACK_URL",
        "None",
        "Callback URL to use with the Keycloak Connection for this Application"
    ),
    ConfigOption(
        "KEYCLOAK_ADMIN_CLIENT_ID",
        "'admin-cli'",
        "Client ID to use for the Keycloak Administration API for this Application"
    ),
    ConfigOption(
        "KEYCLOAK_ADMIN_CLIENT_SECRET",
        "None",
        "Client Secret to use for the Keycloak Administration API for this Application"
    ),
    ConfigOption(
        'KEYCLOAK_NAMESPACE',
        "'https://tendril.link/schema/keycloak'",
        "Namespace for Custom Token Contents for this Application"
    ),
    ConfigOption(
        'KEYCLOAK_SSL_VERIFICATION',
        "True",
        "Whether to verify SSL Certificates for Keycloak Connections"
    ),
    ConfigOption(
        'KEYCLOAK_REALMS',
        "AUTH_REALMS",
        "Realms for which administration should be allowed from this application. "
        "This should only be configured on applications / components from which external "
        "realms need to be configured."
    )
]


def load(manager):
    if manager.AUTH_PROVIDER == "keycloak":
        logger.debug("Loading {0}".format(__name__))
        manager.load_elements(config_elements_keycloak,
                              doc="Keycloak Configuration")
