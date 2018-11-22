#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from datetime import datetime, timezone
import django
import configparser
import json
from requests_oauthlib import OAuth1Session
import pymysql
pymysql.install_as_MySQLdb()

version = '%(prog)s 20171110'
conffile = os.path.join(os.path.dirname(__file__), "conf/twitter.conf")
conf = configparser.SafeConfigParser()
conf.read(conffile)

## Django Setup
sys.path.append(conf.get('exist', 'syspath'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'intelligence.settings')
django.setup()
from twitter.models import tweet
from django.db import IntegrityError

## Logger Setup
from logging import getLogger, StreamHandler, FileHandler, DEBUG, Formatter
logfilename = os.path.join(os.path.dirname(__file__), 'logs/insert2db.log')
logger = getLogger(__name__)
handler_file = FileHandler(filename=logfilename)
handler_file.setFormatter(Formatter("%(asctime)s %(levelname)8s %(message)s"))
logger.setLevel(DEBUG)
logger.addHandler(handler_file)
logger.propagate = False

def getTimeline_test():
    f = open('data.json', 'r')
    timeline = json.load(f)
    return timeline

def getTimeline():
    params = {}

    CK = conf.get('auth-timeline', 'CK')
    CS = conf.get('auth-timeline', 'CS')
    AT = conf.get('auth-timeline', 'AT')
    AS = conf.get('auth-timeline', 'AS')
    url = conf.get('url', 'timeline')

    twitter = OAuth1Session(CK, CS, AT, AS)
    try:
        req = twitter.get(url, params = params)
    except Exception as e:
        logger.error(e)
        return

    if req.status_code == 200:
        timeline = json.loads(req.text)
        limit = req.headers['x-rate-limit-remaining']
        reset = req.headers['x-rate-limit-reset']
        logger.info("API remain: %s", limit)
        logger.info("API reset: %s", reset)
        return timeline
    else:
        logger.error("HTTP status_code: %d", req.status_code)
        return

def parseTimeline(timeline):
    cnt = 0
    for line in timeline:
        logger.info("%s start", line["id"])
        try:
            query = tweet(
                id = line["id"],
                datetime = datetime.strptime(line["created_at"], "%a %b %d %H:%M:%S +0000 %Y").replace(tzinfo=timezone.utc),
                user = line["user"]["name"],
                screen_name = line["user"]["screen_name"],
                text = line["text"],
            )
        except Exception as e:
            logger.error("%s: %s", e, line)
        if saveQuery(query, line):
            cnt += 1
    logger.info("%d inserted", cnt)

def saveQuery(q, line):
    try:
        q.save(force_insert=True)
        return 1
    except IntegrityError:
        return 0
    except Exception as e:
        logger.error("%s: %s", e, line)
        return 0

def printQuery(q):
    print("============")
    print(q.id)
    print(q.user)
    print(q.screen_name)
    print(q.datetime)
    print(q.text)

if __name__ == "__main__":
    logger.info("%s start", __file__)
    timeline = getTimeline()
    #timeline = getTimeline_test()
    parseTimeline(timeline)
    logger.info("%s done", __file__)

