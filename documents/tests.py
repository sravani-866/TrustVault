
import tempfile

from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from accounts.models import User
from audit.models import AuditLog
from .models import Document, DocumentPermission


class DocumentSecurityTests(TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

        settings_override = override_settings(
            MEDIA_ROOT=self.temp_dir.name
        )
        settings_override.enable()

        self.addCleanup(settings_override.disable)
        self.addCleanup(self.temp_dir.cleanup)

        self.owner = User.objects.create_user(
            username="owner_test",
            password="TestPass123!",
            role="OWNER"
        )

        self.viewer = User.objects.create_user(
            username="viewer_test",
            password="TestPass123!",
            role="VIEWER"
        )

        self.document = Document.objects.create(
            owner=self.owner,
            title="Security Test PDF",
            description="Test document",
            file=SimpleUploadedFile(
                "test.pdf",
                b"%PDF-1.4 test document content",
                content_type="application/pdf"
            )
        )

    def edit_url(self):
        return reverse(
            "edit_document",
            args=[self.document.id]
        )

    def grant_permission(self, access_level):
        return DocumentPermission.objects.create(
            document=self.document,
            user=self.viewer,
            access_level=access_level,
            granted_by=self.owner,
            is_active=True
        )

    def test_owner_can_download_document(self):
        self.client.login(
            username="owner_test",
            password="TestPass123!"
        )

        response = self.client.get(
            reverse("download_document", args=[self.document.id])
        )

        self.assertEqual(response.status_code, 200)
        response.close()

    def test_unshared_viewer_cannot_download(self):
        self.client.login(
            username="viewer_test",
            password="TestPass123!"
        )

        response = self.client.get(
            reverse("download_document", args=[self.document.id])
        )

        self.assertEqual(response.status_code, 403)

    def test_shared_viewer_can_download(self):
        self.grant_permission("READ")

        self.client.login(
            username="viewer_test",
            password="TestPass123!"
        )

        response = self.client.get(
            reverse("download_document", args=[self.document.id])
        )

        self.assertEqual(response.status_code, 200)
        response.close()

    def test_revoked_viewer_cannot_download(self):
        permission = self.grant_permission("READ")
        permission.is_active = False
        permission.save()

        self.client.login(
            username="viewer_test",
            password="TestPass123!"
        )

        response = self.client.get(
            reverse("download_document", args=[self.document.id])
        )

        self.assertEqual(response.status_code, 403)

    def test_viewer_cannot_upload(self):
        self.client.login(
            username="viewer_test",
            password="TestPass123!"
        )

        response = self.client.get(
            reverse("document_upload")
        )

        self.assertEqual(response.status_code, 403)

        self.assertTrue(
            AuditLog.objects.filter(
                actor=self.viewer,
                action="ACCESS_DENIED",
                details__attempted_action="DOCUMENT_UPLOAD"
            ).exists()
        )

    def test_download_is_recorded_in_audit_log(self):
        self.client.login(
            username="owner_test",
            password="TestPass123!"
        )

        response = self.client.get(
            reverse("download_document", args=[self.document.id])
        )

        self.assertEqual(response.status_code, 200)

        self.assertTrue(
            AuditLog.objects.filter(
                actor=self.owner,
                document=self.document,
                action="DOCUMENT_DOWNLOADED"
            ).exists()
        )

        response.close()

    def test_owner_can_edit_document(self):
        self.client.login(
            username="owner_test",
            password="TestPass123!"
        )

        response = self.client.post(
            self.edit_url(),
            {
                "title": "Owner Updated Document",
                "category": "GENERAL",
                "description": "Updated by owner"
            }
        )

        self.assertEqual(response.status_code, 302)

        self.document.refresh_from_db()
        self.assertEqual(
            self.document.title,
            "Owner Updated Document"
        )

    def test_viewer_with_edit_permission_can_edit(self):
        self.grant_permission("EDIT")

        self.client.login(
            username="viewer_test",
            password="TestPass123!"
        )

        response = self.client.post(
            self.edit_url(),
            {
                "title": "Viewer Edited Document",
                "category": "GENERAL",
                "description": "Updated by editor"
            }
        )

        self.assertEqual(response.status_code, 302)

        self.document.refresh_from_db()
        self.assertEqual(
            self.document.title,
            "Viewer Edited Document"
        )

    def test_read_only_viewer_cannot_edit(self):
        self.grant_permission("READ")

        self.client.login(
            username="viewer_test",
            password="TestPass123!"
        )

        response = self.client.get(self.edit_url())

        self.assertEqual(response.status_code, 403)

    def test_revoked_viewer_cannot_edit(self):
        permission = self.grant_permission("EDIT")
        permission.is_active = False
        permission.save()

        self.client.login(
            username="viewer_test",
            password="TestPass123!"
        )

        response = self.client.get(self.edit_url())

        self.assertEqual(response.status_code, 403)

    def test_document_edit_is_recorded_in_audit_log(self):
        self.client.login(
            username="owner_test",
            password="TestPass123!"
        )

        response = self.client.post(
            self.edit_url(),
            {
                "title": "Audited Document Edit",
                "category": "GENERAL",
                "description": "Audit test"
            }
        )

        self.assertEqual(response.status_code, 302)

        self.assertTrue(
            AuditLog.objects.filter(
                actor=self.owner,
                document=self.document,
                action="DOCUMENT_EDITED"
            ).exists()
        )

    def test_denied_download_is_recorded_in_audit_log(self):
        self.client.login(
            username="viewer_test",
            password="TestPass123!"
        )

        response = self.client.get(
            reverse("download_document", args=[self.document.id])
        )

        self.assertEqual(response.status_code, 403)

        self.assertTrue(
            AuditLog.objects.filter(
                actor=self.viewer,
                document=self.document,
                action="ACCESS_DENIED",
                details__attempted_action="DOCUMENT_DOWNLOAD"
            ).exists()
        )

    def test_denied_edit_is_recorded_in_audit_log(self):
        self.client.login(
            username="viewer_test",
            password="TestPass123!"
        )

        response = self.client.get(self.edit_url())

        self.assertEqual(response.status_code, 403)

        self.assertTrue(
            AuditLog.objects.filter(
                actor=self.viewer,
                document=self.document,
                action="ACCESS_DENIED",
                details__attempted_action="DOCUMENT_EDIT"
            ).exists()
        )

    def test_owner_can_delete_document_and_audit_is_recorded(self):
        self.client.login(
            username="owner_test",
            password="TestPass123!"
        )

        document_id = self.document.id

        response = self.client.post(
            reverse("delete_document", args=[document_id])
        )

        self.assertEqual(response.status_code, 302)

        self.assertFalse(
            Document.objects.filter(id=document_id).exists()
        )

        self.assertTrue(
            AuditLog.objects.filter(
                actor=self.owner,
                action="DOCUMENT_DELETED",
                details__document_id=str(document_id)
            ).exists()
        )

    def test_viewer_cannot_delete_document_and_denial_is_recorded(self):
        self.client.login(
            username="viewer_test",
            password="TestPass123!"
        )

        response = self.client.post(
            reverse("delete_document", args=[self.document.id])
        )

        self.assertEqual(response.status_code, 403)

        self.assertTrue(
            Document.objects.filter(id=self.document.id).exists()
        )

        self.assertTrue(
            AuditLog.objects.filter(
                actor=self.viewer,
                document=self.document,
                action="ACCESS_DENIED",
                details__attempted_action="DOCUMENT_DELETE"
            ).exists()
        )

    def test_search_documents_by_name(self):
        self.client.login(
            username="owner_test",
            password="TestPass123!"
        )

        response = self.client.get(
            reverse("document_list"),
            {"q": "Security Test"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Security Test PDF")

    def test_filter_documents_by_owner(self):
        self.client.login(
            username="owner_test",
            password="TestPass123!"
        )

        response = self.client.get(
            reverse("document_list"),
            {"owner": "owner_test"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Security Test PDF")

    def test_filter_documents_by_category(self):
        self.client.login(
            username="owner_test",
            password="TestPass123!"
        )

        response = self.client.get(
            reverse("document_list"),
            {"category": "GENERAL"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Security Test PDF")

    def test_filter_documents_by_upload_date(self):
        self.client.login(
            username="owner_test",
            password="TestPass123!"
        )

        selected_date = self.document.uploaded_at.date().isoformat()

        response = self.client.get(
            reverse("document_list"),
            {"date": selected_date}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Security Test PDF")

    def test_document_share_is_recorded_in_audit_log(self):
        self.client.login(
            username="owner_test",
            password="TestPass123!"
        )

        response = self.client.post(
            reverse("share_document", args=[self.document.id]),
            {
                "username": "viewer_test",
                "access_level": "READ"
            }
        )

        self.assertEqual(response.status_code, 200)

        self.assertTrue(
            AuditLog.objects.filter(
                actor=self.owner,
                document=self.document,
                action="DOCUMENT_SHARED",
                details__shared_with="viewer_test",
                details__access_level="READ"
            ).exists()
        )

    def test_access_revoke_is_recorded_in_audit_log(self):
        permission = self.grant_permission("READ")

        self.client.login(
            username="owner_test",
            password="TestPass123!"
        )

        response = self.client.post(
            reverse(
                "revoke_access",
                args=[self.document.id, permission.id]
            )
        )

        self.assertEqual(response.status_code, 302)

        permission.refresh_from_db()
        self.assertFalse(permission.is_active)

        self.assertTrue(
            AuditLog.objects.filter(
                actor=self.owner,
                document=self.document,
                action="ACCESS_REVOKED",
                details__revoked_from="viewer_test"
            ).exists()
        )

    def test_viewer_cannot_revoke_access_and_denial_is_recorded(self):
        permission = self.grant_permission("READ")

        self.client.login(
            username="viewer_test",
            password="TestPass123!"
        )

        response = self.client.post(
            reverse(
                "revoke_access",
                args=[self.document.id, permission.id]
            )
        )

        self.assertEqual(response.status_code, 403)

        self.assertTrue(
            AuditLog.objects.filter(
                actor=self.viewer,
                document=self.document,
                action="ACCESS_DENIED",
                details__attempted_action="ACCESS_REVOKE"
            ).exists()
        )

    def test_audit_log_cannot_be_modified(self):
        audit_log = AuditLog.objects.create(
            actor=self.owner,
            document=self.document,
            action="TEST_EVENT"
        )

        audit_log.action = "MODIFIED_EVENT"

        with self.assertRaises(ValueError):
            audit_log.save()

        audit_log.refresh_from_db()
        self.assertEqual(audit_log.action, "TEST_EVENT")

    def test_audit_log_cannot_be_deleted(self):
        audit_log = AuditLog.objects.create(
            actor=self.owner,
            document=self.document,
            action="TEST_EVENT"
        )

        with self.assertRaises(ValueError):
            audit_log.delete()

        self.assertTrue(
            AuditLog.objects.filter(pk=audit_log.pk).exists()
        )    
        
    def test_viewer_cannot_share_document_and_denial_is_recorded(self):
        self.client.login(
            username="viewer_test",
            password="TestPass123!"
        )

        response = self.client.get(
            reverse("share_document", args=[self.document.id])
        )

        self.assertEqual(response.status_code, 403)

        self.assertTrue(
            AuditLog.objects.filter(
                actor=self.viewer,
                document=self.document,
                action="ACCESS_DENIED",
                details__attempted_action="DOCUMENT_SHARE"
            ).exists()
        )        