from django.forms import ModelForm, CharField
from django.utils.translation import ugettext_lazy as _
from .models import Hunt

def popover_html(label, content):
        return label + ' <a role="button" data-toggle="tooltip" data-placement="auto" title="' + content + '"><i class="fas fa-info-circle"></i></a>'

class HuntForm(ModelForm):
    class Meta:
        model = Hunt
        fields = ('name', 'keyword', 'channel', 'notice', )
        labels = {
                'notice': popover_html('slack notice', "Slack will be notified if checked."),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['keyword'].widget.attrs['placeholder'] = "e.g. 'apt1 osint' is apt1 AND osint, and 'apt1,osint' is apt1 OR osint"
        self.fields['channel'].widget.attrs['placeholder'] = "slack channel name. default is th-[Name]."


