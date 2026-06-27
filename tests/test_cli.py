import json

from hotmail_cli import cli


class FakeAuthenticator:
    def __init__(self, access_token="token"):
        self.access_token = access_token

    def get_access_token(self):
        return self.access_token


class FakeGraphClient:
    def __init__(self, access_token):
        self.access_token = access_token

    def search_messages(self, search):
        return [{"id": "m1", "subject": search.subject, "top": search.top}]


def test_search_command_outputs_json(monkeypatch, capsys):
    monkeypatch.setattr(cli, "_authenticator", lambda args: FakeAuthenticator())
    monkeypatch.setattr(cli, "GraphClient", FakeGraphClient)

    exit_code = cli.main(["search", "--subject", "invoice", "--top", "3"])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload == [{"id": "m1", "subject": "invoice", "top": 3}]
