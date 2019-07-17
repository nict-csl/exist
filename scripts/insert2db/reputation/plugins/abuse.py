import sys
import os
import configparser
import requests
import json
import hashlib
from io import StringIO
from datetime import datetime, timezone

## Django Setup
import django
import pymysql
pymysql.install_as_MySQLdb()
conffile = os.path.join(os.path.dirname(__file__), "../../conf/insert2db.conf")
conf = configparser.SafeConfigParser()
conf.read(conffile)
sys.path.append(conf.get('exist', 'syspath'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'intelligence.settings')
django.setup()
from apps.reputation.models import blacklist
import django.utils.timezone as tzone
from django.db import IntegrityError

## Logger Setup
from logging import getLogger, DEBUG, NullHandler
logger = getLogger(__name__)
logger.addHandler(NullHandler())
logger.setLevel(DEBUG)
logger.propagate = True

DataDir = os.path.join(os.path.dirname(__file__), '../data/')

class Tracker():
    def __init__(self):
        self.name = 'AbuseIPDB'
        self.ID = 301
        self.URL = 'https://api.abuseipdb.com/api/v2/blacklist'
        self.DataFilePath = DataDir + 'abuse/blacklist.json'
        self.key = conf.get('abuse', 'api_key')

    def getBlacklist(self):
        report = {}
        headers = {
            'Key': self.key,
            'Accept': 'application/json'
        }
        payloads = {
            'countMinimum': 15,
            'maxAgeInDays':  30,
            'confidenceMinimum': 90,
        }
        try:
            res = requests.post(self.URL, headers=headers, data=payloads)
        except Exception as e:
            logger.error(e)
        try:
            report = json.loads(res.text)
            #report = json.load(open(self.DataFilePath))
        except Exception as e:
            logger.error(e)
        return report

    def parse(self):
        logger.info("start parsing: %s", self.name)

        report = self.getBlacklist()
        #print(json.dumps(blacklist))
        queries = []
        if 'data' in report:
            for data in report['data']:
                line = str(self.ID) + ","
                line += str(data['ipAddress'])
                md5 = hashlib.md5(line.encode('utf-8')).hexdigest()
                try:
                    query = blacklist(
                        id = md5,
                        ip = data['ipAddress'],
                        datetime = tzone.now(),
                        description = "totalReports: " + str(data['totalReports']) + ", abuseConfidenceScore: " + str(data['abuseConfidenceScore']),
                        source = self.ID,
                        referrer = 'https://www.abuseipdb.com/check/' + data['ipAddress'],
                    )
                except Exception as e:
                    print(e)
                    logger.error(e)
                queries.append(query)
        else:
            logger.error("no update")

        logger.info("done parsing: %s, %s queries were parsed", self.name, len(queries))
        return queries

