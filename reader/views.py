from django.shortcuts import render,reverse
from django.core.paginator import Paginator
from django.http import JsonResponse,HttpResponseRedirect
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from reader.forms import PdfUploadForm,AddProjectMemberForm,RemoveProjectMemberForm
from reader.models import *
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

@login_required
def project_list_view(request):
    owned_projects = Project.objects.filter(user=request.user)
  
    shared_projects = Project.objects.filter(allowed_users=request.user).exclude(user=request.user)
    owned_paginator = Paginator(owned_projects, 30)
    owned_page_number = request.GET.get('owned_page')
    owned_projects_paginated = owned_paginator.get_page(owned_page_number)

    shared_paginator = Paginator(shared_projects, 30)
    shared_page_number = request.GET.get('shared_page')
    shared_projects_paginated = shared_paginator.get_page(shared_page_number)

    return render(request, 'projects.html', {'owned_projects': owned_projects_paginated,'shared_projects': shared_projects_paginated  })

def landing(request):
    return render(request, 'landing.html')

@login_required
def project_home(request,slug,*args, **kwargs):
    project = get_object_or_404(Project, slug=slug)
    add_mem_form = AddProjectMemberForm(initial={'project_slug':project.slug})

    self_note = Note.objects.filter(user=request.user, source__project=project).first()
    if request.user != project.user and request.user not in project.allowed_users.all():
        logger.warning(f"Unauthorized access attempt by {request.user.username} to project {slug}")
        return JsonResponse({'error': 'Unauthorized access'}, status=403)

    return render(request, 'reader.html', {'project': project,'note':self_note,'add_mem_form':add_mem_form})

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
            source = Sources(project=form.cleaned_data['project'], pdf=form.cleaned_data['pdf_file'])
            try:
                source.save()
                return JsonResponse({'status': 'success', 'message': 'PDF uploaded successfully.'}, status=200)
            except ValidationError as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        errors = {field: error[0] for field, error in form.errors.items()}
        return JsonResponse({'status': 'error', 'message': errors}, status=400)
    
@login_required
def remove_source(request, slug):
    source = get_object_or_404(Sources, slug=slug)
    project = get_object_or_404(Project, slug=source.project.slug)
    try:
        if request.user == project.user or request.user in project.allowed_users.all():
            source.delete()
            return JsonResponse({'status': 'success', 'message': 'Source removed successfully.'}, status=200)
        
        logger.warning(f"Unauthorized access attempt by {request.user.username} to source {slug}")
        return JsonResponse({'status': 'error', 'message': 'Unauthorized access.'}, status=403)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': 'Try again later'}, status=400)

@login_required
def fetch_all_notes(request, slug, *args, **kwargs):
    src = get_object_or_404(Sources,slug=slug)
    project = get_object_or_404(Project, slug=src.project.slug)
    if request.user != project.user and request.user not in project.allowed_users.all():
        logger.warning(f"Unauthorized access attempt by {request.user.username} to PDF {slug}")
        return JsonResponse({'error': 'Unauthorized access'}, status=403)
   
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
            logger.warning(f"Unauthorized access attempt by {request.user.username} to PDF {source_slug}")
            return JsonResponse({'error': 'Unauthorized access'}, status=403)
        note = Note(user=request.user, source=source, content=content)

        try:
            note.save()
            return JsonResponse({'status': 'success', 'message': 'Note saved successfully.'}, status=200)
        except ValidationError as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        
@login_required
def get_self_note(request,slug):
    source = get_object_or_404(Sources, slug=slug)
    project = Project.objects.get(slug=source.project.slug)
    if request.user != project.user and request.user not in project.allowed_users.all():
            logger.warning(f"Unauthorized access attempt by {request.user.username} to PDF {slug}")
            return JsonResponse({'error': 'Unauthorized access'}, status=403)

    notes = Note.objects.filter(user=request.user, source=source).values('content',)
    return JsonResponse(list(notes), safe=False)

@login_required
@require_POST
def add_member_to_project(request):
    form = AddProjectMemberForm(request.POST)
    if form.is_valid():
        project = form.cleaned_data['project']
        member = form.cleaned_data['member']

        if request.user != project.user:
            logger.warning(f"Unauthorized access attempt by {request.user.username} to project {project.slug}")
            return JsonResponse({'error': 'Unauthorized access'}, status=403)

        project.allowed_users.add(member)
        project.save()
        logger.info(f"User {member.username} added to project {project.slug} by {request.user.username}")
        return JsonResponse({
            'status': 'success', 
            'message': 'Member added successfully.', 
            'new_member_name': f"{member.first_name} {member.last_name}"
        }, status=200)
    else:
        return JsonResponse({
            'status': 'error', 
            'errors': form.errors.get_json_data()
        }, status=400)

@login_required
@require_POST
def remove_member_from_project(request):
    form = RemoveProjectMemberForm(request.POST)
    if form.is_valid():
        project = form.cleaned_data['project']
        member = form.cleaned_data['member']

        if request.user != project.user:
            logger.warning(f"Unauthorized access attempt by {request.user.username} to project {project.slug}")
            return JsonResponse({'error': 'Unauthorized access'}, status=403)

        sources = Sources.objects.filter(project=project)
        for view_source in sources:
          Note.objects.filter(source=view_source,user=member).delete()
        # Remove the member from the project
        project.allowed_users.remove(member)
        logger.info(f"User {member.username} removed from project {project.slug} by {request.user.username}")
        return JsonResponse({
            'status': 'success', 
            'message': 'Member removed successfully.', 
            'removed_member_id': member.id
        }, status=200)
    else:
        return JsonResponse({
            'status': 'error', 
            'errors': form.errors.get_json_data()
        }, status=400)


@login_required
def remove_project_or_self(request, slug):
    project = get_object_or_404(Project, slug=slug)
    
    if project.user == request.user:
        project.delete()
    elif request.user in project.allowed_users.all():
        project.allowed_users.remove(request.user)
    
    return HttpResponseRedirect(reverse('project_list'))

@login_required
def create_project(request):
    print(request)
    if request.method == 'POST':
        project_name = request.POST.get('project_name')
        print(project_name)
        project = Project(user=request.user, title=project_name)
        try:
            project.save()

            return JsonResponse({'status': 'success','slug':project.slug, 'message': 'Project created successfully.'}, status=200)
        except ValidationError as e:
            return JsonResponse({'status': 'error','slug':project.slug, 'message': str(e)}, status=400)
