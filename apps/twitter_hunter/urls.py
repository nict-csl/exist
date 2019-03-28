from django.conf.urls import url

from . import views

app_name = 'twitter_hunter'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^add/$', views.HuntCreateView.as_view(), name='hunt_create'),
    url(r'^(?P<pk>\d+)/edit/$', views.HuntUpdateView.as_view(), name='hunt_edit'),
    url(r'^(?P<pk>\d+)/csv/$', views.hunt_export, name='hunt_export'),
    url(r'^(?P<pk>\d+)/switch_notice/$', views.hunt_switch_notice, name='hunt_switch_notice'),
    url(r'^(?P<pk>\d+)/switch_enable/$', views.hunt_switch_enable, name='hunt_switch_enable'),
    url(r'^ajax/expand_url/$', views.expand_url, name='expand_url'),
    url(r'^(?P<pk>\d+)/$', views.TweetsView.as_view(), name='tweets'),
]

