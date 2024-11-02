from django.urls import path
from reader import views
from reader import embedpdf

urlpatterns = [
    path('',views.landing,name='home'),
    path("project/<slug:slug>",views.project_home, name="project_home"),


    path('embed/resource/<slug:slug>/',embedpdf.serve_pdf_by_slug, name='pdf_embed'),


    path('api/list/<slug:slug>',views.list_resources,name='file_listing'),
    path('api/upload/',views.upload_pdf_view, name='upload_pdf',)
]           
