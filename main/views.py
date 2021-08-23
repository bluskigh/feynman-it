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

from .models import User, Note, Folder, Link, Iteration


class NewFolderForm(ModelForm):
    title = forms.CharField(max_length=64, widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    class Meta:
        model = Folder 
        exclude = ['owner', 'title']


class LoginForm(forms.Form):
    username = forms.CharField(max_length=64, widget=forms.TextInput(attrs={'autocomplete': 'off'}))
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
    email = forms.CharField(widget=forms.EmailInput(attrs={'autocomplete': 'off'}))
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
    title = forms.CharField(max_length=64, widget=forms.TextInput(attrs={'autocomplete': 'off'}))
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
    widget = forms.Textarea(attrs={'autocomplete': 'off'})

    def __init__(self, *, placeholder='', empty_value='', **kwargs):
        self.empty_value = empty_value
        self.placeholder = placeholder 
        super().__init__(**kwargs)

    def to_python(self, value):
        if value not in self.empty_value:
            # should be an array of values
            data = loads(value)
            print(data)
            return data
        else:
            return self.empty_value 

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        if self.placeholder not in self.empty_value:
            attrs['placeholder'] = self.placeholder
        return attrs


class NoteForm(ModelForm):
    class Meta:
        model = Note
        exclude = ['owner', 'folder', 'step_one_iterations', 'step_two_iterations', 'links']


class FolderForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.usernotes = kwargs.pop('usernotes', None)
        self.folder = kwargs.pop('folder', None)
        notes = self.usernotes.exclude(folder=self.folder)
        super(FolderForm, self).__init__(*args, **kwargs)
        self.fields['available_notes'] = forms.MultipleChoiceField(choices=[(note.id, note.title) for note in notes])


@login_required
def index(request):
    return HttpResponseRedirect(reverse('notes'))


def home(request):
    return render(request, 'main/index.html')


@login_required
def notes(request):
    # right now index handles rendering all notes
    return render(request, 'main/notes.html', {
        'notes': [n.basic_information() for n in Note.objects.filter(owner=request.user)], 
        'new_note_form': NewNoteForm()})


@login_required
def iterations(request, id=None):
    if request.method == 'POST':
        data = loads(request.body)
        noteid = data.get('noteid')
        title = data.get('title')
        text = data.get('text')
        which = data.get('which')
        if not noteid or not title or not text or not which:
            return HttpResponse(status=400)
        note = Note.objects.get(id=noteid)
        iteration = Iteration(title=title, text=text)
        if which == 1:
            iteration.note_step_one = note 
        else:
            iteration.note_step_two = note
        iteration.save()
        return JsonResponse({'id': iteration.id}, status=200)


@login_required
def iteration(request, id):
    try:
        iteration = Iteration.objects.get(id=id)
    except:
        return HttpResponse(status=400)

    if (iteration.note_step_one and iteration.note_step_one.owner == request.user) or (iteration.note_step_two and iteration.note_step_two.owner == request.user):
        if request.method == 'DELETE':
            iteration.delete()
            return HttpResponse(status=200)
        elif request.method == 'PATCH':
            data = loads(request.body)
            title = data.get('title')
            text = data.get('text')
            if title:
                iteration.title = title
            if text:
                iteration.text = text
            iteration.save()
            return HttpResponse(status=200)
        
    return HttpResponse(status=400)


@login_required
def links(request):
    """POST request requires following: title, href"""
    if request.method == 'POST':
        data = loads(request.body)
        if not data.get('title') or not data.get('href') or not data.get('noteid'):
            # invalid request
            return HttpResponse(status=400)
        note = Note.objects.get(id=data.get('noteid'))
        link = Link(title=data.get('title'), href=data.get('href'))
        if data.get('which') == 0:
            link.general = note
        else:
            iteration = Iteration.objects.get(id=data.get('which'))
            link.which_iteration = iteration
        link.save()
        # for now just return id, on frontend we will wait until this id is returned back
        return JsonResponse({'id': link.id}, status=200)


@login_required
def link(request, id):
    link = Link.objects.get(id=id)
    if link is None:
        return HttpResponse(status=400)
    if request.method == 'DELETE':
        link.delete()
    elif request.method == 'PATCH':
        data = loads(request.body)
        title = data.get('title')
        text = data.get('text')
        if title is not None:
            link.title = title
        if text is not None:
            link.text = text
        link.save()
    return HttpResponse(status=200)


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
            add_folder = request.user.folders.all()[0]
            note = Note.objects.create(title=cd.get('title'), owner=request.user, folder=add_folder)
            result = note.basic_information()
            result['route'] = reverse('view_note', kwargs={'id': note.id})
            return JsonResponse(result, status=200)
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
        return render(request, 'main/edit_note.html', {'note': note.more_information(), 'form': NoteForm(initial={'step_three': note.step_three, 'title': note.title, 'understand': note.understand})})
    elif request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            changed_data = form.changed_data
            cleaned_data = form.cleaned_data
            if 'title' in changed_data:
                note.title = cleaned_data.get('title')
            if 'step_three' in changed_data:
                note.step_three = cleaned_data.get('step_three')
            note.understand = cleaned_data.get('understand')
            note.save()
            messages.success(request, 'Successfully saved note')
            return HttpResponseRedirect(reverse('view_note', kwargs={'id': id}))
        else:
            # being naive here, error are goign to be a bit complex due to how its all structured
            return render(request, 'main/edit_note.html', {'note': note.more_information(), 'form': form})


@login_required
def folders(request):
    return render(request, 'main/folders.html', {'form': NewFolderForm(), 
        'folders': [folder.basic_information() for folder in Folder.objects.filter(owner=request.user)]})


@login_required
@permission_required('main.add_folder')
def new_folder(request):
    form = NewFolderForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        Folder.objects.create(title=cd.get('title').strip(), owner=request.user)
        messages.success(request, 'Successfully created folder')
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
        return render(request, 'main/view_folder.html', {'folder': folder.basic_information(), 
            'notes': request.user.notes.filter(folder=folder), 'form': form})
    elif request.method == 'POST':
        form = FolderForm(usernotes=request.user.notes, folder=folder, data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            for option in cd.get('available_notes'):
                option = int(option)
                note = Note.objects.get(id=option)
                note.folder = folder
                note.save()
            messages.success(request, 'Successfully moved notes')
            return HttpResponseRedirect(reverse('view_folder', kwargs={'id': id}))
        else:
            return render(request, 'main/view_folder.html', {'folder': folder, 'notes': request.user.notes.filter(folder=folder), 'form': form})


@login_required
@permission_required('main.delete_folder')
def delete_folder(request, id):
    folder = Folder.objects.get(id=id)
    deleted_folder = request.user.folders.all()[1]
    all_folder = request.user.folders.all()[0]
    notes = folder.folder_notes.all()
    if folder != deleted_folder:
        for note in notes:
            note.folder = deleted_folder 
            note.save()
    else:
        messages.info(request, f'Deleted notes from "{folder.title}"')
        for note in folder.folder_notes.all():
            note.delete()

    if folder != all_folder and folder != deleted_folder and len(notes) == 0:
        messages.success(request, f'Successfully deleted folder "{folder.title}"')
        folder.delete()

    return HttpResponseRedirect(reverse('folders'))


def register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))

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
            
            # create delete and all folders, now should be [0] = add, [1] = delete when attemping to access users folders
            Folder.objects.create(title='All', owner=user)
            Folder.objects.create(title='Deleted', owner=user)
            return HttpResponseRedirect(reverse('login'))
        else:
            return render(request, 'main/register.html', 
                    {'form': form})


def login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))

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
