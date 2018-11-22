#!/usr/bin/env python

import os
import argparse
import configparser
import requests

try:
    import simplejson as json
except ImportError:
    import json

version = '%(prog)s 20180910'

class Umbrella():
    def __init__(self):
        conffile = 'conf/umbrella.conf'
        conf = configparser.SafeConfigParser()
        conf.read(conffile)
        token = conf.get('investigate', 'token')
        self.__headers = {
            'Authorization': 'Bearer ' + token
        }
        self.__baseURL = conf.get('investigate', 'baseURL')

    def get_dnsdb(self, domain):
        url = self.__baseURL + "dnsdb/name/a/" + domain
        r = requests.get(url, headers=self.__headers)
        a = json.loads(r.text)
        return a

    def get_cname(self, domain):
        url = self.__baseURL + "dnsdb/name/cname/" + domain
        r = requests.get(url, headers=self.__headers)
        a = json.loads(r.text)
        return a

    def get_score(self, domain):
        score = 0
        url = self.__baseURL + "domains/risk-score/" + domain
        r = requests.get(url, headers=self.__headers)
        score = json.loads(r.text)
        return score

    def get_samples(self, domain):
        url = self.__baseURL + "samples/" + domain
        try:
            r = requests.get(url, headers=self.__headers)
        except Exception as e:
            return e
        samples = json.loads(r.text)
        return samples

    def get_sample(self, filehash):
        url = self.__baseURL + "sample/" + filehash
        try:
            r = requests.get(url, headers=self.__headers)
        except Exception as e:
            return e
        sample = json.loads(r.text)
        return sample

def ArgParse():
    parser = argparse.ArgumentParser(description=
    '''This script investigate from Umbrella.
    ConfigureFile: ./umbrella.conf
    ''',
    formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('type', action='store', type=str, help='domain / hash')
    parser.add_argument('resource', action='store', type=str, help='resource')
    parser.add_argument('-v', '--version', action='version', version=version)
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    if ArgParse().type == 'domain':
        print(json.dumps(Umbrella().get_score(ArgParse().resource)))
        #print(json.dumps(Umbrella().get_dnsdb(ArgParse().resource)))
        #print(json.dumps(Umbrella().get_cname(ArgParse().resource)))
        #print(json.dumps(Umbrella().get_samples(ArgParse().resource)))
    elif ArgParse().type == 'hash':
        print(json.dumps(Umbrella().get_sample(ArgParse().resource)))

