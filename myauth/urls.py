from django.urls import path
from myauth import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login,),
    path('logout/', views.auth_logout, name='logout'),
    path('', views.login, name='login'),

]
