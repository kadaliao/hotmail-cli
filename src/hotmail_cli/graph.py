from __future__ import annotations

import base64
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests


GRAPH_ROOT = "https://graph.microsoft.com/v1.0"


@dataclass(frozen=True)
class MessageSearch:
    subject: str | None = None
    sender: str | None = None
    since: str | None = None
    until: str | None = None
    top: int = 10


class GraphClient:
    def __init__(self, access_token: str, *, session: requests.Session | None = None) -> None:
        self.access_token = access_token
        self.session = session or requests.Session()

    def search_messages(self, search: MessageSearch) -> list[dict[str, Any]]:
        params = {
            "$top": str(search.top),
            "$select": "id,subject,receivedDateTime,from,hasAttachments,webLink",
        }
        if search.subject:
            params["$search"] = f'"subject:{search.subject}"'
        else:
            params["$orderby"] = "receivedDateTime desc"
        if not search.subject:
            filters = _build_filters(search)
            if filters:
                params["$filter"] = " and ".join(filters)
        response = self.session.get(
            f"{GRAPH_ROOT}/me/messages",
            headers=self._headers(),
            params=params,
        )
        response.raise_for_status()
        messages = response.json().get("value", [])
        if search.subject:
            messages = _filter_messages_locally(messages, search)
        return messages

    def get_message(self, message_id: str) -> dict[str, Any]:
        response = self.session.get(
            f"{GRAPH_ROOT}/me/messages/{message_id}",
            headers=self._headers(),
            params={"$select": "id,subject,receivedDateTime,from,body,hasAttachments,webLink"},
        )
        response.raise_for_status()
        return response.json()

    def list_attachments(self, message_id: str) -> list[dict[str, Any]]:
        response = self.session.get(
            f"{GRAPH_ROOT}/me/messages/{message_id}/attachments",
            headers=self._headers(),
        )
        response.raise_for_status()
        return response.json().get("value", [])

    def download_attachments(self, message_id: str, output_dir: Path) -> list[Path]:
        attachments = self.list_attachments(message_id)
        saved: list[Path] = []
        for attachment in attachments:
            if attachment.get("@odata.type") == "#microsoft.graph.fileAttachment":
                saved.append(self.save_attachment(attachment, output_dir))
        return saved

    @staticmethod
    def save_attachment(attachment: dict[str, Any], output_dir: Path) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = _safe_filename(attachment["name"])
        path = _unique_path(output_dir / filename)
        path.write_bytes(base64.b64decode(attachment["contentBytes"]))
        return path

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.access_token}"}


def _build_filters(search: MessageSearch) -> list[str]:
    filters: list[str] = []
    if search.sender:
        filters.append(f"from/emailAddress/address eq '{_odata_quote(search.sender)}'")
    if search.since:
        filters.append(f"receivedDateTime ge {search.since}T00:00:00Z")
    if search.until:
        filters.append(f"receivedDateTime le {search.until}T23:59:59Z")
    return filters


def _odata_quote(value: str) -> str:
    return value.replace("'", "''")


def _safe_filename(filename: str) -> str:
    cleaned = re.sub(r"[/\\:\0]", "_", filename).strip()
    return cleaned or "attachment"


def _unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    counter = 2
    while True:
        candidate = parent / f"{stem}-{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def _filter_messages_locally(messages: list[dict[str, Any]], search: MessageSearch) -> list[dict[str, Any]]:
    filtered = messages
    if search.sender:
        sender = search.sender.lower()
        filtered = [
            message
            for message in filtered
            if message.get("from", {}).get("emailAddress", {}).get("address", "").lower() == sender
        ]
    if search.since:
        lower = f"{search.since}T00:00:00Z"
        filtered = [message for message in filtered if message.get("receivedDateTime", "") >= lower]
    if search.until:
        upper = f"{search.until}T23:59:59Z"
        filtered = [message for message in filtered if message.get("receivedDateTime", "") <= upper]
    return filtered
