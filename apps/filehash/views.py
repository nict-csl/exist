from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views.generic import TemplateView, DetailView
from .forms import SearchForm
from lib.vt import VT
from lib.threatminer import ThreatMiner
from django.db.models import Q
from apps.threat.models import Event, Attribute
from apps.reputation.models import blacklist
from apps.twitter.models import tweet
from apps.exploit.models import Exploit
import re
from logging import getLogger

logger = getLogger('command')

class IndexView(TemplateView):
    template_name = 'filehash/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchForm()
        return context

    def get(self, request, **kwargs):
        if request.GET.get('keyword'):
            filehash = request.GET.get('keyword')
            if self.is_valid_hash(filehash):
                return HttpResponseRedirect(filehash)
            else:
                return redirect('filehash:index')
        context = self.get_context_data()
        return self.render_to_response(context)

    def is_valid_hash(self, value):
        compiled_pattern_md5 = re.compile(r'(?=(\b[a-fA-F0-9]{32}\b))')
        compiled_pattern_sha1 = re.compile(r'(?=(\b[a-fA-F0-9]{40}\b))')
        compiled_pattern_sha256 = re.compile(r'(?=(\b[a-fA-F0-9]{64}\b))')
        if compiled_pattern_md5.match(value) or compiled_pattern_sha1.match(value) or compiled_pattern_sha256.match(value):
            return True
        else:
            return False

class DetailView(TemplateView):
    template_name = 'filehash/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchForm()
        filehash = self.kwargs['pk']

        try:
            vt = VT()
            context['vt_hash'] = vt.getFileReport(filehash)
            context['vt_behavior'] = vt.getFileBehavior(filehash)
        except Exception as e:
            logger.error(e)

#        try:
#            tm = ThreatMiner()
#            context['tm_meta'] = tm.getMetaFromSample(filehash)
#            context['tm_http'] = tm.getHttpFromSample(filehash)
#            context['tm_host'] = tm.getHostsFromSample(filehash)
#            context['tm_av'] = tm.getAVFromSample(filehash)
#            context['tm_report'] = tm.getReportFromSample(filehash)
#        except Exception as e:
#            logger.error(e)

        #context['bls'] = blacklist.objects.filter(Q(url__contains=filehash))
        #count = context['bls'].count()
        #if count > 0:
        #    context['bls_count'] = count
        context['events'] = Event.objects.filter(Q(info__icontains=filehash)).order_by('-publish_timestamp')
        count = context['events'].count()
        if count > 0:
            context['events_count'] = count
        context['attributes'] = Attribute.objects.filter(Q(value__icontains=filehash)).order_by('-timestamp')
        count = context['attributes'].count()
        if count > 0:
            context['attributes_count'] = count
        context['tws'] = tweet.objects.filter(Q(text__icontains=filehash)).order_by('-datetime')
        count = context['tws'].count()
        if count > 0:
            context['tws_count'] = count
        context['exs'] = Exploit.objects.filter(Q(text__icontains=filehash)).order_by('-datetime')
        count = context['exs'].count()
        if count > 0:
            context['exs_count'] = count

        return context

def getpcap(request, pk):
    response = HttpResponse(VT().getPcap(pk), content_type="application/vnd.tcpdump.pcap")
    response["Content-Disposition"] = "filename=%s.pcap" % pk
    return response

def get_context_vt(request, **kwargs):
    filehash = kwargs['pk']
    context = {}
    vt = VT()
    context['vt_hash'] = vt.getFileReport(filehash)
    context['vt_behavior'] = vt.getFileBehavior(filehash)
    return render(request, 'filehash/virustotal.html', context)

def get_context_tm(request, **kwargs):
    filehash = kwargs['pk']
    context = {}
    tm = ThreatMiner()
    context['tm_meta'] = tm.getMetaFromSample(filehash)
    context['tm_http'] = tm.getHttpFromSample(filehash)
    context['tm_host'] = tm.getHostsFromSample(filehash)
    context['tm_av'] = tm.getAVFromSample(filehash)
    context['tm_report'] = tm.getReportFromSample(filehash)
    return render(request, 'filehash/threatminer.html', context)
