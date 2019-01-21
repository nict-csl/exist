"""intelligence URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from dashboard.views import IndexView, CrossView, LookupView
from . import apis

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^cross$', CrossView.as_view(), name='cross'),
    url(r'^lookup$', LookupView.as_view(), name='lookup'),
    url(r'^reputation/', include('reputation.urls')),
    url(r'^twitter/', include('twitter.urls')),
    url(r'^twitter_hunter/', include('twitter_hunter.urls')),
    url(r'^exploit/', include('exploit.urls')),
    url(r'^threat/', include('threat.urls')),
    url(r'^threat_hunter/', include('threat_hunter.urls')),
    url(r'^domain/', include('domain.urls')),
    url(r'^ip/', include('ip.urls')),
    url(r'^hash/', include('filehash.urls')),
    url(r'^url/', include('url.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(apis.router.urls)),
]
