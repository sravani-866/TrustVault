# TrustVault – Application Architecture

## 1. Overview

TrustVault is a Django-based secure document management application. It provides authenticated document uploads, owner-controlled sharing, permission revocation and audit logging.

## 2. Technology

- Python
- Django
- SQLite (development)
- Django ORM
- HTML

## 3. Application Modules

| Module | Responsibility |
|---|---|
| accounts | Custom user model and roles |
| documents | Upload, listing, sharing, permissions and downloads |
| audit | Activity logging |
| core | Login, dashboard and logout |
| config | Django project settings and URL configuration |

## 4. Database Design

### User

Custom Django user model.

- id
- username
- email
- password (stored using Django password hashing)
- role: ADMIN, OWNER or VIEWER
- is_active

### Document

Stores document metadata and private file references.

- id: UUID primary key
- owner: Foreign key to User
- title
- description
- file
- uploaded_at

### DocumentPermission

Stores document-specific user permissions.

- id
- document: Foreign key to Document
- user: Foreign key to User
- access_level: READ or EDIT
- granted_by: Foreign key to User
- is_active
- created_at

A unique database constraint prevents duplicate permission records for the same document and user.

### AuditLog

Records sensitive document activity.

- id
- actor: Foreign key to User
- document: Foreign key to Document
- action
- details: JSON data
- ip_address
- timestamp

Audit records are read-only through the Django Admin interface.

## 5. Main Application Routes

| Method | Route | Purpose |
|---|---|---|
| GET/POST | / | Login |
| GET | /dashboard/ | User dashboard |
| POST | /logout/ | Logout |
| GET/POST | /documents/upload/ | Upload document |
| GET | /documents/ | List and search accessible documents |
| GET | /documents/download/UUID/ | Authorized document download |
| GET/POST | /documents/share/UUID/ | Manage sharing |
| POST | /documents/revoke/UUID/ID/ | Revoke permission |

These are Django application routes, not a separate REST API.

## 6. Authorization Flow

1. User must authenticate before accessing document operations.
2. Only OWNER users can upload documents.
3. Owners can share their documents with active VIEWER users.
4. A user can list documents they own or have active permissions for.
5. A download is allowed only when the user owns the document or has an active permission.
6. Revocation sets the permission to inactive.
7. Every download request checks the current database permission.

## 7. Audit Events

The application records:

- DOCUMENT_UPLOADED
- DOCUMENT_DOWNLOADED
- DOCUMENT_SHARED
- ACCESS_REVOKED

Audit events include the actor, document, timestamp and available request IP address.

## 8. Private File Storage

Uploaded documents are stored under the private_media directory. Files are delivered through an authenticated Django view rather than public media URLs.

Uploads are restricted to PDF files with a maximum size of 5 MB. The application checks the file extension and PDF signature.

## 9. Security Limitations

This is a development implementation. Production use requires HTTPS, secure secret management, production database configuration, malware scanning, stronger file validation, private object storage and operational monitoring.