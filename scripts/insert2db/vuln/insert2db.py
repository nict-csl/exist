#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import json
import hashlib
import requests
import configparser
from time import sleep
from io import StringIO
from datetime import datetime, timezone, timedelta

## Django Setup
import django
import pymysql
pymysql.install_as_MySQLdb()
conffile = os.path.join(os.path.dirname(__file__), "conf/insert2db.conf")
conf = configparser.SafeConfigParser()
conf.read(conffile)
sys.path.append(conf.get('exist', 'syspath'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'intelligence.settings')
django.setup()
from vuln.models import Vuln, Tag, Vendor, Product, Reference, CVSS, NVD, NVDref, Author
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

def printQuery(q):
    print("==========")
    print(q.id)
    print(q)
    return

def saveQuery(q, forceinsert=False):
    try:
        q.save(force_insert=forceinsert)
        return q
    except IntegrityError as e:
        logger.warn("IntegrityError: ID: %s" % q)
        return 0
    except Exception as e:
        logger.error(e)
        return 0

def insertRef(ref):
    logger.info("insert ref")
    line = ref.get('type') + ref.get('value')
    md5 = hashlib.md5(line.encode('utf-8')).hexdigest()
    try:
        query = Reference(
            id = md5,
            reftype = ref.get('type'),
            value = ref.get('value'),
        )
    except Exception as e:
        logger.error(e)
        return 0
    return saveQuery(query)

def insertTag(tag):
    logger.info("Tag ID: %s insert" % tag['id'])
    query = Tag(
        id = int(tag['id']),
        name = tag.get('name'),
        description = tag.get('description'),
        longname = tag.get('longname'),
    )
    return saveQuery(query)

def insertCVSS(cvss):
    logger.info("CVSS ID: %s insert" % cvss['id'])
    query = CVSS(
        id = int(cvss['id']),
        access_complexity = cvss.get('access_complexity'),
        availability_impact = cvss.get('availability_impact'),
        confidentiality_impact = cvss.get('confidentiality_impact'),
        access_vector = cvss.get('access_vector'),
        authentication = cvss.get('authentication'),
        integrity_impact = cvss.get('integrity_impact'),
        cve_id = cvss.get('cve_id'),
        source = cvss.get('source'),
        generated_on = datetime.strptime(cvss.get('generated_on'), '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc),
        score = cvss.get('score'),
        calculated_cvss_base_score = cvss.get('calculated_cvss_base_score'),
    )
    return saveQuery(query)

def insertVendor(vendor):
    logger.info("Vendor ID: %s insert" % vendor['id'])
    query = Vendor(
        id = int(vendor['id']),
        name = vendor.get('name'),
    )
    return saveQuery(query)

def insertProduct(product):
    logger.info("Product ID: %s insert" % product['id'])
    query = Product(
        id = int(product['id']),
        name = product.get('name'),
    )
    return saveQuery(query)

def insertAuthor(author):
    logger.info("Author ID: %s insert" % author['id'])
    query = Author(
        id = int(author['id']),
        name = author.get('name'),
    )
    return saveQuery(query)

def insertNVDRef(nvd_ref):
    logger.info("insert nvd_ref")
    line = nvd_ref.get('url') + nvd_ref.get('source') + nvd_ref.get('name')
    md5 = hashlib.md5(line.encode('utf-8')).hexdigest()
    try:
        query = NVDref(
            id = md5,
            url = nvd_ref.get('url')[:254],
            source = nvd_ref.get('source'),
            name = nvd_ref.get('name'),
        )
    except Exception as e:
        logger.error(e)
        return 0
    return saveQuery(query)

def insertNVD(nvd):
    logger.info("CVE_ID: %s insert" % nvd['cve_id'])
    if type(nvd['cvss_score']) == str:
        cvss_access_complexity = None
        cvss_availability_impact = None
        cvss_confidentiality_impact = None
        cvss_access_vector = None
        cvss_authentication = None
        cvss_integrity_impact = None
        cvss_score = None
    else:
        cvss_access_complexity = nvd['cvss_score'].get('access_complexity')
        cvss_availability_impact = nvd['cvss_score'].get('availability_impact')
        cvss_confidentiality_impact = nvd['cvss_score'].get('confidentiality_impact')
        cvss_access_vector = nvd['cvss_score'].get('access_vector')
        cvss_authentication = nvd['cvss_score'].get('authentication')
        cvss_integrity_impact = nvd['cvss_score'].get('integrity_impact')
        cvss_score = nvd['cvss_score'].get('score')

    try:
        query = NVD(
            id = nvd.get('cve_id'),
            cwe_id = nvd.get('cwe_id'),
            cvss_access_complexity = cvss_access_complexity,
            cvss_availability_impact = cvss_availability_impact,
            cvss_confidentiality_impact = cvss_confidentiality_impact,
            cvss_access_vector = cvss_access_vector,
            cvss_authentication = cvss_authentication,
            cvss_integrity_impact = cvss_integrity_impact,
            cvss_score = cvss_score,
            summary = nvd.get('summary'),
        )
    except Exception as e:
        logger.error(e)
    saveQuery(query)

    if len(nvd.get('references', '')) > 0:
        for nvd_ref in nvd['references']:
            try:
                nvd_ref_obj = insertNVDRef(nvd_ref)
                query.references.add(nvd_ref_obj)
            except Exception as e:
                logger.error(e)
    return query

def insertVuln(result, tag_list, ref_list, cvss_list, vendor_list, product_list, nvd_list, author_list, src_id):
    logger.info("insertVuln " + str(result['vulndb_id']))
    try:
        vulndb_published_date = datetime.strptime(result['vulndb_published_date'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
    except Exception as e:
        vulndb_published_date = datetime.strptime('1999-01-01T00:00:00+0900', '%Y-%m-%dT%H:%M:%S%z')
    try:
        exploit_publish_date = datetime.strptime(result['exploit_publish_date'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
    except Exception as e:
        exploit_publish_date = None
    try:
        vulndb_last_modified = datetime.strptime(result['vulndb_last_modified'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
    except Exception as e:
        vulndb_last_modified = None
    try:
        discovery_date = datetime.strptime(result['discovery_date'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
    except Exception as e:
        discovery_date = None
    try:
        disclosure_date = datetime.strptime(result['disclosure_date'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
    except Exception as e:
        disclosure_date = None
    try:
        vendor_informed_date = datetime.strptime(result['vendor_informed_date'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
    except Exception as e:
        vendor_informed_date = None
    try:
        vendor_ack_date = datetime.strptime(result['vendor_ack_date'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
    except Exception as e:
        vendor_ack_date = None
    try:
        solution_date = datetime.strptime(result['solution_date'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
    except Exception as e:
        solution_date = None
    try:
        third_party_solution_date = datetime.strptime(result['third_party_solution_date'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
    except Exception as e:
        third_party_solution_date = None
    try:
        query = Vuln(
            id = result['vulndb_id'],
            title = result['title'],
            description = result['description'],
            t_description = result['t_description'],
            vulndb_published_date = vulndb_published_date,
            exploit_publish_date = exploit_publish_date,
            vulndb_last_modified = vulndb_last_modified,
            discovery_date = discovery_date,
            disclosure_date = disclosure_date,
            vendor_informed_date = vendor_informed_date,
            vendor_ack_date = vendor_ack_date,
            solution_date = solution_date,
            third_party_solution_date = third_party_solution_date,
            solution = result['solution'],
            manual_notes = result['manual_notes'],
            keywords = result['keywords'][:254],
            source = src_id,
        )
    except Exception as e:
        logger.error(e)
    saveQuery(query)

    for tag in tag_list:
        try:
            tag_obj = insertTag(tag)
            query.tags.add(tag_obj)
        except Exception as e:
            logger.error(e)
    for ref in ref_list:
        try:
            ref_obj = insertRef(ref)
            query.references.add(ref_obj)
        except Exception as e:
            logger.error(e)
    for cvss in cvss_list:
        try:
            cvss_obj = insertCVSS(cvss)
            query.cvsses.add(cvss_obj)
        except Exception as e:
            logger.error(e)
    for author in author_list:
        try:
            author_obj = insertAuthor(author)
            query.authors.add(author_obj)
        except Exception as e:
            logger.error(e)
    for vendor in vendor_list:
        try:
            vendor_obj = insertVendor(vendor)
            query.vendors.add(vendor_obj)
        except Exception as e:
            logger.error(e)
    for product in product_list:
        try:
            product_obj = insertProduct(product)
            query.products.add(product_obj)
        except Exception as e:
            logger.error(e)
    for nvd in nvd_list:
        try:
            nvd_obj = insertNVD(nvd)
            query.nvds.add(nvd_obj)
        except Exception as e:
            logger.error(e)

def parseVuln(src_name, src_id):
    logger.info("parseVuln " + str(sys.argv[1]))
    f = open(sys.argv[1], 'r')
    json_data = json.load(f)
    if not 'results' in json_data:
        return
    for result in json_data['results']:
        tag_list = []
        if len(result.get('classifications', '')) > 0:
            for tag in result['classifications']:
                tag_list.append(tag)
        ref_list = []
        if len(result.get('ext_references', '')) > 0:
            for ref in result['ext_references']:
                ref_list.append(ref)
        cvss_list = []
        if len(result.get('cvss_metrics', '')) > 0:
            for cvss in result['cvss_metrics']:
                cvss_list.append(cvss)
        author_list = []
        if len(result.get('authors', '')) > 0:
            for author in result['authors']:
                author_list.append(author)
        vendor_list = []
        product_list = []
        if len(result.get('vendors', '')) > 0:
            for vendor in result['vendors']:
                vendor_list.append(vendor)
                if len(vendor.get('products', '')) > 0:
                    for product in vendor['products']:
                        product_list.append(product)
        nvd_list = []
        if len(result.get('nvd_additional_information', '')) > 0:
            for nvd in result['nvd_additional_information']:
                if len(nvd) > 0:
                    nvd_list.append(nvd)

        insertVuln(result, tag_list, ref_list, cvss_list, vendor_list, product_list, nvd_list, author_list, src_id)

if __name__ == '__main__':
    logger.info("start")
    parseVuln("vuln", 101)
    logger.info("done")

