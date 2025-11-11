

import httpx
import hashlib
from typing import List, Optional
from urllib.parse import urlencode
from fastapi import Security
from fastapi import HTTPException
from tendril.utils.www import async_client

from tendril.connectors.keycloak.client import KeycloakClient
from tendril.connectors.keycloak.client import make_scheme
from tendril.connectors.keycloak.client import build_get_user
from tendril.connectors.keycloak.client import KeycloakUserModel

from tendril.connectors.keycloak.admin import KeycloakAdminClient
from tendril.authn.scaffold import null_dependency

from tendril import config
from tendril.config import AUTH_USERINFO_CACHING
from tendril.config import AUTH_ENABLE_LOGIN
from tendril.config import AUTH_ENABLE_ADMIN
from tendril.config import AUTH_ENABLE_ADMIN_REALMS

from tendril.config import AUTH_PROVIDER

from tendril.config import KEYCLOAK_SERVER_URL
from tendril.config import KEYCLOAK_REALM
from tendril.config import KEYCLOAK_AUDIENCE
from tendril.config import KEYCLOAK_CLIENT_ID
from tendril.config import KEYCLOAK_CLIENT_SECRET
from tendril.config import KEYCLOAK_CALLBACK_URL
from tendril.config import KEYCLOAK_ADMIN_CLIENT_ID
from tendril.config import KEYCLOAK_ADMIN_CLIENT_SECRET
from tendril.config import KEYCLOAK_NAMESPACE
from tendril.config import KEYCLOAK_SSL_VERIFICATION

from tendril.config import AUTH_ENABLE_ADMIN_REALMS
from tendril.config import AUTH_REALMS

from tendril.apiserver.server import fastapi_app

from tendril.utils import log
logger = log.get_logger(__name__, log.DEBUG)


if AUTH_USERINFO_CACHING == 'platform':
    logger.info("Using platform level caching for Keycloak UserInfo")
    from tendril.caching import platform_cache as cache
else:
    logger.warning("Auth caching is not configured, not caching Keycloak UserInfo")
    from tendril.caching import no_cache as cache

AuthUserModel = KeycloakUserModel
admin_clients = {}

if AUTH_ENABLE_LOGIN and AUTH_PROVIDER == 'keycloak':
    logger.info(f"Using Keycloak for Authentication with parameters:\n"
                f"  - url             {KEYCLOAK_SERVER_URL} \n"
                f"  - realm           {KEYCLOAK_REALM} \n"
                f"  - client_id       {KEYCLOAK_CLIENT_ID} \n"
                f"  - callback_uri    {KEYCLOAK_CALLBACK_URL} \n")

    idp = KeycloakClient(
        server_url=KEYCLOAK_SERVER_URL,
        realm=KEYCLOAK_REALM,
        audience=KEYCLOAK_AUDIENCE,
        client_id=KEYCLOAK_CLIENT_ID,
        client_secret=KEYCLOAK_CLIENT_SECRET,
        ssl_verify=KEYCLOAK_SSL_VERIFICATION,
    )

    _scheme = make_scheme(KEYCLOAK_SERVER_URL, KEYCLOAK_REALM)
    get_user = build_get_user(idp, _scheme)
    fastapi_app.swagger_ui_init_oauth = {
        "clientId": KEYCLOAK_CLIENT_ID,
        "usePkceWithAuthorizationCodeGrant": True,
        "clientSecret": KEYCLOAK_CLIENT_SECRET,
    }
    swagger_auth = null_dependency

    def security(scopes=None):
        kwargs = {}
        if scopes:
            kwargs['scopes'] = scopes
        return Security(get_user, **kwargs)

if AUTH_ENABLE_ADMIN and AUTH_PROVIDER == 'keycloak':
    logger.info(f"Using Keycloak Admin interface with parameters:\n"
                f"  - url             {KEYCLOAK_SERVER_URL} \n"
                f"  - realm           {KEYCLOAK_REALM} \n"
                f"  - admin_client_id {KEYCLOAK_ADMIN_CLIENT_ID} \n")

    admin = KeycloakAdminClient(
        server_url=KEYCLOAK_SERVER_URL,
        realm=KEYCLOAK_REALM,
        admin_client_id=KEYCLOAK_ADMIN_CLIENT_ID,
        admin_client_secret=KEYCLOAK_ADMIN_CLIENT_SECRET,
        ssl_verify=KEYCLOAK_SSL_VERIFICATION,
    )
    admin_clients['default'] = admin
    admin_clients[KEYCLOAK_REALM] = admin

def _create_admin(realm):
    params = getattr(config, 'KEYCLOAK_{}_ADMIN_PARAMETERS'.format(realm.upper()), None)
    if params:
        logger.info(f"Installing interface to Remote Authn Realm {realm} Keycloak Admin\n")
        logger.debug(f"Using parameters:\n")
        logger.debug(f" {params}")
        return KeycloakAdminClient(**params)
    logger.warning(f"Requested Auth Realm {realm} is not available. Check configuration.\n")
    return None

if AUTH_ENABLE_ADMIN_REALMS and AUTH_REALMS:
    # TODO Consider a global admin clients registry
    for realm in AUTH_REALMS:
        lclient = _create_admin(realm)
        if lclient is not None:
            admin_clients[realm] = lclient

def get_admin_client(realm=None) -> KeycloakAdminClient:
    if not realm or realm=='default':
        return admin
    elif realm in admin_clients.keys():
        return admin_clients[realm]
    else:
        raise ValueError(f"Unknown Keycloak Authn realm '{realm}'")


def _key_func(user_id):
    return user_id

@cache(namespace="userinfo", ttl=86400, key=lambda user_id: user_id)
async def get_user_profile(user_id: str, realm=None):
    kc_admin = get_admin_client(realm)

    # Detect service accounts
    if user_id.startswith("service-account-"):
        client_id = user_id.replace("service-account-", "")
        try:
            return await kc_admin.get_service_account_user(client_id)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail=f"Service account not found: {user_id}")
            raise

    # Regular human user
    try:
        return await kc_admin.users.get(user_id)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        raise


def is_service_account(profile: dict) -> bool:
    """
    Detects whether this Keycloak user profile represents
    a service account automatically created for a client.
    """
    return profile.get("username", "").startswith("service-account-")


@cache(namespace="userstub", ttl=86400, key=_key_func)
async def get_user_stub(user_id, realm=None):
    """
    Retrieve a simplified user stub profile from Keycloak.

    Adds `nickname` and `picture` fields if missing,
    and detects service (M2M) accounts based on username.
    """
    profile = await get_user_profile(user_id, realm)
    if is_service_account(profile):
        profile["description"] = f"Service account for {profile.get('username')}"
        return profile

    name = profile.get("firstName", "") + " " + profile.get("lastName", "")
    name = name.strip() or profile.get("username", user_id)

    email = profile.get("email")
    nickname = profile.get("username") or (email.split("@")[0] if email else name)
    user_id_field = profile.get("id") or user_id

    if email:
        email_hash = hashlib.md5(email.lower().encode("utf-8")).hexdigest()
        gravatar_url = f"https://www.gravatar.com/avatar/{email_hash}?{urlencode({'d': 'identicon', 's': '128'})}"
    else:
        gravatar_url = None

    return {
        "name": name,
        "nickname": nickname,
        "picture": gravatar_url,
        "user_id": user_id_field,
    }


# ---------------------------------------------------------------------
# User Management : Search
# ---------------------------------------------------------------------

def _extract_user_ids(user_list: list[dict]) -> list[str]:
    return [u["id"] for u in user_list if "id" in u]


async def search_users(q: Optional[str] = None, realm=None) -> List[str]:
    kc_admin = get_admin_client(realm)
    first = 0
    limit = 50
    all_users: list[dict] = []

    while True:
        users = await kc_admin.users.list(search=q or "", first=first, max=limit)
        if not users:
            break
        all_users.extend(users)
        if len(users) < limit:
            break
        first += limit

    return _extract_user_ids(all_users)


# ---------------------------------------------------------------------
# User Management : Role operations
# ---------------------------------------------------------------------

async def get_roles(client_id: str=KEYCLOAK_CLIENT_ID, realm=None) -> list[dict]:
    """
    List all roles defined for a given client.
    The client_id must be the human-readable clientId (not UUID).
    """
    kc_admin : KeycloakAdminClient = get_admin_client(realm)
    client = await kc_admin.get_client(client_id)
    return await kc_admin.users.list_client_roles(client["id"])


async def get_role_id(name: str, client_id: str= KEYCLOAK_CLIENT_ID, realm=None) -> Optional[str]:
    """
    Find the ID of a given client role by name.
    """
    roles = await get_roles(client_id, realm)
    for role in roles:
        if role["name"] == name:
            return role["id"]
    return None


async def assign_role_to_users(role_name: str, users: list[str],
                               client_id: str=KEYCLOAK_CLIENT_ID, realm=None):
    """
    Assign the given client role to a list of users.
    """
    kc_admin : KeycloakAdminClient = get_admin_client(realm)
    client = await kc_admin.get_client(client_id)
    role_id = await get_role_id(role_name, client_id, realm)
    if not role_id:
        raise ValueError(f"Role '{role_name}' not found for client '{client_id}' in realm '{realm}'")

    roles = [{"id": role_id, "name": role_name}]
    for user_id in users:
        await kc_admin.users.add_client_roles(user_id, client["id"], roles)


async def assign_role_to_user(role_name: str, user_id: str,
                              client_id: str=KEYCLOAK_CLIENT_ID, realm=None):
    """
    Assign a specific client role to one user.
    """
    kc_admin : KeycloakAdminClient = get_admin_client(realm)
    client = await kc_admin.get_client(client_id)
    role_id = await get_role_id(role_name, client_id, realm)
    if not role_id:
        raise ValueError(f"Role '{role_name}' not found for client '{client_id}' in realm '{realm}'")

    await kc_admin.users.add_client_roles(user_id, client["id"], [{"id": role_id, "name": role_name}])


# ---------------------------------------------------------------------
# User Management
# ---------------------------------------------------------------------
async def create_user(
    email: str,
    username: str,
    name: Optional[str] = None,
    role: Optional[str] = None,
    password: Optional[str] = None,
    client_id: Optional[str] = KEYCLOAK_CLIENT_ID,
    realm: Optional[str] = None,
):
    """
    Create a new Keycloak user and optionally assign a client role.
    """
    kc_admin : KeycloakAdminClient = get_admin_client(realm)
    payload = {
        "email": email,
        "username": username,
        "enabled": True,
        "firstName": name or username,
        "credentials": [{"type": "password", "value": password, "temporary": False}],
    }

    user_id = await kc_admin.users.create(payload)
    if not user_id:
        raise RuntimeError("User creation failed")

    if role and client_id:
        await assign_role_to_user(role, user_id, client_id, realm)

    return {"id": user_id, "email": email, "username": username}


async def find_user_by_email(email: str, realm=None) -> list[str]:
    """
    Search for users by email address.
    """
    kc_admin : KeycloakAdminClient = get_admin_client(realm)
    users = await kc_admin.users.list(search=email)
    return _extract_user_ids(users)


async def set_user_password(user_id: str, password: str, realm=None):
    """
    Reset a user's password (non-temporary).
    """
    kc_admin : KeycloakAdminClient = get_admin_client(realm)
    await kc_admin.users.set_password(user_id, password, temporary=False)


# ---------------------------------------------------------------------
# Intramural Authentication
# ---------------------------------------------------------------------
async def get_service_access_token(realm, audience, client_id, client_secret, ssl_verify):
    """
    Obtain an access token from Keycloak for a machine-to-machine client.
    'audience' here corresponds to the resource server (API) this token is intended for.
    The client (identified by client_id+client_secret) must:
      - Have 'Service Accounts Enabled'
      - Have appropriate roles/client scopes mapped to the service account
      - (Optionally) Use a mapper to populate aud claim if needed

    Returns: (token, expires_in_seconds)
    """
    if realm is None:
        realm = KEYCLOAK_REALM

    token_url = urllib.parse.urljoin(
        KEYCLOAK_SERVER_URL,
        f"/realms/{realm}/protocol/openid-connect/token"
    )
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }

    logger.debug(f"Requesting Keycloak token for client '{client_id}' audience '{audience}'")
    async with async_client(verify=ssl_verify) as client:
        response = await client.post(
            token_url,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencExtract providers. Migrate authn to async. Various cleanup.oded"},
        )
        response.raise_for_status()
        resp = response.json()
        token = resp["access_token"]
        expires_in = resp.get("expires_in", 3600)
        logger.debug(f"Received token (exp in {expires_in}s) for client '{client_id}' audience '{audience}'")
        return token


def init():
    pass
