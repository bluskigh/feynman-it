from datetime import date 

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser 
from django.contrib.postgres.fields import ArrayField


class User(AbstractUser):
    sub = models.CharField(max_length=64, default=None, null=True)


class Folder(models.Model):
    title = models.CharField(max_length=64)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='folders')

    def basic_information(self):
        return {'id': self.id, 'title': self.title, 'owner': self.owner, 'notes_length': self.folder_notes.count()}


class Note(models.Model):
    # title of the note
    title = models.CharField(blank=True, max_length=64)
    # step three text
    step_three = models.TextField(blank=True)
    # does user understand new note
    understand = models.BooleanField(default=False)
    # who owns the note
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes', default=None, null=True)
    # what folder is it in
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='folder_notes', default=None, null=True)
    created = models.DateField(auto_now_add=True)

    def basic_information(self):
        return {'id': self.id, 'title': self.title, 'understand': self.understand}

    def more_information(self):
        return {
            'id': self.id, 
            'title': self.title, 
            'folder_title': self.folder.title,
            'step_one_iterations': [iteration.basic_information() for iteration in self.step_one_iterations.all().order_by('id')],
            'step_two_iterations': [iteration.basic_information() for iteration in self.step_two_iterations.all().order_by('id')], 
            'step_three': self.step_three,
            'general_links': [link.basic_information() for link in self.general_links.all().order_by('id')],
            'understand': self.understand, 
            'owner': self.owner}


class Iteration(models.Model):
    """Iteration layout: (x) {{ title }} \n {{ text }}"""
    title = models.CharField(blank=True, max_length=84)
    text = models.TextField(blank=True)
    # either of these below can be blank 
    note_step_one = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='step_one_iterations', null=True)
    note_step_two = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='step_two_iterations', null=True)
    def basic_information(self):
        return {'title': self.title, 'text': self.text, 'note_step_one': self.note_step_one, 'note_step_two': self.note_step_two, 'id': self.id, 'links': [link.basic_information() for link in self.links.all()]}


class Link(models.Model):
    """Two foreign keys: iteration link belongs to, and note"""
    title = models.CharField(blank=True, max_length=64)
    href = models.TextField(blank=True) 
    which_iteration = models.ForeignKey(Iteration, on_delete=models.CASCADE, related_name='links', null=True)
    # apart of the note itself since its a general link, applies to all iterations
    general = models.ForeignKey(Note, blank=True, on_delete=models.CASCADE, related_name='general_links', null=True)
    # note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='links', null=True)
    def basic_information(self):
        return {'id': self.id, 'title': self.title, 'href': self.href, 'which_iteration': self.which_iteration, 'general': self.general}
