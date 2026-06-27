from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import msal


DEFAULT_AUTHORITY = "https://login.microsoftonline.com/consumers"
DEFAULT_SCOPES = ["https://graph.microsoft.com/Mail.Read"]
CLIENT_ID_ENV = "HOTMAIL_CLIENT_ID"


class TokenStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or default_token_path()

    def load(self) -> dict[str, Any] | None:
        if not self.path.exists():
            return None
        return json.loads(self.path.read_text())

    def save(self, token: dict[str, Any]) -> None:
        self.save_text(json.dumps(token, indent=2, sort_keys=True))

    def load_text(self) -> str | None:
        if not self.path.exists():
            return None
        return self.path.read_text()

    def save_text(self, value: str) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp_path.write_text(value)
        os.chmod(tmp_path, 0o600)
        tmp_path.replace(self.path)
        os.chmod(self.path, 0o600)


class DeviceCodeAuthenticator:
    def __init__(
        self,
        *,
        client_id: str | None = None,
        authority: str = DEFAULT_AUTHORITY,
        scopes: list[str] | None = None,
        store: TokenStore | None = None,
    ) -> None:
        self.client_id = client_id or os.environ.get(CLIENT_ID_ENV)
        if not self.client_id:
            raise RuntimeError(
                f"Missing Microsoft app client id. Pass --client-id or set {CLIENT_ID_ENV}."
            )
        self.authority = authority
        self.scopes = scopes or DEFAULT_SCOPES
        self.store = store or TokenStore()
        self.cache = msal.SerializableTokenCache()
        cached = self.store.load_text()
        if cached:
            self.cache.deserialize(cached)
        self.app = msal.PublicClientApplication(self.client_id, authority=authority, token_cache=self.cache)

    def get_access_token(self) -> str:
        accounts = self.app.get_accounts()
        if accounts:
            result = self.app.acquire_token_silent(self.scopes, account=accounts[0])
            if result and "access_token" in result:
                self._persist_cache()
                return result["access_token"]
        return self.login()["access_token"]

    def login(self) -> dict[str, Any]:
        flow = self.app.initiate_device_flow(scopes=self.scopes)
        if "user_code" not in flow:
            raise RuntimeError(f"Failed to create device flow: {flow}")
        print(flow["message"])
        result = self.app.acquire_token_by_device_flow(flow)
        if "access_token" not in result:
            error = result.get("error_description") or result
            raise RuntimeError(f"Microsoft login failed: {error}")
        self._persist_cache()
        return result

    def _persist_cache(self) -> None:
        if self.cache.has_state_changed:
            self.store.save_text(self.cache.serialize())


def default_token_path() -> Path:
    return Path.home() / ".hotmail-cli" / "token.json"
