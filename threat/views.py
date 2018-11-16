from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView
from pure_pagination.mixins import PaginationMixin
from django.db.models import Q
from .models import Event, Attribute, Org, Tag, Object, ObjectReference
from .forms import EventSearchForm, AttributeSearchForm
from datetime import datetime, timezone, timedelta

class EventListView(PaginationMixin, ListView):
    model = Event
    template_name = 'threat/event_list.html'
    context_object_name = 'events'
    paginate_by = 30

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['count'] = self.object_list.count()
        context['alltag'] = Tag.objects.order_by('id')
        taglist = self.request.GET.getlist('tag')
        context['tags'] = Tag.objects.filter(id__in=taglist)
        search_form = EventSearchForm(self.request.GET)
        context['search_form'] = search_form
        context['30_day_labels'] = self.thirty_day_labels()
        context['30_day_data'] = self.thirty_day_data()
        return context

    def get_queryset(self):
        query = Event.objects.order_by('-publish_timestamp')
        tag = self.request.GET.get('tag')
        if tag is not None:
            query = query.filter(tags__id=tag)
        org = self.request.GET.get('org')
        if org is not None:
            query = query.filter(orgc=org)
        level = self.request.GET.get('level')
        if level is not None:
            query = query.filter(threat_level_id=level)
        keyword = self.request.GET.get('keyword')
        if keyword is not None:
            query = query.filter(Q(info__icontains=keyword)).order_by('-publish_timestamp')
        return query

    def thirty_day_data(self):
        data = []
        today = datetime.now(timezone(timedelta(hours=+9), 'JST'))
        today = today.replace(hour=0, minute=0, second=0, microsecond=0)
        for day in range(30)[::-1]:
            from_date = today - timedelta(days=day)
            to_date = today - timedelta(days=day-1)
            count = self.object_list.filter(publish_timestamp__gte=from_date, publish_timestamp__lte=to_date).count()
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

class EventDetailView(PaginationMixin, ListView):
    model = Attribute
    template_name = 'threat/event_detail.html'
    context_object_name = 'attributes'
    paginate_by = 30

    def get_context_data(self, **kwargs):
        pk = self.kwargs['pk']
        event_obj = Event.objects.get(pk=pk)
        objects_obj = Object.objects.filter(event=pk)
        context = super().get_context_data(**kwargs)
        context['event'] = event_obj
        context['objects'] = objects_obj
        context['categories'] = event_obj.getUniqCategory()
        context['types'] = event_obj.getUniqType()
        context['count'] = self.object_list.count()
        return context

    def get_queryset(self):
        pk = self.kwargs['pk']
        query = Attribute.objects.filter(event=pk).order_by('id')
        category = self.request.GET.get('category')
        type = self.request.GET.get('type')
        if category is not None:
            query = query.filter(category=category)
        if type is not None:
            query = query.filter(type=type)
        return query

class AttributeListView(PaginationMixin, ListView):
    model = Attribute
    template_name = 'threat/attribute_list.html'
    context_object_name = 'attributes'
    paginate_by = 30

    def get_context_data(self, **kwargs):
        attr = Attribute.objects.all()
        context = super().get_context_data(**kwargs)
        context['categories'] = attr.values_list('category', flat=True).order_by('category').distinct()
        context['types'] = attr.values_list('type', flat=True).order_by('type').distinct()
        context['count'] = self.object_list.count()
        search_form = AttributeSearchForm(self.request.GET)
        context['search_form'] = search_form
        #context['30_day_labels'] = self.thirty_day_labels()
        #context['30_day_data'] = self.thirty_day_data()
        return context

    def get_queryset(self):
        query = Attribute.objects.order_by('-timestamp')
        category = self.request.GET.get('category')
        type = self.request.GET.get('type')
        if category is not None:
            query = query.filter(category=category)
        if type is not None:
            query = query.filter(type=type)
        keyword = self.request.GET.get('keyword')
        if keyword is not None:
            query = query.filter(Q(value__icontains=keyword)).order_by('-timestamp')
        return query

    def thirty_day_data(self):
        data = []
        today = datetime.now(timezone(timedelta(hours=+9), 'JST'))
        today = today.replace(hour=0, minute=0, second=0, microsecond=0)
        for day in range(30)[::-1]:
            from_date = today - timedelta(days=day)
            to_date = today - timedelta(days=day-1)
            count = self.object_list.filter(timestamp__gte=from_date, timestamp__lte=to_date).count()
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

class OrgListView(ListView):
    model = Org
    template_name = 'threat/org_list.html'
    context_object_name = 'orgs'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        count = self.object_list.count()
        context['count'] = count
        return context

    def get_queryset(self):
        query = Org.objects.order_by('id')
        return query

class TagListView(ListView):
    model = Tag
    template_name = 'threat/tag_list.html'
    context_object_name = 'tags'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        count = self.object_list.count()
        context['count'] = count
        return context

    def get_queryset(self):
        query = Tag.objects.order_by('id')
        return query

