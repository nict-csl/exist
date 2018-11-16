from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic import TemplateView
from pure_pagination.mixins import PaginationMixin
from django.db.models import Q
from threat.models import Event, Attribute
from threat.forms import EventSearchForm, AttributeSearchForm
from reputation.models import blacklist
from reputation.forms import SearchForm as ReputationSearchForm
from twitter.models import tweet
from twitter.forms import SearchForm as TwitterSearchForm
from exploit.models import Exploit
from exploit.forms import SearchForm as ExploitSearchForm
from vuln.models import Vuln
from vuln.forms import SearchForm as VulnSearchForm
from ip.forms import SearchForm as IPSearchForm
from domain.forms import SearchForm as DomainSearchForm
from url.forms import SearchForm as URLSearchForm
from filehash.forms import SearchForm as HashSearchForm
from .forms import SearchForm as CCSearchForm

class IndexView(TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cc_search_form'] = CCSearchForm()
        context['events'] = Event.objects.order_by('-publish_timestamp')[:5]
        context['event_search_form'] = EventSearchForm()
        context['attribute_search_form'] = AttributeSearchForm()
        context['bls'] = blacklist.objects.order_by('-datetime')[:5]
        context['reputation_search_form'] = ReputationSearchForm()
        context['tws'] = tweet.objects.order_by('-datetime')[:5]
        context['twitter_search_form'] = TwitterSearchForm()
        context['exs'] = Exploit.objects.order_by('-datetime')[:5]
        context['exploit_search_form'] = ExploitSearchForm()
        context['vus'] = Vuln.objects.exclude(vulndb_published_date='1999-01-01 00:00:00+09:00').order_by('-vulndb_last_modified')[:5]
        context['vuln_search_form'] = VulnSearchForm()
        context['ip_search_form'] = IPSearchForm()
        context['domain_search_form'] = DomainSearchForm()
        context['url_search_form'] = URLSearchForm()
        context['hash_search_form'] = HashSearchForm()
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

