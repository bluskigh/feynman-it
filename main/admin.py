from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Permission

from .models import User, Note, Folder, Link, Iteration

admin.site.register(User, UserAdmin)
admin.site.register(Permission)
admin.site.register(Note)
admin.site.register(Folder)
admin.site.register(Link)
admin.site.register(Iteration)
