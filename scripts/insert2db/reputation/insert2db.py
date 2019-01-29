#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import configparser
import inspect
import plugins
from plugins import *
import plugins_private
from plugins_private import *

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
from apps.reputation.models import blacklist
import django.utils.timezone as tzone
from django.db import IntegrityError

## Logger Setup
from logging.handlers import TimedRotatingFileHandler
from logging import getLogger, DEBUG, Formatter
logfilename = os.path.join(os.path.dirname(__file__), 'logs/insert2db.log')
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

def printQuery(queries):
    for query in queries:
        print("==========")
        print(query.id)
        print(query.ip)
        print(query.domain)
        print(query.url)
        print(query.datetime)
        print(query.referrer)
        print(query.description)
        print(query.countrycode)
        print(query.get_source_display())

def saveQuery(queries):
    res = []
    cnt = 0
    try:
        res = blacklist.objects.bulk_create(queries)
    except:
        for query in queries:
            try:
                query.save(force_insert=True)
                cnt += 1
            except IntegrityError:
                continue
            except Exception as e:
                logger.error("%s: %s", e, query)
                continue

    cnt += len(res)
    logger.info("%s queries were inserted", cnt)

if __name__ == '__main__':
    logger.info("%s start", __file__)

    modules = list(map(lambda x:x[0], inspect.getmembers(plugins, inspect.ismodule)))
    for module in modules:
        if module == 'glob' or module == 'os':
            continue
        try:
            queries = getattr(plugins, module).Tracker().parse()
        except Exception as e:
            logger.error(e)
        saveQuery(queries)

    modules = list(map(lambda x:x[0], inspect.getmembers(plugins_private, inspect.ismodule)))
    for module in modules:
        if module == 'glob' or module == 'os':
            continue
        try:
            queries = getattr(plugins_private, module).Tracker().parse()
        except Exception as e:
            logger.error(e)
        saveQuery(queries)

    logger.info("%s done", __file__)

