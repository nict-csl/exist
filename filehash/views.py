from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic import TemplateView, DetailView
from .forms import SearchForm
from .umbrella import Umbrella
from .vt import VT
from .threatminer import ThreatMiner

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

        return context

def getpcap(request, pk):
    response = HttpResponse(VT().getPcap(pk), content_type="application/vnd.tcpdump.pcap")
    response["Content-Disposition"] = "filename=%s.pcap" % pk
    return response

