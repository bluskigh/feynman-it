from django import template 
from django.urls import reverse

from json import dumps

register = template.Library()

@register.filter(name='get_path')
def get_path(value):
    value =  value.lower()
    if value in ['profile', 'login', 'register', 'logout']:
        return reverse(value)
    elif value == 'notes':
        return reverse('index')


@register.simple_tag
def define(authenticated=None):
    if authenticated:
        return ['Notes', 'Profile', 'Logout']
    else:
        return ['Login', 'Register']


@register.filter(name='has_permission')
def has_permission(user, permission):
    return user.has_perm(permission)
 

@register.filter(name='get_value')
def get_value(value, index):
    return value[index]


@register.filter(name='to_string')
def to_string(value):
    return dumps(value)
