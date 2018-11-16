from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView
from pure_pagination.mixins import PaginationMixin
from django.db.models import Q
from .models import blacklist
from .forms import SearchForm, TargetForm
from datetime import datetime, timezone, timedelta

class IndexView(PaginationMixin, ListView):
    template_name = 'reputation/index.html'
    context_object_name = 'bls'
    paginate_by = 30

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_form = SearchForm(self.request.GET)
        context['search_form'] = search_form
        target_form = TargetForm()
        context['target_form'] = target_form
        count = self.object_list.count()
        context['count'] = count
        #context['source_count'] = self.count_source()
        context['30_day_labels'] = self.thirty_day_labels()
        context['30_day_data'] = self.thirty_day_data()
        return context

    def get_queryset(self):
        query = blacklist.objects.order_by('-datetime')
        #twomonthago = datetime.now() - timedelta(days=60)
        #query = blacklist.objects.exclude(datetime__lte=twomonthago).order_by('-datetime')
        keyword = self.request.GET.get('keyword')
        source = self.request.GET.get('source')
        if keyword is not None:
            query = query.filter(Q(ip=keyword)|Q(domain__contains=keyword)|Q(url__contains=keyword))
        if source is not None:
            query = query.filter(source=source)
        return query

#    def thirty_day_data(self):
#        alldata = {}
#        today = datetime.now(timezone(timedelta(hours=+9), 'JST'))
#        today = today.replace(hour=0, minute=0, second=0, microsecond=0)
#        for src in blacklist.SOURCES:
#            data = []
#            for day in range(30)[::-1]:
#                from_date = today - timedelta(days=day)
#                to_date = today - timedelta(days=day-1)
#                count = self.object_list.filter(source=src[0], datetime__gte=from_date, datetime__lte=to_date).count()
#                data.append(count)
#            alldata[src[1]] = data
#        return alldata

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

#    def thirty_day_labels(self):
#        labels = []
#        today = datetime.now(timezone(timedelta(hours=+9), 'JST'))
#        today = today.replace(hour=0, minute=0, second=0, microsecond=0)
#        for day in range(30)[::-1]:
#            date = today - timedelta(days=day)
#            label = date.strftime('%Y-%m-%d')
#            labels.append(label)
#        return labels

    def thirty_day_labels(self):
        labels = []
        today = datetime.now(timezone(timedelta(hours=+9), 'JST'))
        today = today.replace(hour=0, minute=0, second=0, microsecond=0)
        for day in range(30)[::-1]:
            date = today - timedelta(days=day)
            label = date.strftime('%Y-%m-%d')
            labels.append(label)
        return labels

    def count_source(self):
        data = {}
        for src in blacklist.SOURCES:
            count = self.object_list.filter(source=src[0]).count()
            data[src[0]] = count
        return data

class DetailView(DetailView):
    model = blacklist
    template_name = 'reputation/detail.html'

