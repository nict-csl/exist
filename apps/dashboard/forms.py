from django import forms

class SearchForm(forms.Form):
    keyword = forms.CharField(label='', max_length=100, required=True)
    keyword.widget.attrs['class'] = 'form-control mr-sm-2 my-2'
    keyword.widget.attrs['placeholder'] = 'Search for IP address, Domain, URL, Hash(md5, sha1, sha256), and any keyword'

