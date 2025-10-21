from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import CreateUser
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
# Create your views here.

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next') or 'dashboard'
            return redirect(next_url)
        messages.error(request, 'Invalid username or password')
    else:
        form = AuthenticationForm()

    return render(request, 'auth/login.html', {'form' : form})

def registee_view(request):
    if request.method == 'POST':
        form = CreateUser(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            login(request, user)
            return redirect('dashboard')
        else:
            print(form.errors)
    else:
        form = CreateUser()
    return render(request, 'auth/register.html', {'form' : form})            

def logout_view(request):
    logout(request)
    return redirect('login')