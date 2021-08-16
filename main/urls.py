from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
        path('', views.index, name='index'),
        path('notes/', views.notes, name='notes'),
        path('new_note/', views.new_note, name='new_note'),
        path('notes/<int:id>', views.view_note, name='view_note'),
        path('notes/<int:id>/edit', views.edit_note, name='edit_note'),
        path('folders/', views.folders, name='folders'),
        path('new_folder/', views.new_folder, name='new_folder'),
        path('folders/<int:id>', views.view_folder, name='view_folder'),
        path('accounts/login/', views.login, name='login'),
        path('accounts/register/', views.register, name='register'),
        path('accounts/logout', views.logout, name='logout')
]
