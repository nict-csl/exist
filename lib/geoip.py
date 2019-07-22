#!/usr/bin/env python

import socket
import sys
import geoip2.database
import argparse
import configparser

version = '%(prog)s 20180910'

class GeoIP():
    def __init__(self):
        conffile = 'conf/geoip.conf'
        conf = configparser.SafeConfigParser()
        conf.read(conffile)
        self.reader = geoip2.database.Reader(conf.get('geoip', 'database'))

    def lookup(self, ip):
        if ip.find(".") != -1:
            try:
                ip = socket.gethostbyname(ip)
            except Exception as e:
                pass
        try:
            record = self.reader.city(ip)
        except Exception as e:
            pass
        try:
            record
        except NameError:
            return None
        return record.country

def ArgParse():
    parser = argparse.ArgumentParser(description=
    '''This script lookup country from IP address by GeoIP.
    ''',
    formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('ipaddress', action='store', type=str, help='IP Address')
    parser.add_argument('-v', '--version', action='version', version=version)
    args = parser.parse_args()
    return args

if __name__== "__main__":
    ipaddress = ArgParse().ipaddress
    geoip = GeoIP()
    print(geoip.lookup(ipaddress))

