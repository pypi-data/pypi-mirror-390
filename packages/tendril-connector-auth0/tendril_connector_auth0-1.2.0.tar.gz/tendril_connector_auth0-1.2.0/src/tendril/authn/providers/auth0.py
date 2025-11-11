

import os
from tendril.config import AUTH0_NAMESPACE
os.environ['AUTH0_RULE_NAMESPACE'] = AUTH0_NAMESPACE

from fastapi import Security
from fastapi_auth0 import Auth0, Auth0User

from auth0.exceptions import Auth0Error
from auth0.authentication import GetToken
from auth0.management import Auth0 as Auth0PythonClient

from tendril.utils.www import async_client
from tendril.authz import scopes

from tendril.config import AUTH0_DOMAIN
from tendril.config import AUTH0_AUDIENCE
from tendril.config import AUTH0_USER_MANAGEMENT_API_CLIENTID
from tendril.config import AUTH0_USER_MANAGEMENT_API_CLIENTSECRET
from tendril.config import AUTH0_USERINFO_CACHING
from tendril.config import AUTH0_M2M_CLIENTS
from tendril.config import AUTH0_MECHANIZED_CONNECTION

from tendril.utils import log
logger = log.get_logger(__name__, log.DEBUG)


logger.info("Using Auth0 parameters:\n"
            "  - domain    {} \n"
            "  - audience  {} \n"
            "  - namespace {} ".format(AUTH0_DOMAIN, AUTH0_AUDIENCE, AUTH0_NAMESPACE))


if AUTH0_USERINFO_CACHING == 'platform':
    logger.info("Using platform level caching for Auth0 UserInfo")
    from tendril.caching import platform_cache as cache
else:
    logger.info("Not caching Auth0 UserInfo")
    from tendril.caching import no_cache as cache


auth = Auth0(domain=AUTH0_DOMAIN,
             api_audience=AUTH0_AUDIENCE,
             scopes=scopes.scopes)

management_api_token = None

AuthUserModel = Auth0User
swagger_auth = auth.implicit_scheme

def security(scopes=None):
    kwargs = {}
    if scopes:
        kwargs['scopes'] = scopes
    return Security(auth.get_user, **kwargs)


def get_management_api_token():
    global management_api_token
    logger.debug("Attempting to get the management API token using:\n"
                 "  - domain          {}\n"
                 "  - client id       {}\n"
                 "  - client secret   ending with {}".format(
        AUTH0_DOMAIN, AUTH0_USER_MANAGEMENT_API_CLIENTID,
        AUTH0_USER_MANAGEMENT_API_CLIENTSECRET[-5:0])
    )
    get_token = GetToken(AUTH0_DOMAIN, AUTH0_USER_MANAGEMENT_API_CLIENTID,
                         client_secret=AUTH0_USER_MANAGEMENT_API_CLIENTSECRET)
    token = get_token.client_credentials('https://{}/api/v2/'.format(AUTH0_DOMAIN))
    management_api_token = token['access_token']
    logger.info("Successfully received Management API token ending in {}".format(management_api_token[-5:]))


def management_api(func):
    def _wrapper(*args, **kwargs):
        global management_api_token
        if management_api_token is None:
            get_management_api_token()
        try:
            auth0 = Auth0PythonClient(AUTH0_DOMAIN, management_api_token)
            return func(*args, auth0=auth0, **kwargs)
        except Auth0Error as error:
            if error.status_code == 401:
                get_management_api_token()
                auth0 = Auth0PythonClient(AUTH0_DOMAIN, management_api_token)
                return func(*args, auth0=auth0, **kwargs)
            if error.status_code == 400:
                # this may be an M2M client
                raise
            else:
                raise
    return _wrapper


@management_api
def get_user_object(user_id, auth0=None):
    logger.debug("Attempting to fetch user information for {} from Auth0".format(user_id))
    user_profile = auth0.users.get(user_id)
    logger.info("Got user details for {} from Auth0 Management API".format(user_id))
    return user_profile


_m2m_clients = {}


def _key_func(user_id):
    return user_id


def is_m2m_client(user_id):
    if user_id in _m2m_clients.keys():
        return True
    return False


@cache(namespace='userinfo', ttl=86400, key=_key_func)
def get_user_profile(user_id):
    if is_m2m_client(user_id):
        return _m2m_clients[user_id]
    global management_api_token
    if management_api_token is None:
        get_management_api_token()
    try:
        return get_user_object(user_id)
    except Auth0Error as error:
        if error.status_code == 401:
            get_management_api_token()
            return get_user_object(user_id)
        if error.status_code == 400:
            # this may be an M2M client
            raise
        else:
            raise


@cache(namespace='userstub', ttl=86400, key=_key_func)
def get_user_stub(user_id):
    profile = get_user_profile(user_id)
    if 'description' in profile.keys():
        return profile
    return {
        'name': profile['name'],
        'nickname': profile['nickname'],
        'picture': profile['picture'],
        'user_id': profile['user_id'],
    }


@management_api
def get_connections(auth0: Auth0PythonClient = None):
    return auth0.connections.all()


def get_connection_id(name):
    for connection in get_connections():
        if connection['name'] == name:
            return connection['id']


def _extract_user_ids(user_list):
    return [x['user_id'] for x in user_list]

@management_api
def search_users(q, auth0: Auth0PythonClient = None):
    start = 0
    limit = 25
    total = None
    got = 0
    page = 0
    result = []

    response = auth0.users.list(page=0, per_page=limit, q=q)
    total = response['total']

    got = response['length']
    result.extend(_extract_user_ids(response['users']))

    while got < total:
        page += 1
        response = auth0.users.list(page=page, per_page=limit, q=q)
        result.extend(_extract_user_ids(response['users']))
        got += response['length']

    return result


def get_connection_users(connection_name):
    return search_users(q=f'identities.connection:"{connection_name}"')


@management_api
def get_roles(auth0: Auth0PythonClient = None):
    return auth0.roles.list()['roles']


def get_role_id(name):
    for role in get_roles():
        if role['name'] == name:
            return role['id']


@management_api
def assign_role_to_users(role, users, auth0: Auth0PythonClient=None):
    per_page = 50
    total_users = len(users)

    for start_index in range(0, total_users, per_page):
        end_index = min(start_index + per_page, total_users)
        batch_users = users[start_index:end_index]
        auth0.roles.add_users(role, batch_users)

    # Handle any remaining users (if the total_users is not a multiple of per_page)
    remaining_users = users[end_index:]
    if remaining_users:
        auth0.roles.add_users(role, remaining_users)


@management_api
def assign_role_to_user(role, user_id, auth0: Auth0PythonClient=None):
    if not role:
        return
    role_id = get_role_id(role)
    return auth0.users.add_roles(user_id, [role_id])


@management_api
def create_user(email=None, username=None, name=None, role=None, password=None,
                auth0: Auth0PythonClient = None, mechanized=True):
    if not mechanized:
        raise (ValueError('auth0 provider currently supports the creation '
                          'of mechanized users only.'))
    if mechanized and not AUTH0_MECHANIZED_CONNECTION:
        raise (ValueError('AUTH0_MECHANIZED_CONNECTION needs to be '
                          'provided to enable mechanized user creation'))
    response = auth0.users.create(body={
        'email': email,
        'name': name,
        'username': username,
        'connection': AUTH0_MECHANIZED_CONNECTION,
        'password': password,
    })
    user_id = response['user_id']
    if role:
        assign_role_to_user(role, user_id)
    return response


@management_api
def find_user_by_email(email, mechanized=True, auth0: Auth0PythonClient = None):
    results = auth0.users_by_email.search_users_by_email(email, fields=['user_id', 'identities'])
    if mechanized:
        return [x['user_id'] for x in results if
                x['identities'][0]['connection'] == AUTH0_MECHANIZED_CONNECTION]
    else:
        return [x['user_id'] for x in results]


@management_api
def set_user_password(user_id, password, auth0: Auth0PythonClient = None):
    # TODO This should only apply to mechanized users
    auth0.users.update(user_id, {'password': password})


async def get_service_access_token(realm, audience, client_id, client_secret):
    if realm is not None:
        # TODO Realms here would probably correspond to the 'connection' of the
        #   Auth0 Domain. We don't need to provide a separate realm here, auth0
        #   provides separate M2N clients which is what we use instead, and this
        #   is separate from the Auth0 connection infrastructure..
        raise ValueError("Auth0 Provider does not support multiple realms")
    async with async_client() as auth_client:
        response = await auth_client.post(
            f"https://{AUTH0_DOMAIN}/oauth/token",
            json={"audience": self._audience,
                  "grant_type": "client_credentials",
                  "client_id": self._client_id,
                  "client_secret": self._client_secret},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()['access_token']


def init():
    global _m2m_clients
    _m2m_clients = AUTH0_M2M_CLIENTS
