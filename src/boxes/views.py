from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from boxes.models import Box, Idea, Vote, Comment
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.contrib import messages
from django import forms
from boxes import helpers
from boxes import decorators
from django.views import generic

@decorators.idea
def idea(request, box_pk, idea_pk, idea=None):
    user_key = request.session.session_key
    vote = Vote.objects.filter(idea=idea, user_key=user_key).first()
    if request.method == 'POST':
        comment = Comment(idea=idea, user_key=user_key, content=request.POST.get('content'))
        comment.save()

    if vote:
        idea.user_vote = vote.vote
    return render(request,'box/idea.html',{
        'idea':idea, 
        'box':idea.box,
        'user_key':user_key,
    })

@require_POST
@decorators.box
def logout(request, box_pk, box=None, user_key=None):
    keys = request.session.get('boxes_keys',{})
    if box_pk in keys:
        del keys[box_pk]
    request.session['boxes_keys'] = keys
    return HttpResponseRedirect(box.url())

@require_POST
@decorators.idea
def idea_delete(request, box_pk, idea_pk, idea=None, user_key=None):
    idea.delete()
    return HttpResponseRedirect(idea.box.url())

@require_POST
@decorators.idea
def idea_vote(request, box_pk, idea_pk, vote, idea=None, user_key=None):
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

class HomepageView(generic.TemplateView):
    template_name = 'home.html'

    def post(self, request, *args, **kwargs):
        slug = helpers.randascii(6)
        box = Box(slug=slug,name="My discussion box")
        box.save()
        return HttpResponseRedirect(box.url())

home = HomepageView.as_view()

class BoxMixin:
    def dispatch(self, request, *args, **kwargs):
        self.box = Box.objects.get(pk=kwargs['box_pk'])
        self.user_key = request.session.session_key
        return super(BoxMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return super(BoxMixin, self).get_context_data(
                box=self.box, **kwargs)

class BoxView(BoxMixin, generic.ListView):
    template_name = 'box/home.html'
    context_object_name = 'ideas'
    
    def get_context_data(self, **kwargs):
        return super(BoxView, self).get_context_data(
            sort=self.kwargs['sort'], **kwargs)

    def get_queryset(self):
        ideas = Idea.objects.filter(box=self.box) 
        sort = self.kwargs['sort']
        if sort is 'top':
            ideas = ideas.order_by('-cached_score','-date')
        elif sort == 'new':
            ideas = ideas.order_by('-date')
        elif sort == 'hot':
            ideas = list(ideas.order_by('-date')[:200])
            for idea in ideas:
                idea.hot_score = idea.compute_hot_score()
            ideas.sort(key=lambda x: x.hot_score, reverse=True)
        
        #add user current vote
        votes = Vote.objects.filter(user_key=self.user_key)
        for idea in ideas:
            for vote in votes:
                if vote.idea_id == idea.pk:
                    idea.user_vote = vote.vote
        
        return ideas

    def post(self, request, *args, **kwargs):
        idea = Idea(box=self.box, title=request.POST.get('title'), 
                user_key=self.user_key)
        idea.save()
        return self.get(request, *args, **kwargs)

box = BoxView.as_view()

class SettingsForm(forms.ModelForm): 
    class Meta:
        model = Box
        fields = ('name','access_mode','email_suffix')

class SettingsView(generic.UpdateView):
    form_class = SettingsForm
    pk_url_kwarg = 'box_pk'
    model = Box
    template_name = 'box/settings.html'

settings = SettingsView.as_view()
