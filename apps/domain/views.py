from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views.generic import TemplateView, DetailView
from .forms import SearchForm
from lib.geoip import GeoIP
from lib.vt import VT
from lib.threatminer import ThreatMiner
import socket
import re
from django.db.models import Q
from apps.threat.models import Event, Attribute
from apps.reputation.models import blacklist
from apps.twitter.models import tweet
from apps.exploit.models import Exploit
from logging import getLogger

logger = getLogger('command')

class IndexView(TemplateView):
    template_name = 'domain/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchForm()
        return context

    def get(self, request, **kwargs):
        if request.GET.get('keyword'):
            domain = request.GET.get('keyword')
            if self.is_valid_domain(domain):
                return HttpResponseRedirect(domain)
            else:
                return redirect('domain:index')
        context = self.get_context_data()
        return self.render_to_response(context)

    def is_valid_domain(self, value):
        compiled_pattern = re.compile('\w+\.\w+')
        if compiled_pattern.match(value):
            return True
        else:
            return False

class DetailView(TemplateView):
    template_name = 'domain/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchForm()
        domain = self.kwargs['pk']
        try:
            context['geoip'] = GeoIP().lookup(domain)
        except Exception as e:
            logger.error(e)
        try:
            context['ipaddress'] = socket.gethostbyname(domain)
        except Exception as e:
            logger.error(e)

        try:
            context['vt_domain'] = VT().getDomainReport(domain)
        except Exception as e:
            logger.error(e)

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

        return context

def get_context_vt(request, **kwargs):
    domain = kwargs['pk']
    context = {}
    try:
        context['vt_domain'] = VT().getDomainReport(domain)
    except Exception as e:
        logger.error(e)
    return render(request, 'domain/virustotal.html', context)

def get_context_tm(self, **kwargs):
    domain = kwargs['pk']
    context = {}
    tm = ThreatMiner()
    try:
        context['tm_url'] = tm.getURIFromDomain(domain)
        context['tm_sample'] = tm.getSamplesFromDomain(domain)
        context['tm_report'] = tm.getReportFromDomain(domain)
    except Exception as e:
        logger.error(e)
    return render(request, 'domain/threatminer.html', context)
