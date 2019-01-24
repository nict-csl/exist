from django.db import models

# Create your models here.
import datetime
from django.utils import timezone
from time import sleep
import subprocess

class Hunt(models.Model):
    id = models.AutoField(primary_key=True)
    datetime = models.DateTimeField(default=timezone.now)
    name = models.CharField(max_length=255, null=True)
    track = models.CharField(max_length=255, null=True, blank=True)
    follow = models.CharField(max_length=255, null=True, blank=True)
    notice = models.BooleanField(default=False)
    channel = models.CharField(max_length=255, null=True, blank=True)
    enable = models.BooleanField(default=True)

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

    def start(self):
        cmd = "python scripts/hunter/twitter/tw_hunter.py " + str(self.id)
        subprocess.Popen(cmd, shell=True)

    def stop(self):
        cmd = "ps aux|grep \"tw_hunter.py " + str(self.id) + "$\"|grep -v grep |awk '{print \"kill -9\", $2}'|sh"
        subprocess.Popen(cmd, shell=True)

    def restart(self):
        self.stop()
        sleep(1)
        self.start()

class tweet(models.Model):
    id = models.BigAutoField(primary_key=True)
    text = models.TextField()
    datetime = models.DateTimeField()
    user = models.CharField(max_length=255)
    screen_name = models.CharField(max_length=15)
    hunt_id = models.ForeignKey(Hunt)

    def __str__(self):
        return str(self.id)

    def was_published_recently(self):
        return self.datetime >= timezone.now() - datetime.timedelta(days=7)
