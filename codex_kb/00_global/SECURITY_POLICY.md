# Security Policy

Дата обновления: 2026-05-11

## Core Rule

Do not store live secrets in permanent project files.

This includes:

- passwords;
- API tokens;
- private keys;
- Bitrix webhook URLs with secrets;
- Google OAuth secrets;
- n8n encryption keys;
- WireGuard private keys;
- session cookies.

Permanent project files means:

- markdown;
- workflow JSON exported to disk;
- prompt files;
- progress files;
- knowledge base files;
- chat export artifacts;
- scripts committed to the workspace.

## Allowed In Chat / Interactive Setup

Live secrets may be passed to Codex in chat for a one-time setup, verification or troubleshooting step.

Rules:

- use them only for the current task;
- do not copy them into markdown, JSON, prompts, progress files or exported artifacts;
- when documenting the result, keep only credential names, placeholders and storage locations;
- prefer n8n Credentials, `.env`, protected config files or server-side secret storage for long-term use.

## Placeholder Format

Use placeholders in docs, commands, n8n examples and scripts:

```text
${BITRIX_WEBHOOK_BASE_URL}
${ONEC_ODATA_USER}
${ONEC_ODATA_PASSWORD}
${GOOGLE_OAUTH_CLIENT_SECRET}
${N8N_ENCRYPTION_KEY}
${N8N_BASIC_AUTH_PASSWORD}
${WIREGUARD_PRIVATE_KEY}
${SMTP_PASSWORD}
```

## Safe to Document

- Domain names.
- Public endpoints without embedded secrets.
- Service names.
- File paths.
- Credential names.
- Where a secret is stored, without the secret value.
- That a live secret was provided in chat for a one-time step, without the secret value itself.

## n8n

- Store credentials in n8n credentials storage.
- Markdown may describe credential names and required fields.
- Workflow examples must use placeholders.

## VPS

- Do not paste root passwords or SSH private keys.
- Do not store full provider panel credentials.
- Use placeholders in shell commands.

## 1C

- Use a dedicated 1C user for automation, for example `${ONEC_ODATA_USER}`.
- Do not store `${ONEC_ODATA_PASSWORD}` in markdown.
- Do not grant permanent full admin rights to automation users unless explicitly approved.

## File Encoding

- Markdown files with Cyrillic must be saved as UTF-8 with BOM.
- If PowerShell displays mojibake, fix encoding before adding more content.
