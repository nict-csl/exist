from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from django_filters import DateTimeFromToRangeFilter, CharFilter, ChoiceFilter, FilterSet
from django_filters.rest_framework import DjangoFilterBackend
from apps.threat.models import Event, Attribute
from apps.threat.serializers import EventSerializer, AttributeSerializer
from django.db.models import Q

class threatEventFilter(FilterSet):
    publish_timestamp = DateTimeFromToRangeFilter()
    attr = CharFilter(method='getEventsByAttribute', label='attr')

    class Meta:
        model = Event
        fields = ['id', 'publish_timestamp', 'threat_level_id']

    def getEventsByAttribute(self, queryset, name, value):
        events = Attribute.objects.filter(Q(value__icontains=value)).values_list('event')
        return queryset.filter(id__in=events)

class threatEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Event.objects.order_by('-publish_timestamp')
    serializer_class = EventSerializer
    filter_class = threatEventFilter
    filter_backends = (SearchFilter, DjangoFilterBackend)
    search_fields = ['$info']

class threatAttrFilter(FilterSet):
    timestamp = DateTimeFromToRangeFilter()
    value = CharFilter(field_name='value', lookup_expr='iexact')
    type = CharFilter(field_name='type')

    class Meta:
        model = Attribute
        fields = ['id', 'timestamp', 'event__id']

class threatAttrViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Attribute.objects.order_by('-timestamp')
    serializer_class = AttributeSerializer
    filter_class = threatAttrFilter
    filter_backends = (SearchFilter, DjangoFilterBackend)
    search_fields = ['$value']
