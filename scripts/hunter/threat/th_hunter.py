#!/usr/bin/env python
# -*- coding: utf-8 -*-

import slackwrapper

import sys
import os
import re
import random
from datetime import datetime, timezone, timedelta
import django
import configparser
import argparse
import json
from requests_oauthlib import OAuth1Session
import pymysql
pymysql.install_as_MySQLdb()

version = '%(prog)s 20180223'
conffile = os.path.join(os.path.dirname(__file__), 'conf/threat.conf')
conf = configparser.SafeConfigParser()
conf.read(conffile)

## Django Setup
sys.path.append(conf.get('exist', 'syspath'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'intelligence.settings')
django.setup()
from threat_hunter.models import Hunt
from threat.models import Event, Attribute
from django.db import IntegrityError
from django.db.models import Q

## Logger Setup
from logging import getLogger, StreamHandler, FileHandler, DEBUG, Formatter
logfilename = os.path.join(os.path.dirname(__file__), 'logs/hunter.log')
logger = getLogger(__name__)
#handler_stream = StreamHandler()
#handler_stream.setFormatter(logging.Formatter("%(asctime)s %(levelname)8s %(message)s"))
handler_file = FileHandler(filename=logfilename)
handler_file.setFormatter(Formatter("%(asctime)s %(levelname)8s %(message)s"))
logger.setLevel(DEBUG)
#logger.addHandler(handler_stream)
logger.addHandler(handler_file)
logger.propagate = False

def argParse():
    parser = argparse.ArgumentParser(description=
            '''This is Threat Hunter script
            ''',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('hunt_id', type=int, help='Hunt ID')
    parser.add_argument('-v', '--version', action='version', version=version)
    args = parser.parse_args()
    return args

def postSlack(name, channel, events):
    if channel is None:
        channel = "th-" + name
    slack = slackwrapper.SlackWrapper()
    for event in sorted(events):
        datetime_jst = event.publish_timestamp + timedelta(hours=9)
        message = "===============\n{published}\n{info}\nhttp://10.13.2.32/threat/event/{id}/".format(
            published = datetime_jst.strftime("%Y/%m/%d %H:%M:%S"),
            info = event.info,
            id = event.id,
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

def searchThreat(keyword_list):
    logger.info("search: %s", keyword_list)
    events = Event.objects.all()
    q_info = Q()
    for keyword_or in keyword_list:
        q_info_and = Q()
        for keyword_and in keyword_or:
            q_info_and.add(Q(info__icontains=keyword_and), Q.AND)
        q_info.add(q_info_and, Q.OR)
    q_attr = Q()
    for keyword_or in keyword_list:
        q_attr_and = Q()
        for keyword_and in keyword_or:
            q_attr_and.add(Q(value__icontains=keyword_and), Q.AND)
        q_attr.add(q_attr_and, Q.OR)
    event_list = Attribute.objects.filter(q_attr).values_list('event')
    return events.filter(q_info| Q(id__in=event_list))

def addEvents(hunt_id, events):
    hunt = Hunt.objects.get(id=hunt_id)
    diff_set = set(events) - set(hunt.events.all())
    if len(diff_set) > 0:
        logger.info("add: %s %s", hunt_id, diff_set)
        for event in diff_set:
            hunt.events.add(event)
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
    events = searchThreat(keyword_list)
    diff_set = addEvents(hunt_id, events)
    if len(diff_set) != 0 and notice:
        postSlack(name, channel, diff_set)
    logger.info("done: %s", hunt_id)

