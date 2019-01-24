from django.conf.urls import url

from . import views

app_name = 'threat'
urlpatterns = [
    #url(r'^$', views.EventListView.as_view(), name='event_list'),
    url(r'^event/$', views.EventListView.as_view(), name='event_list'),
    url(r'^event/(?P<pk>\d+)/$', views.EventDetailView.as_view(), name='event_detail'),
    url(r'^attribute/$', views.AttributeListView.as_view(), name='attribute_list'),
    url(r'^org/$', views.OrgListView.as_view(), name='org_list'),
    url(r'^tag/$', views.TagListView.as_view(), name='tag_list'),
]
