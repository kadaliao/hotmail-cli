from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .auth import DeviceCodeAuthenticator, TokenStore
from .graph import GraphClient, MessageSearch


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "auth":
        authenticator = _authenticator(args)
        token = authenticator.login()
        print(json.dumps({"token_type": token.get("token_type"), "expires_in": token.get("expires_in")}))
        return 0

    client = GraphClient(_authenticator(args).get_access_token())

    if args.command == "search":
        messages = client.search_messages(
            MessageSearch(
                subject=args.subject,
                sender=args.sender,
                since=args.since,
                until=args.until,
                top=args.top,
            )
        )
        print(json.dumps(messages, ensure_ascii=False, indent=2))
        return 0

    if args.command == "fetch":
        message = client.get_message(args.message_id)
        print(json.dumps(message, ensure_ascii=False, indent=2))
        return 0

    if args.command == "attachments":
        saved = client.download_attachments(args.message_id, Path(args.output_dir))
        print(json.dumps([str(path) for path in saved], ensure_ascii=False, indent=2))
        return 0

    parser.error("missing command")
    return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hotmail", description="Fetch Hotmail/Outlook mail via Microsoft Graph.")
    parser.add_argument("--token-file", help="Token cache path. Defaults to ~/.hotmail-cli/token.json.")
    parser.add_argument("--client-id", help="Microsoft app client id. Or set HOTMAIL_CLIENT_ID.")

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("auth", help="Sign in with Microsoft device code flow.")

    search = subparsers.add_parser("search", help="Search messages.")
    search.add_argument("--subject", help="Subject keyword.")
    search.add_argument("--sender", help="Sender email address.")
    search.add_argument("--since", help="Start date in YYYY-MM-DD.")
    search.add_argument("--until", help="End date in YYYY-MM-DD.")
    search.add_argument("--top", type=int, default=10, help="Maximum messages to return.")

    fetch = subparsers.add_parser("fetch", help="Fetch one message by id.")
    fetch.add_argument("message_id")

    attachments = subparsers.add_parser("attachments", help="Download file attachments for one message.")
    attachments.add_argument("message_id")
    attachments.add_argument("--output-dir", default="downloads")

    return parser


def _authenticator(args: argparse.Namespace) -> DeviceCodeAuthenticator:
    token_path = Path(args.token_file).expanduser() if args.token_file else None
    return DeviceCodeAuthenticator(client_id=args.client_id, store=TokenStore(token_path))


if __name__ == "__main__":
    raise SystemExit(main())
