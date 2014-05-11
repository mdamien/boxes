from django.shortcuts import get_object_or_404,render
from django.http import HttpResponseRedirect
from boxes.models import Box, Idea
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import random

def idea(request, box_pk, idea_pk):
    idea = get_object_or_404(Idea, pk=idea_pk)
    return render(request,'box/idea.html',{
        'idea':idea, 
        'box':idea.box
    })

def vote_to_int(vote):
    return {'up':1,'down':-1}[vote]

@require_POST
@csrf_exempt
def vote(request, box_pk, idea_pk, vote):
    idea = get_object_or_404(Idea, pk=idea_pk)
    votes = request.session.get('votes', {})
    if idea_pk in votes:
        idea.score -= vote_to_int(votes[idea.pk])
    votes[idea_pk] = vote
    idea.score += vote_to_int(vote)
    idea.save()
    request.session['votes'] = votes

def box(request, box_pk):
    box = get_object_or_404(Box, pk=box_pk)
    ideas = Idea.objects.filter(box=box).order_by('-score')
    if request.method == 'POST':
        if 'submit_idea' in request.POST:
            idea = Idea(box=box, title=request.POST.get('title'))
            idea.save()
    votes = request.session.get('votes',{})
    for idea in ideas:
        if idea.pk in votes:
            idea.user_vote = votes.get(idea.pk)
    return render(request,'box/home.html',{
        'box':box,    
        'ideas':ideas,
    })

def home(request):
    if request.method == 'POST':
        box = Box(pk=random.randint(1,100000),name=request.POST.get('name'))
        box.save()
        return HttpResponseRedirect(box.url())
    return render(request,'home.html')

