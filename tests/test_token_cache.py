import json

import pytest

from hotmail_cli import auth
from hotmail_cli.auth import TokenStore


def test_token_store_writes_private_json_file(tmp_path):
    path = tmp_path / "token.json"
    store = TokenStore(path)

    store.save({"access_token": "abc", "refresh_token": "def"})

    assert json.loads(path.read_text())["access_token"] == "abc"
    assert oct(path.stat().st_mode & 0o777) == "0o600"


def test_authenticator_requires_client_id(monkeypatch, tmp_path):
    monkeypatch.delenv(auth.CLIENT_ID_ENV, raising=False)

    with pytest.raises(RuntimeError, match="client id"):
        auth.DeviceCodeAuthenticator(store=TokenStore(tmp_path / "token.json"))
