from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic import TemplateView, DetailView
from .forms import SearchForm
from lib.umbrella import Umbrella
from lib.vt import VT
from lib.threatminer import ThreatMiner
from django.db.models import Q
from threat.models import Event, Attribute
from reputation.models import blacklist
from twitter.models import tweet
from exploit.models import Exploit
from vuln.models import Vuln

class IndexView(TemplateView):
    template_name = 'filehash/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchForm()
        return context

    def get(self, request, **kwargs):
        if request.GET.get('keyword'):
            filehash = request.GET.get('keyword')
            return HttpResponseRedirect(filehash)
        context = self.get_context_data()
        return self.render_to_response(context)

class DetailView(TemplateView):
    template_name = 'filehash/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchForm()
        filehash = self.kwargs['pk']

        umb = Umbrella()
        context['umbrella_sample'] = umb.get_sample(filehash)

        vt = VT()
        context['vt_hash'] = vt.getFileReport(filehash)
        context['vt_behavior'] = vt.getFileBehavior(filehash)

        tm = ThreatMiner()
        context['tm_meta'] = tm.getMetaFromSample(filehash)
        context['tm_http'] = tm.getHttpFromSample(filehash)
        context['tm_host'] = tm.getHostsFromSample(filehash)
        context['tm_av'] = tm.getAVFromSample(filehash)
        context['tm_report'] = tm.getReportFromSample(filehash)

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
        context['vus'] = Vuln.objects.filter(Q(title__icontains=filehash)).order_by('-vulndb_last_modified')
        count = context['vus'].count()
        if count > 0:
            context['vus_count'] = count

        return context

def getpcap(request, pk):
    response = HttpResponse(VT().getPcap(pk), content_type="application/vnd.tcpdump.pcap")
    response["Content-Disposition"] = "filename=%s.pcap" % pk
    return response

