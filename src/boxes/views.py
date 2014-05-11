from django.shortcuts import get_object_or_404,render
from django.http import HttpResponseRedirect, HttpResponse
from boxes.models import Box, Idea, Vote
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import random

def idea(request, box_pk, idea_pk):
    idea = get_object_or_404(Idea, pk=idea_pk)
    return render(request,'box/idea.html',{
        'idea':idea, 
        'box':idea.box
    })

@require_POST
def vote(request, box_pk, idea_pk, vote):
    idea = get_object_or_404(Idea, pk=idea_pk)
    session_key = request.session.session_key
    try:
        current_vote = Vote.objects.get(session_key=session_key, idea=idea)
        current_vote.delete()
    except Vote.DoesNotExist:
        pass
    vote = Vote(idea=idea, session_key=session_key, vote=Vote.from_str(vote))
    vote.save()
    idea.update_cached_score()
    return HttpResponse(str(idea.score()))

def box(request, box_pk, sort='top'):
    box = get_object_or_404(Box, pk=box_pk)
    ideas = Idea.objects.filter(box=box)
    if sort is 'top':
        ideas = ideas.order_by('-cached_score')
    elif sort == 'new':
        ideas = ideas.order_by('-date')
    
    if request.method == 'POST':
        idea = Idea(box=box, title=request.POST.get('title'))
        idea.save()
        #todo: redirect to idea

    #pagination
    paginator = Paginator(ideas, 100)
    page = request.GET.get('page')
    try:
        ideas = paginator.page(page)
    except PageNotAnInteger:
        ideas = paginator.page(1)
    except EmptyPage:
        ideas = paginator.page(paginator.num_pages)

    #add user current vote
    session_key = request.session.session_key
    votes = Vote.objects.filter(session_key=session_key)
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
        box = Box(pk=random.randint(1,100000),name=request.POST.get('name'))
        box.save()
        return HttpResponseRedirect(box.url())
    return render(request,'home.html')

