from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class CreateUser(UserCreationForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['email', 'username', 'password1', 'password2']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows':4, 'class':'w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-xl text-white resize-none'}),
            'avatar': forms.ClearableFileInput(attrs={'accept':'image/*'}),
        }