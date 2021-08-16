from django import template 
from django.urls import reverse

from json import dumps

register = template.Library()

@register.filter(name='get_path')
def get_path(value):
    value =  value.lower()
    # path is simple, just the name
    if value in ['folders', 'notes', 'login', 'register', 'logout']:
        return reverse(value)


@register.simple_tag
def define(authenticated=None):
    """Returns a list of lis to be displayed if the user is authenticated"""
    if authenticated:
        return ['Folders', 'Notes', 'Logout']
    else:
        return ['Login', 'Register']


@register.filter(name='has_permission')
def has_permission(user, permission):
    return user.has_perm(permission)
 

@register.filter(name='get_value')
def get_value(value, index):
    try:
        return value[index]
    except Exception as e:
        return []


@register.filter(name='to_string')
def to_string(value):
    return dumps(value)
