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
from django.contrib.messages import get_messages
from django import forms
from django.forms import ModelForm
from django.db.models import Q

from json import loads, dumps

from .models import User, Note, Folder 


class NewFolderForm(ModelForm):
    class Meta:
        model = Folder 
        exclude = ['owner']


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


class LargeTextField(forms.Field):
    """Utilizes text area widget, and converts data from widget into json"""
    widget = forms.Textarea


    def __init__(self, *, placeholder='', empty_value='', **kwargs):
        self.empty_value = empty_value
        self.placeholder = placeholder 
        super().__init__(**kwargs)


    def to_python(self, value):
        if value not in self.empty_value:
            # should be an array of values
            data = loads(value)
            return data
        else:
            return self.empty_value 


    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        if self.placeholder not in self.empty_value:
            attrs['placeholder'] = self.placeholder
        return attrs


class NoteForm(ModelForm):
    step_one_iterations = LargeTextField(required=False, placeholder='Enter iteration for step one')
    step_two_iterations = LargeTextField(required=False, placeholder='Enter iteration for step two')
    links = LargeTextField(required=False, placeholder='Enter link here') 
    class Meta:
        model = Note
        exclude = ['owner', 'folder']


class FolderForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.usernotes = kwargs.pop('usernotes', None)
        self.folder = kwargs.pop('folder', None)
        notes = self.usernotes.exclude(folder=self.folder)
        super(FolderForm, self).__init__(*args, **kwargs)
        self.fields['available_notes'] = forms.MultipleChoiceField(choices=[(note.id, note.title) for note in notes])


@login_required
def index(request):
    return HttpResponse('<a href="notes/">Go to notes</a>')


@login_required
def notes(request):
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
        form = NoteForm(request.POST)
        if form.is_valid():
            changed_data = form.changed_data
            cleaned_data = form.cleaned_data
            # updating
            if 'step_three' in changed_data:
                note.step_three = cleaned_data.get('step_three')
            if 'title' in changed_data:
                note.title = cleaned_data.get('title')
            if 'step_one_iterations' in changed_data:
                soi = cleaned_data.get('step_one_iterations')
                # user updated iteration
                if soi.get('edit'):
                    for key in soi.get('edit'):
                        note.step_one_iterations[int(key)-1] = soi.get('edit').get(key)
                else:
                    if soi.get('added'):
                        note.step_one_iterations.extend(soi.get('added'))
            if 'step_two_iterations' in changed_data:
                sti = cleaned_data.get('step_two_iterations')
                if sti.get('edit'):
                    for key in sti.get('edit'):
                        note.step_two_iterations[int(key)-1] = sti.get('edit').get(key)
                else:
                    if sti.get('added'):
                        note.step_two_iterations.extend(sti.get('added'))
            if 'links' in changed_data:
                l = cleaned_data.get('links')
                if l.get('edit'):
                    for key in l.get('edit'):
                        note.links[int(key)] = l.get('edit').get(key)
                else:
                    if l.get('added'):
                        for arr in l.get('added'):
                            note.links.append(arr)
                            # note.links.extend(l.get('added'))
            if 'understand' in changed_data:
                note.understand = cleaned_data.get('understand')
            note.save()
            return HttpResponseRedirect(reverse('view_note', kwargs={'id': id}))
        else:
            # being naive here, error are goign to be a bit complex due to how its all structured
            return render(request, 'main/edit_note.html', {'note': note.more_information(), 'form': form})


@login_required
def folders(request):
    return render(request, 'main/folders.html', {'form': NewFolderForm(), 'folders': Folder.objects.filter(owner=request.user)})


@login_required
@permission_required('main.add_folder')
def new_folder(request):
    form = NewFolderForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        Folder.objects.create(title=cd.get('title').strip(), owner=request.user)
        return HttpResponseRedirect(reverse('folders'))
    else:
        return render(request, 'main/folders.html', {'form': form, 'folders': Folder.objects.filter(owner=request.user)})


@login_required
def view_folder(request, id):
    folder = Folder.objects.get(id=id)
    if folder is None:
        messages.info(request, f'404: Could not find foler with id of {id}')
    notes = request.user.notes.exclude(folder=folder)
    if request.method == 'GET':
        # filtering all notes by the current user, and notes that are not in the current folder.
        form = FolderForm(usernotes=request.user.notes, folder=folder)
        return render(request, 'main/view_folder.html', {'folder': folder, 'notes': request.user.notes.filter(folder=folder), 'form': form})
    elif request.method == 'POST':
        form = FolderForm(usernotes=request.user.notes, folder=folder, data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            for option in cd.get('available_notes'):
                option = int(option)
                note = Note.objects.get(id=option)
                note.folder = folder
                note.save()
            return HttpResponseRedirect(reverse('view_folder', kwargs={'id': id}))
        else:
            return render(request, 'main/view_folder.html', {'folder': folder, 'notes': request.user.notes.filter(folder=folder), 'form': form})


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
            # permissions = Permission.objects.filter(codename__contains='_note')
            # user.user_permissions.add(*permissions)

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
            note_query = Q(codename__contains='_note')
            folder_query = Q(codename__contains='_folder')
            note_permissions = Permission.objects.filter(note_query)
            folder_permissions = Permission.objects.filter(folder_query)
            # THIS may be a bit silly, since a user can have old model permissions and not new model permissions therefore the adding of permission will run
            # but we don't want to readd permission he already has, therefore instead look by group
            if not user.has_perms([p.codename for p in folder_permissions]):
                user.user_permissions.add(*folder_permissions)
            if not user.has_perms([p.codename for p in note_permissions]):
                user.user_permissions.add(*note_permissions)

            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, 'main/login.html', {'form': form})


def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse('login'))
