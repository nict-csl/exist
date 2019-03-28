from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView
from pure_pagination.mixins import PaginationMixin
from django.db.models import Q, Count
from .models import Hunt
from apps.threat.models import Event
from .forms import HuntForm
import csv
from io import StringIO, BytesIO
from codecs import BOM_UTF8
from pytz import timezone
from django.http import JsonResponse
from urllib.parse import urlparse
from http.client import HTTPConnection

class IndexView(PaginationMixin, ListView):
    model = Hunt
    template_name = 'threat_hunter/index.html'
    context_object_name = 'hunts'
    paginate_by = 30

    def get_queryset(self):
        query = Hunt.objects.order_by('id')
        query = query.annotate(count=Count('events'))
        return query

    def post(self, request, *args, **kwargs):
        hunt_id = request.POST['delete']
        hunt = get_object_or_404(Hunt, id=hunt_id)
        hunt.delete()
        return redirect('threat_hunter:index')

class EventListView(PaginationMixin, ListView):
    model = Event
    template_name = 'threat_hunter/event_list.html'
    context_object_name = 'events'
    paginate_by = 30

    def get_queryset(self, pk):
        pk = self.kwargs['pk']
        query = Event.objects.filter(Q(id__in=Hunt(id=pk).events.all())).order_by('-publish_timestamp')
        return query

    def get(self, request, pk):
        self.object_list = self.get_queryset(pk)
        context = self.get_context_data()
        return render(request, 'threat_hunter/event_list.html', context)

class HuntCreateView(CreateView):
    model = Hunt
    form_class = HuntForm
    template_name = 'threat_hunter/hunt_form.html'

    def get_success_url(self):
        self.object.run()
        return '/threat_hunter'
        
class HuntUpdateView(UpdateView):
    model = Hunt
    form_class = HuntForm
    template_name = 'threat_hunter/hunt_edit_form.html'

    def get_success_url(self):
        self.object.run()
        return '/threat_hunter'

def hunt_export(request, pk):
    stream = StringIO()
    writer = csv.writer(stream)
    header = ['#published', 'date', 'info', 'level', 'attribute_count', 'org']
    writer.writerow(header)
    for event in Event.objects.filter(id__in=Hunt(id=pk).events.all()).order_by('publish_timestamp'):
        dt = event.publish_timestamp.astimezone(timezone('Asia/Tokyo'))
        row = [dt, event.date, event.info, event.get_threat_level_id_display(), event.attribute_count, event.org.name]
        writer.writerow(row)
    b_stream = BytesIO(BOM_UTF8 + stream.getvalue().encode('utf8'))
    response = HttpResponse(b_stream.getvalue(), content_type="text/csv")
    response["Content-Disposition"] = "filename=hunter%s.csv" % pk
    return response

def hunt_switch_notice(request, pk):
    hunt = get_object_or_404(Hunt, id=pk)
    if hunt.notice == True:
        hunt.setNoticeFalse()
    else:
        hunt.setNoticeTrue()
    hunt.run()
    return redirect('threat_hunter:index')

def hunt_switch_enable(request, pk):
    hunt = get_object_or_404(Hunt, id=pk)
    if hunt.enable == True:
        hunt.setDisable()
    else:
        hunt.setEnable()
        hunt.run()
    return redirect('threat_hunter:index')

