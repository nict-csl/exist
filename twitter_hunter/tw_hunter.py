#!/usr/bin/env python
# -*- coding: utf-8 -*-

import slackwrapper

import sys
import os
import random
from datetime import datetime, timezone, timedelta
import django
import configparser
import argparse
import json
from requests_oauthlib import OAuth1Session
import pymysql
pymysql.install_as_MySQLdb()

version = '%(prog)s 20171116'
conffile = os.path.dirname(__file__) + "/twitter.conf"
conf = configparser.SafeConfigParser()
conf.read(conffile)

## Django Setup
sys.path.append(conf.get('insertdb', 'syspath'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'intelligence.settings')
django.setup()
from twitter_hunter.models import tweet, Hunt
from django.db import IntegrityError

## Logger Setup
from logging import getLogger, StreamHandler, FileHandler, DEBUG, Formatter
logfilename = conf.get('hunter', 'logdir') + "/hunter.log"
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
            '''This is Twitter Hunter script
            ''',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('hunt_id', type=int, help='Hunt ID')
    parser.add_argument('-v', '--version', action='version', version=version)
    args = parser.parse_args()
    return args

def getClientKey():
    auth_hunter = 'auth-hunter%02d' % random.randint(0,18)
    CK = conf.get(auth_hunter, 'CK')
    CS = conf.get(auth_hunter, 'CS')
    AT = conf.get(auth_hunter, 'AT')
    AS = conf.get(auth_hunter, 'AS')
    client = OAuth1Session(CK, CS, AT, AS)
    return client

def getScreenName(tw, screen_name):
    params = {
        'screen_name': screen_name
    }
    url = conf.get('url', 'showuser')
    try:
        res = tw.get(url, params = params)
    except Exception as e:
        logger.error(e)
        return

    if res.status_code == 200:
        return json.loads(res.text)['id']
    else:
        logger.error("Error: %d" % res.status_code)
        return

def getResponse(tw, track, follow):
    if follow is not None and follow != '':
        follow = getScreenName(tw, follow)
    params = {
        'track': track,
        'follow': follow,
    }
    url = conf.get('url', 'filter')

    try:
        res = tw.post(url, params = params, stream = True)
    except Exception as e:
        logger.error(e)
        return

    return res
    if res.status_code == 200:
        return res
    else:
        logger.error("Error: %d" % res.status_code)
        return

def saveResponse(res, name, hunt_id, notice, channel):
    for line_json in res.iter_lines(chunk_size=64):
        try:
            line = json.loads(line_json.decode('utf-8'))
        except json.JSONDecodeError as e:
            logger.debug("%s 再取得: %s", hunt_id, e)
            continue
        except Exception as e:
            logger.debug(e)
            continue
        logger.info("%s %s get tweet", hunt_id, line["id"])
        try:
            query = tweet(
                id = line["id"],
                datetime = datetime.strptime(line["created_at"], "%a %b %d %H:%M:%S +0000 %Y").replace(tzinfo=timezone.utc),
                user = line["user"]["name"],
                screen_name = line["user"]["screen_name"],
                text = line["text"],
                hunt_id = Hunt.objects.get(id=hunt_id)
            )
        except Exception as e:
            logger.warn("%s: %s" % (e, line))
        #printQuery(query)
        if saveQuery(query, line):
            if notice:
                postSlack(name, channel, query)

def postSlack(name, channel, query):
    logger.info("postSlack %s" % channel)
    if channel is None:
        channel = "th-" + name
    slack = slackwrapper.SlackWrapper()
    datetime_jst = query.datetime + timedelta(hours=9)
    message = "===============\n{datetime}\n{user} @{screen_name}\n{text}".format(
        datetime = datetime_jst.strftime("%Y/%m/%d %H:%M:%S"),
        user = query.user,
        screen_name = query.screen_name,
        text = query.text,
    )
    try:
        res = json.loads(slack.post(channel, message).text)
    except Exception as e:
        logger.error(e)
    if not res["ok"] and res["error"] == "channel_not_found":
        slack.createChannel(channel)
        logger.info("Create Channel %s", name)
        slack.post(channel, message)
    return

def printResponse(res):
    for line in res.iter_lines(chunk_size=64):
        try:
            tweet = json.loads(line.decode('utf-8'))
            print("=========================")
            print(tweet["id"])
            print(("%s @%s") % (tweet["user"]["name"], tweet["user"]["screen_name"]))
            print(tweet["created_at"])
            print(tweet["text"])
        except json.JSONDecodeError as e:
            print('再取得')
            continue
        except Exception as e:
            print(e)
            continue

def saveQuery(q, line):
    try:
        q.save(force_insert=True)
        return 1
    except IntegrityError:
        return 0
    except Exception as e:
        logger.warn(e, line)
        return 0

def printQuery(q):
    print("============")
    print(q.id)
    print(q.user)
    print(q.screen_name)
    print(q.datetime)
    print(q.text)

def getHuntInfo(hunt_id):
    hunt = Hunt.objects.get(id=hunt_id)
    return hunt.name, hunt.notice, hunt.track, hunt.follow, hunt.channel

if __name__ == "__main__":
    hunt_id = argParse().hunt_id
    name, notice, track, follow, channel = getHuntInfo(hunt_id)
    client = getClientKey()
    res = getResponse(client, track, follow)
    saveResponse(res, name, hunt_id, notice, channel)

