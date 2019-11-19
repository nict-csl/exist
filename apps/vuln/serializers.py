from rest_framework import serializers
from .models import Vuln, NVD, CVSS, Reference, Product, Tag

class ReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reference
        fields = (
            'id',
            'reftype',
            'value',
        )

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'id',
            'name',
        )

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'description',
            'longname',
        )

class NVDSerializer(serializers.ModelSerializer):
    class Meta:
        model = NVD
        fields = (
            'id',
            'cwe_id',
            'cvss_score',
            'summary',
        )

class CVSSSerializer(serializers.ModelSerializer):
    class Meta:
        model = CVSS
        fields = (
            'id',
            'access_complexity',
            'availability_impact',
            'confidentiality_impact',
            'access_vector',
            'authentication',
            'integrity_impact',
            'score',
            'calculated_cvss_base_score',
            'cve_id',
            'source',
            'generated_on',
        )

class vulnSerializer(serializers.ModelSerializer):
    source = serializers.CharField(source='get_source_display')
#    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')
    tags = TagSerializer(many=True, read_only=True)
#    products = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')
    products = ProductSerializer(many=True, read_only=True)
    vendors = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')
#    references = serializers.SlugRelatedField(many=True, read_only=True, slug_field='value')
    references = ReferenceSerializer(many=True, read_only=True)
    nvds = NVDSerializer(many=True, read_only=True)
    cvsses = CVSSSerializer(many=True, read_only=True)
    class Meta:
        model = Vuln
        fields = (
            'id',
            'title',
            'description',
            't_description',
            'vulndb_published_date',
            'vulndb_last_modified',
            'products',
            'vendors',
            'references',
            'tags',
            'solution',
            'nvds',
            'cvsses',
            'source',
        )

