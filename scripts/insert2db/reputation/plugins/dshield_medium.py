import sys
import os
import configparser
import requests
import pandas as pd
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
        self.name = 'Dshield_Medium'
        self.ID = 222
        self.URL = 'https://www.dshield.org/feeds/suspiciousdomains_Medium.txt'
        self.DataFilePath = DataDir + 'dshield/suspiciousdomains_Medium.txt'
        self.header = [
            'domain',
        ]

    def cmpFiles(self, oldfile, newtext):
        diffline = ''
        if not os.path.exists(oldfile):
            f = open(oldfile, 'w')
            f.close()
        oldsets = set(open(oldfile).readlines())
        newsets = set(newtext.replace('\r\n','\n').splitlines(True))
        results = newsets.difference(oldsets)
        for result in results:
            diffline += result
        return diffline[:-1]

    def delComment(self, s):
        result = ''
        for line in s.splitlines(True):
            if not line.startswith('#') \
                    and line != "Site\n":
                result += line
        return result

    def makeDataframe(self):
        df = pd.DataFrame()
        newline = ''
        try:
            res = requests.get(self.URL)
            if res.status_code != 200:
                return df
            newline = self.cmpFiles(self.DataFilePath, res.text)
            newline = self.delComment(newline)
        except Exception as e:
            logger.error(e)
        if not newline == '':
            open(self.DataFilePath, 'w').write(res.text)
            df = pd.read_csv(StringIO(newline), names=self.header)
        return df

    def parse(self):
        logger.info("start parsing: %s", self.name)

        df = self.makeDataframe()
        queries = []
        if not df.empty:
            for i, v in df.iterrows():
                line = str(self.ID) + ","
                line += str(v.values)
                md5 = hashlib.md5(line.encode('utf-8')).hexdigest()
                try:
                    query = blacklist(
                        id = md5,
                        domain = v.domain,
                        datetime = tzone.now(),
                        source = self.ID,
                        referrer = 'https://www.dshield.org/feeds/suspiciousdomains_Medium.txt',
                    )
                except Exception as e:
                    logger.error("%s: %s", e, line)
                queries.append(query)
        else:
            logger.info("no update")

        logger.info("done parsing: %s, %s queries were parsed", self.name, len(queries))
        return queries

