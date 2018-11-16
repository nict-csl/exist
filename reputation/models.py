from django.db import models

# Create your models here.
import datetime
from django.utils import timezone
#import ipaddress

class blacklist(models.Model):
    SOURCES = (
        (101, 'SecureWorks IP'),
        (102, 'SecureWorks Doamin'),
        (201, 'MalwareDomainList'),
        (211, 'abuse.ch Ransomware Tracker'),
        (212, 'abuse.ch ZeuS Tracker'),
        (221, 'DShield Low'),
        (222, 'DShield Medium'),
        (223, 'DShield High'),
        (231, 'ThreatExpert'),
        (241, 'PhishTank'),
        (251, 'Bambenek CnC IP'),
        (252, 'Bambenek CnC Domain'),
        (261, 'CINS'),
        (271, 'CyberCrime Tracker'),
        (281, 'Malshare'),
        (291, 'Minotr.net'),
    )
    id = models.SlugField(max_length=32, primary_key=True)
    ip = models.GenericIPAddressField(protocol='IPv4', null=True)
    domain = models.CharField(max_length=100)
    url = models.URLField(max_length=255)
    source = models.IntegerField(choices=SOURCES)
    description = models.CharField(max_length=255, null=True)
    referrer = models.URLField(max_length=255, null=True)
    countrycode = models.CharField(max_length=3)
    datetime = models.DateTimeField()

    def __str__(self):
        return self.id

    def was_published_recently(self):
        return self.datetime >= timezone.now() - datetime.timedelta(days=7)

    def get_vturl(self):
        url = ''
        if self.ip is not None:
            url = "https://www.virustotal.com/#/ip-address/" + self.ip
        elif self.domain != '':
            url = "https://www.virustotal.com/#/domain/" + self.domain
        elif self.url != '' and "//" in self.url:
            url = "https://www.virustotal.com/#/domain/" + self.url.split('/')[2]
        return url

    def get_dturl(self):
        url = ''
        if self.ip is not None:
            url = "https://whois.domaintools.com/" + self.ip
        elif self.domain != '':
            url = "https://whois.domaintools.com/" + self.domain
        elif self.url != '' and "//" in self.url:
            url = "https://whois.domaintools.com/" + self.url.split('/')[2]
        return url

