#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from datetime import datetime, timezone
import django
import pandas as pd
import xml.etree.ElementTree as ET
import hashlib
import requests
import configparser
from io import StringIO
import pymysql
pymysql.install_as_MySQLdb()
import plugins
import plugins_private

## Django Setup
conffile = os.path.join(os.path.dirname(__file__), "conf/insert2db.conf")
conf = configparser.SafeConfigParser()
conf.read(conffile)
sys.path.append(conf.get('exist', 'syspath'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'intelligence.settings')
django.setup()
from reputation.models import blacklist
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

def saveQuery(queries, name):
    cnt = 0
    if queries is None:
        logger.info("queries is None: %s", name)
        return
    for query in queries:
        try:
            query.save(force_insert=True)
            cnt += 1
        except IntegrityError:
            continue
        except Exception as e:
            logger.error("%s: %s", e, query)
            continue
    logger.info("done insert queries: %s, %s queries were inserted", name, cnt)

if __name__ == '__main__':
    logger.info("%s start", __file__)

    # SecureWorks IP
    queries = plugins_private.sw_ip.SW_IP(ID=101).parse()
    if queries is not None:
        saveQuery(queries, 'SecureWorksIP')

    # SecureWorks Domain
    queries = plugins_private.sw_domain.SW_DOMAIN(ID=102).parse()
    if queries is not None:
        saveQuery(queries, 'SecureWorksDomain')

    # MalwareDomainList
    queries = plugins.mdl.MDL(ID=201).parse()
    if queries is not None:
        saveQuery(queries, 'MDL')

    # RansomWareTracker
    queries = plugins.rwtracker.RWTracker(ID=211).parse()
    if queries is not None:
        saveQuery(queries, 'RansomWareTracker')

    # ZeusTracker
    queries = plugins.zeus.ZeusTracker(ID=212).parse()
    if queries is not None:
        saveQuery(queries, 'ZeusTracker')

#    # ThreatExpert
#    queries = plugins.threatexpert.ThreatExpert(ID=231).parse()
#    if queries is not None:
#        saveQuery(queries, 'ThreatExpert')

    # Dshield Low
    queries = plugins.dshield_low.DshieldLow(ID=221).parse()
    if queries is not None:
        saveQuery(queries, 'Dshield_Low')

    # Dshield Medium
    queries = plugins.dshield_medium.DshieldMedium(ID=222).parse()
    if queries is not None:
        saveQuery(queries, 'Dshield_Medium')

    # Dshield High
    queries = plugins.dshield_high.DshieldHigh(ID=223).parse()
    if queries is not None:
        saveQuery(queries, 'Dshield_High')

    # PhishTank
    queries = plugins.phishtank.PhishTank(ID=241).parse()
    if queries is not None:
        saveQuery(queries, 'PhishTank')

    # BambenekIP
    queries = plugins.bambenek_ip.BambenekIP(ID=251).parse()
    if queries is not None:
        saveQuery(queries, 'BambenekIP')

    # BambenekDomain
    queries = plugins.bambenek_domain.BambenekDomain(ID=252).parse()
    if queries is not None:
        saveQuery(queries, 'BambenekDomain')

    # Cins
    queries = plugins.cins.Cins(ID=261).parse()
    if queries is not None:
        saveQuery(queries, 'Cins')

    # CyberCrime
    queries = plugins.cybercrime.CyberCrime(ID=271).parse()
    if queries is not None:
        saveQuery(queries, 'CyberCrimeTracker')

    # Malshare
    queries = plugins.malshare.Malshare(ID=281).parse()
    if queries is not None:
        saveQuery(queries, 'Malshare')

#    # Minotr
#    queries = plugins.minotr.Minotr(ID=291).parse()
#    if queries is not None:
#        saveQuery(queries, 'Minotr')

    logger.info("%s done", __file__)

