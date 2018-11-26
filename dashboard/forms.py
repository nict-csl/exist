from django import forms

LOOKUP_TYPES = (
    ('ip', 'IP Address'),
    ('domain', 'Domain'),
    ('url', 'URL'),
    ('hash', 'Hash'),
)

class CCSearchForm(forms.Form):
    keyword = forms.CharField(label='', max_length=100, required=False)
    keyword.widget.attrs['class'] = 'form-control mr-sm-2 my-2'
    keyword.widget.attrs['placeholder'] = 'Cross-cutting Search'

class LookupForm(forms.Form):
    value = forms.CharField(label='', max_length=100, required=False)
    value.widget.attrs['class'] = 'form-control my-2 mx-3'
    value.widget.attrs['placeholder'] = 'Lookup Value'

class LookupChoiceForm(forms.Form):
    lookup_type = forms.ChoiceField(label='', widget=forms.Select(attrs={'class': 'form-control mr-sm-2 my-2'}), choices=LOOKUP_TYPES)
