from django.conf.urls import url

from . import views

app_name = 'ip'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<pk>.+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^(?P<pk>.+)/get_vt$', views.get_context_vt, name='get_vt'),
    url(r'^(?P<pk>.+)/get_tm$', views.get_context_tm, name='get_tm'),
    url(r'^(?P<pk>.+)/get_ipvoid$', views.get_context_ipvoid, name='get_ipvoid'),
    url(r'^(?P<pk>.+)/get_abuse$', views.get_context_abuse, name='get_ipvoid'),
    url(r'^(?P<pk>.+)/get_shodan$', views.get_context_shodan, name='get_shodan'),
    url(r'^(?P<pk>.+)/get_censys$', views.get_context_censys, name='get_censys'),
]

