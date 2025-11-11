
import pprint
pp = pprint.PrettyPrinter(indent=4)
import pytest
import pytest_asyncio
import asyncio
from tendril.config import (
    KEYCLOAK_SERVER_URL,
    KEYCLOAK_REALM,
    KEYCLOAK_ADMIN_CLIENT_ID,
    KEYCLOAK_ADMIN_CLIENT_SECRET,
    KEYCLOAK_SSL_VERIFICATION,
)
from tendril.connectors.keycloak.admin import KeycloakAdminClient


@pytest_asyncio.fixture
async def admin():
    """
    Create a fresh admin client per test, bound to the test's event loop.
    This ensures httpx.AsyncClient is never reused across loops.
    """
    client = KeycloakAdminClient(
        server_url=KEYCLOAK_SERVER_URL,
        realm=KEYCLOAK_REALM,
        admin_client_id=KEYCLOAK_ADMIN_CLIENT_ID,
        admin_client_secret=KEYCLOAK_ADMIN_CLIENT_SECRET,
        ssl_verify=KEYCLOAK_SSL_VERIFICATION,
    )
    yield client
    await client.close()

# ============================================================
# KeycloakAdminClient tests
# ============================================================

@pytest.mark.asyncio
async def test_request_and_token_lifecycle(admin: KeycloakAdminClient):
    token = await admin._get_token()
    assert isinstance(token, str)
    headers = await admin._headers()
    assert "Authorization" in headers
    # Verify that basic request() works
    clients = await admin.request("GET", "clients?max=1")
    assert isinstance(clients, list)


@pytest.mark.asyncio
async def test_get_client_and_service_account_user(admin: KeycloakAdminClient):
    # Get a client by its clientId (human-readable)
    clients = await admin.request("GET", "clients?max=1")
    if not clients:
        pytest.skip("No clients available for test")
    client = clients[0]
    by_name = await admin.get_client(client["clientId"])
    assert by_name["id"] == client["id"]

    # Get service account user (may not exist for all clients)
    try:
        svc_user = await admin.get_service_account_user(client["clientId"])
        assert "username" in svc_user
    except Exception as e:
        pytest.skip(f"No service account user for {client['clientId']}: {e}")


@pytest.mark.asyncio
async def test_request_raw_flag(admin: KeycloakAdminClient):
    response = await admin.request("GET", "clients?max=1", raw=True)
    assert hasattr(response, "status_code")
    assert response.status_code in (200, 204)


# ============================================================
# _KeycloakUsersAPI tests
# ============================================================

@pytest.mark.asyncio
async def test_users_list_and_get(admin: KeycloakAdminClient):
    users = await admin.users.list()
    # pp.pprint(users)
    assert isinstance(users, list)
    if users:
        user = users[0]
        got = await admin.users.get(user["id"])
        # pp.pprint(got)
        assert got["id"] == user["id"]


@pytest.mark.asyncio
async def test_users_create_update_get_delete(admin: KeycloakAdminClient):
    # Create a temporary user
    payload = {
        "username": "apitest_temp_user",
        "email": "apitest_temp_user@example.com",
        "enabled": True,
    }
    user_id = await admin.users.create(payload)
    assert isinstance(user_id, str) and len(user_id) > 5

    # Update user fields
    await admin.users.update(user_id, {"firstName": "API", "lastName": "Tester"})
    fetched = await admin.users.get(user_id)
    assert fetched["username"] == "apitest_temp_user"

    # Delete user
    await admin.request("DELETE", f"users/{user_id}")
    # Verify cleanup
    remaining = await admin.users.list(search="apitest_temp_user")
    assert not any(u["id"] == user_id for u in remaining)


@pytest.mark.asyncio
async def test_users_find_by_email(admin: KeycloakAdminClient):
    users = await admin.users.find_by_email("admin")
    assert isinstance(users, list)
    for u in users:
        assert "email" in u


@pytest.mark.asyncio
async def test_users_set_password(admin: KeycloakAdminClient):
    payload = {"username": "pwtemp", "email": "pwtemp@example.com", "enabled": True}
    user_id = await admin.users.create(payload)
    assert user_id

    await admin.users.set_password(user_id, "StrongTempPass!23", temporary=True)
    # Cleanup
    await admin.request("DELETE", f"users/{user_id}")


# -------------------------------
# Realm Role Management
# -------------------------------

@pytest.mark.asyncio
async def test_users_realm_roles_list_and_get(admin: KeycloakAdminClient):
    roles = await admin.users.list_realm_roles()
    assert isinstance(roles, list)
    if roles:
        role = roles[0]
        assert "name" in role

    users = await admin.users.list()
    if not users:
        pytest.skip("No users to test realm role retrieval")

    roles_assigned = await admin.users.get_realm_roles(users[0]["id"])
    assert isinstance(roles_assigned, list)


@pytest.mark.asyncio
async def test_users_realm_role_add_remove(admin: KeycloakAdminClient):
    users = await admin.users.list()
    if not users:
        pytest.skip("No users available for realm role test")
    user_id = users[0]["id"]

    roles = await admin.users.list_realm_roles()
    if not roles:
        pytest.skip("No roles in realm to assign")

    role = roles[0]
    # Add and remove role safely (idempotent)
    await admin.users.add_realm_roles(user_id, [role])
    await admin.users.remove_realm_roles(user_id, [role])


# -------------------------------
# Client Role Management
# -------------------------------

@pytest.mark.asyncio
async def test_users_client_roles_list_get_add_remove(admin: KeycloakAdminClient):
    clients = await admin.request("GET", "clients?max=1")
    if not clients:
        pytest.skip("No clients available")

    client = clients[0]
    client_roles = await admin.users.list_client_roles(client["id"])
    assert isinstance(client_roles, list)

    users = await admin.users.list()
    if not users:
        pytest.skip("No users for client role assignment")

    user_id = users[0]["id"]

    if client_roles:
        test_role = client_roles[0]
        # Assign and remove to confirm endpoints work
        await admin.users.add_client_roles(user_id, client["id"], [test_role])
        await admin.users.remove_client_roles(user_id, client["id"], [test_role])

    assigned_roles = await admin.users.get_client_roles(user_id, client["id"])
    assert isinstance(assigned_roles, list)
