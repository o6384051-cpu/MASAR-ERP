# MASAR-ERP — Engineering Execution Plan

## Delivery commitment

This repository is currently a 0.1.0 Frappe app foundation, not a complete ERP product. The existing CI compiles Python and runs smoke/static-contract tests; it does not install ERPNext or execute accounting workflows.

Time is therefore split into two honest targets:

- **7 business days:** establish a reproducible ERPNext staging environment, install MASAR, configure a clearly marked test company, and demonstrate the critical accounting and inventory workflows using standard ERPNext features. This target depends on access to a suitable host and compatible MariaDB/Redis services.
- **15–20 business days:** target for a controlled pilot after the staging baseline, including security/integration tests, backup-and-restore proof, operational monitoring, and validated Egypt-specific configuration. This is not a promise of statutory e-invoicing certification; that depends on current official specifications, credentials, and external acceptance.

No production launch date is committed until the release gates below pass.

## Work sequence

### Gate 0 — Repository and dependency baseline
- Pin a supported, mutually compatible Frappe and ERPNext release.
- Define a reproducible bench/container build and lock Python/Node dependencies.
- Verify the app installs on a clean test site.
- Record the exact versions and migration procedure.

### Gate 1 — Staging platform
- Provision only infrastructure that is technically suitable for Frappe, MariaDB, Redis, background workers, scheduler, and persistent private files.
- Prefer free resources where viable; do not create paid resources without explicit approval.
- Configure secrets outside Git and enable TLS.
- Create a disposable test site and confirm health, queues, scheduler, and logs.

### Gate 2 — Core business configuration
- Configure Arabic language and RTL; test mobile and desktop layouts.
- Configure a test company, fiscal year, base currency, chart of accounts, warehouses, roles, and cost centers.
- Record all assumptions; do not invent tax rates, legal requirements, or production balances.

### Gate 3 — Critical business flows
- Verify journal entry creation, validation, submission, cancellation/reversal, and GL impact.
- Verify sales invoice, payment, purchase invoice, supplier payment, stock receipt/issue/transfer, and valuation.
- Reconcile subledgers to the general ledger and trial balance.
- Use ERPNext standard controllers and posting paths; never update ledger balances directly.

### Gate 4 — Security and data integrity
- Test role permissions, company isolation, API access, exports, reports, and private-file access with multiple users.
- Test duplicate submission/idempotency and concurrent updates where relevant.
- Review every privileged operation and every use of permission bypass flags.
- Verify audit trail and immutable correction paths for submitted financial documents.

### Gate 5 — Operational readiness
- Produce encrypted backups and perform a restore into a separate test site.
- Test migration/upgrade and rollback procedures.
- Verify monitoring, error logs, queue recovery, scheduler behavior, and incident runbook.
- Run dependency/security checks and resolve all critical/high findings.

### Gate 6 — Acceptance and release
- Execute documented end-to-end scenarios on staging with synthetic data.
- Require all mandatory checks to pass and attach evidence to the release.
- Obtain accounting-domain review for Egyptian chart/tax configuration.
- Keep production blocked until backup restore, security, accounting reconciliation, and user acceptance are signed off.

## Five-phase acceptance test matrix

Every item below starts as **NOT TESTED**. It may be marked PASS only when a reproducible test has run against the pinned Frappe/ERPNext staging environment and its evidence (test output, transaction IDs, report/export, or logs) is attached to the relevant change. Static source inspection alone is not runtime proof.

### Phase 1 — Business logic and workflow integration
- [ ] End-to-end purchasing cycle: Purchase Request → Purchase Order → Purchase Receipt → Purchase Invoice → submitted accounting ledger entries.
- [ ] Verify every submitted financial voucher balances: total debit equals total credit; verify currency precision, rounding, cancellation, and reversal behavior.
- [ ] Reconcile Accounts Payable, stock ledger/valuation, and General Ledger after the cycle.
- [ ] Verify stock quantities update correctly on receipt, issue, sale, return, and transfer.
- [ ] Verify negative stock is rejected by default; any exception must be explicitly configured, permission-gated, audited, and tested.
- [ ] Repeat equivalent sales and payment flows; test duplicate submission and idempotency.

### Phase 2 — Security and access control
- [ ] Build a role matrix for sales, purchasing, warehouse, accounting, HR, and senior management.
- [ ] Prove users cannot read or export unauthorized reports, salary data, accounting records, or another company's records through UI, API, list, report, print, or direct document access.
- [ ] Test server-side validation and parameterized query paths against SQL injection and unsafe input; escape output in rendered contexts.
- [ ] Verify password handling is delegated to Frappe's supported authentication mechanisms; never store plaintext passwords.
- [ ] Verify API keys, tokens, and secrets are not committed, logged, or returned to clients; rotate exposed secrets.
- [ ] Test private-file access by direct URL, not only by hiding links in the UI.
- [ ] Review every `ignore_permissions=True`, privileged endpoint, and permission-query override.

### Phase 3 — Performance and concurrency
- [ ] Capture baseline timings and query plans for trial balance, profit/loss, stock ledger, and large date-range reports on representative synthetic data.
- [ ] Add indexes only from measured query plans and validate migration cost and write impact.
- [ ] Run concurrent invoice, receipt, payment, and stock submissions; verify transaction isolation, locking, retry behavior, and absence of duplicate postings.
- [ ] Run sustained-use tests and inspect worker queues, memory, cache growth, database connections, and slow queries.
- [ ] Set explicit performance thresholds before testing; do not claim "fast" without measured results.

### Phase 4 — UI/UX and responsive field use
- [ ] Test critical workflows on supported desktop, tablet, and mobile viewport sizes.
- [ ] Verify Arabic RTL, tables, filters, dialogs, buttons, and validation messages do not overlap or disappear.
- [ ] Verify errors are actionable Arabic messages and do not expose stack traces or internal identifiers.
- [ ] Test keyboard navigation (Tab/Enter) and touch interactions on purchase, sales, and warehouse forms.
- [ ] Verify accessibility basics: labels, focus visibility, contrast, and usable control sizes.

### Phase 5 — Backup and production readiness
- [ ] Configure scheduled daily and weekly encrypted backups, including database and required private files/configuration.
- [ ] Store copies separately from the primary host with restricted access and retention policy.
- [ ] Restore a backup into a separate clean environment and verify counts, attachments, balances, and application health.
- [ ] Verify TLS, secure cookies, least-privilege secrets, environment separation, and production environment variables.
- [ ] Document and rehearse rollback for application release and database migrations; database rollback must use a verified backup/restore strategy, not merely code rollback.
- [ ] Verify monitoring, alerting, logs, queue/scheduler recovery, and an incident runbook.

## Evidence and status rules

- Status values: **NOT TESTED**, **PASS**, **FAIL**, or **BLOCKED**.
- A PASS requires the test command/scenario, environment and version, timestamp, result, and evidence reference.
- A BLOCKED item must name its dependency (for example, no staging host or no test credentials).
- Never replace a failed test with a weaker assertion just to make CI green.
- CI green is necessary but does not imply ERP workflow acceptance or production readiness.

## Mandatory release gates

A release is blocked if any of the following is true:
- Frappe/ERPNext versions are unpinned or the clean install is not reproducible.
- Accounting postings do not balance or subledgers do not reconcile.
- A user can access another company's records or another room's private files.
- Critical/high security findings remain unresolved.
- Backup restoration has not been demonstrated.
- Tests are static-only for a feature that requires runtime behavior.
- Egyptian tax/e-invoicing compliance is claimed without current authoritative requirements and successful integration evidence.

## Current known blockers

- No running Frappe/ERPNext staging site is connected to this repository.
- No approved production-grade hosting and persistent database/storage have been provisioned.
- Existing workflow is a lightweight Python compile/smoke check, not an ERP integration suite.
- Accounting, inventory, sales, purchasing, and Egyptian localization workflows have not yet been demonstrated in this repository.
- The current collaboration permission tests are static contracts; live Frappe authorization and private-file download tests remain outstanding.

## Change-control rules

- Work on feature branches; protect `main`.
- Never merge a change solely because static CI passes.
- Never deploy to production from an unverified branch.
- Preserve the independent `mohasaba` repository and all unrelated projects.
- Never create paid infrastructure without explicit user approval.
