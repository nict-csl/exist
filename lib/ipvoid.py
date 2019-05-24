#!/usr/bin/env python

import argparse
import requests

try:
    import simplejson as json
except ImportError:
    import json

version = '%(prog)s 20190524'

class IPVoid():
    def __init__(self):
        self.__baseURL = "https://www.ipvoid.com/ip-blacklist-check/"

    def sendQuery(self, endpoint, q):
        payload = {
            'ip': q,
        }
        url = self.__baseURL + endpoint
        try:
            res = requests.post(url, data=payload)
        except Exception as e:
            return e
        return res.text

    def getScoreFromIP(self, q):
        endpoint = ""
        score = 0
        result = self.sendQuery(endpoint, q)
        if 'BLACKLISTED' in result:
            score = result.split('BLACKLISTED ')[1].split('<')[0]
        elif 'POSSIBLY' in result:
            score = result.split('POSSIBLY SAFE ')[1].split('<')[0]
        return score

    def getResultFromIP(self, q):
        endpoint = ""
        result = self.sendQuery(endpoint, q)
        reports = {}
        score = 0
        if 'BLACKLISTED' in result:
            score = result.split('BLACKLISTED ')[1].split('<')[0]
            hits = result.split('BLACKLISTED ')[1].split('/')[0]
            lists = result.split('BLACKLISTED ')[1].split('/')[1].split('<')[0]
        elif 'POSSIBLY' in result:
            score = result.split('POSSIBLY SAFE ')[1].split('<')[0]
            hits = result.split('POSSIBLY SAFE ')[1].split('/')[0]
            lists = result.split('POSSIBLY SAFE ')[1].split('/')[1].split('<')[0]
        reports['score'] = score
        reports['hits'] = int(hits)
        reports['lists'] = int(lists)
        reports['results'] = []
        lists = result.split('IP Blacklist Report')[1].split('<tbody>')[1].split('</tbody>')[0].split('<tr><td>')
        for l in lists:
            if 'class' not in l:
                continue
            results = {}
            results['engine'] = l.split('</i> ')[1].split('</td>')[0]
            if 'text-danger' in l:
                results['listed'] = True
            else:
                results['listed'] = False
            results['referrer'] = l.split('href="')[1].split('"')[0]
            reports['results'].append(results)
        return reports

def ArgParse():
    parser = argparse.ArgumentParser(description=
    '''This script check blacklist from IPVoid.
    ''',
    formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('resource', action='store', type=str, help='resource')
    parser.add_argument('-v', '--version', action='version', version=version)
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    print(json.dumps(IPVoid().getResultFromIP(ArgParse().resource)))

