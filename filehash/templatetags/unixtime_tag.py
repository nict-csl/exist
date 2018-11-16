from django import template
from datetime import datetime
register = template.Library()

@register.filter(name="unixtimetostr")
def unixtimetostr(unixtime):
    return datetime.fromtimestamp(unixtime).strftime('%Y-%m-%d %H:%M:%S')

@register.filter(name="unixtimetostrmillisec")
def unixtimetostrmillisec(unixtime):
    return datetime.fromtimestamp(unixtime / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
