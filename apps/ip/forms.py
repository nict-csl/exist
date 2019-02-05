from django import forms

class SearchForm(forms.Form):
    keyword = forms.GenericIPAddressField(label='', required=True, protocol='IPv4')
    keyword.widget.attrs['class'] = 'form-control mr-sm-2 my-2'
    keyword.widget.attrs['placeholder'] = 'Lookup IP Address'

