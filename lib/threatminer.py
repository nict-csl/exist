#!/usr/bin/env python

import argparse
import requests

try:
    import simplejson as json
except ImportError:
    import json

version = '%(prog)s 20180912'

class ThreatMiner():
    def __init__(self):
        self.__baseURL = "https://api.threatminer.org/v2/"

    def sendQuery(self, endpoint, rt, q):
        params = {
            'rt': rt,
            'q': q,
        }
        url = self.__baseURL + endpoint
        try:
            res = requests.get(url, params=params)
        except Exception as e:
            return e
        res_dict = json.loads(res.text)
        return res_dict

    ### From Domain
    def getURIFromDomain(self, q):
        rt = 3
        endpoint = "domain.php"
        result = self.sendQuery(endpoint, rt, q)
        return result

    def getSamplesFromDomain(self, q):
        rt = 4
        endpoint = "domain.php"
        result = self.sendQuery(endpoint, rt, q)
        return result

    def getSubdomainsFromDomain(self, q):
        rt = 5
        endpoint = "domain.php"
        result = self.sendQuery(endpoint, rt, q)
        return result

    def getReportFromDomain(self, q):
        rt = 6
        endpoint = "domain.php"
        result = self.sendQuery(endpoint, rt, q)
        return result

    ### From IP address
    def getURIFromIP(self, q):
        rt = 3
        endpoint = "host.php"
        result = self.sendQuery(endpoint, rt, q)
        return result

    def getSamplesFromIP(self, q):
        rt = 4
        endpoint = "host.php"
        result = self.sendQuery(endpoint, rt, q)
        return result

    def getReportFromIP(self, q):
        rt = 6
        endpoint = "host.php"
        result = self.sendQuery(endpoint, rt, q)
        return result

    ### From Sample
    def getMetaFromSample(self, q):
        rt = 1
        endpoint = "sample.php"
        result = self.sendQuery(endpoint, rt, q)
        return result

    def getHttpFromSample(self, q):
        rt = 2
        endpoint = "sample.php"
        result = self.sendQuery(endpoint, rt, q)
        return result

    def getHostsFromSample(self, q):
        rt = 3
        endpoint = "sample.php"
        result = self.sendQuery(endpoint, rt, q)
        return result

    def getMutantsFromSample(self, q):
        rt = 4
        endpoint = "sample.php"
        result = self.sendQuery(endpoint, rt, q)
        return result

    def getRegistryFromSample(self, q):
        rt = 5
        endpoint = "sample.php"
        result = self.sendQuery(endpoint, rt, q)
        return result

    def getAVFromSample(self, q):
        rt = 6
        endpoint = "sample.php"
        result = self.sendQuery(endpoint, rt, q)
        return result

    def getReportFromSample(self, q):
        rt = 7
        endpoint = "sample.php"
        result = self.sendQuery(endpoint, rt, q)
        return result

    ### From AV
    def getSamplesFromAV(self, q):
        rt = 1
        endpoint = "av.php"
        result = self.sendQuery(endpoint, rt, q)
        return result

    def getReportFromAV(self, q):
        rt = 2
        endpoint = "av.php"
        result = self.sendQuery(endpoint, rt, q)
        return result

    ### From Report
    def getDomainFromReport(self, q):
        rt = 1
        endpoint = "report.php"
        result = self.sendQuery(endpoint, rt, q)
        return result

    def getHostsFromReport(self, q):
        rt = 2
        endpoint = "report.php"
        result = self.sendQuery(endpoint, rt, q)
        return result

    def getEmailFromReport(self, q):
        rt = 3
        endpoint = "report.php"
        result = self.sendQuery(endpoint, rt, q)
        return result

    def getSamplesFromReport(self, q):
        rt = 4
        endpoint = "report.php"
        result = self.sendQuery(endpoint, rt, q)
        return result

    ### Search APINotes
    def getReportFromKeyword(self, q):
        rt = 1
        endpoint = "reports.php"
        result = self.sendQuery(endpoint, rt, q)
        return result

    def getReportFromYear(self, q):
        rt = 2
        endpoint = "reports.php"
        result = self.sendQuery(endpoint, rt, q)
        return result

def ArgParse():
    parser = argparse.ArgumentParser(description=
    '''This script get report from ThreatMiner.
    ''',
    formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('type', action='store', type=str, help='domain / ip / hash / av / report / keyword / year')
    parser.add_argument('resource', action='store', type=str, help='resource')
    parser.add_argument('-v', '--version', action='version', version=version)
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    if ArgParse().type == 'domain':
        print(json.dumps(ThreatMiner().getURIFromDomain(ArgParse().resource)))
        print(json.dumps(ThreatMiner().getSamplesFromDomain(ArgParse().resource)))
        print(json.dumps(ThreatMiner().getSubdomainsFromDomain(ArgParse().resource)))
        print(json.dumps(ThreatMiner().getReportFromDomain(ArgParse().resource)))
    elif ArgParse().type == 'ip':
        print(json.dumps(ThreatMiner().getURIFromIP(ArgParse().resource)))
        print(json.dumps(ThreatMiner().getSamplesFromIP(ArgParse().resource)))
        print(json.dumps(ThreatMiner().getReportFromIP(ArgParse().resource)))
    elif ArgParse().type == 'hash':
        print(json.dumps(ThreatMiner().getMetaFromSample(ArgParse().resource)))
        print(json.dumps(ThreatMiner().getHttpFromSample(ArgParse().resource)))
        print(json.dumps(ThreatMiner().getHostsFromSample(ArgParse().resource)))
        print(json.dumps(ThreatMiner().getMutantsFromSample(ArgParse().resource)))
        print(json.dumps(ThreatMiner().getRegistryFromSample(ArgParse().resource)))
        print(json.dumps(ThreatMiner().getAVFromSample(ArgParse().resource)))
        print(json.dumps(ThreatMiner().getReportFromSample(ArgParse().resource)))
    elif ArgParse().type == 'av':
        print(json.dumps(ThreatMiner().getSamplesFromAV(ArgParse().resource)))
        print(json.dumps(ThreatMiner().getReportFromAV(ArgParse().resource)))
    elif ArgParse().type == 'report':
        print(json.dumps(ThreatMiner().getDomainFromReport(ArgParse().resource)))
        print(json.dumps(ThreatMiner().getHostsFromReport(ArgParse().resource)))
        print(json.dumps(ThreatMiner().getEmailFromReport(ArgParse().resource)))
        print(json.dumps(ThreatMiner().getSamplesFromReport(ArgParse().resource)))
    elif ArgParse().type == 'keyword':
        print(json.dumps(ThreatMiner().getReportFromKeyword(ArgParse().resource)))
    elif ArgParse().type == 'year':
        print(json.dumps(ThreatMiner().getReportFromYear(ArgParse().resource)))

