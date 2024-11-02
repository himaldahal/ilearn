# embedpdf.py
from django.http import JsonResponse, FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
import logging
import os

from .models import Sources

logger = logging.getLogger(__name__)

@login_required
def serve_pdf_by_slug(request, slug,*args, **kwargs):
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            source = get_object_or_404(Sources, slug=slug)
            if request.user != source.project.user and request.user not in source.project.allowed_users.all():
                logger.warning(f"Unauthorized access attempt by {request.user.username} to PDF {slug}")
                return JsonResponse({'error': 'Unauthorized access'}, status=403)

            # Send URL for frontend AJAX to load in PDF.js
            return JsonResponse({'pdf_url': source.pdf.url})
        except Sources.DoesNotExist:
            logger.error(f"No Sources object found with slug: {slug}")
            return JsonResponse({'error': f"No source found with slug '{slug}'"}, status=404)
        except Exception as e:
            logger.exception(f"Unexpected error in PDF view for slug {slug}: {e}")
            return JsonResponse({'error': 'An unexpected error occurred'}, status=500)

    # Directly serve the file if the request isn’t AJAX (i.e., user directly accesses the PDF)
    try:
        source = get_object_or_404(Sources, slug=slug)
        if request.user != source.project.user and request.user not in source.project.allowed_users.all():
            raise PermissionError("Unauthorized access")
        
        pdf_path = source.pdf.path
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            raise Http404("PDF file not found")
            
        return FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')

    except PermissionError as e:
        return JsonResponse({'error': str(e)}, status=403)
    except Http404 as e:
        return JsonResponse({'error': str(e)}, status=404)
    except Exception as e:
        logger.exception(f"Unexpected error in PDF view for slug {slug}: {e}")
        return JsonResponse({'error': 'An unexpected error occurred'}, status=500)
