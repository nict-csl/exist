import sys
import os
import configparser
import requests
import pandas as pd
import hashlib
from datetime import datetime, timezone
import glob

## Django Setup
import django
import pymysql
pymysql.install_as_MySQLdb()
conffile = os.path.join(os.path.dirname(__file__), "../conf/insert2db.conf")
conf = configparser.SafeConfigParser()
conf.read(conffile)
sys.path.append(conf.get('exist', 'syspath'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'intelligence.settings')
django.setup()
from reputation.models import blacklist
import django.utils.timezone as tzone
from django.db import IntegrityError

## Logger Setup
from logging import getLogger, DEBUG, NullHandler
logger = getLogger(__name__)
logger.addHandler(NullHandler())
logger.setLevel(DEBUG)
logger.propagate = True

DataDir = conf.get('t5_c2', 'DataDir')

class Tracker():
    def __init__(self):
        self.name = 'TeamT5_c2'
        self.ID = 121
        self.DataFilePathList = glob.glob(DataDir + '*.csv')
        self.header = [
            'IP',
            'last_seen',
            'malware',
        ]

    def makeDataframe(self):
        df_all = pd.DataFrame()
        df = pd.DataFrame()
        for filepath in self.DataFilePathList:
            try:
                df = pd.read_csv(filepath, names=self.header, header=0)
                df_all = pd.concat([df_all, df])
            except Exception as e:
                logger.error(e)
                continue
        return df_all

    def parse(self):
        logger.info("start parsing: %s", self.name)

        df = self.makeDataframe()
        queries = []
        if df.empty:
            logger.info("no update")
            return queries

        df = df.drop(0)
        for i, v in df.iterrows():
            line = str(self.ID) + ","
            line += str(v.values)
            md5 = hashlib.md5(line.encode('utf-8')).hexdigest()
            try:
                query = blacklist(
                    id = md5,
                    ip = v.IP,
                    datetime = datetime.strptime(v.last_seen, '%Y-%m-%d').replace(tzinfo=timezone.utc),
                    description = v.malware,
                    source = self.ID,
                )
            except Exception as e:
                logger.error("%s: %s", e, line)
            queries.append(query)

        logger.info("done parsing: %s, %s queries were parsed", self.name, len(queries))
        return queries

