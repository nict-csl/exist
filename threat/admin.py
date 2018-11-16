from django.contrib import admin

# Register your models here.
from .models import Event, Attribute, Org, Tag, Object, ObjectReference

admin.site.register(Event)
admin.site.register(Attribute)
admin.site.register(Org)
admin.site.register(Tag)
admin.site.register(Object)
admin.site.register(ObjectReference)

