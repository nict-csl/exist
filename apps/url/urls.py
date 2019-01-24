from django.conf.urls import url

from . import views

app_name = 'url'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^code/(?P<pk>.+)/$', views.CodeView.as_view(), name='code'),
    url(r'^download/(?P<pk>.+)/$', views.getContents, name='getcontents'),
    url(r'^(?P<pk>.+)/$', views.DetailView.as_view(), name='detail'),
]

