from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView
from pure_pagination.mixins import PaginationMixin
from django.db.models import Q, Count
from .models import Hunt
from apps.news.models import News
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
    template_name = 'news_hunter/index.html'
    context_object_name = 'hunts'
    paginate_by = 30

    def get_queryset(self):
        query = Hunt.objects.order_by('id')
        query = query.annotate(count=Count('newss'))
        return query

    def post(self, request, *args, **kwargs):
        hunt_id = request.POST['delete']
        hunt = get_object_or_404(Hunt, id=hunt_id)
        hunt.delete()
        return redirect('news_hunter:index')

class NewsListView(PaginationMixin, ListView):
    model = News
    template_name = 'news_hunter/news_list.html'
    context_object_name = 'newss'
    paginate_by = 30

    def get_queryset(self, pk):
        pk = self.kwargs['pk']
        query = News.objects.filter(Q(id__in=Hunt(id=pk).newss.all())).order_by('-datetime')
        return query

    def get(self, request, pk):
        self.object_list = self.get_queryset(pk)
        context = self.get_context_data()
        return render(request, 'news_hunter/news_list.html', context)

class HuntCreateView(CreateView):
    model = Hunt
    form_class = HuntForm
    template_name = 'news_hunter/hunt_form.html'

    def get_success_url(self):
        self.object.run()
        return '/news_hunter'

class HuntUpdateView(UpdateView):
    model = Hunt
    form_class = HuntForm
    template_name = 'news_hunter/hunt_edit_form.html'

    def get_success_url(self):
        self.object.run()
        return '/news_hunter'

def hunt_export(request, pk):
    stream = StringIO()
    writer = csv.writer(stream)
    header = ['#datetime', 'title', 'referrer', 'source_title']
    writer.writerow(header)
    for news in News.objects.filter(id__in=Hunt(id=pk).newss.all()).order_by('datetime'):
        dt = news.datetime.astimezone(timezone('Asia/Tokyo'))
        row = [dt, news.title, news.referrer, news.source_title]
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
    return redirect('news_hunter:index')

def hunt_switch_enable(request, pk):
    hunt = get_object_or_404(Hunt, id=pk)
    if hunt.enable == True:
        hunt.setDisable()
    else:
        hunt.setEnable()
        hunt.run()
    return redirect('news_hunter:index')
