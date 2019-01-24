from django.db import models

# Create your models here.
import datetime
from django.utils import timezone

class tweet(models.Model):
    id = models.BigAutoField(primary_key=True)
    text = models.TextField()
    datetime = models.DateTimeField()
    user = models.CharField(max_length=255)
    screen_name = models.CharField(max_length=15)

def __str__(self):
    return self.id

def was_published_recently(self):
    return self.datetime >= timezone.now() - datetime.timedelta(days=7)

