from rest_framework import serializers
from .models import blacklist

class blSerializer(serializers.ModelSerializer):
    source = serializers.CharField(source='get_source_display')
    class Meta:
        model = blacklist
        fields = ('__all__')

class sourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = blacklist
        fields = ('SOURCES',)
