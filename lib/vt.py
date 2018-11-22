#!/usr/bin/env python

import os
import argparse
import configparser
import requests

try:
    import simplejson as json
except ImportError:
    import json

version = '%(prog)s 20180912'

class VT():
    def __init__(self):
        conffile = 'conf/vt.conf'
        conf = configparser.SafeConfigParser()
        conf.read(conffile)
        self.__baseURL = conf.get('vt', 'baseURL')
        self.__params = {
            'apikey': conf.get('vt', 'apikey'),
        }

    def getFileReport(self, filehash, allinfo=1):
        params = self.__params
        params['resource'] = filehash
        params['allinfo'] = allinfo
        url = self.__baseURL + "file/report"
        try:
            res = requests.get(url, params=params)
        except Exception as e:
            return e
        res_dict = json.loads(res.text)
        return res_dict

    def getFileBehavior(self, filehash):
        params = self.__params
        params['hash'] = filehash
        url = self.__baseURL + "file/behaviour"
        try:
            res = requests.get(url, params=params)
        except Exception as e:
            return e
        res_dict = json.loads(res.text)
        return res_dict

    def getDomainReport(self, domain):
        params = self.__params
        params['domain'] = domain
        url = self.__baseURL + "domain/report"
        try:
            res = requests.get(url, params=params)
        except Exception as e:
            return e
        res_dict = json.loads(res.text)
        return res_dict

    def getIPReport(self, ip):
        params = self.__params
        params['ip'] = ip
        url = self.__baseURL + "ip-address/report"
        try:
            res = requests.get(url, params=params)
        except Exception as e:
            return e
        res_dict = json.loads(res.text)
        return res_dict

    def getURLReport(self, url, scan=0, allinfo=1):
        params = self.__params
        params['resource'] = url
        params['scan'] = scan
        params['allinfo'] = allinfo
        url = self.__baseURL + "url/report"
        try:
            res = requests.get(url, params=params)
        except Exception as e:
            return e
        res_dict = json.loads(res.text)
        return res_dict

    def download(self, filehash):
        params = self.__params
        params['hash'] = filehash
        url = self.__baseURL + "file/download"
        try:
            res = requests.get(url, params=params)
        except Exception as e:
            return e
        return res

    def getPcap(self, filehash):
        params = self.__params
        params['hash'] = filehash
        url = self.__baseURL + "file/network-traffic"
        headers = {
            "Accept-Encoding": "gzip, deflate",
        }
        try:
            res = requests.get(url, params=params, headers=headers)
        except Exception as e:
            return e
        return res

def ArgParse():
    parser = argparse.ArgumentParser(description=
    '''This script get report from VirusTotal private api.
    ConfigureFile: ./vt.conf
    ''',
    formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('type', action='store', type=str, help='filehash/filehash-behavior/domain/ip/url/download/download-pcap')
    parser.add_argument('resource', action='store', type=str, help='resource')
    parser.add_argument('-v', '--version', action='version', version=version)
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    if ArgParse().type == 'filehash':
        print(json.dumps(VT().getFileReport(ArgParse().resource)))
        #print(json.dumps(VT().getFileReport(ArgParse().resource, allinfo=0)))
    elif ArgParse().type == 'filehash-behavior':
        print(json.dumps(VT().getFileBehavior(ArgParse().resource)))
    elif ArgParse().type == 'domain':
        print(json.dumps(VT().getDomainReport(ArgParse().resource)))
    elif ArgParse().type == 'ip':
        print(json.dumps(VT().getIPReport(ArgParse().resource)))
    elif ArgParse().type == 'url':
        print(json.dumps(VT().getURLReport(ArgParse().resource)))
        #print(json.dumps(VT().getURLReport(ArgParse().resource, scan=1)))
    elif ArgParse().type == 'download':
        res = VT().download(ArgParse().resource)
        with open(ArgParse().resource, 'wb') as file:
            for chunk in res.iter_content(chunk_size=1024):
                file.write(chunk)
    elif ArgParse().type == 'download-pcap':
        res = VT().getPcap(ArgParse().resource)
        with open(ArgParse().resource, 'wb') as file:
            for chunk in res.iter_content(chunk_size=1024):
                file.write(chunk)
