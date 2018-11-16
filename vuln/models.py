from django.db import models

# Create your models here.
import datetime
from django.utils import timezone
from hashlib import md5

class Product(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    googlehit = models.BigIntegerField(null=True, blank=True)
    
    def __str__(self):
        return str(self.id)

    class Meta:
        get_latest_by = 'googlehit'

class Vendor(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return str(self.id)

class Reference(models.Model):
    id = models.SlugField(max_length=32, primary_key=True)
    reftype = models.CharField(max_length=255, null=True, blank=True)
    value = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return str(self.id)

class Tag(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    longname = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return str(self.name)

    def get_backgroundcolor(self):
        num = str(self.id).encode('utf-8')
        md5str = md5(num).hexdigest()
        red = md5str[0:2]
        green = md5str[2:4]
        blue = md5str[4:6]
        color = "#{}{}{}".format(red, green, blue)
        return color

    def get_textcolor(self):
        bgcolor = self.get_backgroundcolor()
        red = int(bgcolor[1:3], 16)
        green = int(bgcolor[3:5], 16)
        blue = int(bgcolor[5:7], 16)

        color = '#000000'
        bg = red * 0.299 + green * 0.587 + blue * 0.114
        if bg < 186:
            color = '#ffffff'
        return color

class CVSS(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    access_vector = models.CharField(max_length=32, null=True, blank=True)
    access_complexity = models.CharField(max_length=32, null=True, blank=True)
    authentication = models.CharField(max_length=32, null=True, blank=True)
    confidentiality_impact = models.CharField(max_length=32, null=True, blank=True)
    integrity_impact = models.CharField(max_length=32, null=True, blank=True)
    availability_impact = models.CharField(max_length=32, null=True, blank=True)
    score = models.DecimalField(max_digits=3, decimal_places=1)
    calculated_cvss_base_score = models.DecimalField(max_digits=3, decimal_places=1)
    cve_id = models.CharField(max_length=32, null=True, blank=True)
    source = models.CharField(max_length=32, null=True, blank=True)
    generated_on = models.DateTimeField()
    
    def __str__(self):
        return str(self.id)
    
class NVDref(models.Model):
    id = models.SlugField(max_length=32, primary_key=True)
    url = models.CharField(max_length=255, null=True, blank=True)
    source = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return str(self.id)

class NVD(models.Model):
    id = models.SlugField(max_length=16, primary_key=True)
    cwe_id = models.SlugField(max_length=8, null=True, blank=True)
    references = models.ManyToManyField(NVDref)
    cvss_access_complexity = models.CharField(max_length=32, null=True, blank=True)
    cvss_availability_impact = models.CharField(max_length=32, null=True, blank=True)
    cvss_confidentiality_impact = models.CharField(max_length=32, null=True, blank=True)
    cvss_access_vector = models.CharField(max_length=32, null=True, blank=True)
    cvss_authentication = models.CharField(max_length=32, null=True, blank=True)
    cvss_integrity_impact = models.CharField(max_length=32, null=True, blank=True)
    cvss_score = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    summary = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.id)

class Author(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return str(self.id)

class Vuln(models.Model):
    SOURCES = (
        (101, 'VulnDB'),
    )
    id = models.PositiveIntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    t_description = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    vulndb_published_date = models.DateTimeField()
    vulndb_last_modified = models.DateTimeField(null=True, blank=True)
    discovery_date = models.TextField(null=True, blank=True)
    disclosure_date = models.TextField(null=True, blank=True)
    exploit_publish_date = models.DateTimeField(null=True, blank=True)
    products = models.ManyToManyField(Product)
    vendors = models.ManyToManyField(Vendor)
    vendor_informed_date = models.DateTimeField(null=True, blank=True)
    vendor_ack_date = models.DateTimeField(null=True, blank=True)
    references = models.ManyToManyField(Reference)
    tags = models.ManyToManyField(Tag)
    solution = models.TextField(null=True, blank=True)
    solution_date = models.DateTimeField(null=True, blank=True)
    third_party_solution_date = models.DateTimeField(null=True, blank=True)
    cvsses = models.ManyToManyField(CVSS)
    source = models.IntegerField(choices=SOURCES)
    nvds = models.ManyToManyField(NVD)
    authors = models.ManyToManyField(Author)
    manual_notes = models.TextField(null=True, blank=True)
    keywords = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return str(self.id)

