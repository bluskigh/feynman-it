from django.db import models
from django.contrib.auth.models import AbstractUser 


class User(AbstractUser):
    pass


class Note(models.Model):
    class Meta:
        permissions = [
                ('new_note', 'Allows for creation of note.'),
                ('close_note', 'Allows for deletion of note.'),
                ('modify_note', 'Allows for modification of note.')
        ]
