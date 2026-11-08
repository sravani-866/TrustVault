# TrustVault API and Endpoint Permissions

## 1. Overview

TrustVault is a Django-based secure document management application.

The application uses Django session-based authentication. All document endpoints require an authenticated user unless stated otherwise.

**Base URL:** `/`

## 2. Authentication

| Endpoint | Method | Access | Description |
|---|---|---|---|
| `/` | GET | Public | Display login page |
| `/` | POST | Public | Authenticate user |
| `/dashboard/` | GET | Authenticated users | Display dashboard |
| `/logout/` | POST | Any session | Log out the current session |

Invalid login credentials display an error message.

Logout is accepted only through POST.

## 3. Document Endpoints

| Endpoint | Method | Required permission | Description |
|---|---|---|---|
| `/documents/` | GET | Authenticated user | List owned and actively shared documents |
| `/documents/upload/` | GET, POST | ADMIN or OWNER | Display upload form and upload a document |
| `/documents/download/<document_id>/` | GET | Owner or active READ/EDIT permission | Download a document |
| `/documents/edit/<document_id>/` | GET, POST | Owner or active EDIT permission | Edit document details or file |
| `/documents/delete/<document_id>/` | POST | Document owner | Delete a document |
| `/documents/share/<document_id>/` | GET, POST | Document owner | Grant or manage document permissions |
| `/documents/revoke/<document_id>/<permission_id>/` | POST | Document owner | Revoke a user's document access |

`<document_id>` is a UUID. `<permission_id>` is an integer.

## 4. Role and Permission Rules

### ADMIN
- Can upload documents.
- Can access authenticated application pages.
- Document ownership or explicit permission is still required for document operations.

### OWNER
- Can upload documents.
- Can list and download owned documents.
- Can edit and delete owned documents.
- Can grant READ or EDIT access to eligible VIEWER accounts.
- Can revoke previously granted access.

### VIEWER
- Can list documents actively shared with them.
- Can download documents with active READ or EDIT permission.
- Cannot upload, share, revoke, edit with READ permission, or delete another user's document.

### Permission levels

| Permission | Download | Edit | Delete | Share |
|---|---|---|---|---|
| READ | Yes | No | No | No |
| EDIT | Yes | Yes | No | No |
| OWNER | Yes | Yes | Yes | Yes |

Permissions apply only while the corresponding document permission is active.

## 5. Authorization and Security

- Login is required for all document endpoints.
- Authorization is checked on the server side.
- Document access is restricted to the owner or users with active permissions.
- Only owners can share or revoke access.
- Only owners can delete their documents.
- Revoked permissions no longer authorize document access.
- Unauthorized document operations return HTTP 403 and create an `ACCESS_DENIED` audit event where implemented.
- Missing document or permission records return HTTP 404.
- Django session authentication and CSRF protection are used for browser form submissions.
- Revoke and delete operations require POST requests.

## 6. Audit Logging

The application records audit events for implemented operations, including:

- Document uploads
- Document downloads
- Document edits
- Document deletions
- Permission grants
- Permission revocations
- Denied upload, download, edit, delete, share, and revoke attempts

Audit records include available actor, document, action, details, IP address, and timestamp information.

Audit logs are available through the application's Django admin interface to authorized administrators. There is no separate public audit API endpoint.

## 7. Document Upload Validation

Document uploads are validated by the application form.

- Accepted file type: PDF
- Maximum file size: 5 MB

Invalid uploads are rejected by form validation.

## 8. HTTP Response Behavior

| Status | Meaning |
|---|---|
| 200 | Request completed successfully |
| 302 | Redirect after login, logout, or successful form operation |
| 403 | Authenticated user is not authorized |
| 404 | Requested document or permission does not exist |

## 9. Important Notes

- These are browser-facing Django routes, not a separate REST API.
- Most successful form operations return redirects and display Django messages.
- Document access is checked on the server for each protected operation.
- The application does not expose a public endpoint for direct audit-log modification.
