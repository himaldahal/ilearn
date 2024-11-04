from django.shortcuts import render
from reader.models import *
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from reader.forms import PdfUploadForm

import logging

logger = logging.getLogger(__name__)

def landing(request):
    return render(request, 'landing.html')

@login_required
def project_home(request,slug,*args, **kwargs):
    project = get_object_or_404(Project, slug=slug)
    self_note = Note.objects.filter(user=request.user, source__project=project).first()
    if request.user != project.user and request.user not in project.allowed_users.all():
        logger.warning(f"Unauthorized access attempt by {request.user.username} to project {slug}")
        return JsonResponse({'error': 'Unauthorized access'}, status=403)

    return render(request, 'reader.html', {'project': project,'note':self_note})





#APIs
def list_resources(request,slug,*args, **kwargs):
    project = get_object_or_404(Project,slug=slug)
    if request.user != project.user and request.user not in project.allowed_users.all():
        logger.warning(f"Unauthorized access attempt by {request.user.username} to PDF {slug}")
        return JsonResponse({'error': 'Unauthorized access'}, status=403)

    resources = Sources.objects.filter(project=project).values('title','pdf','slug',)
    return JsonResponse(list(resources),safe=False)

@require_POST
@login_required
def upload_pdf_view(request):
    if request.method == 'POST':
        form = PdfUploadForm(request.POST, request.FILES, user=request.user) 
        if form.is_valid():
            source = Sources(project=form.cleaned_data['project'],pdf=form.cleaned_data['pdf_file'],)
            try:
                source.save()
                return JsonResponse({'status': 'success', 'message': 'PDF uploaded successfully.'}, status=200)
            except ValidationError as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        errors = {field: error[0] for field, error in form.errors.items()}
        return JsonResponse({'status': 'error', 'message': errors}, status=400)
    
@require_POST
@login_required
def remove_source(request):
    if request.method == 'POST':
        slug = request.POST.get('slug')
        source = get_object_or_404(Sources, slug=slug)
        if source.project.user == request.user:
            source.delete()
            return JsonResponse({'status': 'success', 'message': 'Source removed successfully.'}, status=200)
        else:
            return JsonResponse({'status': 'error', 'message': 'Unauthorized access.'}, status=403)
        
@login_required
def fetch_all_notes(request, slug, *args, **kwargs):
    src = get_object_or_404(Sources,slug=slug)
    
    project = get_object_or_404(Project, slug=src.project.slug)
    if request.user != project.user and request.user not in project.allowed_users.all():
        logger.warning(f"Unauthorized access attempt by {request.user.username} to PDF {slug}")
        return JsonResponse({'error': 'Unauthorized access'}, status=403)
    print(request.user.username)
    notes = Note.objects.filter(source=src).values('user__first_name','user__last_name','content',).exclude(user=request.user)
    return JsonResponse(list(notes), safe=False)

@login_required
def save_note(request):
    if request.method == 'POST':
        source_slug = request.POST.get('source_slug')
        content = request.POST.get('content')

        source = get_object_or_404(Sources, slug=source_slug)
        project = Project.objects.get(slug=source.project.slug)
        if request.user != project.user and request.user not in project.allowed_users.all():
            logger.warning(f"Unauthorized access attempt by {request.user.username} to PDF {slug}")
            return JsonResponse({'error': 'Unauthorized access'}, status=403)
        note = Note(user=request.user, source=source, content=content)

        try:
            note.save()
            return JsonResponse({'status': 'success', 'message': 'Note saved successfully.'}, status=200)
        except ValidationError as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)