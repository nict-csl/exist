from django.conf.urls import url

from . import views

app_name = 'filehash'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^pcap/(?P<pk>.+)/$', views.getpcap, name='getpcap'),
    url(r'^(?P<pk>.+)/$', views.DetailView.as_view(), name='detail'),
]

