from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic import TemplateView, DetailView
from django.urls import reverse
from django.utils.http import urlquote
from .forms import SearchForm
from lib.vt import VT
import os
import subprocess
import hashlib
import requests
import imgkit
import shutil
from django.db.models import Q
from apps.threat.models import Event, Attribute
from apps.reputation.models import blacklist
from apps.twitter.models import tweet
from apps.exploit.models import Exploit
from django.conf import settings

class IndexView(TemplateView):
    template_name = 'url/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchForm()
        return context

    def get(self, request, **kwargs):
        if request.GET.get('keyword'):
            url = request.GET.get('keyword')
            return HttpResponseRedirect(reverse("url:index") + urlquote(url, safe='') + '/')
        context = self.get_context_data()
        return self.render_to_response(context)

class DetailView(TemplateView):
    template_name = 'url/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchForm()
        url = self.kwargs['pk']

        response = self.getResponse(url)
        if response is not None:
            context['response_code'] = response.status_code
            if "content-type" in response.headers:
                context['content_type'] = response.headers["content-type"]
                context['response_sha256'] = self.getHash(response)
                context['title'] = self.getTitle(response)
            if "last-modified" in response.headers:
                context['last_modified'] = response.headers["last-modified"]
            if "server" in response.headers:
                context['server'] = response.headers["server"]
            if "content-length" in response.headers:
                context['content_length'] = response.headers["content-length"]
        context['imagefile'] = self.getImage(url)
        context['websrc'] = self.getSrc(url)

        vt = VT()
        context['vt_url'] = vt.getURLReport(url)

        context['bls'] = blacklist.objects.filter(Q(url__contains=url))
        count = context['bls'].count()
        if count > 0:
            context['bls_count'] = count
        context['events'] = Event.objects.filter(Q(info__icontains=url)).order_by('-publish_timestamp')
        count = context['events'].count()
        if count > 0:
            context['events_count'] = count
        context['attributes'] = Attribute.objects.filter(Q(value__icontains=url)).order_by('-timestamp')
        count = context['attributes'].count()
        if count > 0:
            context['attributes_count'] = count
        context['tws'] = tweet.objects.filter(Q(text__icontains=url)).order_by('-datetime')
        count = context['tws'].count()
        if count > 0:
            context['tws_count'] = count
        context['exs'] = Exploit.objects.filter(Q(text__icontains=url)).order_by('-datetime')
        count = context['exs'].count()
        if count > 0:
            context['exs_count'] = count

        return context

    def getResponse(self, url):
        ua = "Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv 11.0) like Gecko"
        headers = {'User-Agent': ua}
        try:
            res = requests.get(url, headers=headers, verify=False)
        except Exception as e:
            return
        res.encoding = res.apparent_encoding
        return res

    def getHash(self, res):
        if 'text/html' in res.headers["content-type"]:
            sha256 = hashlib.sha256(res.text.encode('utf-8')).hexdigest()
        else:
            sha256 = hashlib.sha256(res.content).hexdigest()
        return sha256

    def getTitle(self, res):
        title = ''
        if 'text/html' in res.headers["content-type"]:
            if '<title>' in res.text:
                title = res.text.split('<title>')[1].split('</title>')[0]
            elif '<TITLE>' in res.text:
                title = res.text.split('<TITLE>')[1].split('</TITLE>')[0]
        return title

    def getImage(self, url):
        imagehash = hashlib.md5(url.encode('utf-8')).hexdigest()
        if settings.STATIC_ROOT is None:
            filepath = settings.STATICFILES_DIRS[0] + "webimg/" + imagehash + ".png"
        else:
            filepath = settings.STATIC_ROOT + "webimg/" + imagehash + ".png"
        path = "static/webimg/" + imagehash + ".png"
        options = {
            'quiet': '',
        }
        if not os.path.exists(filepath):
            imgkit.from_url(url, filepath, options=options)
        return path

    def getSrc(self, url):
        imagehash = hashlib.md5(url.encode('utf-8')).hexdigest()
        if settings.STATIC_ROOT is None:
            filepath = settings.STATICFILES_DIRS[0] + "websrc/" + imagehash
        else:
            filepath = settings.STATIC_ROOT + "websrc/" + imagehash

        if not os.path.exists(filepath):
            ua = "Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv 11.0) like Gecko"
            headers = {
                'User-Agent': ua
            }
            try:
                res = requests.get(url, headers=headers, verify=False)
            except Exception as e:
                return
            if 'text/html' in res.headers['content-type']:
                with open(filepath, 'w') as fp:
                    fp.write(res.text)
            else:
                with open(filepath, 'wb') as fp:
                    fp.write(res.content)
        return imagehash

class CodeView(TemplateView):
    template_name = 'url/code.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if settings.STATIC_ROOT is None:
            srcpath = settings.STATICFILES_DIRS[0] + 'websrc/' + self.kwargs['pk']
        else:
            srcpath = settings.STATIC_ROOT + 'websrc/' + self.kwargs['pk']
        f = open(srcpath, 'r')
        context['websrc'] = f.read()
        f.close()
        return context

def getContents(request, pk):
    if settings.STATIC_ROOT is None:
        filepath = settings.STATICFILES_DIRS[0] + 'websrc/' + pk
    else:
        filepath = settings.STATIC_ROOT + 'websrc/' + pk
    f = open(filepath, 'rb')
    contents = f.read()
    f.close()
    response = HttpResponse(contents)
    response["Content-Disposition"] = "filename=%s" % pk
    return response
