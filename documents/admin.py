from django.contrib import admin
from .models import Document, DocumentPermission


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "uploaded_at")
    search_fields = ("title", "owner__username")
    list_filter = ("uploaded_at",)


@admin.register(DocumentPermission)
class DocumentPermissionAdmin(admin.ModelAdmin):
    list_display = (
        "document",
        "user",
        "access_level",
        "is_active",
        "granted_by",
    )
    list_filter = ("access_level", "is_active")
    search_fields = ("document__title", "user__username")