from django.forms import ModelForm, CharField
from django.utils.translation import ugettext_lazy as _
from .models import Hunt

def popover_html(label, content):
    return label + ' <a role="button" data-toggle="tooltip" data-placement="auto" title="' + content + '"><i class="fas fa-info-circle"></i></a>'

class HuntForm(ModelForm):
    class Meta:
        model = Hunt
        fields = ('name', 'track', 'follow', 'channel', 'notice', )
        labels = {
                'notice': popover_html('slack notice', "Slack will be notified if checked."),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['track'].widget.attrs['placeholder'] = "e.g. ‘the twitter’ is the AND twitter, and ‘the,twitter’ is the OR twitter"
        self.fields['track'].required = False
        self.fields['follow'].widget.attrs['placeholder'] = "e.g. 'user1,user2' is user1 OR user2"
        self.fields['follow'].required = False
        self.fields['channel'].widget.attrs['placeholder'] = "slack channel name. default is th-[Name]."
        self.fields['channel'].required = False

