from django import template
register = template.Library()

#import re
#from urllib.parse import urlparse
#from http.client import HTTPSConnection

#def expand(url):
#    o = urlparse(url)
#    con = HTTPSConnection(o.netloc)
#    con.request('HEAD', o.path)
#    res = con.getresponse()
#    if res.getheader('location') == None:
#        return url
#    print(res.getheader('location'))
#    return res.getheader('location')
#
#@register.filter(name="expandurl", is_safe=True, needs_autoescape=True)
#def expandurl(value, autoescape=True):
#    result = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', lambda m:expand(m.group(0)), value)
#    return result

@register.filter(name="add_a_tag_name_tooltip", is_safe=True, needs_autoescape=True)
def add_a_tag_name_tooltip(value, autoescape=True):
    result = value.replace('rel="nofollow"', 'rel="nofollow" name="tooltip"')
    return result

