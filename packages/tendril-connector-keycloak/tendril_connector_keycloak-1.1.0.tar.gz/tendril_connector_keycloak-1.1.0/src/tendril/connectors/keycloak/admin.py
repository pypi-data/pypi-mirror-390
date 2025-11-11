
from typing import Any, List
import time
import httpx
import asyncio
from .base import KeycloakClientBase


class KeycloakAdminClient(KeycloakClientBase):
    def __init__(self, server_url: str, realm: str,
                 admin_client_id: str, admin_client_secret: str,
                 ssl_verify: bool = True, timeout: int = 10):
        super().__init__(server_url, realm, ssl_verify)
        self.admin_client_id: str = admin_client_id
        self.admin_client_secret: str = admin_client_secret

        self._token = None
        self._token_expiry = 0
        self._client = httpx.AsyncClient(verify=ssl_verify, timeout=timeout)

        self.users = _KeycloakUsersAPI(self)

    @property
    def _token_url(self):
        return self._protocol_url + "/token"

    @property
    def _realm_admin_url(self):
        return f"{self._server_url}/admin/realms/{self.realm}"

    async def _get_token(self):
        if self._token and time.time() < self._token_expiry - 30:
            return self._token

        data = {
            "grant_type": "client_credentials",
            "client_id": self.admin_client_id,
            "client_secret": self.admin_client_secret,
        }

        response = await self._client.post(self._token_url, data=data)
        response.raise_for_status()
        payload = response.json()

        self._token = payload["access_token"]
        self._token_expiry = time.time() + payload.get("expires_in", 60)
        return self._token

    async def _headers(self) -> dict[str, str]:
        token = await self._get_token()
        return {"Authorization": f"Bearer {token}"}

    async def request(self, method: str, path: str, raw: bool=False, **kwargs) -> Any:
        headers = await self._headers()
        url = f"{self._realm_admin_url}/{path.lstrip('/')}"
        response = await self._client.request(method, url, headers=headers, **kwargs)

        if response.status_code == 401:
            self._token = None
            headers = await self._headers()
            response = await self._client.request(method, url, headers=headers, **kwargs)

        response.raise_for_status()
        if raw:
            return response

        if response.text:
            try:
                return response.json()
            except Exception:
                return response.text
        return None

    async def get_client(self, client_id: str) -> dict:
        clients = await self.request('GET', f"clients?clientId={client_id}")
        if not clients:
            raise ValueError(f'Client {client_id} not found')
        return clients[0]

    async def get_service_account_user(self, client_id: str) -> dict:
        client = await self.get_client(client_id)
        client_uuid = client["id"]
        return await self.request('GET', f"clients/{client_uuid}/service-account-user")

    async def close(self):
        try:
            await self._client.aclose()
        except RuntimeError as e:
            if "Event loop is closed" not in str(e):
                raise


class _KeycloakUsersAPI:
    def __init__(self, admin: KeycloakAdminClient):
        self.admin = admin

    # -------------------------------
    # Basic User CRUD
    # -------------------------------
    async def list(self, search: str = "", first: int = 0, max: int = 25) -> List[dict]:
        q = f"users?first={first}&max={max}"
        if search:
            q += f"&search={search}"
        return await self.admin.request("GET", q)

    async def get(self, user_id: str) -> dict:
        return await self.admin.request("GET", f"users/{user_id}")

    async def create(self, payload: dict) -> str:
        """Create a new user and return its ID (from Location header if available)."""
        response = await self.admin.request("POST", "users", json=payload, raw=True)
        if response.status_code in (200, 201):
            loc = response.headers.get("Location", "")
            return loc.rstrip("/").split("/")[-1] if loc else ""
        return ""

    async def update(self, user_id: str, payload: dict) -> None:
        await self.admin.request("PUT", f"users/{user_id}", json=payload)

    async def find_by_email(self, email: str) -> List[dict]:
        return await self.admin.request("GET", f"users?email={email}")

    async def set_password(self, user_id: str, password: str, temporary: bool = False) -> None:
        payload = {"type": "password", "value": password, "temporary": temporary}
        await self.admin.request("PUT", f"users/{user_id}/reset-password", json=payload)

    # -------------------------------
    # Realm Role Management
    # -------------------------------
    async def list_realm_roles(self) -> List[dict]:
        return await self.admin.request("GET", "roles")

    async def get_realm_roles(self, user_id: str) -> List[dict]:
        return await self.admin.request("GET", f"users/{user_id}/role-mappings/realm")

    async def add_realm_roles(self, user_id: str, roles: List[dict]) -> None:
        await self.admin.request("POST", f"users/{user_id}/role-mappings/realm", json=roles)

    async def remove_realm_roles(self, user_id: str, roles: List[dict]) -> None:
        await self.admin.request("DELETE", f"users/{user_id}/role-mappings/realm", json=roles)

    # -------------------------------
    # Client Role Management
    # -------------------------------
    async def list_client_roles(self, client_id: str) -> List[dict]:
        return await self.admin.request("GET", f"clients/{client_id}/roles")

    async def get_client_roles(self, user_id: str, client_id: str) -> List[dict]:
        return await self.admin.request(
            "GET", f"users/{user_id}/role-mappings/clients/{client_id}/composite"
        )

    async def add_client_roles(self, user_id: str, client_id: str, roles: List[dict]) -> None:
        await self.admin.request(
            "POST", f"users/{user_id}/role-mappings/clients/{client_id}", json=roles
        )

    async def remove_client_roles(self, user_id: str, client_id: str, roles: List[dict]) -> None:
        await self.admin.request(
            "DELETE", f"users/{user_id}/role-mappings/clients/{client_id}", json=roles
        )
