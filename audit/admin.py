from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "actor",
        "document",
        "action",
        "ip_address",
        "timestamp",
    )

    list_filter = ("action", "timestamp")
    search_fields = ("actor__username", "action")
    readonly_fields = (
        "actor",
        "document",
        "action",
        "details",
        "ip_address",
        "timestamp",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False