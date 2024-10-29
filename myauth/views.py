from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.models import User
from .forms import Registration, Login

def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = Registration(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['email'],
                first_name=form.cleaned_data['fname'],
                last_name=form.cleaned_data['lname'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            user.save()
            auth_login(request, user)
            messages.success(request, f'Welcome, {user.first_name}! Your account has been created successfully.')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = Registration()

    return render(request, 'registration/register.html', {'form': form})

def login(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = Login(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                auth_login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid email or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = Login()
   
    return render(request, 'registration/login.html', {'form': form})
def auth_logout(request):
    if request.user.is_authenticated is False:
        return redirect('home')
    
    logout(request)
    return redirect('login')