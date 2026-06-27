# Hotmail CLI

A small read-only CLI for Hotmail and Outlook.com mailboxes. It uses Microsoft Graph to search messages and download file attachments from your mailbox.

中文文档: [README.zh-CN.md](https://github.com/kadaliao/hotmail-cli/blob/main/README.zh-CN.md)

## Why Use This

- Works with personal Microsoft accounts such as Hotmail and Outlook.com.
- Uses Microsoft device code login, so the CLI never sees your password.
- Requests only `Mail.Read`.
- Downloads attachments from matching messages.
- Stores the OAuth token locally with `0600` file permissions.

This tool is intentionally narrow. It does not send email, delete messages, mark messages, or manage calendars.

## Installation

```bash
uvx hotmail-cli --help
```

Or install it into an environment:

```bash
uv tool install hotmail-cli
hotmail --help
```

## Microsoft App Setup

You need your own Microsoft Entra app registration. This is free and lets Microsoft show you exactly what the CLI is allowed to access.

1. Open the [Microsoft Entra admin center](https://entra.microsoft.com/).
2. Go to **App registrations** -> **New registration**.
3. Name it `hotmail-cli` or any name you prefer.
4. For **Supported account types**, choose **Personal Microsoft accounts only** for Hotmail/Outlook.com.
5. Leave **Redirect URI** empty.
6. Create the app.
7. Open **Authentication** -> **Settings**.
8. Enable **Allow public client flows** and save.
9. Copy the **Application (client) ID**.

## Sign In

```bash
export HOTMAIL_CLIENT_ID="your Microsoft app client id"
hotmail auth
```

The command prints a URL and code. Open the URL in your browser, enter the code, sign in to Microsoft, and approve the requested `Mail.Read` access.

The token cache is saved to:

```text
~/.hotmail-cli/token.json
```

You can also pass the client id directly:

```bash
hotmail --client-id "your Microsoft app client id" auth
```

## Search Messages

Search by subject:

```bash
hotmail search --subject "statement" --top 10
```

Search by subject, sender, and date range:

```bash
hotmail search \
  --subject "invoice" \
  --sender "billing@example.com" \
  --since 2026-06-01 \
  --until 2026-06-27 \
  --top 10
```

The output is Microsoft Graph message JSON. Each message includes an `id` that can be used with `fetch` and `attachments`.

Microsoft Graph message `$search` cannot be reliably combined with `$filter` or `$orderby`, so Hotmail CLI searches by subject server-side first, then applies sender and date filters locally.

## Fetch One Message

```bash
hotmail fetch MESSAGE_ID
```

## Download Attachments

```bash
hotmail attachments MESSAGE_ID --output-dir downloads
```

Only Microsoft Graph `fileAttachment` items are saved. Inline items and reference attachments are ignored.

## Local Development

```bash
uv sync
uv run pytest
uv run hotmail --help
```

Build the package:

```bash
uv build
```

## Security Notes

- Do not commit `~/.hotmail-cli/token.json`.
- Do not share message IDs or downloaded attachments publicly.
- Revoke access anytime from your Microsoft account security page or from the app registration.

## License

MIT
