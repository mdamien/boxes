from django.conf.urls import patterns, include, url

idea = patterns('boxes.views',
    url(r'vote/(?P<vote>[a-z]+)/$','vote'),
    url(r'delete/$','delete_idea'),
    url(r'$', 'idea'),
)

box = patterns('boxes.views',
    url(r'^post/(?P<idea_pk>[0-9]+)/', include(idea)),
    url(r'join/$', 'join'),
    url(r'new/$', 'box', {'sort':'new'}, name='sort_new'),
    url(r'top/$', 'box', {'sort':'top'}, name='sort_top'),
    url(r'settings/$', 'settings'),
    url(r'logout/$', 'logout'),
    url(r'$', 'box',{'sort':'hot'}),
)

urlpatterns = patterns('boxes.views',
    url(r'^$', 'home'),
    url(r'^box/(?P<box_pk>[0-9]+)/', include(box)),
)
