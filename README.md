# Hotmail CLI

A local CLI for reading Hotmail/Outlook messages and downloading attachments through Microsoft Graph.

## Features

- Sign in with Microsoft device code flow.
- Search messages by subject keyword.
- Filter results by sender and date range locally.
- Fetch message details by id.
- Download file attachments to a local directory.

The CLI requests Microsoft Graph `Mail.Read` only. It does not ask for mailbox write/delete permissions.

## Setup

```bash
UV_CACHE_DIR=.uv-cache uv sync
```

## Microsoft App Registration

Create a Microsoft Entra app registration for a public/native client:

1. Go to **Microsoft Entra admin center** -> **App registrations** -> **New registration**.
2. Set a display name such as `hotmail-cli`.
3. Choose **Personal Microsoft accounts only** if you only need Hotmail/Outlook consumer accounts.
4. Leave redirect URI empty for device code flow.
5. After creation, open **Authentication** -> **Settings** and enable **Allow public client flows**.
6. Copy the **Application (client) ID**.

## Authentication

```bash
export HOTMAIL_CLIENT_ID="your Microsoft app client id"
UV_CACHE_DIR=.uv-cache uv run hotmail auth
```

The command prints a Microsoft device code flow URL and code. After you sign in and approve access, the token cache is saved to:

```text
~/.hotmail-cli/token.json
```

The file is written with `0600` permissions.

You can also pass the client id directly:

```bash
UV_CACHE_DIR=.uv-cache uv run hotmail --client-id "your Microsoft app client id" auth
```

## Search Messages

```bash
UV_CACHE_DIR=.uv-cache uv run hotmail search \
  --subject "invoice" \
  --sender "billing@example.com" \
  --since 2026-06-01 \
  --until 2026-06-27 \
  --top 10
```

Or search by subject only:

```bash
UV_CACHE_DIR=.uv-cache uv run hotmail search --subject "statement" --top 5
```

The output is Microsoft Graph message JSON. Use the returned `id` to fetch details or download attachments.

Microsoft Graph message `$search` cannot be reliably combined with `$filter`/`$orderby`, so the CLI uses server-side subject search first and then applies sender/date filters locally.

## Fetch Message Details

```bash
UV_CACHE_DIR=.uv-cache uv run hotmail fetch MESSAGE_ID
```

## Download Attachments

```bash
UV_CACHE_DIR=.uv-cache uv run hotmail attachments MESSAGE_ID --output-dir downloads
```

Only Microsoft Graph `fileAttachment` items are saved.

## Development

```bash
UV_CACHE_DIR=.uv-cache uv run pytest
```

