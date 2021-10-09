from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
        path('', views.home, name='home'),
        path('dashboard/', views.dashboard, name='dashboard'),
        path('profile/', views.profile, name='profile'),
        path('get_heatmap/', views.get_heatmap, name='get_heatmap'),
        path('notes/', views.notes, name='notes'),
        path('new_note/', views.new_note, name='new_note'),
        path('notes/<int:id>/', views.view_note, name='view_note'),
        path('notes/<int:id>/edit/', views.edit_note, name='edit_note'),
        path('iterations/', views.iterations, name='iterations'),
        path('iterations/<int:id>/', views.iteration, name='iteration'),
        path('links/', views.links, name='links'),
        path('links/<int:id>/', views.link, name='link'),
        path('folders/', views.folders, name='folders'),
        path('new_folder/', views.new_folder, name='new_folder'),
        path('folders/<int:id>/', views.view_folder, name='view_folder'),
        path('folders/<int:id>/delete/', views.delete_folder, name='delete_folder'),

        path('login-result/', views.login_result, name='login-result'),
        path('logout/', views.logout, name='logout')
]
