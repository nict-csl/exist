#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import django
import requests
import configparser
import pymysql
pymysql.install_as_MySQLdb()

conffile = os.path.join(os.path.dirname(__file__), "conf/insert2db.conf"
conf = configparser.SafeConfigParser()
conf.read(conffile)

sys.path.append(conf.get('exist', 'syspath'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'intelligence.settings')
django.setup()
from vuln.models import Product
import django.utils.timezone as tzone
from django.db import IntegrityError

def get_num_google(keyword):
    url = "https://google.com/search?q={}".format(keyword)
    res = requests.get(url)
    html = res.text
    num_str = html.split(">&#32004; ")[1].split(" &#20214;")[0]
    num_str = "".join( [ str for str in num_str.split(",") ])
    return num_str

if __name__ == "__main__":
    for product in Product.objects.filter(googlehit__isnull=True):
        print(product.id, product.name, product.googlehit)
        product.googlehit = get_num_google(product.name)
        print("{}, {}, {}".format(product.id, product.name, product.googlehit))
        product.save()

