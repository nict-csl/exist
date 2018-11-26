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
from vuln.models import Vuln
from .forms import CCSearchForm, LookupForm, LookupChoiceForm

class IndexView(TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cc_search_form'] = CCSearchForm()
        context['lookup_form'] = LookupForm()
        context['lookup_choice_form'] = LookupChoiceForm()
        context['events'] = Event.objects.order_by('-publish_timestamp')[:5]
        context['bls'] = blacklist.objects.order_by('-datetime')[:5]
        context['tws'] = tweet.objects.order_by('-datetime')[:5]
        context['exs'] = Exploit.objects.order_by('-datetime')[:5]
        context['vus'] = Vuln.objects.exclude(vulndb_published_date='1999-01-01 00:00:00+09:00').order_by('-vulndb_last_modified')[:5]
        return context

class CrossView(TemplateView):
    template_name = 'dashboard/cross.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cc_search_form'] = CCSearchForm(self.request.GET)
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
            context['vus'] = Vuln.objects.filter(Q(title__icontains=keyword)|Q(nvds__id=keyword)).order_by('-vulndb_last_modified')
            count = context['vus'].count()
            if count > 0:
                context['vus_count'] = count
        return context

class LookupView(View):
    def get(self, request, **kwargs):
        lookup_type = request.GET.get('lookup_type')
        value = request.GET.get('value')
        if lookup_type == 'ip':
            return redirect('ip:detail', pk=value)
        elif lookup_type == 'domain':
            return redirect('domain:detail', pk=value)
        elif lookup_type == 'url':
            return HttpResponseRedirect(reverse("url:index") + urlquote(value, safe='') + '/')
        elif lookup_type == 'hash':
            return redirect('filehash:detail', pk=value)
        return redirect('index')
