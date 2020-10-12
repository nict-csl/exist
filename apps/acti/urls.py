# from django.urls import path
from django.conf.urls import url, include
from django.contrib import admin
from . import views

app_name = 'acti'
urlpatterns = [
    url(r'^$',views.index, name='index'),  # インデックス
    url(r'^add/$', views.tweet_add, name="tweet_add"),
    url(r'^get/$',views.tweet_get, name="tweet_get"),
    url(r'^tweet/',include([
        url(r'add_annotation/$',views.annotation, name='add_annotation'),
        url(r'annotation/(?P<tweet_id>[0-9]+)/$', views.tweet_edit, name='tweet_annotation'),
        url(r'view/(?P<tweet_id>[0-9]+)/$', views.tweet_view, name='tweet_view'),
        url(r'(?P<mode>.+)/$', views.TweetList.as_view(), name='tweet_list'),
    ])),
    url(r'^label/',include([
        url(r'add_label/$', views.add_label, name='add_label'),
        url(r'delete_label/$', views.delete_label, name='delete_label'),
    ]))
]
