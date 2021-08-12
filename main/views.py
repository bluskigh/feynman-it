from django.http import HttpResponse, HttpResponseRedirect, JsonResponse 
from django.shortcuts import render, reverse
from django.contrib.auth import authenticate 
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout 
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.contrib import messages
from django import forms
from django.forms import ModelForm

from json import loads, dumps

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


class NewNoteForm(ModelForm):
    class Meta:
        model = Note 
        fields = ['title']


    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not len(title):
            raise ValidationError(_('Please provide a value for the notes title.'), code='invalid_title')
        return title 


class NoteForm(ModelForm):
    class Meta:
        model = Note
        exclude = ['owner']
        # fields = ['title', 'step_one_iterations', 'links', 'step_two_iterations', 'step_three', 'understand'] 
        widgets = {'step_one_iterations': forms.Textarea, 'step_two_iterations': forms.Textarea}

    def clean_step_one_iterations(self):
        data = self.cleaned_data.get('step_one_iterations')
        print(data)
        return data


@login_required
def index(request):
    # right now index handles rendering all notes
    return render(request, 'main/index.html', {
        'notes': [n.basic_information() for n in Note.objects.all()], 
        'new_note_form': NewNoteForm()})


@login_required
def profile(request):
    return render(request, 'main/view_profile.html', {
        'username': request.user.get('username'),
        })


@login_required
@permission_required('main.add_note')
def new_note(request):
    if request.method == 'POST':
        data = loads(request.body)
        form = NewNoteForm(data)
        if form.is_valid():
            cd = form.cleaned_data
            note = Note.objects.create(title=cd.get('title'), owner=request.user)
            return JsonResponse(note.basic_information(), status=200)
        else:
            return JsonResponse({'errors': form.errors, 'status': 400}, status=400)


@login_required
@permission_required('main.view_note')
def view_note(request, id):
    note = Note.objects.get(id=id)
    if note is None:
        messages.info(request, f'404: Could not locate note of id: {id}')
        return HttpResponseRedirect(reverse('index'))
    return render(request, 'main/view_note.html', {'note': note.more_information()})


@login_required
@permission_required('main.change_note')
def edit_note(request, id):
    note = Note.objects.get(id=id)
    if note is None:
        messages.info(request, f'404: Could not locate note of id: {id}')
    if request.method == 'GET':
        return render(request, 'main/edit_note.html', {'note': note.more_information(), 'form': NoteForm(initial={'step_three': note.step_three, 'title': note.title})})
    elif request.method == 'POST':
        data = loads(request.body)
        form = NoteForm(data)
        if form.is_valid():
            changed_data = form.changed_data
            print(form.cleaned_data.get('step_one_iterations'))
            cleaned_data = form.cleaned_data
            # updating
            if 'step_three' in changed_data:
                note.step_three = cleaned_data.get('step_three')
            if 'title' in changed_data:
                note.title = cleaned_data.get('title')
            if 'step_one_iterations' in changed_data:
                note.step_one_iterations.extend(cleaned_data.get('step_one_iterations'))
            if 'step_two_iterations' in changed_data:
                note.step_two_iterations.extend(cleaned_data.get('step_two_iterations'))
            if 'links' in changed_data:
                note.links.extend(cleaned_data.get('links'))
            if 'understand' in changed_data:
                note.understand = cleaned_data.get('understand')
            note.save()
            return HttpResponseRedirect(reverse('view_note', kwargs={'id': id}))
        else:
            # being naive here, error are goign to be a bit complex due to how its all structured
            return render(request, 'main/edit_note.html', {'note': note.more_information(), 'form': form})


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
