from django import forms
from django.core.exceptions import ValidationError
from reader.models import Project,Sources,Note
from django.contrib.auth.models import User

class PdfUploadForm(forms.Form):
    project_slug = forms.CharField(max_length=100, label='Project Slug', required=True)
    pdf_file = forms.FileField(label='Select a PDF file', required=True)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Remove 'user' from kwargs
        super().__init__(*args, **kwargs)  # Call the base class constructor

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


class AddProjectMemberForm(forms.Form):
    project_slug = forms.CharField(required=True, widget=forms.HiddenInput())
    member_email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'placeholder': 'Enter email', 'autocomplete': 'off', 'class': 'form-control'
    }))

    def clean(self):
        cleaned_data = super().clean()
        project_slug = cleaned_data.get('project_slug')
        member_email = cleaned_data.get('member_email')

        # Validate project slug
        try:
            project = Project.objects.get(slug=project_slug)
        except Project.DoesNotExist:
            raise ValidationError('Invalid project slug. Project not found.')

        # Validate member email
        try:
            member = User.objects.get(email=member_email)
        except User.DoesNotExist:
            raise ValidationError('Invalid member email. User not found.')

        # Check if the user is the project owner
        if member == project.user:
            raise ValidationError('You cannot add yourself as a member.')

        if member in project.allowed_users.all():
            raise ValidationError('User is already a member of the project.')

        cleaned_data['project'] = project
        cleaned_data['member'] = member
        return cleaned_data
    

    
class RemoveProjectMemberForm(forms.Form):
    project_slug = forms.CharField(required=True, widget=forms.HiddenInput())
    member_id = forms.IntegerField(required=True, widget=forms.HiddenInput())

    def clean(self):
        cleaned_data = super().clean()
        project_slug = cleaned_data.get('project_slug')
        member_id = cleaned_data.get('member_id')

        try:
            project = Project.objects.get(slug=project_slug)
        except Project.DoesNotExist:
            raise ValidationError('Invalid project slug. Project not found.')

        try:
            member = User.objects.get(id=member_id)
        except User.DoesNotExist:
            raise ValidationError('Invalid member ID. User not found.')

        if member not in project.allowed_users.all():
            raise ValidationError('User is not a member of the project.')

        cleaned_data['project'] = project
        cleaned_data['member'] = member
        return cleaned_data