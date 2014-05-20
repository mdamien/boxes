from functools import wraps
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from .models import Box, Idea

def auth_check(request, box):
    if box.is_access_by_email():
        if not box.key_valid(request.session.get('boxes_keys',{}).get(str(box.pk),'')):
            return False, HttpResponseRedirect(reverse('boxes.views.join', args=(box.pk,))) 
    return True, None

def box(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        box = get_object_or_404(Box, pk=kwargs['box_pk'])
        auth, redirect = auth_check(args[0], box)
        if not auth:
            return redirect
        kwargs['box'] = box
        return func(*args, **kwargs)
    return wrapper

def idea(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        idea = get_object_or_404(Idea, pk=kwargs['idea_pk'], box__pk=kwargs['box_pk'])
        auth, redirect = auth_check(args[0], idea.box)
        if not auth:
            return redirect
        kwargs['idea'] = idea
        return func(*args, **kwargs)
    return wrapper
