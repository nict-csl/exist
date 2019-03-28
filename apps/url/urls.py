from django.conf.urls import url

from . import views

app_name = 'url'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^code/(?P<pk>\w{32})/$', views.CodeView.as_view(), name='code'),
    url(r'^code/.+/$', views.IndexView.as_view(), name='index'),
    url(r'^download/(?P<pk>\w{32})/$', views.getContents, name='getcontents'),
    url(r'^download/.+/$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<pk>.+)/$', views.DetailView.as_view(), name='detail'),
]

