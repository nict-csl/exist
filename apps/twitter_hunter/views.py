from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView
from pure_pagination.mixins import PaginationMixin
from django.db.models import Q, Count
from .models import tweet, Hunt
from .forms import HuntForm
import csv
from io import StringIO, BytesIO
from codecs import BOM_UTF8
from pytz import timezone
from django.http import JsonResponse
from urllib.parse import urlparse
from http.client import HTTPSConnection

class IndexView(PaginationMixin, ListView):
    template_name = 'twitter_hunter/index.html'
    context_object_name = 'hts'
    paginate_by = 30

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self, request):
        query = Hunt.objects.order_by('id')
        query = query.annotate(count=Count('tweet'))
        return query

    def get(self, request):
        self.object_list = self.get_queryset(request)
        context = self.get_context_data()
        return render(request, 'twitter_hunter/index.html', context)

class TweetsView(PaginationMixin, ListView):
    template_name = 'twitter_hunter/tweets.html'
    context_object_name = 'tws'
    paginate_by = 30

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self, request, pk):
        query = tweet.objects.filter(hunt_id=Hunt(id=pk)).order_by('-datetime')
        return query

    def get(self, request, pk):
        self.object_list = self.get_queryset(request, pk)
        context = self.get_context_data()
        return render(request, 'twitter_hunter/tweets.html', context)

class HuntCreateView(CreateView):
    model = Hunt
    form_class = HuntForm
    template_name = 'twitter_hunter/hunt_form.html'

    def get_success_url(self):
        self.object.start()
        return '/twitter_hunter'

class HuntUpdateView(UpdateView):
    model = Hunt
    form_class = HuntForm
    template_name = 'twitter_hunter/hunt_edit_form.html'

    def get_success_url(self):
        self.object.restart()
        return '/twitter_hunter'

def hunt_del(request, pk):
    hunt = get_object_or_404(Hunt, id=pk)
    hunt.stop()
    hunt.delete()
    return redirect('twitter_hunter:index')

def hunt_export(request, pk):
    stream = StringIO()
    writer = csv.writer(stream)
    header = ['#datetime', 'user', 'screen_name', 'text']
    writer.writerow(header)
    for tw in tweet.objects.filter(hunt_id=Hunt(id=pk)).order_by('datetime'):
        dt = tw.datetime.astimezone(timezone('Asia/Tokyo'))
        row = [dt, tw.user, tw.screen_name, tw.text]
        writer.writerow(row)
    b_stream = BytesIO(BOM_UTF8 + stream.getvalue().encode('utf8'))
    response = HttpResponse(b_stream.getvalue(), content_type="text/csv")
    response["Content-Disposition"] = "filename=hunter%s.csv" % pk
    return response

def hunt_switch_notice(request, pk):
    hunt = get_object_or_404(Hunt, id=pk)
    hunt.stop()
    if hunt.notice == True:
        hunt.setNoticeFalse()
    else:
        hunt.setNoticeTrue()
    hunt.start()
    return redirect('twitter_hunter:index')

def hunt_switch_enable(request, pk):
    hunt = get_object_or_404(Hunt, id=pk)
    if hunt.enable == True:
        hunt.setDisable()
        hunt.stop()
    else:
        hunt.setEnable()
        hunt.start()
    return redirect('twitter_hunter:index')

def expand_url(request):
    url = request.GET.get('url', None)
    exurl = expand(url)
    while exurl != url:
        url = exurl
        exurl = expand(url)
    return JsonResponse({'url': exurl})

def expand(url):
    o = urlparse(url)
    con = HTTPSConnection(o.netloc)
    con.request('HEAD', o.path)
    res = con.getresponse()
    if res.getheader('location') == None:
        return url
    return res.getheader('location')

