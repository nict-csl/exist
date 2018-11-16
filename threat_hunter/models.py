from django.db import models
from django.utils import timezone
import subprocess
from threat.models import Event

class Hunt(models.Model):
    id = models.AutoField(primary_key=True)
    datetime = models.DateTimeField(default=timezone.now)
    name = models.CharField(max_length=255)
    keyword = models.CharField(max_length=255)
    notice = models.BooleanField(default=False)
    channel = models.CharField(max_length=255, null=True, blank=True)
    enable = models.BooleanField(default=True)
    events = models.ManyToManyField(Event)

    def __str__(self):
        return str(self.id)

    def setDisable(self):
        self.enable = False
        self.save()

    def setEnable(self):
        self.enable = True
        self.save()

    def setNoticeTrue(self):
        self.notice = True
        self.save()

    def setNoticeFalse(self):
        self.notice = False
        self.save()

    def run(self):
        cmd = "/home/jingu/.pyenv/shims/python ./threat_hunter/th_hunter.py " + str(self.id)
        subprocess.Popen(cmd, shell=True)

