from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from boxes.models import Box, Idea, Vote, Comment
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.contrib import messages
from boxes import helpers
from boxes import decorators

@decorators.box
def join(request, box_pk, box=None):
    if request.method == 'POST':
        if request.POST.get('request-key'):
            email = request.POST.get('email')
            try:
                key = box.email_register(email)
                send_mail('kioto.io: Access code for "%s"' % box.name,key,
                      'no-reply@kioto.io',[email], fail_silently=False)
                messages.add_message(request, messages.SUCCESS, 'Access code sent to %s' % email)
            except ValidationError as e:
                messages.add_message(request, messages.ERROR, e.message)
        else:
            if box.key_valid(request.POST.get('key')):
                keys = request.session.get('boxes_keys',{})
                keys[box.pk] = request.POST.get('key')
                request.session['boxes_keys'] = keys
                return HttpResponseRedirect(box.url())
            else:
                messages.add_message(request, messages.ERROR, 'Invalid access code')

    return render(request, 'box/join.html', { 'box': box, 'hide_logout':True})

@decorators.idea
def idea(request, box_pk, idea_pk, idea=None):
    session_key = request.session.session_key
    vote = Vote.objects.filter(idea=idea, user_key=session_key).first()

    if request.method == 'POST':
        comment = Comment(idea=idea, user_key=session_key, content=request.POST.get('content'))
        comment.save()

    if vote:
        idea.user_vote = vote.vote
    return render(request,'box/idea.html',{
        'idea':idea, 
        'box':idea.box
    })

@require_POST
@decorators.box
def logout(request, box_pk, box=None):
    keys = request.session.get('boxes_keys',{})
    if box_pk in keys:
        del keys[box_pk]
    request.session['boxes_keys'] = keys
    return HttpResponseRedirect(box.url())

@require_POST
@decorators.idea
def delete_idea(request, box_pk, idea_pk, idea=None):
    idea.delete()
    return HttpResponseRedirect(idea.box.url())

@require_POST
@decorators.idea
def vote(request, box_pk, idea_pk, vote, idea=None):
    session_key = request.session.session_key
    try:
        current_vote = Vote.objects.get(user_key=session_key, idea=idea)
        current_vote.delete()
    except Vote.DoesNotExist:
        pass
    vote = Vote(idea=idea, user_key=session_key, vote=Vote.from_str(vote))
    vote.save()
    idea.update_cached_score()
    return HttpResponse(str(idea.score()))

@decorators.box
def box(request, box_pk, sort='top', box=None):
    ideas = Idea.objects.filter(box=box) 
    session_key = request.session.session_key
    if request.method == 'POST':
        idea = Idea(box=box, title=request.POST.get('title'), user_key=session_key)
        idea.save()

    if sort is 'top':
        ideas = ideas.order_by('-cached_score','-date')
    elif sort == 'new':
        ideas = ideas.order_by('-date')
    elif sort == 'hot':
        ideas = list(ideas.order_by('-date')[:200])
        for idea in ideas:
            idea.hot_score = idea.compute_hot_score()
        ideas.sort(key=lambda x: x.hot_score, reverse=True)
    

    #pagination
    paginator = Paginator(ideas, 40)
    page = request.GET.get('page')
    try:
        ideas = paginator.page(page)
    except PageNotAnInteger:
        ideas = paginator.page(1)
    except EmptyPage:
        ideas = paginator.page(paginator.num_pages)

    #add user current vote
    votes = Vote.objects.filter(user_key=session_key)
    for idea in ideas:
        for vote in votes:
            if vote.idea_id == idea.pk:
                idea.user_vote = vote.vote

    return render(request,'box/home.html',{
        'box':box,    
        'ideas':ideas,
        'sort':sort,
    })


def home(request):
    if request.method == 'POST':
        slug = helpers.randascii(6)
        name = request.POST.get('name')
        if request.POST.get('access-method') == 'email':
            box = Box(slug=slug,name=name, access_mode=Box.ACCESS_BY_EMAIL,
                    email_suffix=request.POST.get('email-suffix'))
            messages.add_message(request, messages.SUCCESS, 
            'Box successfully created, now you need to request an access code')
        else:
            box = Box(slug=slug,name=name)
        box.save()
        return HttpResponseRedirect(box.url())
    return render(request,'home.html')

