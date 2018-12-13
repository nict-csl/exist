#!/usr/bin/env python

import sys
import os
import configparser
import subprocess

## Django Setup
import django
import pymysql
pymysql.install_as_MySQLdb()
conffile = os.path.join(os.path.dirname(__file__), "conf/twitter.conf")
conf = configparser.SafeConfigParser()
conf.read(conffile)
sys.path.append(conf.get('exist', 'syspath'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'intelligence.settings')
django.setup()
from twitter_hunter.models import Hunt

## Logger Setup
from logging.handlers import TimedRotatingFileHandler
from logging import getLogger, DEBUG, Formatter
logfilename = os.path.join(os.path.dirname(__file__), 'logs/watchhunter.log')
logger = getLogger()
handler = TimedRotatingFileHandler(
    filename=logfilename,
    when="D",
    interval=1,
    backupCount=31,
)
handler.setFormatter(Formatter("%(asctime)s %(name)s %(funcName)s [%(levelname)s]: %(message)s"))
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False

def isRunning(hunt_id):
    cmd = "ps aux|grep \"tw_hunter.py " + str(hunt_id) + "$\"|grep -v grep |wc -l"
    result = subprocess.check_output(cmd, shell=True)
    if int(result.decode('utf-8').strip('\n\n')) > 0:
        return True
    return False

def startHunter(entry):
    hunter_path = os.path.join(os.path.dirname(__file__), "tw_hunter.py")
    cmd = "{hunter} {id}".format(
        hunter = hunter_path,
        id = entry['id'],
    )
    subprocess.Popen(cmd, shell=True)
    logger.info("run %s: ", id)

if __name__ == "__main__":
    logger.info("start")
    entry_list = list(Hunt.objects.all().values('id', 'enable'))
    for entry in entry_list:
        if entry['enable'] and not isRunning(entry['id']):
            startHunter(entry)
    logger.info("done")
