from django.db import models
from django.contrib.auth.models import AbstractUser 

# Create your models here.
class Learner(AbstractUser):
    class Meta:
        permissions = [
                ('create_note', 'Allows for creation of note.'),
                ('delete_note', 'Allows for deletion of note.'),
                ('edit_note', 'Allows for modification of note.')
                ]
