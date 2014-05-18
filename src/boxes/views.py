from django.shortcuts import get_object_or_404,render
from django.http import HttpResponseRedirect, HttpResponse
from boxes.models import Box, Idea, Vote, Comment
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
import random

def join(request, box_pk):
    box = get_object_or_404(Box, pk=box_pk)
    return render(request, 'box/join.html', { 'box': box })

def idea(request, box_pk, idea_pk):
    idea = get_object_or_404(Idea, pk=idea_pk)
    session_key = request.session.session_key
    vote = Vote.objects.filter(idea=idea, access_key=session_key).first()

    if request.method == 'POST':
        comment = Comment(idea=idea, session_key=session_key, content=request.POST.get('content'))
        comment.save()

    if vote:
        idea.user_vote = vote.vote
    return render(request,'box/idea.html',{
        'idea':idea, 
        'box':idea.box
    })

@require_POST
def delete_idea(request, box_pk, idea_pk):
    idea = get_object_or_404(Idea, pk=idea_pk)
    idea.delete()
    return HttpResponseRedirect(box.url())

@require_POST
def vote(request, box_pk, idea_pk, vote):
    idea = get_object_or_404(Idea, pk=idea_pk)
    session_key = request.session.session_key
    try:
        current_vote = Vote.objects.get(access_key=session_key, idea=idea)
        current_vote.delete()
    except Vote.DoesNotExist:
        pass
    vote = Vote(idea=idea, access_key=session_key, vote=Vote.from_str(vote))
    vote.save()
    idea.update_cached_score()
    return HttpResponse(str(idea.score()))

def box(request, box_pk, sort='top'):
    box = get_object_or_404(Box, pk=box_pk)
    ideas = Idea.objects.filter(box=box)

    if box.access_mode == Box.ACCESS_BY_EMAIL:
        return HttpResponseRedirect(reverse('boxes.views.join', args=(box.pk,))) 

    if sort is 'top':
        ideas = ideas.order_by('-cached_score','-date')
    elif sort == 'new':
        ideas = ideas.order_by('-date')
    
    session_key = request.session.session_key
    
    if request.method == 'POST':
        idea = Idea(box=box, title=request.POST.get('title'), session_key=session_key)
        idea.save()
        #return HttpResponseRedirect(idea.url())

    #pagination
    paginator = Paginator(ideas, 10)
    page = request.GET.get('page')
    try:
        ideas = paginator.page(page)
    except PageNotAnInteger:
        ideas = paginator.page(1)
    except EmptyPage:
        ideas = paginator.page(paginator.num_pages)

    #add user current vote
    votes = Vote.objects.filter(access_key=session_key)
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
        pk = random.randint(1,100000)
        name = request.POST.get('name')
        if request.POST.get('access-method') == 'email':
            box = Box(pk=pk,name=name, access_mode=Box.ACCESS_BY_EMAIL,
                    email_suffix=request.POST.get('email-suffix'))
        else:
            box = Box(pk=pk,name=name)
        box.save()
        return HttpResponseRedirect(box.url())
    return render(request,'home.html')

