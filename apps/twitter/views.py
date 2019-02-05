from django.views.generic import ListView, DetailView
from pure_pagination.mixins import PaginationMixin
from django.db.models import Q
from .models import tweet
from .forms import SearchForm
from django.http import JsonResponse
from urllib.parse import urlparse
from http.client import HTTPSConnection
from datetime import datetime, timezone, timedelta

class IndexView(PaginationMixin, ListView):
    template_name = 'twitter/index.html'
    context_object_name = 'tws'
    paginate_by = 30

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_form = SearchForm(self.request.GET)
        context['search_form'] = search_form
        count = self.object_list.count()
        context['count'] = count
        context['30_day_labels'] = self.thirty_day_labels()
        context['30_day_data'] = self.thirty_day_data()
        return context

    def get_queryset(self):
        query = tweet.objects.order_by('-datetime')
        keyword = self.request.GET.get('keyword')
        if keyword is not None:
            query = query.filter(Q(text__icontains=keyword)).order_by('-datetime')
        return query

    def thirty_day_data(self):
        data = []
        today = datetime.now(timezone(timedelta(hours=+9), 'JST'))
        today = today.replace(hour=0, minute=0, second=0, microsecond=0)
        for day in range(30)[::-1]:
            from_date = today - timedelta(days=day)
            to_date = today - timedelta(days=day-1)
            count = self.object_list.filter(datetime__gte=from_date, datetime__lte=to_date).count()
            data.append(count)
        return data

    def thirty_day_labels(self):
        labels = []
        today = datetime.now(timezone(timedelta(hours=+9), 'JST'))
        today = today.replace(hour=0, minute=0, second=0, microsecond=0)
        for day in range(30)[::-1]:
            date = today - timedelta(days=day)
            label = date.strftime('%Y-%m-%d')
            labels.append(label)
        return labels

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
