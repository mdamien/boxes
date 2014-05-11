from django.conf.urls import patterns, include, url

idea = patterns('boxes.views',
    url(r'$', 'idea'),
    url(r'vote/(?P<vote>[a-z]+)/$','vote'),
)

box = patterns('boxes.views',
    url(r'^idea/(?P<idea_pk>[0-9]+)/', include(idea)),
    url(r'$', 'box'),
)

urlpatterns = patterns('boxes.views',
    url(r'^$', 'home'),
    url(r'^box/(?P<box_pk>[0-9]+)/', include(box)),
)
