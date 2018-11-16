from rest_framework import viewsets
from rest_framework.filters import SearchFilter, FilterSet
from django_filters import DateTimeFromToRangeFilter, CharFilter, ModelMultipleChoiceFilter
from django_filters.rest_framework import DjangoFilterBackend
from vuln.models import Vuln, Tag
from vuln.serializers import vulnSerializer

class vulnFilter(FilterSet):
    vulndb_published_date = DateTimeFromToRangeFilter()
    vulndb_last_modified = DateTimeFromToRangeFilter()
    cve = CharFilter(name='nvds__id')
    tag = ModelMultipleChoiceFilter(name='tags__name', to_field_name='name', queryset=Tag.objects.all(), conjoined=True)
    class Meta:
        model = Vuln
        fields = ['vulndb_published_date', 'vulndb_last_modified']

class vulnViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Vuln.objects.order_by('-vulndb_last_modified')
    serializer_class = vulnSerializer
    filter_class = vulnFilter
    filter_backends = (SearchFilter, DjangoFilterBackend)
    search_fields = ['$title', '$description']
