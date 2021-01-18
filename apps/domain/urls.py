from django.conf.urls import url

from . import views

app_name = 'domain'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<pk>.+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^(?P<pk>.+)/update_vt$', views.update_context_vt, name='update_vt'),
    url(r'^(?P<pk>.+)/update_tm$', views.update_context_tm, name='update_tm'),
]

