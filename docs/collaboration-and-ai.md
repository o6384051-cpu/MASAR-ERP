# MASAR ERP — Internal Collaboration and AI

## Approved product scope
- Private one-to-one and department/group conversations.
- Membership-based room access checked on every server request.
- Message history with pagination and realtime notifications.
- Private file attachments linked to messages.
- Printable conversation transcripts and printable ERP documents.
- Arabic-first interface and RTL support.
- AI assistant for explanations, summaries and reporting assistance, subject to the signed-in user permissions.

## Security rules
1. Never make chat messages or rooms globally readable.
2. Every message read/write must validate room membership on the server.
3. Uploaded files must be private and inherit the parent message access policy.
4. Never put provider keys in Git, browser JavaScript, or chat messages.
5. AI must not perform journal-entry, payment, stock, payroll, or other financial mutations autonomously.
6. AI context must be permission-filtered and minimized; sensitive company data is not sent to a provider unless an administrator explicitly configures and approves that integration.
7. Record access and administrative actions; apply retention and backup policies before production.

## Current implementation boundary
The first backend API scaffold is in masar_erp/collaboration.py. It provides membership-checked room listing, message creation, history retrieval, and a printable transcript payload. The AI endpoint in masar_erp/ai_assistant.py is intentionally fail-closed until a provider, model, endpoint, privacy terms, and server-side secret configuration are approved and tested.

This is a development scaffold, not a deployed chat service. Do not claim file upload, realtime UI, or PDF printing is production-ready until the DocTypes, private-file permission checks, browser interface, and integration tests are complete.
