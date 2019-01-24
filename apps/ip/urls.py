from django.conf.urls import url

from . import views

app_name = 'ip'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<pk>.+)/$', views.DetailView.as_view(), name='detail'),
]

