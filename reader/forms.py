from django import forms
from django.core.exceptions import ValidationError
from reader.models import Project,Sources,Note

class PdfUploadForm(forms.Form):
    project_slug = forms.CharField(max_length=100, label='Project Slug',required=True)
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


class NoteForm(forms.Form):
    source_slug = forms.CharField(required=True)
    note = forms.Textarea()

    def clean(self):
        cleaned_data = super().clean()
        project_slug = cleaned_data.get('source_slug')
        try:
            source = Sources.objects.get(slug=project_slug)
        except Sources.DoesNotExist:
            raise ValidationError("{ 'status':'error','message':'Form manipulation isn\'t allowed.'")

        cleaned_data['source'] = source
        return cleaned_data