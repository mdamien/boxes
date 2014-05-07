from django.conf.urls import patterns, include, url

box = patterns('boxes.views',
    url(r'$', 'box'),
)

urlpatterns = patterns('boxes.views',
    url(r'^$', 'home'),
    url(r'^box/(?P<box_pk>\d+)/', include(box)),
)
