from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import CreateUser
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import ProfileForm

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
            # profile is created by signal but ensure existence
            if not hasattr(user, 'profile'):
                from .models import Profile
                Profile.objects.create(user=user)
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CreateUser()
    return render(request, 'auth/register.html', {'form' : form})            

def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile_view(request):
    # show profile
    profile = request.user.profile
    return render(request, 'auth/profile.html', {'profile': profile})


@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'auth/edit_profile.html', {'form': form})