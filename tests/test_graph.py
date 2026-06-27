import base64
from pathlib import Path

from hotmail_cli.graph import GraphClient, MessageSearch


class FakeSession:
    def __init__(self):
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return FakeResponse(
            {
                "value": [
                    {
                        "id": "m1",
                        "subject": "Monthly Statement",
                        "receivedDateTime": "2026-06-26T10:00:00Z",
                        "from": {"emailAddress": {"address": "noreply@example.com"}},
                        "hasAttachments": True,
                    }
                ]
            }
        )


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_search_messages_builds_graph_filter_and_select():
    session = FakeSession()
    client = GraphClient("token", session=session)

    messages = client.search_messages(
        MessageSearch(
            subject="Statement",
            sender="noreply@example.com",
            since="2026-06-01",
            until="2026-06-27",
            top=5,
        )
    )

    assert messages[0]["id"] == "m1"
    url, kwargs = session.calls[0]
    assert url == "https://graph.microsoft.com/v1.0/me/messages"
    assert kwargs["headers"]["Authorization"] == "Bearer token"
    assert kwargs["params"]["$top"] == "5"
    assert kwargs["params"]["$search"] == '"subject:Statement"'
    assert "$filter" not in kwargs["params"]
    assert "subject" in kwargs["params"]["$select"]
    assert messages[0]["from"]["emailAddress"]["address"] == "noreply@example.com"


def test_search_messages_uses_graph_search_for_subject_only():
    session = FakeSession()
    client = GraphClient("token", session=session)

    client.search_messages(MessageSearch(subject="invoice", top=5))

    _, kwargs = session.calls[0]
    assert kwargs["params"]["$search"] == '"subject:invoice"'
    assert "$filter" not in kwargs["params"]
    assert "$orderby" not in kwargs["params"]


def test_download_file_attachments_writes_base64_content(tmp_path: Path):
    attachment = {
        "@odata.type": "#microsoft.graph.fileAttachment",
        "name": "statement.pdf",
        "contentBytes": base64.b64encode(b"pdf bytes").decode("ascii"),
    }

    saved = GraphClient.save_attachment(attachment, tmp_path)

    assert saved == tmp_path / "statement.pdf"
    assert saved.read_bytes() == b"pdf bytes"
