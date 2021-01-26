from django.conf.urls import url

from . import views

app_name = 'filehash'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^pcap/(?P<pk>.+)/$', views.getpcap, name='getpcap'),
    url(r'^(?P<pk>.+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^(?P<pk>.+)/get_vt$', views.get_context_vt, name='get_vt'),
    url(r'^(?P<pk>.+)/get_tm$', views.get_context_tm, name='get_tm'),
]

