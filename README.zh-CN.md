# Hotmail CLI

一个小型只读命令行工具，用于读取 Hotmail 和 Outlook.com 邮箱。它通过 Microsoft Graph 搜索邮件，并下载邮件里的文件附件。

English documentation: [README.md](README.md)

## 为什么用它

- 支持 Hotmail、Outlook.com 等个人 Microsoft 账号。
- 使用 Microsoft device code 登录，CLI 不会接触你的密码。
- 只申请 `Mail.Read` 权限。
- 可以下载匹配邮件里的附件。
- OAuth token 保存在本地，并使用 `0600` 文件权限。

这个工具刻意保持窄范围。它不会发邮件、删除邮件、标记已读，也不会管理日历。

## 安装

```bash
uvx hotmail-cli --help
```

或者安装到本地工具环境：

```bash
uv tool install hotmail-cli
hotmail --help
```

## 创建 Microsoft 应用

你需要创建一个自己的 Microsoft Entra app registration。这个过程免费，也能让 Microsoft 明确展示 CLI 被授权访问哪些内容。

1. 打开 [Microsoft Entra admin center](https://entra.microsoft.com/)。
2. 进入 **App registrations** -> **New registration**。
3. 名称可以填 `hotmail-cli`，也可以用你自己的名称。
4. **Supported account types** 选择 **Personal Microsoft accounts only**。
5. **Redirect URI** 留空。
6. 创建应用。
7. 打开 **Authentication** -> **Settings**。
8. 启用 **Allow public client flows** 并保存。
9. 复制 **Application (client) ID**。

## 登录授权

```bash
export HOTMAIL_CLIENT_ID="你的 Microsoft app client id"
hotmail auth
```

命令会输出一个 URL 和验证码。用浏览器打开 URL，输入验证码，登录 Microsoft，并批准 `Mail.Read` 权限。

token 缓存会保存到：

```text
~/.hotmail-cli/token.json
```

也可以直接传入 client id：

```bash
hotmail --client-id "你的 Microsoft app client id" auth
```

## 搜索邮件

按主题搜索：

```bash
hotmail search --subject "statement" --top 10
```

按主题、发件人和日期范围搜索：

```bash
hotmail search \
  --subject "invoice" \
  --sender "billing@example.com" \
  --since 2026-06-01 \
  --until 2026-06-27 \
  --top 10
```

输出是 Microsoft Graph message JSON。每封邮件都有一个 `id`，可以继续用于 `fetch` 和 `attachments` 命令。

Microsoft Graph 的邮件 `$search` 不能稳定地和 `$filter` 或 `$orderby` 混用，所以 Hotmail CLI 会先在服务端按主题搜索，再在本地按发件人和日期过滤。

## 获取单封邮件

```bash
hotmail fetch MESSAGE_ID
```

## 下载附件

```bash
hotmail attachments MESSAGE_ID --output-dir downloads
```

当前只保存 Microsoft Graph 的 `fileAttachment`。内联附件和引用附件会被忽略。

## 本地开发

```bash
uv sync
uv run pytest
uv run hotmail --help
```

构建包：

```bash
uv build
```

## 安全说明

- 不要提交 `~/.hotmail-cli/token.json`。
- 不要公开分享邮件 ID 或下载的附件。
- 可以随时在 Microsoft 账号安全页面或 app registration 中撤销访问。

## License

MIT

