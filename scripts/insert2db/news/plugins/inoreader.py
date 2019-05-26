import sys
import os
import configparser
import requests
import hashlib
from io import StringIO
from datetime import datetime
import pytz
from urllib import parse
import json

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
from apps.news.models import News
import django.utils.timezone as tzone
from django.db import IntegrityError

### Logger Setup
from . import getModuleLogger
logger = getModuleLogger(__name__)

class Tracker():
    def __init__(self):
        self.name = 'Inoreader'
        self.app_id = conf.get('inoreader', 'AppID')
        self.app_key = conf.get('inoreader', 'AppKey')
        self.email = conf.get('inoreader', 'Email')
        self.passwd = conf.get('inoreader', 'Passwd')
        self.LoginURL = 'https://www.inoreader.com/accounts/ClientLogin'
        self.URL = 'https://www.inoreader.com/reader/api/0/stream/contents'

    def login(self):
        payloads = {
            'Email': self.email,
            'Passwd': self.passwd,
        }
        try:
            res = requests.post(self.LoginURL, data=payloads)
        except Exception as e:
            logger.error(e)

        auth = res.text.split('Auth=')[1].rstrip()
        return auth

    def download(self):
        auth = self.login()
        headers = {
            'Authorization': 'GoogleLogin auth=' + auth,
        }

        params = {
            'AppId': self.app_id,
            'AppKey': self.app_key,
            'n': 1000,
        }

        current_news = ""
        try:
            res = requests.get(self.URL, headers=headers, params=params)
        except Exception as e:
            logger.error(e)

        current_news = json.loads(res.text)
        return current_news

    def formatNews(self, data):
        news = {}
        news['id'] = hashlib.md5(data['title'].encode('utf-8')).hexdigest()

        if 'title' in data:
            news['title'] = data['title'][:255]
        else:
            news['title'] = ''

        if 'summary' in data:
            news['content'] = data['summary']['content']
        else:
            news['content'] = ''

        news['datetime'] = data['published']
        news['source_title'] = data['origin']['title'][:255]
        news['source_url'] = data['origin']['htmlUrl'][:255]
        news['referrer'] = data['canonical'][0]['href'][:255]

        return news

    def parse(self):
        logger.info("start parsing: %s", self.name)
        downloaded_news = self.download()

        queries = []
        for data in downloaded_news['items']:
            news_data = self.formatNews(data)

            try:
                query = News(
                    id = news_data['id'],
                    datetime = datetime.fromtimestamp(news_data['datetime'], pytz.utc),
                    title = news_data['title'],
                    content = news_data['content'],
                    source_title = news_data['source_title'],
                    source_url = news_data['source_url'],
                    referrer = news_data['referrer'],
                )
            except Exception as e:
                logger.error("%s: %s", e, str(data))

            queries.append(query)

        logger.info("done parsing: %s, %s queries were parsed", self.name, len(queries))

        return queries
