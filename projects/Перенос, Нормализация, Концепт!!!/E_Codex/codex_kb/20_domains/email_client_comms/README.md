# Domain: Email and Client Correspondence

## Role

Email is expected to become an input stream for:

- client correspondence;
- tender-related documents;
- quotes and commercial offers;
- attachments converted to tables;
- tasks in Bitrix;
- records or documents in 1C;
- future LLM-assisted analysis and drafts.

## Target architecture

```text
Mailbox
-> n8n email trigger / IMAP / Gmail / Outlook
-> filtering and classification
-> attachment extraction
-> parser
-> normalized data object
-> marketing_db / table / Bitrix / 1C / notification
```

For the current stage, 1C is read-only. New normalized correspondence and matching data must go to PostgreSQL `marketing_db`, not back into 1C.

## Parser stages

1. Deterministic extraction where possible:
   - sender;
   - subject;
   - dates;
   - attachments;
   - file names;
   - known XML/XLSX/CSV structures.
2. LLM parser for messy correspondence.
3. Human review for ambiguous business actions.
4. Write to downstream systems only after validation.

## Likely outputs

- Excel/Google Sheet table.
- `marketing_db.clients_intel` row or update.
- matched contact/lead/counterparty rows in `marketing_db`.
- Bitrix task.
- 1C object through OData.
- Draft reply.
- Tender/project folder.
- Error notification.

## Planned AI pipeline

From `master_doc.md`, the longer-term design is:

```text
Archive workflow
-> Triage workflow
-> Follow-up workflow
-> Feedback Loop
```

Meaning:

- Archive: store mail and match sender to 1C/client data.
- Matching must support email on the lead/counterparty itself and on individual contacts.
- Triage: classify seriousness, segment, and priority.
- Follow-up: generate draft replies with RAG and client history.
- Feedback Loop: watch replies and update client summary/status.

The generated reply stage should start as draft-only.

## Important future decisions

- Which mailbox or mailboxes are source of truth.
- IMAP vs Gmail/Outlook OAuth.
- Attachment retention policy.
- How to identify client/company.
- How to handle duplicate emails and threads.
- Whether to store parsed mail in a database.
- Whether `marketing_db` is already created or still needs SQL setup.
- Which RAG categories are safe and useful for mail drafting.

## Safety

- Do not let automation send client replies without review at first.
- Do not write to 1C automatically until read-only checks and dry-run are proven.
- Store original email/message ID for traceability.
