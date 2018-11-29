from django import forms

LOOKUP_TYPES = (
    ('ip', 'IP Address'),
    ('domain', 'Domain'),
    ('url', 'URL'),
    ('hash', 'Hash'),
)

class CCSearchForm(forms.Form):
    keyword = forms.CharField(label='', max_length=100, required=True)
    keyword.widget.attrs['class'] = 'form-control mr-sm-2 my-2'
    keyword.widget.attrs['placeholder'] = 'Cross-cutting Search'

class LookupForm(forms.Form):
    value = forms.CharField(label='', max_length=100, required=True)
    value.widget.attrs['class'] = 'form-control mr-sm-2 my-2'
    value.widget.attrs['placeholder'] = 'Lookup IP address, Domain, URL, Hash(md5, sha1, sha256)'

