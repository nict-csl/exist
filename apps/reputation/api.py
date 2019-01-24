from rest_framework import viewsets
from rest_framework.filters import SearchFilter, FilterSet
from rest_framework.decorators import list_route
from rest_framework.response import Response
from apps.reputation.models import blacklist
from apps.reputation.serializers import blSerializer, sourceSerializer
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import ModelChoiceFilter
from django.db.models import Q

class blViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = blacklist.objects.order_by('-datetime')
    serializer_class = blSerializer
    filter_backends = (SearchFilter, DjangoFilterBackend)
    search_fields = ['$ip', '$domain', '$url']
    filter_fields = ('ip', 'domain', 'url', 'source')

    @list_route()
    def sources(self, request):
        sources = blacklist.SOURCES
        return Response(dict(sources))
