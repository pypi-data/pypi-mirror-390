from tendril.utils.config import ConfigOption
from tendril.utils import log
logger = log.get_logger(__name__, log.DEFAULT)

depends = ['tendril.config.core',
           'tendril.config.auth']


config_elements_auth0 = [
    ConfigOption(
        'AUTH0_DOMAIN',
        "None",
        "Auth0 Domain"
    ),
    ConfigOption(
        'AUTH0_AUDIENCE',
        "AUTH_AUDIENCE",
        "Auth0 Audience"
    ),
    ConfigOption(
        'AUTH0_AUDIENCE_ID',
        'None',
        'Auth0 Resource ID for the Auth0 Audience '
        'provided by the application.',
        masked=True
    ),
    ConfigOption(
        'AUTH0_NAMESPACE',
        "'https://tendril.link/schema/auth0'",
        "Auth0 Namespace for Token Contents"
    ),
    ConfigOption(
        'AUTH0_USER_MANAGEMENT_API_CLIENTID',
        "None",
        "Client ID for interaction with the Auth0 Management API. "
        "Required for User database integration.",
        masked=True
    ),
    ConfigOption(
        'AUTH0_USER_MANAGEMENT_API_CLIENTSECRET',
        "None",
        "Client Secret for interaction with the Auth0 Management API. "
        "Required for User database integration.",
        masked=True
    ),
    ConfigOption(
        'AUTH0_M2M_CLIENTS',
        '{}',
        "A dictionary of M2M clients which are allowed to access this instance. "
        "This needs to be specified here to prevent an attempt to get the "
        "User Profile from Auth0, which would fail. Use of the management "
        "API along with exception handling would be a better approach "
        "to do this."
    ),
    ConfigOption(
        'AUTH0_MECHANIZED_CONNECTION',
        'None',
        'Auth0 Connection to use to store Mechanized Users'
    )
]

config_elements_deprecated = [
    ConfigOption(
        'AUTH0_MECHANIZED_USER_DOMAIN',
        'AUTH_MECHANIZED_USER_DOMAIN',
        "Domain to use for mechanized user email addresses. This is "
        "deprecated, use AUTH_MECHANIZED_USER_DOMAIN instead."
    ),
    ConfigOption(
        'AUTH0_USERINFO_CACHING',
        "AUTH_USERINFO_CACHING",
        "Whether to cache userinfo acquired from the management API. "
        "Set to 'platform' for using platform-level caching, using redis. "
        "Other options not presently implemented. This is "
        "deprecated, use AUTH_USERINFO_CACHING instead."
    ),
    ConfigOption(
        'AUTH0_PATCH_SCOPES_ON_STARTUP',
        'AUTH_PATCH_SCOPES_ON_STARTUP',
        "Whether to patch scopes on Auth0 at startup."
    ),
]

def load(manager):
    if manager.AUTH_PROVIDER == "auth0":
        logger.debug("Loading {0}".format(__name__))
        manager.load_elements(config_elements_auth0,
                              doc="Auth0 Configuration")
        manager.load_elements(config_elements_deprecated,
                              doc="Deprecated Auth0 Configuration Options")
