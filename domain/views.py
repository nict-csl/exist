from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic import TemplateView, DetailView
from .forms import SearchForm
from lib.umbrella import Umbrella
from lib.domaintools import DomainTools
from lib.geoip import GeoIP
from lib.vt import VT
from lib.threatminer import ThreatMiner
import socket
from django.db.models import Q
from threat.models import Event, Attribute
from reputation.models import blacklist
from twitter.models import tweet
from exploit.models import Exploit
from vuln.models import Vuln

class IndexView(TemplateView):
    template_name = 'domain/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchForm()
        return context

    def get(self, request, **kwargs):
        if request.GET.get('keyword'):
            domain = request.GET.get('keyword')
            return HttpResponseRedirect(domain)
        context = self.get_context_data()
        return self.render_to_response(context)

class DetailView(TemplateView):
    template_name = 'domain/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchForm()
        domain = self.kwargs['pk']
        try:
            context['geoip'] = GeoIP().lookup(domain)
        except Exception as e:
            print(e)
            pass
        try:
            context['ipaddress'] = socket.gethostbyname(domain)
        except Exception as e:
            pass

        umb = Umbrella()
        context['umbrella_dnsdb'] = umb.get_dnsdb(domain)
        context['umbrella_cname'] = umb.get_cname(domain)
        try:
            context['umbrella_score'] = umb.get_score(domain)['risk_score']
        except Exception as e:
            pass
        context['umbrella_samples'] = umb.get_samples(domain)

        dt = DomainTools()
        try:
            context['domaintools_domainprofile'] = dt.getDomainProfile(domain)['response']
        except Exception as e:
            pass
        try:
            context['domaintools_whois'] = dt.getWhois(domain)['response']['parsed_whois']
        except Exception as e:
            pass

        vt = VT()
        context['vt_domain'] = vt.getDomainReport(domain)

        tm = ThreatMiner()
        context['tm_url'] = tm.getURIFromDomain(domain)
        context['tm_sample'] = tm.getSamplesFromDomain(domain)
        context['tm_report'] = tm.getReportFromDomain(domain)

        context['bls'] = blacklist.objects.filter(Q(domain=domain)|Q(url__contains=domain))
        count = context['bls'].count()
        if count > 0:
            context['bls_count'] = count
        context['events'] = Event.objects.filter(Q(info__icontains=domain)).order_by('-publish_timestamp')
        count = context['events'].count()
        if count > 0:
            context['events_count'] = count
        context['attributes'] = Attribute.objects.filter(Q(value__icontains=domain)).order_by('-timestamp')
        count = context['attributes'].count()
        if count > 0:
            context['attributes_count'] = count
        context['tws'] = tweet.objects.filter(Q(text__icontains=domain)).order_by('-datetime')
        count = context['tws'].count()
        if count > 0:
            context['tws_count'] = count
        context['exs'] = Exploit.objects.filter(Q(text__icontains=domain)).order_by('-datetime')
        count = context['exs'].count()
        if count > 0:
            context['exs_count'] = count
        context['vus'] = Vuln.objects.filter(Q(title__icontains=domain)).order_by('-vulndb_last_modified')
        count = context['vus'].count()
        if count > 0:
            context['vus_count'] = count

        return context

