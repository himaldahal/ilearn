from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.models import User
from .forms import Registration, Login
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.db import IntegrityError

def register(request):
    if request.user.is_authenticated:
        messages.info(request, _('You are already logged in.'))
        return redirect('home')

    if request.method == 'POST':
        form = Registration(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            fname = form.cleaned_data['fname']
            lname = form.cleaned_data['lname']

            # Generate a unique username from the email
            base_username = email.split('@')[0]
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            # Check if email already exists
            if User.objects.filter(email=email).exists():
                form.add_error('email', _('A user with this email already exists.'))
            else:
                try:
                    user = User.objects.create_user(
                        username=username,
                        first_name=fname,
                        last_name=lname,
                        email=email,
                        password=password
                    )
                    user.save()
                    auth_login(request, user)
                    messages.success(request, _('Welcome, {0}! Your account has been created successfully.').format(user.first_name))
                    return redirect('home')
                except IntegrityError:
                    messages.error(request, _('There was an error creating your account. Please try again later.'))
        else:
            messages.error(request, _('Please correct the errors below.'))
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