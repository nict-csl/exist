#!/usr/bin/env python

import argparse
import requests
import configparser

try:
    import simplejson as json
except ImportError:
    import json

class AbuseIPDB():
    def __init__(self):
        conffile = 'conf/exist.conf'
        conf = configparser.SafeConfigParser()
        conf.read(conffile)
        self.__baseURL = conf.get('abuse', 'baseURL')
        self.__key = conf.get('abuse', 'apikey')

    def getReport(self, q):
        headers = {
            'Accept': 'application/json',
            'Key': self.__key,
        }
        params = {
            'ipAddress': q,
            'maxAgeInDays': 90,
            'verbose': '',
        }
        try:
            res = requests.get(self.__baseURL, headers=headers, params=params)
        except Exception as e:
            return e
        res_dict = json.loads(res.text)
        return res_dict

def ArgParse():
    parser = argparse.ArgumentParser(description=
    '''This script get report from AbuseIPDB.
    ''',
    formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('ipAddr', action='store', type=str, help='ipAddr')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    print(json.dumps(AbuseIPDB().getReport(ArgParse().ipAddr)))
