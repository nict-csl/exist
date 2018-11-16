from django import forms
from django.forms import ModelForm
from .models import blacklist

class SearchForm(forms.Form):
    keyword = forms.CharField(label='', max_length=100, required=False)
    keyword.widget.attrs['class'] = 'form-control mr-sm-2 my-2'
    keyword.widget.attrs['placeholder'] = 'Search for IP, Domain, URL.'

class TargetForm(forms.Form):
    source = blacklist.SOURCES

#class TargetForm(ModelForm):
#    class Meta:
#        model = blacklist
#        fields = ('source',)

#    def __init__(self, *args, **kwargs):
#        super(TargetForm, self).__init__(*args, **kwargs)
#        self.fields['source'].empty_label = 'none'

#    def __init__(self, *args, **kwargs):
#        super(TargetForm, self).__init__(*args, **kwargs)
#        for field_name, field in self.fields.items():
#            field.widget.attrs['class'] = 'form-control btn-group'
