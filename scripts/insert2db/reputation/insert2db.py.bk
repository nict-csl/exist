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

conffile = os.path.join(os.path.dirname(__file__), "conf/insert2db.conf")
conf = configparser.SafeConfigParser()
conf.read(conffile)

## Django Setup
sys.path.append(conf.get('exist', 'syspath'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'intelligence.settings')
django.setup()
from reputation.models import blacklist
import django.utils.timezone as tzone
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

URLs = {
    'mdl' : 'http://www.malwaredomainlist.com/updatescsv.php',
    'rw_tracker' : 'https://ransomwaretracker.abuse.ch/feeds/csv/',
    'zeus' : 'https://zeustracker.abuse.ch/rss.php',
    'threatexpert' : 'http://www.networksec.org/grabbho/block.txt',
    'dshield_low' : 'https://www.dshield.org/feeds/suspiciousdomains_Low.txt',
    'dshield_medium' : 'https://www.dshield.org/feeds/suspiciousdomains_Medium.txt',
    'dshield_high' : 'https://www.dshield.org/feeds/suspiciousdomains_High.txt',
    'phishtank' : 'http://data.phishtank.com/data/online-valid.csv',
    'sw_ip' : 'https://ws.secureworks.com/ti/v1/attackerdb-token/blackList?type=ip&listId=0&format=csv&token=d56b88333cf4f53a',
    'sw_domain' : 'https://ws.secureworks.com/ti/v1/attackerdb-token/blackList?type=domain&listId=0&format=csv&token=d56b88333cf4f53a',
    'bambenek_ip' : 'http://osint.bambenekconsulting.com/feeds/c2-ipmasterlist.txt',
    'bambenek_domain' : 'http://osint.bambenekconsulting.com/feeds/c2-dommasterlist.txt',
    'bambenek_dga' : 'http://osint.bambenekconsulting.com/feeds/dga-feed.txt',
    'cins' : 'http://cinsscore.com/list/ci-badguys.txt',
    'cybercrime' : 'https://cybercrime-tracker.net/csv.php',
    'malshare' : 'http://www.malshare.com/api.php?api_key=e252c7bbb821aed33f941b43e331c927f80aee854fbfec601fc4b7b3c3e6dc8a&action=getsourcesraw',
    'minotr' : 'https://minotr.net/raw/urls',
}

Files = {
    'mdl' : 'mdl/updatescsv.php',
    'rw_tracker' : 'abuse/rwt.csv',
    'zeus' : 'abuse/rw.xml',
    'threatexpert' : 'threatexpert/block.txt',
    'dshield_low' : 'dshield/suspiciousdomains_Low.txt',
    'dshield_medium' : 'dshield/suspiciousdomains_Medium.txt',
    'dshield_high' : 'dshield/suspiciousdomains_High.txt',
    'phishtank' : 'phishtank/online-valid.csv',
    'sw_ip' : 'secureworks/ip.csv',
    'sw_domain' : 'secureworks/domain.csv',
    'bambenek_ip' : 'bambenek/c2-ipmasterlist.txt',
    'bambenek_domain' : 'bambenek/c2-dommasterlist.txt',
    'bambenek_dga' : 'bambenek/dga-feed.txt',
    'cins' : 'cins/ci-badguys.txt',
    'cybercrime' : 'cybercrime/c2.csv',
    'malshare' : 'malshare/getsourceraw.txt',
    'minotr' : 'minotr/urls.txt',
}

DataDir = os.path.join(os.path.dirname(__file__), 'data/')

def cmpFiles(oldfile, newtext):
    diffline = ''
    if not os.path.exists(oldfile):
        f = open(oldfile, 'w')
        f.close()
    oldsets = set(open(oldfile).readlines())
    newsets = set(newtext.replace('\r\n','\n').splitlines(True))
    results = newsets.difference(oldsets)
    for result in results:
        diffline += result
    return diffline[:-1]

def delComment(s):
    result = ''
    for line in s.splitlines(True):
        if not line.startswith('#') \
                and line != "Site\n" \
                and line != "TYPE,URL,IP\n" \
                and not line.startswith('"WatchList') \
                and not line.startswith('phish_id'):
            result += line
    return result

def makeDataframe(src, header):
    df = pd.DataFrame()
    newline = ''
    try:
        res = requests.get(URLs[src])
        if res.status_code != 200:
            return df
        newline = cmpFiles(DataDir+Files[src], res.text)
        newline = delComment(newline)
    except Exception as e:
        logger.error(e)
    if not newline == '':
        open(DataDir+Files[src], 'w').write(res.text)
        df = pd.read_csv(StringIO(newline), names=header)
    return df

def printQuery(q):
    print("==========")
    print(q.id)
    print(q.ip)
    print(q.domain)
    print(q.url)
    print(q.datetime)
    print(q.referrer)
    print(q.description)
    print(q.countrycode)
    print(q.get_source_display())

def saveQuery(q, line):
    try:
        q.save(force_insert=True)
        return 1
    except IntegrityError:
        return 0
    except Exception as e:
        logger.error("%s: %s", e, line)
        return 0

def parseMDL(src_name, src_id):
    logger.info("%s start", src_name)
    header = [
        'datetime',
        'domain',
        'ip',
        'reverse',
        'description',
        'registant',
        'asn',
    ]

    df = makeDataframe(src_name, header)
    if df.empty:
        return

    cnt = 0
    for i, v in df.iterrows():
        line = str(src_id) + ","
        line += str(v.values)
        md5 = hashlib.md5(line.encode('utf-8')).hexdigest()
        try:
            query = blacklist(
                id = md5,
                ip = v.ip,
                url = 'http://' + v.domain[:248],
                datetime = datetime.strptime(v.datetime, '%Y/%m/%d_%H:%M').replace(tzinfo=timezone.utc),
                description = v.description,
                source = src_id,
                referrer = 'https://www.malwaredomainlist.com/mdl.php?search=' + v.ip,
            )
        except Exception as e:
            logger.error("%s: %s", e, line)
        if saveQuery(query, line):
            cnt += 1
    logger.info("%s %s inserted", src_name, cnt)

def parseRwTracker(src_name, src_id):
    logger.info("%s start", src_name)
    header = [
        'firstseen',
        'threat',
        'malware',
        'host',
        'url',
        'status',
        'registrar',
        'ip',
        'asn',
        'country',
    ]

    df = makeDataframe(src_name, header)
    if df.empty:
        return
    df = df.fillna('')

    cnt = 0
    for i, v in df.iterrows():
        line = str(src_id) + ","
        line += str(v.values)
        md5 = hashlib.md5(line.encode('utf-8')).hexdigest()
        try:
            query = blacklist(
                id = md5,
                ip = v.ip.split('|')[0],
                domain = v.host,
                url = v.url[:255],
                datetime = datetime.strptime(v.firstseen, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc),
                source = src_id,
                description = v.threat + ', ' + v.malware + ', ' + v.registrar + ', ' + v.asn,
                countrycode = v.country.split('|')[0],
                referrer = 'https://ransomwaretracker.abuse.ch/host/' + v.host + '/',
            )
        except Exception as e:
            logger.error("%s: %s", e, line)
        if saveQuery(query, line):
            cnt += 1
    logger.info("%s %s inserted", src_name, cnt)

def parseZeus(src_name, src_id):
    logger.info("%s start", src_name)
    header = [
        'title',
        'link',
        'description',
        'guid',
    ]

    try:
        res = requests.get(URLs[src_name])
    except Exception as e:
        logger.error(e)
    if not res.text == '':
        open(DataDir+Files[src_name], 'w').write(res.text)
    xml_data = open(DataDir+Files[src_name]).read()
    root = ET.XML(xml_data)
    all_records = []
    for child in root[0]:
        if child.tag == 'item':
            record = {}
            for subchild in child:
                record[subchild.tag] = subchild.text
            all_records.append(record)
    df = pd.DataFrame(all_records)

    if df.empty:
        return

    cnt = 0
    for i, v in df.iterrows():
        line = str(src_id) + ","
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
                source = src_id,
            )
        except Exception as e:
            logger.error("%s: %s", e, line)
        if saveQuery(query, line):
            cnt += 1
    logger.info("%s %s inserted", src_name, cnt)

def parseThreatexpert(src_name, src_id):
    logger.info("%s start", src_name)
    header = [
        'domain',
    ]

    df = makeDataframe(src_name, header)
    if df.empty:
        return

    cnt = 0
    for i, v in df.iterrows():
        line = str(src_id) + ","
        line += str(v.values)
        md5 = hashlib.md5(line.encode('utf-8')).hexdigest()
        try:
            query = blacklist(
                id = md5,
                domain = v.domain,
                datetime = tzone.now(),
                source = src_id,
                referrer = 'http://www.networksec.org/grabbho/block.txt',
            )
        except Exception as e:
            logger.error("%s: %s", e, line)
        if saveQuery(query, line):
            cnt += 1
    logger.info("%s %s inserted", src_name, cnt)

def parseDshieldLow(src_name, src_id):
    logger.info("%s start", src_name)
    header = [
        'domain',
    ]

    df = makeDataframe(src_name, header)
    if df.empty:
        return

    cnt = 0
    for i, v in df.iterrows():
        line = str(src_id) + ","
        line += str(v.values)
        md5 = hashlib.md5(line.encode('utf-8')).hexdigest()
        try:
            query = blacklist(
                id = md5,
                domain = v.domain,
                datetime = tzone.now(),
                source = src_id,
                referrer = 'https://www.dshield.org/feeds/suspiciousdomains_Low.txt',
            )
        except Exception as e:
            logger.error("%s: %s", e, line)
        if saveQuery(query, line):
            cnt += 1
    logger.info("%s %s inserted", src_name, cnt)

def parseDshieldMedium(src_name, src_id):
    logger.info("%s start", src_name)
    header = [
        'domain',
    ]

    df = makeDataframe(src_name, header)
    if df.empty:
        return

    cnt = 0
    for i, v in df.iterrows():
        line = str(src_id) + ","
        line += str(v.values)
        md5 = hashlib.md5(line.encode('utf-8')).hexdigest()
        try:
            query = blacklist(
                id = md5,
                domain = v.domain,
                datetime = tzone.now(),
                source = src_id,
                referrer = 'https://www.dshield.org/feeds/suspiciousdomains_Medium.txt',
            )
        except Exception as e:
            logger.error("%s: %s", e, line)
        if saveQuery(query, line):
            cnt += 1
    logger.info("%s %s inserted", src_name, cnt)

def parseDshieldHigh(src_name, src_id):
    logger.info("%s start", src_name)
    header = [
        'domain',
    ]

    df = makeDataframe(src_name, header)
    if df.empty:
        return

    cnt = 0
    for i, v in df.iterrows():
        line = str(src_id) + ","
        line += str(v.values)
        md5 = hashlib.md5(line.encode('utf-8')).hexdigest()
        try:
            query = blacklist(
                id = md5,
                domain = v.domain,
                datetime = tzone.now(),
                source = src_id,
                referrer = 'https://www.dshield.org/feeds/suspiciousdomains_High.txt',
            )
        except Exception as e:
            logger.error("%s: %s", e, line)
        if saveQuery(query, line):
            cnt += 1
    logger.info("%s %s inserted", src_name, cnt)

def parsePhishtank(src_name, src_id):
    logger.info("%s start", src_name)
    header = [
        'phish_id',
        'url',
        'phish_detail_url',
        'submission_time',
        'verified',
        'verification_time',
        'online',
        'target',
    ]

    df = makeDataframe(src_name, header)
    if df.empty:
        return
    if isinstance(df.iloc[0,0], str):
        logger.warning("%s AccessDenied", src_name)
        return

    cnt = 0
    for i, v in df.iterrows():
        line = str(src_id) + ","
        line += str(v.values)
        md5 = hashlib.md5(line.encode('utf-8')).hexdigest()
        try:
            query = blacklist(
                id = md5,
                url = v.url[:255],
                datetime = datetime.strptime(v.submission_time[:-6], '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc),
                description = v.target,
                referrer = v.phish_detail_url,
                source = src_id,
            )
        except Exception as e:
            logger.error("%s: %s", e, line)
        if saveQuery(query, line):
            cnt += 1
    logger.info("%s %s inserted", src_name, cnt)

def parseSecureworksIP(src_name, src_id):
    logger.info("%s start", src_name)
    header = [
        'WatchList',
        'HostAddress',
        'ReasonAdded',
        'MemberSince',
        'Latitude',
        'Longitude',
        'CountryCode',
        'Location',
    ]

    df = makeDataframe(src_name, header)
    if df.empty:
        return

    cnt = 0
    for i, v in df.iterrows():
        line = str(src_id) + ","
        line += str(v.values)
        md5 = hashlib.md5(line.encode('utf-8')).hexdigest()
        try:
            query = blacklist(
                id = md5,
                ip = v.HostAddress,
                datetime = datetime.strptime(v.MemberSince, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc),
                description = v.WatchList + ", " + v.ReasonAdded,
                countrycode = v.CountryCode,
                source = src_id,
                referrer = 'https://portal.secureworks.com/portal/intel/attackerdb',
            )
        except Exception as e:
            logger.error("%s: %s", e, line)
        if saveQuery(query, line):
            cnt += 1
    logger.info("%s %s inserted", src_name, cnt)

def parseSecureworksDomain(src_name, src_id):
    logger.info("%s start", src_name)
    header = [
        'WatchList',
        'HostAddress',
        'ReasonAdded',
        'MemberSince',
        'nan',
    ]

    df = makeDataframe(src_name, header)
    if df.empty:
        return

    cnt = 0
    for i, v in df.iterrows():
        line = str(src_id) + ","
        line += str(v.values)
        md5 = hashlib.md5(line.encode('utf-8')).hexdigest()
        try:
            query = blacklist(
                id = md5,
                domain = v.HostAddress,
                datetime = datetime.strptime(v.MemberSince, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc),
                description = v.WatchList + ", " + v.ReasonAdded,
                source = src_id,
                referrer = 'https://portal.secureworks.com/portal/intel/attackerdb',
            )
        except Exception as e:
            logger.error("%s: %s", e, line)
        if saveQuery(query, line):
            cnt += 1
    logger.info("%s %s inserted", src_name, cnt)

def parseBambenekIP(src_name, src_id):
    logger.info("%s start", src_name)
    header = [
        'ip',
        'description',
        'datetime',
        'reference',
    ]

    df = makeDataframe(src_name, header)
    if df.empty:
        return

    cnt = 0
    for i, v in df.iterrows():
        line = str(src_id) + ","
        line += str(v.values)
        md5 = hashlib.md5(line.encode('utf-8')).hexdigest()
        try:
            query = blacklist(
                id = md5,
                ip = v.ip,
                datetime = datetime.strptime(v.datetime, '%Y-%m-%d %H:%M').replace(tzinfo=timezone.utc),
                description = v.description,
                referrer = v.reference,
                source = src_id,
            )
        except Exception as e:
            logger.error("%s: %s", e, line)
        if saveQuery(query, line):
            cnt += 1
    logger.info("%s %s inserted", src_name, cnt)

def parseBambenekDomain(src_name, src_id):
    logger.info("%s start", src_name)
    header = [
        'domain',
        'description',
        'datetime',
        'reference',
    ]

    df = makeDataframe(src_name, header)
    if df.empty:
        return

    cnt = 0
    for i, v in df.iterrows():
        line = str(src_id) + ","
        line += str(v.values)
        md5 = hashlib.md5(line.encode('utf-8')).hexdigest()
        try:
            query = blacklist(
                id = md5,
                domain = v.domain,
                datetime = datetime.strptime(v.datetime, '%Y-%m-%d %H:%M').replace(tzinfo=timezone.utc),
                description = v.description,
                referrer = v.reference,
                source = src_id,
            )
        except Exception as e:
            logger.error("%s: %s", e, line)
        if saveQuery(query, line):
            cnt += 1
    logger.info("%s %s inserted", src_name, cnt)

def parseCins(src_name, src_id):
    logger.info("%s start", src_name)
    header = [
        'ip',
    ]

    df = makeDataframe(src_name, header)
    if df.empty:
        logger.warning("%s no update", src_name)
        return

    cnt = 0
    for i, v in df.iterrows():
        line = str(src_id) + "," + str(v.values)
        md5 = hashlib.md5(line.encode('utf-8')).hexdigest()
        try:
            query = blacklist(
                id = md5,
                ip = v.ip,
                datetime = tzone.now(),
                source = src_id,
                referrer = 'http://cinsscore.com/list/ci-badguys.txt',
            )
        except Exception as e:
            logger.error("%s: %s", e, line)
        if saveQuery(query, line):
            cnt += 1
    logger.info("%s %s inserted", src_name, cnt)

def parseCybercrime(src_name, src_id):
    logger.info("%s start", src_name)
    header = [
        'Type',
        'url',
        'ip',
    ]

    df = makeDataframe(src_name, header)
    if df.empty:
        logger.warning("%s no update", src_name)
        return
    df = df.fillna('')

    cnt = 0
    for i, v in df.iterrows():
        line = str(src_id) + "," + str(v.values)
        md5 = hashlib.md5(line.encode('utf-8')).hexdigest()
        try:
            query = blacklist(
                id = md5,
                url = "http://" + v.url[:248],
                ip = v.ip,
                description = v.Type,
                datetime = tzone.now(),
                source = src_id,
                referrer = 'https://cybercrime-tracker.net/index.php',
            )
        except Exception as e:
            logger.error("%s: %s", e, line)
        if saveQuery(query, line):
            cnt += 1
    logger.info("%s %s inserted", src_name, cnt)

def parseMalshare(src_name, src_id):
    logger.info("%s start", src_name)
    header = [
        'url',
    ]

    df = makeDataframe(src_name, header)
    if df.empty:
        logger.warning("%s no update", src_name)
        return

    cnt = 0
    for i, v in df.iterrows():
        line = str(src_id) + "," + str(v.values)
        md5 = hashlib.md5(line.encode('utf-8')).hexdigest()
        try:
            query = blacklist(
                id = md5,
                url = v.url[:255],
                datetime = tzone.now(),
                source = src_id,
                referrer = 'http://www.malshare.com/search.php',
            )
        except Exception as e:
            logger.error("%s: %s", e, line)
        if saveQuery(query, line):
            cnt += 1
    logger.info("%s %s inserted", src_name, cnt)

def parseMinotr(src_name, src_id):
    logger.info("%s start", src_name)
    header = [
        'url',
    ]

    df = makeDataframe(src_name, header)
    if df.empty:
        logger.warning("%s no update", src_name)
        return

    cnt = 0
    for i, v in df.iterrows():
        line = str(src_id) + "," + str(v.values)
        md5 = hashlib.md5(line.encode('utf-8')).hexdigest()
        try:
            query = blacklist(
                id = md5,
                url = v.url[:255],
                datetime = tzone.now(),
                source = src_id,
                referrer = 'https://minotr.net/',
            )
        except Exception as e:
            logger.error("%s: %s", e, line)
        if saveQuery(query, line):
            cnt += 1
    logger.info("%s %s inserted", src_name, cnt)

if __name__ == '__main__':
    logger.info("%s start", __file__)

    parseMDL("mdl", 201)
    parseRwTracker("rw_tracker", 211)
    parseZeus("zeus", 212)
    parseThreatexpert("threatexpert", 231)
    parseDshieldLow("dshield_low", 221)
    parseDshieldMedium("dshield_medium", 222)
    parseDshieldHigh("dshield_high", 223)
    parseSecureworksIP("sw_ip", 101)
    parseSecureworksDomain("sw_domain", 102)
    parsePhishtank("phishtank", 241)
    parseBambenekIP("bambenek_ip", 251)
    parseBambenekDomain("bambenek_domain", 252)
    parseCins("cins", 261)
    parseCybercrime("cybercrime", 271)
    parseMalshare("malshare", 281)
    parseMinotr("minotr", 291)

    logger.info("%s done", __file__)
