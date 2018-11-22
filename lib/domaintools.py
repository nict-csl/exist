#!/usr/bin/env python

import os
import argparse
import configparser
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

try:
    import simplejson as json
except ImportError:
    import json

version = '%(prog)s 20180907'

class DomainTools():
    def __init__(self):
        conffile = 'conf/domaintools.conf'
        conf = configparser.SafeConfigParser()
        conf.read(conffile)
        self.__base_url = conf.get('domaintools', 'url')
        self.__params = {
            'api_username': conf.get('domaintools', 'api_username'),
            'api_key': conf.get('domaintools', 'api_key'),
        }

    def getDomainProfile(self, domain):
        url = "%s%s/" % (self.__base_url, domain)
        try:
            res = requests.get(url, params=self.__params)
        except Exception as e:
            return e
        res_dict = json.loads(res.text)
        return res_dict

    def getWhois(self, domain):
        url = "%s%s/whois/parsed/" % (self.__base_url, domain)
        try:
            res = requests.get(url, params=self.__params)
        except Exception as e:
            return e
        res_dict = json.loads(res.text)
        return res_dict

def ArgParse():
    parser = argparse.ArgumentParser(description=
    '''This script get Whois info from DomainTools.
    ConfigureFile: ./domaintools.conf
    ''',
    formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('domain', action='store', type=str, help='domain')
    parser.add_argument('-v', '--version', action='version', version=version)
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    domain = ArgParse().domain
    print(json.dumps(DomainTools().getDomainProfile(domain)))
    print(json.dumps(DomainTools().getWhois(domain)))
