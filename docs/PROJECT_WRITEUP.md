# TrustVault — Secure Document Management

## 1. Project Overview

TrustVault is a Django-based secure document management application developed for the Snovasys RISE 2026 challenge.

It allows users to upload, organize, search, download and share documents while enforcing role-based and document-level access permissions on the server.

The main objective is to prevent unauthorized document access and maintain an audit trail of important document activities.

## 2. Problem Statement

Sharing and storing documents without proper access controls can expose confidential information to unauthorized users.

Applications that rely only on frontend restrictions or basic authentication may allow users to access documents through direct URLs or unauthorized requests.

TrustVault addresses these risks through server-side authorization, document ownership checks, explicit permissions and activity logging.

## 3. Solution and Key Features

TrustVault provides the following functionality:

- User authentication with ADMIN, OWNER and VIEWER roles.
- PDF document upload with file-type validation and a maximum file size of 5 MB.
- Document listing, editing, downloading and deletion.
- Document search and filtering by name, owner, category and date.
- Document-level READ and EDIT permissions.
- Owners can grant and revoke access to eligible users.
- Server-side authorization for protected document operations.
- Audit events for document uploads, downloads, edits, deletions and permission changes.
- Logging of implemented denied-access attempts.
- An administrative interface for reviewing audit activity.

## 4. User Roles and Permissions

### ADMIN
- Can access the administrative interface according to Django admin permissions.
- Can upload documents where permitted by the application role checks.
- Does not automatically receive ownership or document-level access to every user's document.

### OWNER
- Can upload and manage owned documents.
- Can download, edit and delete owned documents.
- Can grant READ or EDIT permissions to eligible users.
- Can revoke previously granted document permissions.

### VIEWER
- Can view documents actively shared with them.
- Can download documents with active READ or EDIT permission.
- Cannot edit documents with READ permission.
- Cannot share, revoke or delete another user's documents.

### Document Permission Levels

- READ: Allows document download.
- EDIT: Allows document download and editing.
- OWNER: Retains ownership-based management and sharing capabilities.

## 5. Security and Authorization Model

TrustVault uses Django session-based authentication and server-side authorization.

For protected document operations, the application checks whether the current user owns the document or has the required active permission.

Important security measures include:

- Authentication is required for protected document endpoints.
- Document ownership and permission checks are performed on the server.
- Direct URL access does not bypass authorization checks.
- Only document owners can share, revoke access or delete their documents.
- READ and EDIT permissions are checked separately.
- Revoked permissions are no longer accepted by subsequent authorization checks.
- PDF upload validation checks the accepted file type and 5 MB size limit.
- Django CSRF protection is used for browser form submissions.
- Sensitive document operations are restricted to the appropriate HTTP methods.

## 6. Audit Logging and Limitations

TrustVault records audit events for implemented document and permission operations.

Audit records include available information such as:

- Actor
- Document
- Action
- Event details
- IP address
- Timestamp

The application records successful operations and implemented denied-access attempts, including denied document upload, download, edit, delete, share and revoke attempts.

Audit logs are available through the Django admin interface. Admin restrictions make audit records read-only through the normal admin interface. Model-level protections also prevent ordinary instance-level modification and deletion.

However, direct database access and privileged bulk database operations are not prevented by these application-level protections. Therefore, TrustVault does not claim absolute database-level tamper-proofing. This is an accepted limitation documented in THREATS.md.

## 7. Data Consistency

TrustVault uses Django ORM and database transactions in relevant document operations to help maintain consistency when related database changes are performed.

Permission checks are performed when protected operations are requested. Revoked permissions are therefore rejected by subsequent authorization checks.

The application does not claim a separate distributed concurrency-control architecture or immutable database-level audit storage.

## 8. Technology Stack

- **Programming Language:** Python
- **Web Framework:** Django
- **Authentication:** Django session-based authentication
- **Database:** SQLite for local testing and PostgreSQL for production configuration
- **Frontend:** HTML templates and CSS
- **Version Control:** Git and GitHub
- **Deployment:** Render

## 9. Testing and Verification

The latest confirmed local automated test run completed with 25 tests passing.

The Django system check also completed without errors.

The automated tests cover areas including:

- Document access authorization.
- Owner and viewer permissions.
- Document sharing and revocation.
- Unauthorized document operations.
- Search and category filtering.
- Audit event behavior.
- Audit-log instance-level modification and deletion protections.

The application was also deployed to Render, and the live deployment was confirmed as operational during development.

## 10. AI Usage and Human Verification

AI assistance was used during development for Django implementation guidance, authorization logic, audit logging, test development, debugging and documentation.

AI-generated suggestions were reviewed and tested rather than accepted without verification.

Development work included reviewing document ownership and permission checks, correcting authorization-related implementation issues, improving audit logging and adding tests for denied operations.

The prompts and AI-assisted development activities are documented in PROMPTS.md. The Git commit history provides a record of incremental project changes.

## 11. What Was Deliberately Not Built

TrustVault focuses on secure document management, document-level permissions and auditability.

Features outside the challenge's core scope were deliberately not included, such as:

- Payment processing.
- Real-time collaborative document editing.
- Advanced workflow automation.
- AI-powered document analysis.
- Distributed storage infrastructure.

These features were excluded to keep development focused on the challenge's primary security and document-management requirements.

## 12. Known Limitations and Future Improvements

- Audit records are protected through application-level restrictions, but privileged database or bulk-query modifications remain possible.
- The application has not undergone an independent professional security audit.
- Additional independent penetration testing may identify further security issues.
- Further user-interface and usability improvements may be made.
- Additional monitoring and stronger database-level audit protection could be considered in future versions.

These limitations are stated transparently rather than claiming security guarantees that have not been independently verified.

## 13. Deployment and Repository

**Live Application:**

https://trustvault-8nap.onrender.com

**Public GitHub Repository:**

https://github.com/sravani-866/TrustVault

The repository includes:

- README.md
- THREATS.md
- PROMPTS.md
- docs/ARCHITECTURE.md
- docs/API.md
- Django application source code
- Database migrations
- Automated tests

## 14. Conclusion

TrustVault demonstrates how secure document management can combine authentication, role-based capabilities, document-level permissions, controlled sharing, server-side authorization and audit logging.

The project focuses on preventing unauthorized document access, enforcing permission revocation and making important document activities reviewable.

It was developed for the Snovasys RISE 2026 challenge with an emphasis on practical security controls, automated testing and transparent documentation.