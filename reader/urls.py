from django.urls import path
from reader.views import landing
urlpatterns = [
    path('',landing,name='home'),
]
