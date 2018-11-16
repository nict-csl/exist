#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import django
import configparser
import subprocess
import pymysql
pymysql.install_as_MySQLdb()

version = '%(prog)s 20180223'
conffile = os.path.dirname(__file__) + "/threat.conf"
conf = configparser.SafeConfigParser()
conf.read(conffile)

## Django Setup
sys.path.append(conf.get('insertdb', 'syspath'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'intelligence.settings')
django.setup()
from threat_hunter.models import Hunt

## Logger Setup
from logging import getLogger, StreamHandler, FileHandler, DEBUG, Formatter
logfilename = conf.get('watchhunter', 'logdir') + "/watchhunter.log"
logger = getLogger(__name__)
#handler_stream = StreamHandler()
#handler_stream.setFormatter(logging.Formatter("%(asctime)s %(levelname)8s %(message)s"))
handler_file = FileHandler(filename=logfilename)
handler_file.setFormatter(Formatter("%(asctime)s %(levelname)8s %(message)s"))
logger.setLevel(DEBUG)
#logger.addHandler(handler_stream)
logger.addHandler(handler_file)
logger.propagate = False

def runHunter(id):
    hunter_path = conf.get('insertdb', 'syspath') + "/threat_hunter/th_hunter.py"
    cmd = "{hunter} {id}".format(
        hunter = hunter_path,
        id = id,
    )
    subprocess.Popen(cmd, shell=True)
    logger.info("run %s: ", id)

if __name__ == "__main__":
    logger.info("start")
    entry_list = list(Hunt.objects.all().values('id', 'enable'))
    for entry in entry_list:
        if entry['enable']:
            runHunter(entry['id'])
    logger.info("done")
