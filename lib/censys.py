#!/usr/bin/env python

import argparse
import requests
import configparser

try:
    import simplejson as json
except ImportError:
    import json

class Censys():
    def __init__(self):
        conffile = 'conf/censys.conf'
        conf = configparser.SafeConfigParser()
        conf.read(conffile)
        self.__baseURL = conf.get('censys', 'baseURL')
        self.__apiID = conf.get('censys', 'api_id')
        self.__secret = conf.get('censys', 'secret')

    def getReport(self, q):
        auth = (
            self.__apiID,
            self.__secret,
        )
        url = self.__baseURL + 'view/ipv4/' + q
        try:
            res = requests.get(url, auth=auth)
        except Exception as e:
            return e
        res_dict = json.loads(res.text)
        return res_dict

def ArgParse():
    parser = argparse.ArgumentParser(description=
    '''This script get report from Censys.
    ''',
    formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('ipAddr', action='store', type=str, help='ipAddr')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    print(json.dumps(Censys().getReport(ArgParse().ipAddr)))
