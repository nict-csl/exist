import sys
import os
import configparser
import requests
import pandas as pd
import xmltodict
import json
import hashlib
from io import StringIO
from datetime import datetime, timezone
from time import sleep

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
from apps.vuln.models import Vuln, Product, Vendor, Reference, CVSS, NVD
import django.utils.timezone as tzone
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

## Logger Setup
from logging import getLogger, DEBUG, NullHandler
logger = getLogger(__name__)
logger.addHandler(NullHandler())
logger.setLevel(DEBUG)
logger.propagate = True

DataDir = os.path.join(os.path.dirname(__file__), '../data/')

class Tracker():
    def __init__(self):
        self.name = 'JVN'
        self.ID = 201
        self.URL = 'https://jvndb.jvn.jp/myjvn?method=getVulnOverviewList&feed=hnd'
        self.DetailURL = 'https://jvndb.jvn.jp/myjvn?method=getVulnDetailInfo&feed=hnd&vulnId='
        self.DataFilePath = DataDir + 'jvn/myjvn.xml'

    def getOverview(self):
        try:
            res = requests.get(self.URL)
            vulns = xmltodict.parse(res.text)
        except Exception as e:
            logger.error(e)
        if not res.text == '':
            open(self.DataFilePath, 'w').write(res.text)
        return vulns

    def getDetail(self, vulnId):
        URL = self.DetailURL + vulnId
        try:
            res = requests.get(URL)
            detail = xmltodict.parse(res.text)['VULDEF-Document']['Vulinfo']['VulinfoData']
        except Exception as e:
            logger.error(e)
        return detail

    def saveQuery(self, q, forceinsert=False):
        try:
            q.save(force_insert=forceinsert)
            return q
        except IntegrityError as e:
            logger.warn("IntegrityError: ID: %s" % q)
            return 0
        except Exception as e:
            logger.error(e)
            return 0

    def insertRef(self, ref):
        logger.info("Reference: %s insert" % ref['Name'])
        try:
            ref_id = Reference.objects.get(url=ref['URL'])
            return ref_id
        except ObjectDoesNotExist:
            pass
        except Exception as e:
            logger.error(e)

        ref_id = hashlib.md5(ref['URL'].encode('utf-8')).hexdigest()
        try:
            query = Reference(
                id = ref_id,
                reftype = ref['@type'],
                value = ref['Name'] + ': ' + ref['VulinfoID'],
                url = ref['URL'],
            )
        except Exception as e:
            logger.error(e)

        return self.saveQuery(query)

    def insertNvd(self, nvd):
        logger.info("NVD: %s insert" % nvd['VulinfoID'])
        try:
            nvd_id = NVD.objects.get(id=nvd['VulinfoID'])
            return nvd_id
        except ObjectDoesNotExist:
            pass
        except Exception as e:
            logger.error(e)

        nvd_id = nvd['VulinfoID']
        try:
            query = NVD(
                id = nvd_id,
            )
        except Exception as e:
            logger.error(e)

        return self.saveQuery(query)

    def insertCvss(self, cvss):
        logger.info("CVSS: %s insert" % cvss['@version'])
        try:
            cvss_id = CVSS.objects.get(vector=cvss['Vector'])
            return cvss_id
        except ObjectDoesNotExist:
            pass
        except Exception as e:
            logger.error(e)

        cvss_id = hashlib.md5(cvss['Vector'].encode('utf-8')).hexdigest()
        try:
            query = CVSS(
                id = cvss_id,
                score = cvss['Base'],
                calculated_cvss_base_score = cvss['Base'],
                version = cvss['@version'],
                vector = cvss['Vector'],
                generated_on = tzone.now(),
            )
        except Exception as e:
            logger.error(e)

        return self.saveQuery(query)

    def insertVendor(self, vendor):
        logger.info("Vendor: %s insert" % vendor)
        try:
            vendor_id = Vendor.objects.get(name=vendor)
            return vendor_id
        except ObjectDoesNotExist:
            pass
        except Exception as e:
            logger.error(e)

        vendor_id = hashlib.md5(vendor.encode('utf-8')).hexdigest()
        try:
            query = Vendor(
                id = vendor_id,
                name = vendor,
            )
        except Exception as e:
            logger.error(e)

        return self.saveQuery(query)

    def insertProduct(self, product):
        logger.info("Product: %s insert" % product)
        try:
            product_id = Product.objects.get(name=product)
            return product_id
        except ObjectDoesNotExist:
            pass
        except Exception as e:
            logger.error(e)

        product_id = hashlib.md5(product.encode('utf-8')).hexdigest()
        try:
            query = Product(
                id = product_id,
                name = product,
            )
        except Exception as e:
            logger.error(e)

        return self.saveQuery(query)

    def insertVuln(self, item, detail, vendor_list, product_list, ref_list, cvss_list, nvd_list):
        logger.info("insertVuln  " + item.get('sec:identifier'))

        try:
            query = Vuln(
                id = item.get('sec:identifier'),
                title = item.get('title'),
                description = item.get('description'),
                vulndb_published_date = datetime.strptime(item.get('dc:date'), '%Y-%m-%dT%H:%M:%S+09:00').replace(tzinfo=tzone.get_fixed_timezone(540)),
                vulndb_last_modified = datetime.strptime(item.get('dcterms:modified'), '%Y-%m-%dT%H:%M:%S+09:00').replace(tzinfo=tzone.get_fixed_timezone(540)),
                disclosure_date = datetime.strptime(item.get('dcterms:issued'), '%Y-%m-%dT%H:%M:%S+09:00').replace(tzinfo=tzone.get_fixed_timezone(540)),
                solution = detail['Solution']['SolutionItem']['Description'],
                impact = detail['Impact']['ImpactItem']['Description'],
                link = item.get('link'),
                source = self.ID,
            )
        except Exception as e:
            logger.error(e)

        #self.printQuery(query)
        self.saveQuery(query)

        for vendor in vendor_list:
            try:
                vendor_obj = self.insertVendor(vendor)
                query.vendors.add(vendor_obj)
            except Exception as e:
                logger.error(e)

        for product in product_list:
            try:
                product_obj = self.insertProduct(product)
                query.products.add(product_obj)
            except Exception as e:
                logger.error(e)

        for ref in ref_list:
            try:
                ref_obj = self.insertRef(ref)
                query.references.add(ref_obj)
            except Exception as e:
                logger.error(e)

        for nvd in nvd_list:
            try:
                nvd_obj = self.insertNvd(nvd)
                query.nvds.add(nvd_obj)
            except Exception as e:
                logger.error(e)

        for cvss in cvss_list:
            try:
                cvss_obj = self.insertCvss(cvss)
                query.cvsses.add(cvss_obj)
            except Exception as e:
                logger.error(e)

    def printQuery(self, q):
        print(q.id)
        print(q.title)
        print(q.description)
        print(q.vulndb_published_date)
        print(q.vulndb_last_modified)
        print(q.disclosure_date)
        print(q.solution)
        print(q.impact)
        print(q.source)
        return

    def parse(self):
        logger.info("start parsing: %s", self.name)

        vulns = self.getOverview()
        queries = []
        for item in vulns['rdf:RDF']['item']:
            detail = self.getDetail(item.get('sec:identifier'))
            vendor_list = []
            product_list = []
            if isinstance(detail['Affected']['AffectedItem'], dict):
                vendor_list.append(detail['Affected']['AffectedItem']['Name'])
                product_list.append(detail['Affected']['AffectedItem']['ProductName'])
            elif isinstance(detail['Affected']['AffectedItem'], list):
                for aitem in detail['Affected']['AffectedItem']:
                    vendor_list.append(aitem['Name'])
                    product_list.append(aitem['ProductName'])

            ref_list = []
            nvd_list = []
            if isinstance(detail['Related']['RelatedItem'], dict):
                ref_list.append(detail['Related']['RelatedItem'])
                if detail['Related']['RelatedItem']['Name'] == 'Common Vulnerabilities and Exposures (CVE)':
                    nvd_list.append(detail['Related']['RelatedItem'])
            elif isinstance(detail['Related']['RelatedItem'], list):
                for ref in detail['Related']['RelatedItem']:
                    ref_list.append(ref)
                    if ref['Name'] == 'Common Vulnerabilities and Exposures (CVE)':
                        nvd_list.append(ref)

            cvss_list = []
            if 'Cvss' in detail['Impact']:
                if isinstance(detail['Impact']['Cvss'], dict):
                    if detail['Impact']['Cvss']['@version'] == '3.0':
                        cvss_list.append(detail['Impact']['Cvss'])
                elif isinstance(detail['Impact']['Cvss'], list):
                    for cvss in detail['Impact']['Cvss']:
                        if cvss['@version'] == '3.0':
                            cvss_list.append(cvss)

            self.insertVuln(item, detail, vendor_list, product_list, ref_list, cvss_list, nvd_list)

        logger.info("done parsing: %s, %s queries were parsed", self.name, len(queries))
        return queries
