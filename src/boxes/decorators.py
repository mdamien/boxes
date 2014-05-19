from functools import wraps
from django.shortcuts import get_object_or_404
from .models import Box, Idea

def box(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        box = get_object_or_404(Box, pk=kwargs['box_pk'])
        kwargs['box'] = box
        return func(*args, **kwargs)
    return wrapper

def idea(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        idea = get_object_or_404(Idea, pk=kwargs['idea_pk'], box__pk=kwargs['box_pk'])
        kwargs['idea'] = idea
        return func(*args, **kwargs)
    return wrapper
