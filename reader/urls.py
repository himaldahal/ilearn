from django.urls import path
from reader import views
from reader import embedpdf

urlpatterns = [
    path('projects/', views.project_list_view, name='project_list'),
    path('project/remove/<slug:slug>/',views.remove_project_or_self,name='remove_project_or_self'),
    path('project/add/',views.create_project,name='create_project'),
    path('project/<slug:slug>/',views.project_home, name="project_home"),


    path('embed/resource/<slug:slug>/',embedpdf.serve_pdf_by_slug, name='pdf_embed'),

    path('api/project/member/add/',views.add_member_to_project,name='add_member_to_project'),
    path('api/project/member/remove/',views.remove_member_from_project,name='remove_member_from_project'),

    path('api/list/<slug:slug>/',views.list_resources,name='file_listing'),
    path('api/upload/',views.upload_pdf_view, name='upload_pdf'),
    path('api/resource/remove/<slug:slug>',views.remove_source,name='resource_remove'),

    path('api/notes/save/', views.save_note, name='save_note'), 
    path('api/notes/self/<slug:slug>/',views.get_self_note,name='self_notes'),
    path('api/notes/list/<slug:slug>/',views.fetch_all_notes,name='all_notes'),
   
] + [
    path('',views.landing,name='home'),
]