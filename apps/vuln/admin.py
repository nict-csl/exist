from django.contrib import admin

# Register your models here.
from .models import Vuln, Tag, Vendor, Product, CVSS, Reference, NVD, NVDref, Author

admin.site.register(Vuln)
admin.site.register(Tag)
admin.site.register(Vendor)
admin.site.register(Product)
admin.site.register(CVSS)
admin.site.register(Reference)
admin.site.register(NVD)
admin.site.register(NVDref)
admin.site.register(Author)
