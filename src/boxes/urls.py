from django.conf.urls import patterns, include, url

idea = patterns('boxes.views',
    url(r'vote/(?P<vote>[a-z]+)/$','idea_vote', name='idea_vote'),
    url(r'delete/$','idea_delete', name='idea_delete'),
    url(r'$', 'idea', name='idea_view'),
)

box = patterns('boxes.views',
    url(r'^post/(?P<idea_pk>[0-9]+)/', include(idea)),
    url(r'new/$', 'box', {'sort':'new'}, name='list_new'),
    url(r'top/$', 'box', {'sort':'top'}, name='list_top'),
    url(r'settings/$', 'settings', name='settings'),
    url(r'logout/$', 'logout', name='logout'),
    url(r'$', 'box',{'sort':'hot'}, name='view'),
)

urlpatterns = patterns('boxes.views',
    url(r'^$', 'home', name='homepage'),
    url(r'^box/(?P<box_slug>[0-9A-Za-z]+)/', include(box)),
)
