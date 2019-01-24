from rest_framework import viewsets
from rest_framework.filters import SearchFilter, FilterSet
from django_filters import DateTimeFromToRangeFilter, CharFilter
from django_filters.rest_framework import DjangoFilterBackend
from apps.twitter.models import tweet
from apps.twitter.serializers import twSerializer

class twFilter(FilterSet):
    datetime = DateTimeFromToRangeFilter()
    class Meta:
        model = tweet
        fields = ['datetime']

class twViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = tweet.objects.order_by('-datetime')
    serializer_class = twSerializer
    filter_class = twFilter
    filter_backends = (SearchFilter, DjangoFilterBackend)
    search_fields = ['$text', '$user', '$screen_name']
