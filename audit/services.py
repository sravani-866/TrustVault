from .models import AuditLog


def record_activity(
    actor,
    action,
    document=None,
    details=None,
    request=None
):
    ip_address = None

    if request:
        ip_address = request.META.get("REMOTE_ADDR")

    return AuditLog.objects.create(
        actor=actor,
        document=document,
        action=action,
        details=details or {},
        ip_address=ip_address
    )