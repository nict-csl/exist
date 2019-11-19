#!/usr/bin/env python

import argparse
import requests
import configparser

try:
    import simplejson as json
except ImportError:
    import json

class Shodan():
    def __init__(self):
        conffile = 'conf/exist.conf'
        conf = configparser.SafeConfigParser()
        conf.read(conffile)
        self.__baseURL = conf.get('shodan', 'baseURL')
        self.__key = conf.get('shodan', 'apikey')

    def getReport(self, q):
        params = {
            'key': self.__key,
        }
        url = self.__baseURL + q
        try:
            res = requests.get(url, params=params)
        except Exception as e:
            return e
        res_dict = json.loads(res.text)
        return res_dict

def ArgParse():
    parser = argparse.ArgumentParser(description=
    '''This script get report from Shodan.
    ''',
    formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('ipAddr', action='store', type=str, help='ipAddr')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    print(json.dumps(Shodan().getReport(ArgParse().ipAddr)))
