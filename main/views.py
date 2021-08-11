from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, reverse
from django.contrib.auth import authenticate 
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout 
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django import forms
from django.forms import ModelForm

from .models import User, Note


class LoginForm(forms.Form):
    username = forms.CharField(max_length=64)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cd = super().clean()
        username = cd.get('username')
        password = cd.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise ValidationError(
                    _('Failed to authenticate you as "%(username)s"'), 
                    params={'username': username},
                    code='invalid_user')
        else:
            return {'user': user}


class RegisterForm(LoginForm):
    field_order = ['username', 'email', 'password', 'confirmation']
    email = forms.CharField(widget=forms.EmailInput)
    confirmation = forms.CharField(widget=forms.PasswordInput, 
            error_messages={'required': 'Please Re-Enter your password \
                    for confirmation'})

    def clean(self):
        cd = self.cleaned_data
        password = cd.get('password')
        confirmation = cd.get('confirmation')
        if password != confirmation:
            raise ValidationError(_('Confirmation did not match password.')
                    , code='invalid_confirmation') 
        username = cd.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError(_('A user with username of \
                "%(username)s" already exists.'),
                    params={'username': username},
                    code='invalid_username')


class PostForm(ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'step_one_iterations', 'links', 'step_two_iterations', 'step_three', 'understand'] 




@login_required
def index(request):
    # right now index handles rendering all notes
    return render(request, 'main/index.html', {'notes': 
        [n.clean() for n in Note.objects.all()]})


@login_required
def profile(request):
    return render(request, 'main/view_profile.html', {
        'username': request.user.get('username'),
        })


@login_required
@permission_required('main.new_note')
def new_note(request):
    if request.method == 'GET':
        return render(request, 'main/view_new_note.html', 
        {'form': NewNoteForm()})
    elif request.method == 'POST':
        pass


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
            user = User.objects.create_user(
                    username=cd.get('username'), 
                    email=cd.get('email'),
                    password=cd.get('password'))

            # add all permissions related to notes
            permissions = Permission.objects.filter(codename__contains='_note')
            user.user_permissions.add(*permissions)

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
            user = cd.get('user')
            auth_login(request, user)
            # in case of an update we want to check if this user has 
            # certain permissions otherwise if so ignore otherwise add
            permissions = Permission.objects.filter(codename__contains='_note')
            if user.has_perms([p.codename for p in permissions]):
                user.user_permissions.add(*permissions)
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, 'main/login.html', {'form': form})


def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse('login'))
