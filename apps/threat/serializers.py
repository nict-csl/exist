from rest_framework import serializers
from .models import Event, Attribute, Object

class EventSerializer(serializers.ModelSerializer):
    threat_level = serializers.CharField(source='get_threat_level_id_display')
    analysis = serializers.CharField(source='get_analysis_display')
    org = serializers.CharField(source='org.name')
    orgc = serializers.CharField(source='orgc.name')
    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')
    class Meta:
        model = Event
        fields = (
            'id',
            'info',
            'org',
            'orgc',
            'threat_level',
            'tags',
            'date',
            'analysis',
            'published',
            'publish_timestamp',
            'timestamp',
            'attribute_count',
            'relatedevents',
        )

class EventSummarySerializer(serializers.ModelSerializer):
    orgc = serializers.CharField(source='orgc.name')
    class Meta:
        model = Event
        fields = (
            'id',
            'info',
            'orgc',
            'date',
        )

class ObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Object
        fields = (
            'id',
            'name',
            'meta_category',
            'description',
            'timestamp',
            'comment',
            'event',
            'attributes',
            'objectreferences',
        )

class AttributeSerializer(serializers.ModelSerializer):
    Event = EventSummarySerializer(source='event')
    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')
    Object = ObjectSerializer(source='object_id')
    class Meta:
        model = Attribute
        fields = (
            'id',
            'type',
            'category',
            'timestamp',
            'comment',
            'object_relation',
            'value',
            'Event',
            'Object',
            'tags',
        )

