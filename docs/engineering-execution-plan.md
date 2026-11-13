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
