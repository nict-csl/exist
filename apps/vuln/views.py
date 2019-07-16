from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView
from pure_pagination.mixins import PaginationMixin
from django.db.models import Q
from .models import Vuln, Tag
from .forms import SearchForm
from datetime import datetime, timezone, timedelta

class IndexView(PaginationMixin, ListView):
    template_name = 'vuln/index.html'
    context_object_name = 'vus'
    paginate_by = 30

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['count'] = self.object_list.count()
        context['alltag'] = Tag.objects.order_by('id')
        taglist = self.request.GET.getlist('tag')
        context['tags'] = Tag.objects.filter(id__in=taglist)
        search_form = SearchForm(self.request.GET)
        context['search_form'] = search_form
        context['30_day_labels'] = self.thirty_day_labels()
        context['30_day_data'] = self.thirty_day_data()
        return context

    def get_queryset(self):
        query = Vuln.objects.exclude(vulndb_published_date='1999-01-01 00:00:00+09:00').order_by('-vulndb_last_modified')

        filter_value = self.request.GET.get('filter')
        if filter_value == 'cvss_high':
            query = query.filter(cvsses__score__gte=7).order_by('-vulndb_last_modified')

        filter_value = self.request.GET.get('filter')
        if filter_value == 'attack_possible':
            query = query.filter(Q(tags__id=53)|Q(tags__id=21)|Q(tags__id=63), cvsses__score__gte=7).order_by('-vulndb_last_modified')

        filter_value = self.request.GET.get('filter')
        if filter_value == 'in_the_wild':
            query = query.filter(Q(tags__id=53), cvsses__score__gte=7).order_by('-vulndb_last_modified')

        tags = self.request.GET.getlist('tag')
        if tags is not None:
            for tag in tags:
                query = query.filter(tags__id=tag)

        keyword = self.request.GET.get('keyword')
        if keyword is not None:
            query = query.filter(Q(title__icontains=keyword)|Q(nvds__id=keyword)).order_by('-vulndb_last_modified')
        return query

    def thirty_day_data(self):
        data = []
        today = datetime.now(timezone(timedelta(hours=+9), 'JST'))
        today = today.replace(hour=0, minute=0, second=0, microsecond=0)
        for day in range(30)[::-1]:
            from_date = today - timedelta(days=day)
            to_date = today - timedelta(days=day-1)
            count = self.object_list.filter(vulndb_last_modified__gte=from_date, vulndb_last_modified__lte=to_date).count()
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

class DetailView(DetailView):
    model = Vuln
    template_name = 'vuln/detail.html'
