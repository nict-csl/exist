from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import urlquote
from django.views.generic import TemplateView
from django.views import View
from pure_pagination.mixins import PaginationMixin
from django.db.models import Q
from threat.models import Event, Attribute
from reputation.models import blacklist
from twitter.models import tweet
from exploit.models import Exploit
#from .forms import CCSearchForm, LookupForm
from .forms import SearchForm
import ipaddress
import re

class IndexView(TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchForm()
        context['events'] = Event.objects.order_by('-publish_timestamp')[:5]
        context['bls'] = blacklist.objects.order_by('-datetime')[:5]
        context['tws'] = tweet.objects.order_by('-datetime')[:5]
        context['exs'] = Exploit.objects.order_by('-datetime')[:5]
        return context

class CrossView(TemplateView):
    template_name = 'dashboard/cross.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchForm(self.request.GET)
        keyword = self.request.GET.get('keyword')
        if keyword is not None:
            context['bls'] = blacklist.objects.filter(Q(ip=keyword)|Q(domain__contains=keyword)|Q(url__contains=keyword))
            count = context['bls'].count()
            if count > 0:
                context['bls_count'] = count
            context['events'] = Event.objects.filter(Q(info__icontains=keyword)).order_by('-publish_timestamp')
            count = context['events'].count()
            if count > 0:
                context['events_count'] = count
            context['attributes'] = Attribute.objects.filter(Q(value__icontains=keyword)).order_by('-timestamp')
            count = context['attributes'].count()
            if count > 0:
                context['attributes_count'] = count
            context['tws'] = tweet.objects.filter(Q(text__icontains=keyword)).order_by('-datetime')
            count = context['tws'].count()
            if count > 0:
                context['tws_count'] = count
            context['exs'] = Exploit.objects.filter(Q(text__icontains=keyword)).order_by('-datetime')
            count = context['exs'].count()
            if count > 0:
                context['exs_count'] = count
        return context

class LookupView(View):
    def get(self, request, **kwargs):
        value = request.GET.get('keyword')
        if self.is_valid_ip(value):
            return redirect('ip:detail', pk=value)
        elif self.is_valid_domain(value):
            return redirect('domain:detail', pk=value)
        elif self.is_valid_url(value):
            return HttpResponseRedirect(reverse("url:index") + urlquote(value, safe='') + '/')
        elif self.is_valid_hash(value):
            return redirect('filehash:detail', pk=value)
        else:
            return redirect('/cross?keyword=' + value)
        return redirect('index')

    def is_valid_ip(self, value):
        try:
            ipaddress.ip_address(value)
            return True
        except ValueError:
            return False

    def is_valid_domain(self, value):
        compiled_pattern = re.compile('\w+\.\w+')
        if compiled_pattern.match(value):
            return True
        else:
            return False

    def is_valid_url(self, value):
        compiled_pattern = re.compile('http(s)?://\w+')
        if compiled_pattern.match(value):
            return True
        else:
            return False

    def is_valid_hash(self, value):
        compiled_pattern_md5 = re.compile(r'(?=(\b[a-fA-F0-9]{32}\b))')
        compiled_pattern_sha1 = re.compile(r'(?=(\b[a-fA-F0-9]{40}\b))')
        compiled_pattern_sha256 = re.compile(r'(?=(\b[a-fA-F0-9]{64}\b))')
        if compiled_pattern_md5.match(value) or compiled_pattern_sha1.match(value) or compiled_pattern_sha256.match(value):
            return True
        else:
            return False
