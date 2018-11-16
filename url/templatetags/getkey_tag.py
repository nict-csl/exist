from django import template
register = template.Library()

@register.filter(name="getkey")
def getkey(mapping, key):
  return mapping.get(key, '')
