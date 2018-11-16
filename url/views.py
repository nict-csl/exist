from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic import TemplateView, DetailView
from django.urls import reverse
from django.utils.http import urlquote
from .forms import SearchForm
from .vt import VT
import os
import subprocess
import hashlib

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

        print(url)
        image = self.getimage(url)
        context['imagefile'] = image

        vt = VT()
        context['vt_url'] = vt.getURLReport(url)

        return context

    def getimage(self, url):
        imagehash = hashlib.md5(url.encode('utf-8')).hexdigest()
        filepath = "url/images/" + imagehash + ".png"
        print(filepath)
        if not os.path.exists(filepath):
            print(filepath + " is not exist")
            cmd = "/usr/local/bin/wkhtmltoimage " + url + " " + filepath
            print(cmd)
            subprocess.Popen(cmd, shell=True)
        return filepath
