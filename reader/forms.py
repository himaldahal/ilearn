from django import forms
from django.core.exceptions import ValidationError
from reader.models import Project

class PdfUploadForm(forms.Form):
    project_slug = forms.CharField(max_length=100, label='Project Slug', required=True)
    pdf_file = forms.FileField(label='Select a PDF file', required=True)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        project_slug = cleaned_data.get('project_slug')

        try:
            project = Project.objects.get(slug=project_slug)
        except Project.DoesNotExist:
            raise ValidationError('Invalid project slug. Project not found.')

        if self.user != project.user and self.user not in project.allowed_users.all():
            raise ValidationError('Unauthorized access to upload PDF for this project.')

        pdf_file = cleaned_data.get('pdf_file')
        if pdf_file:
            if pdf_file.size > 50 * 1024 * 1024:
                raise ValidationError('PDF file size should not exceed 50 MB.')
            if not pdf_file.name.endswith('.pdf'):
                raise ValidationError('File must be a PDF.')

        cleaned_data['project'] = project

        return cleaned_data
