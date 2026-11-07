
# TrustVault – Threat Model

## 1. Overview

TrustVault is a secure document management application. Its main security objective is to ensure that confidential documents are accessible only to their owners and users who have been explicitly granted permission.

## 2. Assets to Protect

- Uploaded confidential PDF documents.
- User accounts and authentication credentials.
- Document ownership information.
- Document permissions and access levels.
- Audit logs and activity history.
- Application configuration and database.

## 3. Trust Boundaries

1. The browser is an untrusted client.
2. All document authorization decisions must happen on the server.
3. Uploaded files are treated as untrusted input.
4. Users must not be able to change their own roles or permissions through client-side requests.
5. Private document storage must not be directly exposed as a public directory.

## 4. Threats and Mitigations

### Threat 1: Insecure Direct Object Reference (IDOR)

**Scenario:** A viewer changes a document UUID in a download URL to access another user's document.

**Impact:** Unauthorized disclosure of confidential documents.

**Mitigation:** The download view checks document ownership or an active permission before returning the file.

**Verification:** Automated tests confirm that unshared viewers receive HTTP 403.

### Threat 2: Privilege Escalation

**Scenario:** A viewer attempts to access owner-only upload or sharing operations.

**Impact:** Unauthorized document creation or permission management.

**Mitigation:** Server-side role and ownership checks restrict these operations.

**Verification:** An automated test confirms that viewers cannot upload documents.

### Threat 3: Permission Revocation Bypass

**Scenario:** A viewer attempts to download a document after the owner revokes access.

**Impact:** Continued unauthorized access.

**Mitigation:** The application checks the latest active permission record for every download request.

**Verification:** An automated test confirms that revoked viewers receive HTTP 403.

### Threat 4: Malicious File Upload

**Scenario:** An attacker uploads a non-PDF file disguised with a PDF extension.

**Impact:** Malicious content may be stored or distributed.

**Mitigation:** Upload validation checks the filename extension, file size and PDF signature. Uploads are limited to 5 MB.

**Remaining risk:** Signature checking alone does not guarantee that a PDF is safe. Production deployment should include robust PDF parsing and malware scanning.

### Threat 5: Audit Log Tampering

**Scenario:** A user attempts to alter or delete activity records.

**Impact:** Loss of accountability and unreliable investigation evidence.

**Mitigation:** Audit records are read-only through the Django Admin interface, with add, change and delete permissions disabled.

**Remaining risk:** Database administrators or attackers with database-level access may still modify records. Production should use restricted database privileges and external append-only audit storage.

### Threat 6: Cross-Site Request Forgery (CSRF)

**Scenario:** An attacker tricks an authenticated owner into submitting an unwanted permission-changing request.

**Impact:** Unauthorized sharing or revocation.

**Mitigation:** Django CSRF tokens are included in POST forms, and revocation accepts POST requests only.

### Threat 7: Unauthorized Document Search

**Scenario:** A viewer attempts to discover documents that have not been shared with them through search.

**Impact:** Disclosure of confidential document metadata.

**Mitigation:** Document listing is filtered by ownership and active permission before search filtering.

### Threat 8: Password Compromise

**Scenario:** An attacker obtains a user's password.

**Impact:** Account takeover and unauthorized document access.

**Mitigation:** Django authentication stores password hashes rather than raw passwords.

**Remaining risk:** Production should add rate limiting, MFA and account security monitoring.

## 5. Security Principles

- Deny by default.
- Least privilege.
- Server-side authorization.
- Explicit document sharing.
- Immediate permission revocation.
- Private file storage.
- Input validation.
- Auditability.
- Defense in depth.

## 6. Security Testing

The following automated document security tests have passed:

1. Owner can download a document.
2. Unshared viewer cannot download a document.
3. Shared viewer can download a document.
4. Revoked viewer cannot download a document.
5. Viewer cannot upload a document.
6. Successful downloads are recorded in the audit log.

Command:

`python manage.py test documents`

Result: 6 tests passed.

## 7. Production Security Improvements

Before production deployment:

- Use HTTPS.
- Configure secure cookies.
- Use PostgreSQL.
- Store documents in private object storage.
- Add malware scanning and robust file parsing.
- Restrict database access.
- Add rate limiting and MFA.
- Implement external append-only audit storage.
- Configure backups and monitoring.
- Perform an independent security review.

## 8. Conclusion

TrustVault implements basic server-side access control, private document handling, permission revocation and audit recording. Automated tests verify key authorization scenarios. Additional security hardening is necessary before production use.
