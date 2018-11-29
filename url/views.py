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

        context['title'] = self.gettitle(url)
        context['imagefile'] = self.getimage(url)
        context['websrc'] = self.getsrc(url)

        vt = VT()
        context['vt_url'] = vt.getURLReport(url)

        return context

    def gettitle(self, url):
        res = requests.get(url, verify=False)
        res.encoding = res.apparent_encoding
        title = res.text.split('<title>')[1].split('</title>')[0]
        return title

    def getimage(self, url):
        imagehash = hashlib.md5(url.encode('utf-8')).hexdigest()
        filepath = "static/webimg/" + imagehash + ".png"
        if not os.path.exists(filepath):
            cmd = "/usr/local/bin/wkhtmltoimage " + url + " " + filepath
            subprocess.Popen(cmd, shell=True)
        return filepath

    def getsrc(self, url):
        imagehash = hashlib.md5(url.encode('utf-8')).hexdigest()
        filepath = "static/websrc/" + imagehash
        if not os.path.exists(filepath):
            ua = "Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv 11.0) like Gecko"
            cmd = "/usr/bin/wget --no-check-certificate -q --user-agent=\"" + ua + "\" -O " + filepath + " \"" + url + "\""
            subprocess.Popen(cmd, shell=True)
        return imagehash

class CodeView(TemplateView):
    template_name = 'url/code.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        srcpath = 'static/websrc/' + self.kwargs['pk']
        f = open(srcpath, 'r')
        context['websrc'] = f.read()
        f.close()
        return context
