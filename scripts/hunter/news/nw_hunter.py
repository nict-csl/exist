#!/usr/bin/env python
# -*- coding: utf-8 -*-

import slackwrapper

import sys
import os
import re
import random
import configparser
import argparse
import json
from requests_oauthlib import OAuth1Session
from datetime import datetime, timezone, timedelta

version = '%(prog)s 20180223'

## Django Setup
import django
import pymysql
pymysql.install_as_MySQLdb()
conffile = os.path.join(os.path.dirname(__file__), '../conf/hunter.conf')
conf = configparser.SafeConfigParser()
conf.read(conffile)
sys.path.append(conf.get('exist', 'syspath'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'intelligence.settings')
django.setup()
from apps.news_hunter.models import Hunt
from apps.news.models import News
from django.db import IntegrityError
from django.db.models import Q

## Logger Setup
from logging.handlers import TimedRotatingFileHandler
from logging import getLogger, DEBUG, Formatter
logfilename = os.path.join(os.path.dirname(__file__), 'logs/hunter.log')
logger = getLogger()
handler = TimedRotatingFileHandler(
    filename=logfilename,
    when="D",
    interval=1,
    backupCount=31,
)
handler.setFormatter(Formatter("%(asctime)s %(name)s %(funcName)s [%(levelname)s]: %(message)s"))
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False

def argParse():
    parser = argparse.ArgumentParser(description=
            '''This is News Hunter script
            ''',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('hunt_id', type=int, help='Hunt ID')
    parser.add_argument('-v', '--version', action='version', version=version)
    args = parser.parse_args()
    return args

def postSlack(name, channel, newss):
    if channel is None:
        channel = "nw-" + name
    slack = slackwrapper.SlackWrapper()
    for news in sorted(newss):
        datetime_jst = news.publish_timestamp + timedelta(hours=9)
        message = "===============\n{published}\n{title}\n{referrer}".format(
            published = datetime_jst.strftime("%Y/%m/%d %H:%M:%S"),
            title = news.title,
            referrer = news.referrer,
        )
        try:
            res = json.loads(slack.post(channel, message).text)
            logger.info("postSlack: %s %s %s", name, channel, message.replace('\n',''))
        except Exception as e:
            logger.error(e)
        if not res["ok"] and res["error"] == "channel_not_found":
            slack.createChannel(channel)
            logger.info("Create Channel %s", name)
            slack.post(channel, message)
            logger.info("postSlack: %s %s %s", name, channel, message.replace('\n',''))
    return

def makeKeywordList(keyword):
    # , is OR. ' ' is AND
    keyword_list = []
    for klist in re.sub(r' *,+ *', ',', keyword).split(','):
        keyword_list.append(klist.split())
    return keyword_list

def searchNews(keyword_list):
    logger.info("search: %s", keyword_list)
    newss = News.objects.all()
    q_info = Q()
    for keyword_or in keyword_list:
        q_info_and = Q()
        for keyword_and in keyword_or:
            q_info_and.add(Q(content__icontains=keyword_and)|Q(title__icontains=keyword_and), Q.AND)
        q_info.add(q_info_and, Q.OR)
    return newss.filter(q_info)

def addNews(hunt_id, newss):
    hunt = Hunt.objects.get(id=hunt_id)
    diff_set = set(newss) - set(hunt.newss.all())
    if len(diff_set) > 0:
        logger.info("add: %s %s", hunt_id, diff_set)
        for news in diff_set:
            hunt.newss.add(news)
        try:
            hunt.save()
        except Exception as e:
            logger.error(e)
            return 0
    return diff_set

def getHuntInfo(hunt_id):
    hunt = Hunt.objects.get(id=hunt_id)
    return hunt.name, hunt.notice, hunt.keyword, hunt.channel

if __name__ == "__main__":
    hunt_id = argParse().hunt_id
    logger.info("start: %s", hunt_id)
    name, notice, keyword, channel = getHuntInfo(hunt_id)
    keyword_list = makeKeywordList(keyword)
    newss = searchNews(keyword_list)
    diff_set = addNews(hunt_id, newss)
    if len(diff_set) != 0 and notice:
        postSlack(name, channel, diff_set)
    logger.info("done: %s", hunt_id)

