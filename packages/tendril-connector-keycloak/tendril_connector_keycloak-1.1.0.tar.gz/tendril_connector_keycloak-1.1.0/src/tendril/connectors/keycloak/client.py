
import pprint
pp = pprint.PrettyPrinter(indent=2)

from typing import List, Optional
from pydantic import Field
from pydantic import BaseModel
import httpx

from jose import jwt, jwk
from jose.exceptions import JWTError

from fastapi import HTTPException, Security
from fastapi.security import OAuth2AuthorizationCodeBearer, SecurityScopes
from tendril.jwt.secrets import public_key
from .base import KeycloakClientBase


class KeycloakUserModel(BaseModel):
    id: str = Field(..., alias='sub')
    email: Optional[str]
    name: Optional[str]
    username: str = Field(..., alias='preferred_username')
    permissions: List[str]


def make_scheme(server_url: str, realm: str):
    base = f"{server_url}/realms/{realm}/protocol/openid-connect"
    return OAuth2AuthorizationCodeBearer(
        authorizationUrl=f"{base}/auth",
        tokenUrl=f"{base}/token",
        auto_error=False,
    )


class KeycloakClient(KeycloakClientBase):
    def __init__(self, server_url: str, realm: str, audience: str,
                 client_id: str, client_secret: str, ssl_verify: bool = True):
        super().__init__(server_url, realm, ssl_verify)
        self.client_id = client_id
        self.client_secret = client_secret
        self.audience = audience

        self._jwks = None
        self._jwks_pubkeys = {}

    @property
    def _jwks_url(self):
        return f"{self._protocol_url}/certs"

    async def jwks(self):
        if self._jwks is None:
            async with httpx.AsyncClient(verify=self.ssl_verify) as client:
                response = await client.get(self._jwks_url)
                response.raise_for_status()
                self._jwks = response.json()
        return self._jwks

    async def _get_public_key(self, kid):
        if self._jwks_pubkeys.get(kid, None) is None:
            jwks_keys = await self.jwks()
            key_data = next((key for key in jwks_keys['keys'] if key["kid"] == kid))
            if not key_data:
                # kid is not in the jwks. perhaps the jwks needs to be
                # reloaded after key rotation or similar events.
                self._jwks = None
                self._jwks_pubkeys = {}
                raise HTTPException(status_code=401,
                                    detail="Authentication Failure. 'kid' specified by token not found in JWKS. Refreshing JWKS, retry.")
            self._jwks_pubkeys[kid] = jwk.construct(key_data).public_key()
        return self._jwks_pubkeys[kid]

    async def validate_token(self, token: str):
        headers = jwt.get_unverified_headers(token)
        kid = headers.get("kid")
        if not kid:
            raise HTTPException(status_code=401, detail="Authentication Failure. Token missing 'kid' header")

        public_key = await self._get_public_key(kid)

        try:
            payload = jwt.decode(token, key=public_key,
                                 algorithms=["RS256"],
                                 audience=self.audience)
            # TODO Check for required claims here
            return payload
        except JWTError as e:
            raise HTTPException(status_code=401, detail=f"Invalid Token: {e}")

    async def get_user(self, security_scopes: SecurityScopes, token : str) -> KeycloakUserModel:
        if not token:
            raise HTTPException(status_code=401, detail="Authentication Failure")
        token_data = await self.validate_token(token)

        # Check for Required Scopes
        if security_scopes.scopes:
            # print(f"Required Scopes: {security_scopes.scope_str}")

            # realm_roles = set(token_data.get("realm_access", {}).get("roles", []))
            # pp.pprint(realm_roles)

            # resource_roles = set()
            # for res, data in token_data.get("resource_access", {}).items():
            #     resource_roles.update([f'{res}::{x}' for x in data.get("roles", [])])
            # pp.pprint(resource_roles)

            current_resource_roles = set([x for x in token_data["resource_access"].get(self.audience, {}).get("roles", [])])
            actual_scopes = current_resource_roles
            token_data["permissions"] = actual_scopes

            missing_scopes = [x for x in security_scopes.scopes if x not in actual_scopes]
            if missing_scopes:
                raise HTTPException(
                    status_code=403,
                    detail=f"Authorization Failure. Token does not provide "
                           f"scopes {', '.join(missing_scopes)}")
        else:
            token_data["permissions"] = []

        # TODO Assemble Actual User Model
        user = KeycloakUserModel(**token_data)
        return user


def build_get_user(idp: KeycloakClient, scheme: OAuth2AuthorizationCodeBearer):
    # This is a *top-level function object* with a static, inspectable signature.
    async def get_user(
        security_scopes: SecurityScopes,
        token: str = Security(scheme),
    ):
        return await idp.get_user(security_scopes, token)
    return get_user
