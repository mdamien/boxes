from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from boxes.models import Box, Idea, Vote, Comment
from django.contrib.auth import logout as auth_logout
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.core.urlresolvers import reverse
from django.contrib import messages
from django import forms
from boxes import helpers
from django.views import generic
import hashlib

class HomepageView(generic.TemplateView):
    template_name = 'home.html'

    def post(self, request, *args, **kwargs):
        slug = helpers.randascii(4)
        box = Box(slug=slug, name="",
                user_key=request.session.session_key)
        box.save()
        messages.add_message(request, messages.SUCCESS,
                'Box created, you can now share it:  %s' % request.build_absolute_uri(box.url()))
        return HttpResponseRedirect(reverse('boxes.views.settings', args=(box.slug,)))

home = HomepageView.as_view()

class BoxMixin:
    def dispatch(self, request, *args, **kwargs):
        self.box = Box.objects.get(slug=kwargs['box_slug'])
        self.user_key = None
        if self.box.access_mode == Box.ACCESS_BY_SESSION:
            self.user_key = request.session.session_key
        if self.box.access_mode == Box.ACCESS_BY_GOOGLE and request.user.is_authenticated():
            self.user_key = hashlib.sha1(request.user.username.encode('utf-8'))
        if self.box.access_mode == Box.ACCESS_BY_EMAIL:
            if 'key' in request.GET:
                key = request.GET.get('key')
                if self.box.key_valid(key):
                    keys = request.session.get('boxes_keys', {})
                    keys[str(self.box.pk)] = key
                    request.session['boxes_keys'] = keys
            self.user_key = request.session.get('boxes_keys',{}).get(str(self.box.pk))
        result = self.pre_process(request, *args, **kwargs)
        if result:
            return result
        return super(BoxMixin, self).dispatch(request, *args, **kwargs)

    def pre_process(self, request, *args, **kwargs):
        pass

    def get_context_data(self, **kwargs):
        return super(BoxMixin, self).get_context_data(
                user_key=self.user_key, box=self.box, **kwargs)

class BoxView(BoxMixin, generic.ListView):
    template_name = 'box/home.html'
    context_object_name = 'ideas'
    
    def get_context_data(self, **kwargs):
        context = super(BoxView, self).get_context_data(
            nothing_msgs=helpers.nothing_messages,
            sort=self.kwargs['sort'], **kwargs)

        #add vote data
        ideas = context.get('ideas')
        votes = Vote.objects.filter(user_key=self.user_key)
        for idea in ideas:
            for vote in votes:
                if vote.idea_id == idea.pk:
                    idea.user_vote = vote.vote
        context['ideas'] = ideas

        return context

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
        return ideas

    def post(self, request, *args, **kwargs):
        if 'email' in request.POST:
            email = request.POST.get('email')
            try:
                key = self.box.email_register(email)
                send_mail('kioto.io: Access code for "%s"' % self.box.name,
                        request.build_absolute_uri(self.box.url() + "?key=" + key),
                        'no-reply@kioto.io', [email], fail_silently=False)
                messages.add_message(request, messages.SUCCESS, 'Access code sent to %s' % email)
            except ValidationError as e:
                messages.add_message(request, messages.ERROR, e.message)
        else:
            idea = Idea(box=self.box, title=request.POST.get('title'), 
                    user_key=self.user_key)
            idea.save()
        return self.get(request, *args, **kwargs)

box = BoxView.as_view()

class SettingsForm(forms.ModelForm): 
    class Meta:
        model = Box
        fields = ('name','access_mode','email_suffix')

    validate_hostname = RegexValidator(regex=r'[a-zA-Z0-9-_]*\.[a-zA-Z]{2,6}',
        message="Enter a valid domain name")

    def clean_email_suffix(self):
        access_mode = self.cleaned_data['access_mode']
        domain = super(SettingsForm, self).clean()
        if access_mode == Box.ACCESS_BY_EMAIL:
            self.validate_hostname(domain)

    def clean(self):
        cleaned_data = super(SettingsForm, self).clean()
        if self.instance.access_mode != cleaned_data['access_mode'] \
                and self.instance.idea_set.count() > 0:
            raise ValidationError("You can't change the access mode when there are posts in the box")
        return cleaned_data

class SettingsView(BoxMixin, generic.UpdateView):
    form_class = SettingsForm
    template_name = 'box/settings.html'

    def pre_process(self, request, *args, **kwargs):
        if request.session.session_key != self.box.user_key:
            return HttpResponseForbidden("You are not the owner of this box")

    def get_object(self, queryset=None):
        return self.box

settings = SettingsView.as_view()

class BoxLogout(BoxMixin, generic.UpdateView):
    def post(self, request, *args, **kwargs):
        if self.box.access_mode == Box.ACCESS_BY_EMAIL:
            keys = request.session.get('boxes_keys',{})
            if str(self.box.pk) in keys:
                del keys[str(self.box.pk)]
            request.session['boxes_keys'] = keys
        else:
            auth_logout(request)
        return HttpResponseRedirect(self.box.url())

logout = BoxLogout.as_view()

class IdeaMixin(BoxMixin):
    def dispatch(self, request, *args, **kwargs):
        return super(IdeaMixin, self).dispatch(request, *args, **kwargs)
    
    def pre_process(self, request, *args, **kwargs):
        self.idea = Idea.objects.get(pk=kwargs['idea_pk'])
        if self.idea.box_id != self.box.pk:
            return HttpResponseNotFound()
        vote = Vote.objects.filter(idea=self.idea, user_key=self.user_key).first()
        if vote:
            self.idea.user_vote = vote.vote

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
        if self.user_key != self.idea.user_key:
            return HttpResponseForbidden("You aren't the owner of this post")
        self.idea.delete()
        return HttpResponseRedirect(self.idea.box.url())

idea_delete = IdeaDelete.as_view()
