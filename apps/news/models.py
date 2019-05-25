from django.db import models

# Create your models here.
import datetime
from django.utils import timezone

class News(models.Model):
    id = models.SlugField(max_length=32, primary_key=True)
    title = models.CharField(max_length=255)
    datetime = models.DateTimeField()
    referrer = models.URLField(max_length=255, null=True)
    content = models.TextField(null=True)
    source_title = models.CharField(max_length=255)
    source_url = models.URLField(max_length=255, null=True)

    def __str__(self):
        return self.id

