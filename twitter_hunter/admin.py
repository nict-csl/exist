from django.contrib import admin

# Register your models here.
from .models import tweet, Hunt

admin.site.register(tweet)
admin.site.register(Hunt)
