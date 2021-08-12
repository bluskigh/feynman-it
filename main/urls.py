from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
        path('', views.index, name='index'),
        path('profile/', views.profile, name='profile'),
        path('new_note/', views.new_note, name='new_note'),
        path('accounts/login/', views.login, name='login'),
        path('accounts/register/', views.register, name='register'),
        path('accounts/logout', views.logout, name='logout')
]
