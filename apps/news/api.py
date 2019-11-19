from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from django_filters import DateTimeFromToRangeFilter, CharFilter, FilterSet
from django_filters.rest_framework import DjangoFilterBackend
from apps.news.models import News
from apps.news.serializers import nwSerializer

class nwFilter(FilterSet):
    datetime = DateTimeFromToRangeFilter()
    class Meta:
        model = News
        fields = ['datetime']

class nwViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = News.objects.order_by('-datetime')
    serializer_class = nwSerializer
    filter_class = nwFilter
    filter_backends = (SearchFilter, DjangoFilterBackend)
    search_fields = ['$title', '$content']
