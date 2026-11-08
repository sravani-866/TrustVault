# TrustVault – AI Usage Journal

This journal records how AI assistance was used during the development of TrustVault. All prompts and outcomes below reflect actual project work.

## Entry 1 – Django Project Setup

**Date:** 2026-11-07

**Prompt:** Guide me step by step to create a Django project with a custom user model and separate applications for accounts, documents, audit and core.

**Purpose:** Establish the project structure and authentication foundation.

**Outcome:** Created the Django project, configured the custom user model and registered the required applications.

## Entry 2 – Role-Based Access Control

**Date:** 2026-11-07

**Prompt:** Help implement Admin, Owner and Viewer roles. Ensure document operations are restricted according to the user's role.

**Purpose:** Prevent unauthorized users from performing privileged actions.

**Outcome:** Implemented role-based users and server-side restrictions on document uploads.

## Entry 3 – Document Authorization and IDOR Prevention

**Date:** 2026-11-07

**Prompt:** Implement secure document sharing and downloading. A user should download a document only if they own it or have an active permission. Prevent unauthorized access by changing document IDs.

**Purpose:** Address insecure direct object reference (IDOR) and unauthorized document access.

**Outcome:** Implemented ownership and active-permission checks on document download requests. Tested unauthorized access and received HTTP 403.

## Entry 4 – Permission Grant and Revocation

**Date:** 2026-11-07

**Prompt:** Implement owner-controlled document permissions with READ and EDIT levels. Allow owners to revoke access and ensure revoked users cannot download documents.

**Purpose:** Enforce least privilege and immediate permission revocation.

**Outcome:** Implemented sharing and revocation workflows. Verified that a viewer could no longer download a document after revocation.

## Entry 5 – Audit Trail

**Date:** 2026-11-07

**Prompt:** Add audit logging for document uploads, downloads, sharing, permission revocation and document editing. Make audit records read-only in Django Admin.

**Purpose:** Improve accountability and provide visibility into sensitive document activity.

**Outcome:** Created an audit log model and activity-recording service. Restricted adding, changing and deleting audit records through Django Admin.

## Entry 6 – Security Testing and Troubleshooting

**Date:** 2026-11-07

**Prompt:** Create automated tests for authorized downloads, unauthorized downloads, shared access, revoked access, viewer upload restrictions and audit logging.

**Purpose:** Verify important security controls through repeatable tests.

**Outcome:** Fixed Windows temporary-file cleanup issues in tests and successfully ran document security tests. Additional security and audit tests were added during development.

## Responsible AI Usage

- AI assistance was used for implementation guidance, debugging, test design and documentation.
- Code was tested locally in the Django development environment.
- Security behavior was manually verified using separate Owner and Viewer accounts.
- AI-generated suggestions were reviewed and tested before being accepted.
- The project is a development-stage implementation and has not been independently security audited.