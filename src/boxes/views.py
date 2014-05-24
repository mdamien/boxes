from django.http import HttpResponseRedirect, HttpResponse
from boxes.models import Box, Idea, Vote, Comment
from django import forms
from boxes import helpers
from django.views import generic

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
        
        #TODO: Do it after pagination
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

class SettingsView(BoxMixin, generic.UpdateView):
    form_class = SettingsForm
    pk_url_kwarg = 'box_pk'
    model = Box
    template_name = 'box/settings.html'

settings = SettingsView.as_view()

class BoxLogout(BoxMixin, generic. UpdateView):
    def post(self, request, *args, **kwargs):
        keys = request.session.get('boxes_keys',{})
        if self.box.pk in keys:
            del keys[self.box.pk]
        request.session['boxes_keys'] = keys
        return HttpResponseRedirect(self.box.url())

logout = BoxLogout.as_view()

class IdeaMixin(BoxMixin):
    def dispatch(self, request, *args, **kwargs):
        self.idea = Idea.objects.get(pk=kwargs['idea_pk'])
        """
        vote = Vote.objects.filter(idea=idea, user_key=self.user_key).first()
        if vote:
            self.idea.user_vote = vote.vote
        """
        return super(IdeaMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return super(IdeaMixin, self).get_context_data(
                idea=self.idea, **kwargs)

class IdeaView(IdeaMixin, generic.TemplateView):
    template_name = 'box/idea.html'

    def post(self, request, *args, **kwargs):
        comment = Comment(idea=self.idea, user_key=self.user_key, content=request.POST.get('content'))
        comment.save()
        return self.get(request, *args, **kwargs)

idea = IdeaView.as_view()

class IdeaVote(IdeaMixin, generic.View):
    def post(self, request, *args, **kwargs):
        try:
            current_vote = Vote.objects.get(
                    user_key=self.user_key, idea=self.idea)
            current_vote.delete()
        except Vote.DoesNotExist:
            pass
        vote = Vote(idea=self.idea,
                user_key=self.user_key,
                vote=Vote.from_str(kwargs['vote']))
        vote.save()
        self.idea.update_cached_score()
        return HttpResponse(str(self.idea.score()))

idea_vote = IdeaVote.as_view()

class IdeaDelete(IdeaMixin, generic.View):
    def post(self, request, *args, **kwargs):
        self.idea.delete()
        return HttpResponseRedirect(self.idea.box.url())

idea_delete = IdeaDelete.as_view()
