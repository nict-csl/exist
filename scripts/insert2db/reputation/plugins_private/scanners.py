import sys
import os
import configparser
import requests
import pandas as pd
import hashlib
from io import StringIO
from datetime import datetime, timezone
from ipaddress import IPv4Address, IPv4Network, summarize_address_range

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

DataDir = os.path.join(os.path.dirname(__file__), '../data/')

class Tracker():
    def __init__(self):
        self.name = 'Scanners'
        self.ID = 111
        self.DataFilePath = DataDir + 'scanners/list.csv'
        self.header = [
            'org',
            'cidr',
            'fqdn',
            'comment',
        ]

    def parseCidr(self, cidr):
        iplist = []
        if '-' in cidr:
            (ip_start, ip_end) = cidr.split('-')
            iplist += summarize_address_range(IPv4Address(ip_start), IPv4Address(ip_end))
        elif '/' in cidr:
            iplist += IPv4Network(cidr)
        else:
            iplist.append(cidr)
        return iplist

    def makeDataframe(self):
        df = pd.DataFrame()
        try:
            df = pd.read_csv(self.DataFilePath, names=self.header)
        except Exception as e:
            logger.error(e)
        return df

    def parse(self):
        logger.info("start parsing: %s", self.name)

        df = self.makeDataframe()
        queries = []
        if df.empty:
            logger.info("no update")
            return queries

        df = df.drop(0)
        df = df.fillna('')
        for i, v in df.iterrows():
            iplist = self.parseCidr(v.cidr)
            for ip in iplist:
                line = str(self.ID) + ","
                line += str(ip) + str(v.values)
                md5 = hashlib.md5(line.encode('utf-8')).hexdigest()
                description = str(v.org) + '\n' + str(v.fqdn) + '\n' + str(v.comment)
                try:
                    query = blacklist(
                        id = md5,
                        ip = str(ip),
                        datetime = tzone.now(),
                        description = description,
                        source = self.ID,
                    )
                except Exception as e:
                    logger.error("%s: %s", e, line)
                queries.append(query)

        logger.info("done parsing: %s, %s queries were parsed", self.name, len(queries))
        return queries

