from django.conf.urls import patterns, include, url
from boxes.views import *

idea = patterns('boxes.views',
    url(r'vote/(?P<vote>[a-z]+)/$','vote'),
    url(r'delete/$','delete_idea'),
    url(r'$', 'idea'),
)

box = patterns('boxes.views',
    url(r'^idea/(?P<idea_pk>[0-9]+)/', include(idea)),
    url(r'join/$', 'join'),
    url(r'new/$', 'box', {'sort':'new'}, name='sort_new'),
    url(r'logout/$', 'logout'),
    url(r'$', 'box',{'sort':'top'}),
)

urlpatterns = patterns('boxes.views',
    url(r'^$', 'home'),
    url(r'^box/(?P<box_pk>[0-9]+)/', include(box)),
)
