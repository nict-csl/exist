import sys
import os
import configparser
import requests
import pandas as pd
import xml.etree.ElementTree as ET
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
        self.name = 'ZeusTracker'
        self.ID = 212
        self.URL = 'https://zeustracker.abuse.ch/rss.php'
        self.DataFilePath = DataDir + 'abuse/rw.xml'
        self.header = [
            'title',
            'link',
            'description',
            'guid',
        ]

    def parse(self):
        logger.info("start parsing: %s", self.name)

        try:
            res = requests.get(self.URL)
        except Exception as e:
            logger.error(e)
        if not res.text == '':
            open(self.DataFilePath, 'w').write(res.text)
        xml_data = open(self.DataFilePath).read()
        root = ET.XML(xml_data)
        all_records = []
        for child in root[0]:
            if child.tag == 'item':
                record = {}
                for subchild in child:
                    record[subchild.tag] = subchild.text
                all_records.append(record)
        df = pd.DataFrame(all_records)

        queries = []
        if not df.empty:
            for i, v in df.iterrows():
                line = str(self.ID) + ","
                line += str(v.values)
                md5 = hashlib.md5(line.encode('utf-8')).hexdigest()
                try:
                    query = blacklist(
                        id = md5,
                        domain = v.description.split(',')[0].replace('Host: ', ''),
                        ip = v.description.split(',')[1].replace(' IP address: ', ''),
                        datetime = datetime.strptime(v.title.split('(')[1].split(')')[0], '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc),
                        countrycode = v.description.split(',')[7].replace(' country: ', ''),
                        description = ','.join(v.description.split(',')[2:7]),
                        referrer = v.link,
                        source = self.ID,
                    )
                except Exception as e:
                    logger.error("%s: %s", e, line)
                queries.append(query)
        else:
            logger.info("no update")

        logger.info("done parsing: %s, %s queries were parsed", self.name, len(queries))
        return queries

