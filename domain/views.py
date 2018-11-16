from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic import TemplateView, DetailView
from .forms import SearchForm
from .umbrella import Umbrella
from .domaintools import DomainTools
from .geoip import GeoIP
from .vt import VT
from .threatminer import ThreatMiner
import socket

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
        except KeyError:
            pass
        context['umbrella_samples'] = umb.get_samples(domain)

        dt = DomainTools()
        try:
            context['domaintools_domainprofile'] = dt.getDomainProfile(domain)['response']
        except KeyError:
            pass
        try:
            context['domaintools_whois'] = dt.getWhois(domain)['response']['parsed_whois']
        except KeyError:
            pass

        vt = VT()
        context['vt_domain'] = vt.getDomainReport(domain)

        tm = ThreatMiner()
        context['tm_url'] = tm.getURIFromDomain(domain)
        context['tm_sample'] = tm.getSamplesFromDomain(domain)
        context['tm_report'] = tm.getReportFromDomain(domain)

        return context

