from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views.generic import TemplateView, DetailView
from .forms import SearchForm
from lib.geoip import GeoIP
from lib.vt import VT
from lib.threatminer import ThreatMiner
from lib.abuse import AbuseIPDB
from lib.shodan import Shodan
from lib.censys import Censys
from lib.ipvoid import IPVoid
import socket
import ipaddress
from django.db.models import Q
from apps.threat.models import Event, Attribute
from apps.reputation.models import blacklist
from apps.twitter.models import tweet
from apps.exploit.models import Exploit
from logging import getLogger

logger = getLogger('command')

class IndexView(TemplateView):
    template_name = 'ip/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchForm()
        return context

    def get(self, request, **kwargs):
        if request.GET.get('keyword'):
            ip = request.GET.get('keyword')
            if self.is_valid_ip(ip):
                return HttpResponseRedirect(ip)
            else:
                return redirect('ip:index')
        context = self.get_context_data()
        return self.render_to_response(context)

    def is_valid_ip(self, value):
        try:
            ipaddress.ip_address(value)
            return True
        except ValueError:
            return False

class DetailView(TemplateView):
    template_name = 'ip/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchForm()
        ip = self.kwargs['pk']

        try:
            context['geoip'] = GeoIP().lookup(ip)
        except Exception as e:
            logger.error(e)

        try:
            context['domain'] = socket.gethostbyaddr(ip)[0]
        except Exception as e:
            logger.error(e)

        try:
            vt = VT()
            context['vt_ip'] = vt.getIPReport(ip)
        except Exception as e:
            logger.error(e)

        context['bls'] = blacklist.objects.filter(Q(ip=ip)|Q(url__contains=ip))
        count = context['bls'].count()
        if count > 0:
            context['bls_count'] = count
        context['events'] = Event.objects.filter(Q(info__icontains=ip)).order_by('-publish_timestamp')
        count = context['events'].count()
        if count > 0:
            context['events_count'] = count
        context['attributes'] = Attribute.objects.filter(Q(value__icontains=ip)).order_by('-timestamp')
        count = context['attributes'].count()
        if count > 0:
            context['attributes_count'] = count
        context['tws'] = tweet.objects.filter(Q(text__icontains=ip)).order_by('-datetime')
        count = context['tws'].count()
        if count > 0:
            context['tws_count'] = count
        context['exs'] = Exploit.objects.filter(Q(text__icontains=ip)).order_by('-datetime')
        count = context['exs'].count()
        if count > 0:
            context['exs_count'] = count

        return context

def get_context_vt(request, **kwargs):
    ip = kwargs['pk']
    context = {}
    try:
        vt = VT()
        context['vt_ip'] = vt.getIPReport(ip)
    except Exception as e:
        logger.error(e)
    return render(request, 'ip/virustotal.html', context)

def get_context_tm(request, **kwargs):
    ip = kwargs['pk']
    context = {}
    try:
        tm = ThreatMiner()
        context['tm_url'] = tm.getURIFromIP(ip)
        context['tm_sample'] = tm.getSamplesFromIP(ip)
        context['tm_report'] = tm.getReportFromIP(ip)
    except Exception as e:
        logger.error(e)
    return render(request, 'ip/threatminer.html', context)

def get_context_ipvoid(request, **kwargs):
    ip = kwargs['pk']
    context = {}
    try:
        ipvoid = IPVoid()
        context['ipvoid'] = ipvoid.getResultFromIP(ip)
    except Exception as e:
        logger.error(e)
    return render(request, 'ip/ipvoid.html', context)

def get_context_abuse(request, **kwargs):
    ip = kwargs['pk']
    context = {}
    try:
        abuse = AbuseIPDB()
        context['abuse_ip'] = abuse.getReport(ip)
    except Exception as e:
        logger.error(e)
    return render(request, 'ip/abuse.html', context)

def get_context_shodan(request, **kwargs):
    ip = kwargs['pk']
    context = {}
    try:
        shodan = Shodan()
        context['shodan'] = shodan.getReport(ip)
    except Exception as e:
        logger.error(e)
    return render(request, 'ip/shodan.html', context)

def get_context_censys(request, **kwargs):
    ip = kwargs['pk']
    context = {}
    try:
        censys = Censys()
        context['censys'] = censys.getReport(ip)
    except Exception as e:
        logger.error(e)
    return render(request, 'ip/censys.html', context)

