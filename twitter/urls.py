from django.conf.urls import url

from . import views

app_name = 'twitter'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^ajax/expand_url/$', views.expand_url, name='expand_url'),
]

