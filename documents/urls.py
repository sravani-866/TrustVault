from django.urls import path
from . import views

urlpatterns = [
    path("upload/", views.upload_document, name="document_upload"),
    path("delete/<uuid:document_id>/", views.delete_document, name="delete_document"),
    path("", views.document_list, name="document_list"),

    path(
        "download/<uuid:document_id>/",
        views.download_document,
        name="download_document"
    ),

    path(
        "edit/<uuid:document_id>/",
        views.edit_document,
        name="edit_document"
    ),

    path(
        "share/<uuid:document_id>/",
        views.share_document,
        name="share_document"
    ),

    path(
        "revoke/<uuid:document_id>/<int:permission_id>/",
        views.revoke_access,
        name="revoke_access"
    ),
]
