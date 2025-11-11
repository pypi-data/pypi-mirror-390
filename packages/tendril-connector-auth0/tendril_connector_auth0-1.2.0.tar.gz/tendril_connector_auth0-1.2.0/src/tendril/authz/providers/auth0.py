

from tendril.authn.providers.auth0 import Auth0PythonClient
from tendril.authn.providers.auth0 import management_api
from tendril.authn.providers.auth0 import is_m2m_client
from tendril.config import AUTH0_AUDIENCE_ID
from tendril.config import AUTH0_AUDIENCE


from tendril.utils import log
logger = log.get_logger(__name__, log.DEBUG)


@management_api
def get_resource_servers(auth0: Auth0PythonClient):
    return auth0.resource_servers


def get_resource_server():
    return get_resource_servers().get(AUTH0_AUDIENCE_ID)


def get_current_scopes():
    return {x['value']: x['description'] for x in get_resource_server()['scopes']}


def commit_scopes(scopes):
    logger.debug("Patching scopes on Auth0")
    rs = get_resource_servers()
    rs.update(AUTH0_AUDIENCE_ID,
              {'scopes': [{'value': k, 'description': v}
                          for k, v in scopes.items()]})


@management_api
def get_user_scopes(user_id, auth0: Auth0PythonClient):
    if is_m2m_client(user_id):
        logger.warn("Auth0 M2M client scopes must be manually managed.")
        return None
    return [x['permission_name'] for x in
            auth0.users.list_permissions(user_id, per_page=100)['permissions']]


@management_api
def add_user_scopes(user_id, scopes, auth0: Auth0PythonClient):
    if is_m2m_client(user_id):
        logger.warn("Auth0 M2M client scopes must be manually managed.")
        return None
    return auth0.users.add_permissions(
        user_id,
        [{"resource_server_identifier": AUTH0_AUDIENCE,
          "permission_name": x} for x in scopes])


@management_api
def remove_user_scopes(user_id, scopes, auth0: Auth0PythonClient):
    if is_m2m_client(user_id):
        logger.warn("Auth0 M2M client scopes must be manually managed.")
        return None
    return auth0.users.remove_permissions(
        user_id,
        [{"resource_server_identifier": AUTH0_AUDIENCE,
          "permission_name": x} for x in scopes])
