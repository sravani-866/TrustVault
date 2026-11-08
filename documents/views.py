
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, FileResponse
from django.db import transaction
from django.db.models import Q
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST

from accounts.models import User
from .models import Document, DocumentPermission
from .forms import DocumentUploadForm, DocumentEditForm
from audit.services import record_activity


@login_required
def upload_document(request):
    if request.user.role not in ["OWNER", "ADMIN"]:
        record_activity(
            actor=request.user,
            action="ACCESS_DENIED",
            details={
                "attempted_action": "DOCUMENT_UPLOAD"
            },
            request=request
        )
        return HttpResponseForbidden("Not authorized to upload.")

    if request.method == "POST":
        form = DocumentUploadForm(request.POST, request.FILES)

        if form.is_valid():
            with transaction.atomic():
                document = form.save(commit=False)
                document.owner = request.user
                document.save()

                record_activity(
                    actor=request.user,
                    action="DOCUMENT_UPLOADED",
                    document=document,
                    details={"title": document.title},
                    request=request
                )

            messages.success(request, "Document uploaded successfully!")
            return redirect("document_upload")
    else:
        form = DocumentUploadForm()

    return render(request, "documents/upload.html", {"form": form})

@login_required
def document_list(request):
    search_query = request.GET.get("q", "").strip()
    owner_query = request.GET.get("owner", "").strip()
    category_query = request.GET.get("category", "").strip()
    date_query = request.GET.get("date", "").strip()

    # Show only owned or actively shared documents
    documents = Document.objects.filter(
        Q(owner=request.user) |
        Q(
            permissions__user=request.user,
            permissions__is_active=True
        )
    ).distinct()

    # Search by document name
    if search_query:
        documents = documents.filter(
            title__icontains=search_query
        )

    # Search by owner username
    if owner_query:
        documents = documents.filter(
            owner__username__icontains=owner_query
        )

    # Filter by category
    if category_query in dict(Document.CATEGORY_CHOICES):
        documents = documents.filter(
            category=category_query
        )

    # Filter by upload date
    if date_query:
        selected_date = parse_date(date_query)

        if selected_date:
            documents = documents.filter(
                uploaded_at__date=selected_date
            )

    documents = documents.order_by("-uploaded_at")

    return render(request, "documents/list.html", {
        "documents": documents,
        "search_query": search_query,
        "owner_query": owner_query,
        "category_query": category_query,
        "date_query": date_query,
        "category_choices": Document.CATEGORY_CHOICES,
    })

@login_required
def download_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)

    has_access = (
        document.owner_id == request.user.id or
        DocumentPermission.objects.filter(
            document=document,
            user=request.user,
            is_active=True
        ).exists()
    )

    if not has_access:
        record_activity(
            actor=request.user,
            action="ACCESS_DENIED",
            document=document,
            details={"attempted_action": "DOCUMENT_DOWNLOAD"},
            request=request
        )
        return HttpResponseForbidden("Not authorized.")

    record_activity(
        actor=request.user,
        action="DOCUMENT_DOWNLOADED",
        document=document,
        request=request
    )

    return FileResponse(
        document.file.open("rb"),
        as_attachment=True,
        filename=document.file.name.split("/")[-1]
    )


@login_required
def edit_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)

    is_owner = document.owner_id == request.user.id

    has_edit_permission = DocumentPermission.objects.filter(
        document=document,
        user=request.user,
        access_level="EDIT",
        is_active=True
    ).exists()

    if not (is_owner or has_edit_permission):
        record_activity(
            actor=request.user,
            action="ACCESS_DENIED",
            document=document,
            details={"attempted_action": "DOCUMENT_EDIT"},
            request=request
        )
        return HttpResponseForbidden(
            "You do not have permission to edit this document."
        )

    if request.method == "POST":
        form = DocumentEditForm(
            request.POST,
            request.FILES,
            instance=document
        )

        if form.is_valid():
            with transaction.atomic():
                updated_document = form.save()

                record_activity(
                    actor=request.user,
                    action="DOCUMENT_EDITED",
                    document=updated_document,
                    details={"title": updated_document.title},
                    request=request
                )

            messages.success(
                request,
                "Document updated successfully!"
            )
            return redirect("document_list")
    else:
        form = DocumentEditForm(instance=document)

    return render(request, "documents/edit.html", {
        "form": form,
        "document": document
    })


@login_required
def share_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    if document.owner_id != request.user.id:
        record_activity(
            actor=request.user,
            action="ACCESS_DENIED",
            document=document,
            details={
                "attempted_action": "DOCUMENT_SHARE"
            },
            request=request
        )
        return HttpResponseForbidden("Not authorized to share.")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        access_level = request.POST.get("access_level", "READ")

        viewer = User.objects.filter(
            username=username,
            role="VIEWER",
            is_active=True
        ).first()

        if not viewer:
            messages.error(request, "Active Viewer not found.")
        elif access_level not in ["READ", "EDIT"]:
            messages.error(request, "Invalid permission level.")
        else:
            with transaction.atomic():
                DocumentPermission.objects.update_or_create(
                    document=document,
                    user=viewer,
                    defaults={
                        "access_level": access_level,
                        "granted_by": request.user,
                        "is_active": True
                    }
                )

                record_activity(
                    actor=request.user,
                    action="DOCUMENT_SHARED",
                    document=document,
                    details={
                        "shared_with": viewer.username,
                        "access_level": access_level
                    },
                    request=request
                )

            messages.success(request, "Document access granted!")

    permissions = DocumentPermission.objects.filter(
        document=document,
        is_active=True
    ).select_related("user")

    return render(request, "documents/share.html", {
        "document": document,
        "permissions": permissions
    })


@login_required
@require_POST
def revoke_access(request, document_id, permission_id):
    document = get_object_or_404(Document, id=document_id)

    if document.owner_id != request.user.id:
        record_activity(
            actor=request.user,
            action="ACCESS_DENIED",
            document=document,
            details={
                "attempted_action": "ACCESS_REVOKE",
                "permission_id": permission_id
            },
            request=request
        )
        return HttpResponseForbidden("Not authorized to revoke access.")

    permission = get_object_or_404(
        DocumentPermission,
        id=permission_id,
        document=document
    )

    if permission.is_active:
        with transaction.atomic():
            permission.is_active = False
            permission.save(update_fields=["is_active"])

            record_activity(
                actor=request.user,
                action="ACCESS_REVOKED",
                document=document,
                details={
                    "revoked_from": permission.user.username
                },
                request=request
            )

        messages.success(request, "Document access revoked!")

    return redirect("share_document", document_id=document.id)


@login_required
@require_POST
def delete_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)

    if document.owner_id != request.user.id:
        record_activity(
            actor=request.user,
            action="ACCESS_DENIED",
            document=document,
            details={"attempted_action": "DOCUMENT_DELETE"},
            request=request
        )
        return HttpResponseForbidden(
            "You do not have permission to delete this document."
        )

    file_name = document.file.name
    storage = document.file.storage

    with transaction.atomic():
        record_activity(
            actor=request.user,
            action="DOCUMENT_DELETED",
            document=document,
            details={
                "title": document.title,
                "document_id": str(document.id)
            },
            request=request
        )

        document.delete()

        transaction.on_commit(
            lambda: storage.delete(file_name)
        )

    messages.success(request, "Document deleted successfully!")
    return redirect("document_list")
