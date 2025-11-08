from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import requests


@dataclass
class KeycloakService:
    base_url: str  # p.ej. "http://localhost:8080"
    realm: str  # p.ej. "productsRealm"
    timeout: int = 20

    def __post_init__(self):
        self.admin_base = f"{self.base_url}/admin/realms"
        self.session = requests.Session()

    # ---------- AUTH (tokens OIDC) ----------
    def token_password(
        self,
        realm: str,
        client_id: str,
        client_secret: str,
        username: str,
        password: str,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/realms/{realm}/protocol/openid-connect/token"
        data = {
            "grant_type": "password",
            "client_id": client_id,
            "client_secret": client_secret,
            "username": username,
            "password": password,
        }
        response = self.session.post(url, data=data, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def token_client_credentials(
        self, realm: str, client_id: str, client_secret: str
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/realms/{realm}/protocol/openid-connect/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        }
        response = self.session.post(url, data=data, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def set_admin_token(self, token: str) -> None:
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    # ---------- REALMS ----------
    def create_realm(self, realm: str, display_name: str = "") -> None:
        url = f"{self.admin_base}"
        payload = {"realm": realm, "enabled": True}
        if display_name:
            payload["displayName"] = display_name
        response = self.session.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()

    def list_realms(self) -> List[Dict[str, Any]]:
        response = self.session.get(self.admin_base, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    # ---------- CLIENTES ----------
    def create_client(self, client_id: str, **extra) -> str:
        """
        Devuelve el UUID del cliente creado.
        """
        url = f"{self.admin_base}/{self.realm}/clients"
        payload = {"clientId": client_id, "protocol": "openid-connect"}
        payload.update(extra)
        response = self.session.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        # obtener UUID por clientId
        client = self.get_client_by_client_id(client_id)
        return client["id"]

    def get_client_by_client_id(self, client_id: str) -> Dict[str, Any]:
        url = f"{self.admin_base}/{self.realm}/clients"
        response = self.session.get(
            url, params={"clientId": client_id}, timeout=self.timeout
        )
        response.raise_for_status()
        clients_list = response.json()
        if not clients_list:
            raise RuntimeError(f"clientId '{client_id}' no encontrado")
        return clients_list[0]

    def get_client_secret(self, client_uuid: str) -> str:
        url = (
            f"{self.admin_base}/{self.realm}/clients/"
            f"{client_uuid}/client-secret"
        )
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.json()["value"]

    # ---------- ROLES DE CLIENTE ----------
    def create_client_role(
        self, client_uuid: str, name: str, description: str = ""
    ) -> None:
        url = f"{self.admin_base}/{self.realm}/clients/{client_uuid}/roles"
        response = self.session.post(
            url,
            json={"name": name, "description": description},
            timeout=self.timeout,
        )
        response.raise_for_status()

    def get_client_role(
        self, client_uuid: str, role_name: str
    ) -> Dict[str, Any]:
        url = (
            f"{self.admin_base}/{self.realm}"
            f"/clients/{client_uuid}/roles/{role_name}"
        )
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    # ---------- USUARIOS ----------
    def create_user(self, username: str, **fields) -> str:
        url = f"{self.admin_base}/{self.realm}/users"
        payload = {"username": username, "enabled": True}
        payload.update(fields)
        response = self.session.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        # obtener id
        user = self.get_user_by_username(username)
        return user["id"]

    def get_user_by_username(
        self, username: str, exact: bool = False
    ) -> Dict[str, Any]:
        url = f"{self.admin_base}/{self.realm}/users"
        params = {"username": username}
        if exact:
            params["exact"] = "true"
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        users_list = response.json()
        if not users_list:
            raise RuntimeError(f"Usuario '{username}' no encontrado")
        return users_list[0]

    def reset_user_password(
        self, user_id: str, value: str, temporary: bool = False
    ) -> None:
        url = f"{self.admin_base}/{self.realm}/users/{user_id}/reset-password"
        payload = {"type": "password", "value": value, "temporary": temporary}
        response = self.session.put(url, json=payload, timeout=self.timeout)
        response.raise_for_status()

    # ---------- GRUPOS ----------
    def create_group(
        self, name: str, attributes: Optional[Dict[str, List[str]]] = None
    ) -> str:
        url = f"{self.admin_base}/{self.realm}/groups"
        payload: Dict[str, Any] = {"name": name}
        if attributes:
            payload["attributes"] = attributes
        response = self.session.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        group = self.get_group_by_name(name)
        return group["id"]

    def get_group_by_name(self, name: str) -> Dict[str, Any]:
        url = f"{self.admin_base}/{self.realm}/groups"
        response = self.session.get(
            url, params={"search": name}, timeout=self.timeout
        )
        response.raise_for_status()
        groups_list = response.json()
        if not groups_list:
            raise RuntimeError(f"Grupo '{name}' no encontrado")
        return groups_list[0]

    def add_user_to_group(self, user_id: str, group_id: str) -> None:
        url = (
            f"{self.admin_base}/{self.realm}/users/{user_id}/groups/{group_id}"
        )
        response = self.session.put(url, timeout=self.timeout)
        response.raise_for_status()

    # ---------- ROLE-MAPPINGS ----------
    def assign_client_role_to_user(
        self, user_id: str, client_uuid: str, role_id: str, role_name: str
    ) -> None:
        url = (
            f"{self.admin_base}/{self.realm}/users/{user_id}"
            f"/role-mappings/clients/{client_uuid}"
        )
        body = [
            {
                "id": role_id,
                "name": role_name,
                "clientRole": True,
                "containerId": client_uuid,
            }
        ]
        response = self.session.post(url, json=body, timeout=self.timeout)
        response.raise_for_status()

    def assign_client_role_to_group(
        self, group_id: str, client_uuid: str, role_id: str, role_name: str
    ) -> None:
        url = (
            f"{self.admin_base}/{self.realm}/groups/{group_id}"
            f"/role-mappings/clients/{client_uuid}"
        )
        body = [
            {
                "id": role_id,
                "name": role_name,
                "clientRole": True,
                "containerId": client_uuid,
            }
        ]
        response = self.session.post(url, json=body, timeout=self.timeout)
        response.raise_for_status()
        # Role-mappings de grupo/cliente. :contentReference[oaicite:4]{index=4}

    # ---------- CLIENT SCOPES & PROTOCOL MAPPERS ----------
    def create_client_scope(self, name: str, description: str = "") -> str:
        url = f"{self.admin_base}/{self.realm}/client-scopes"
        body = {"name": name, "protocol": "openid-connect"}
        if description:
            body["description"] = description
        response = self.session.post(url, json=body, timeout=self.timeout)
        response.raise_for_status()
        # obtener id
        scope_id = self.get_client_scope_id_by_name(name)
        return scope_id

    def get_client_scope_id_by_name(self, name: str) -> str:
        url = f"{self.admin_base}/{self.realm}/client-scopes"
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        for client_scope in response.json():
            if client_scope.get("name") == name:
                return client_scope["id"]
        raise RuntimeError(f"Client scope '{name}' no encontrado")

    def link_client_scope_default(
        self, client_uuid: str, scope_id: str
    ) -> None:
        url = (
            f"{self.admin_base}/{self.realm}/clients/{client_uuid}"
            f"/default-client-scopes/{scope_id}"
        )
        response = self.session.put(url, timeout=self.timeout)
        response.raise_for_status()

    # -- MAPPER: Audience (oidc-audience-mapper)
    def add_audience_mapper_to_client(
        self,
        client_uuid: str,
        included_client_audience: str,
        name: str = "audience",
    ) -> str:
        url = (
            f"{self.admin_base}/{self.realm}/clients/"
            f"{client_uuid}/protocol-mappers/models"
        )
        body = {
            "name": name,
            "protocol": "openid-connect",
            "protocolMapper": "oidc-audience-mapper",
            "config": {
                "included.client.audience": included_client_audience,
                "included.custom.audience": "",
                "access.token.claim": "true",
                "id.token.claim": "false",
            },
        }
        response = self.session.post(url, json=body, timeout=self.timeout)
        response.raise_for_status()
        return response.headers.get("Location", "")

    def add_audience_mapper_to_client_scope(
        self,
        scope_id: str,
        included_client_audience: str,
        name: str = "audience",
    ) -> str:
        url = (
            f"{self.admin_base}/{self.realm}/client-scopes/{scope_id}"
            f"/protocol-mappers/models"
        )
        body = {
            "name": name,
            "protocol": "openid-connect",
            "protocolMapper": "oidc-audience-mapper",
            "config": {
                "included.client.audience": included_client_audience,
                "included.custom.audience": "",
                "access.token.claim": "true",
                "id.token.claim": "false",
            },
        }
        response = self.session.post(url, json=body, timeout=self.timeout)
        response.raise_for_status()
        return response.headers.get("Location", "")

    # -- MAPPER: Group Membership (oidc-group-membership-mapper)
    def add_group_membership_mapper_to_client(
        self,
        client_uuid: str,
        claim_name: str = "groups",
        full_path: bool = False,
    ) -> str:
        url = (
            f"{self.admin_base}/{self.realm}/clients/{client_uuid}"
            f"/protocol-mappers/models"
        )
        body = {
            "name": claim_name,
            "protocol": "openid-connect",
            "protocolMapper": "oidc-group-membership-mapper",
            "config": {
                "claim.name": claim_name,
                "full.path": "true" if full_path else "false",
                "access.token.claim": "true",
                "id.token.claim": "false",
                "userinfo.token.claim": "false",
            },
        }
        response = self.session.post(url, json=body, timeout=self.timeout)
        response.raise_for_status()
        return response.headers.get("Location", "")