from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, reverse
from django.contrib.auth import authenticate, logout 
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(max_length=64)
    password = forms.CharField(widget=forms.PasswordInput)


class RegisterForm(LoginForm):
    field_order = ["username", "email", "password", "confirmation"]
    email = forms.CharField(widget=forms.EmailInput)
    confirmation = forms.CharField(widget=forms.PasswordInput, 
            error_messages={'required': 'Please Re-Enter your password \
                    for confirmation'})

    def clean(self):
        cd = super().clean()
        password = cd.get('password')
        confirmation = cd.get('confirmation')
        if password != confirmation:
            raise ValidationError(('Confirmation did not match password.')
                    , code='invalid confirmation') 


@login_required
def index(request):
    return render(request, 'main/index.html')


@login_required
def profile(request):
    return render(request, 'main/view_profile.html', {
        'username': request.user.get('username'),
        })


def register(request):
    error_css_class = 'error' 
    required_css_class = 'required'

    if request.method == 'GET':
        return render(request, 'main/register.html', 
                {'form': RegisterForm()})
    elif request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            User.objects.create_user(
                    username=cd.get('username'), 
                    email=cd.get('email'),
                    password=cd.get('password'))
            return HttpResponseRedirect(reverse('login'))
        else:
            return render(request, 'main/register.html', 
                    {'form': form})


def login(request):
    if request.method == 'GET':
        return render(request, 'main/login.html', {'form': LoginForm()})
    elif request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd.get('username'), 
                    password=cd.get('password'))
            auth_login(request, user)
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, 'main/login.html', {'form': form})


def logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))
