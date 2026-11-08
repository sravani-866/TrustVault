import uuid
from django.db import models
from django.conf import settings


class Document(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="documents"
    )

    title = models.CharField(max_length=200)

    CATEGORY_CHOICES = [
        ("GENERAL", "General"),
        ("FINANCE", "Finance"),
        ("LEGAL", "Legal"),
        ("HR", "Human Resources"),
        ("TECHNICAL", "Technical"),
        ("OTHER", "Other"),
    ]

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="GENERAL"
    )

    description = models.TextField(blank=True)

    file = models.FileField(
        upload_to="private_documents/"
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class DocumentPermission(models.Model):

    class AccessLevel(models.TextChoices):
        READ = "READ", "Read"
        EDIT = "EDIT", "Edit"

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="permissions"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="document_permissions"
    )

    access_level = models.CharField(
        max_length=4,
        choices=AccessLevel.choices,
        default=AccessLevel.READ
    )

    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="granted_permissions"
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["document", "user"],
                name="unique_document_user_permission"
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.document} - {self.access_level}"