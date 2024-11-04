from django.urls import path
from reader import views
from reader import embedpdf

urlpatterns = [
    path('',views.landing,name='home'),
    path("project/<slug:slug>",views.project_home, name="project_home"),


    path('embed/resource/<slug:slug>/',embedpdf.serve_pdf_by_slug, name='pdf_embed'),

    path('api/notes/save/', views.save_note, name='save_note'),
    path('api/notes/list/<slug:slug>/',views.fetch_all_notes,name='all_notes'),
    path('api/list/<slug:slug>/',views.list_resources,name='file_listing'),
    path('api/upload/',views.upload_pdf_view, name='upload_pdf',)
]           
