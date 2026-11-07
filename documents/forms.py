
from django import forms
from django.core.files.uploadedfile import UploadedFile
from .models import Document


class PDFValidationMixin:

    def clean_file(self):
        uploaded_file = self.cleaned_data.get("file")

        if not uploaded_file:
            if self.instance and self.instance.pk:
                return self.instance.file
            raise forms.ValidationError("Please select a file.")

        # Maximum file size: 5 MB
        if uploaded_file.size > 5 * 1024 * 1024:
            raise forms.ValidationError(
                "File size must not exceed 5 MB."
            )

        # Allow PDF files only
        if not uploaded_file.name.lower().endswith(".pdf"):
            raise forms.ValidationError(
                "Only PDF files are allowed."
            )

        # Validate newly uploaded PDF signature
        if isinstance(uploaded_file, UploadedFile):
            uploaded_file.seek(0)
            file_header = uploaded_file.read(5)
            uploaded_file.seek(0)

            if file_header != b"%PDF-":
                raise forms.ValidationError(
                    "Invalid PDF file."
                )

        return uploaded_file


class DocumentUploadForm(PDFValidationMixin, forms.ModelForm):

    class Meta:
        model = Document
        fields = ["title", "description", "file"]


class DocumentEditForm(PDFValidationMixin, forms.ModelForm):

    class Meta:
        model = Document
        fields = ["title", "description", "file"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["file"].required = False

