import os
import secrets
import string
import uuid
import re
import PyPDF2


from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.core.files import File
from django.conf import settings

# Helper function to generate a unique slug
def slug_generator(length=64):
    letters = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(letters) for _ in range(length))

class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, default='untitled')
    slug = models.CharField(max_length=100, unique=True, blank=True)
    allowed_users = models.ManyToManyField(User, related_name='allowed_projects', blank=True)

    class Meta:
        ordering = ['-id']
        verbose_name_plural = "Projects"
        verbose_name = "Project"

    def save(self, *args, **kwargs):
        if not self.slug:
            username = self.user.username
            unique_part = slug_generator()
            self.slug = f"{username}-{unique_part}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Sources(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True)
    pdf = models.FileField() 
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(pdf__iendswith='.pdf'), name='pdf_format_check')
        ]
        verbose_name_plural = "Sources"
        verbose_name = "Source"

    def save(self, *args, **kwargs):
        if not self.title and self.pdf:
            base_name = os.path.splitext(self.pdf.name)[0][:32]
            self.title = re.sub(r'[-_]', ' ', base_name)
     
        if not self.slug:
            trimmed_title = slugify(self.title[:32])
            self.slug = f"{trimmed_title}-{uuid.uuid4().hex[:8]}"
  
        if not self.pdf.name.endswith('.pdf'):
            raise ValidationError("File must be a PDF")

        sanitized_pdf = PyPDF2.PdfWriter()
        try:
            pdf_reader = PyPDF2.PdfReader(self.pdf)
            for page_num in range(len(pdf_reader.pages)):
                sanitized_pdf.add_page(pdf_reader.pages[page_num])

            # Saving sanitized file temporarily
            temp_path = f"/tmp/{self.slug}.pdf"
            with open(temp_path, "wb") as output_file:
                sanitized_pdf.write(output_file)

            # Moving sanitized file to 'resources/' path in the media location
            resources_path = os.path.join('resources', f"{self.slug}.pdf")
            with open(temp_path, "rb") as temp_file:
                self.pdf.save(resources_path, File(temp_file), save=False)

            # Cleaning up the temporary file
            os.remove(temp_path)
        except Exception as e:
            raise ValidationError("Failed to sanitize PDF file.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.pdf:
            self.pdf.delete(save=False)
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.title



class Note(models.Model):
    source = models.ForeignKey(Sources, on_delete=models.CASCADE, related_name='notes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)

    class Meta:
     unique_together = ('source', 'user')

    def save(self,*args, **kwargs):
        # remove previous note of the same user and save new it  
        if self.source.notes.filter(user=self.user).exists():
            self.source.notes.filter(user=self.user).delete()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f'Notes for {self.source}'