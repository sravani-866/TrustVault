
# TrustVault – Secure Document Management

TrustVault is a Django-based secure document management application. It allows document owners to upload PDF files, share them with authorized viewers, and revoke access when required.

## Features

- User authentication using Django authentication.
- Role-based users: ADMIN, OWNER and VIEWER.
- PDF upload with a 5 MB size limit.
- PDF extension and file-signature validation.
- Private document storage.
- Document listing and title search.
- Owner-controlled document sharing.
- READ and EDIT permission levels.
- Permission revocation.
- Server-side authorization for document downloads.
- Audit logging for uploads, downloads, sharing, revocation and document edits.
- Django Admin interface for user, document and audit management.
- Automated security tests.

## Technology Stack

- Python
- Django
- SQLite (local development database)
- PostgreSQL (production database)
- Supabase private object storage (production file storage)
- HTML and CSS
- Django ORM
- Django automated testing framework

## User Roles

| Role | Capabilities |
|---|---|
| ADMIN | Manage users and inspect administration records |
| OWNER | Upload documents, view owned documents, share and revoke access |
| VIEWER | View and download documents explicitly shared with them |

Administrators do not automatically receive access to confidential document downloads.

## Installation

1. Clone or download the project.
2. Open the project folder in a terminal.
3. Create a virtual environment:

   `python -m venv venv`

4. Activate it on Windows PowerShell:

   `.\venv\Scripts\Activate.ps1`

5. Install dependencies:

   `pip install -r requirements.txt`

6. Apply database migrations:

   `python manage.py migrate`

7. Create an administrator:

   `python manage.py createsuperuser`

8. Start the development server:

   `python manage.py runserver`

9. Open:

   `http://127.0.0.1:8000/`

## Running Tests

Run all automated tests:

`python manage.py test`

Run document security tests:

`python manage.py test documents`

The document security test suite covers owner downloads, unauthorized downloads, shared access, revoked access, viewer upload restrictions and download audit logging.

## Security Design

- Authentication is required for document operations.
- Document access is checked on the server.
- Document IDs are UUIDs.
- Access is denied unless the user owns the document or has an active permission.
- Revoked permissions are checked against the database on every download.
- Uploads are limited to PDF files of 5 MB or less.
- Uploaded files are stored under a private media directory.
- CSRF protection is used for POST forms.
- Audit records are read-only in the Django Admin interface.

## Important Limitations

Core functionality has been implemented and deployed. Further security and operational improvements may include:

- Configure HTTPS and secure production cookies.
- Add malware scanning and robust PDF parsing.
- Add rate limiting and stronger operational monitoring.
- Review production secret management and backup procedures.
- Expand automated tests for additional security edge cases.

PostgreSQL and Supabase private object storage are already configured for production.

The development server and SQLite database are intended for local development only.
## Project Structure

- `accounts/` – Custom user model and user administration.
- `documents/` – Document models, upload, sharing, permissions and downloads.
- `audit/` – Audit log model and activity recording.
- `core/` – Login, dashboard and logout.
- `config/` – Django project configuration.

## Project Status

Core document management and access-control workflows have been implemented. Eleven automated document security tests have passed in the development environment.
