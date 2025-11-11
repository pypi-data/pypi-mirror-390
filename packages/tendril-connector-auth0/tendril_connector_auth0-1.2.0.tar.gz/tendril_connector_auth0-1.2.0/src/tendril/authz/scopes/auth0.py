

from tendril.config import AUTHZ_PROVIDER

scopes = {
    'openid profile email': 'OpenID Profile Access',
}

if AUTHZ_PROVIDER == 'auth0':
    default_scopes = ['openid profile email']
