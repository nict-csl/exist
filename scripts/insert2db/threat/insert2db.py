#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import json
from datetime import datetime, timezone
import requests
import configparser

## Django Setup
import django
import pymysql
pymysql.install_as_MySQLdb()
conffile = os.path.join(os.path.dirname(__file__), "conf/insert2db.conf")
conf = configparser.SafeConfigParser()
conf.read(conffile)
sys.path.append(conf.get('exist', 'syspath'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'intelligence.settings')
django.setup()
from apps.threat.models import Event, Attribute, Org, Tag, Object, ObjectReference
import django.utils.timezone as tzone
from django.db import IntegrityError

## Logger Setup
from logging.handlers import TimedRotatingFileHandler
from logging import getLogger, DEBUG, Formatter
logfilename = os.path.join(os.path.dirname(__file__), 'logs/insert2db.log')
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

def fetchMispJson():
    MISP_URL = conf.get('misp', 'MISP_URL')
    API_KEY = conf.get('misp', 'API_KEY')
    
    headers = {
        'Authorization': API_KEY,
        'Accept': 'application/json',
        'Content-type': 'application/json'
    }
    
    payloads = {
        "request": {
#            "from":              "2008-01-01",
            "last":               "24h",
        }
    }
    
    try:
        res = requests.post(MISP_URL + "events/restSearch/json", json.dumps(payloads), headers=headers)
    except Exception as e:
        logger.error(e)

    if res.status_code == 200:
        return json.loads(res.text)
    else:
        logger.error("Error: %d" % res.status_code)
        return

def importJsonFile(filename):
    return json.load(open(filename, 'r'))

def saveQuery(q, forceinsert=False):
    try:
        q.save(force_insert=forceinsert)
        return q
    except IntegrityError as e:
        logger.warn("IntegrityError: ID: %s" % q)
        return 0
    except Exception as e:
        logger.error(e)
        return 0

def printQuery(q):
    print(q)
    return

def insertOrg(org):
    logger.info("Org ID: %s insert" % org['id'])
    query = Org(
        id = int(org['id']),
        name = org['name'],
        uuid = org['uuid'],
    )
    saveQuery(query)

def insertTag(tag):
    logger.info("Tag ID: %s insert" % tag['id'])
    query = Tag(
        id = int(tag['id']),
        name = tag.get('name'),
        colour = tag.get('colour', '#ffffff'),
        exportable = tag.get('exportable', True),
        hide_tag = tag.get('hide_tag', False),
    )
    return saveQuery(query)

def getOrCreateTag(tag):
    logger.info("Tag ID: %s get or create" % tag['id'])
    try:
        tag_obj, created = Tag.objects.get_or_create(
            id = int(tag['id']),
            name = tag.get('name'),
            colour = tag.get('colour', '#ffffff'),
            exportable = tag.get('exportable', True),
            hide_tag = tag.get('hide_tag', False),
        )
    except Exception as e:
        logger.error(e)
        return
    return tag_obj, created

def getOrCreateEvent(event):
    logger.info("Event ID: %s get or create" % event['id'])
    try:
        event_obj = Event.objects.get(id = event['id'])
    except Event.DoesNotExist:
        event_obj = Event(
            id = event['id'],
            orgc = Org(id=int(event['orgc_id'])),
            org = Org(id=int(event['org_id'])),
            date = datetime.strptime(event['date'], '%Y-%m-%d').date(),
            threat_level_id = int(event['threat_level_id']),
            info = event['info'],
            published = event['published'],
            uuid = event['uuid'],
            analysis = int(event['analysis']),
            timestamp = datetime.utcfromtimestamp(float(event['timestamp'])).replace(tzinfo=timezone.utc),
            distribution = int(event['distribution']),
            attribute_count = int(event.get('attribute_count', 0)),
            proposal_email_lock = event.get('proposal_email_lock', False),
            locked = event.get('locked', False),
            publish_timestamp = datetime.utcfromtimestamp(float(event.get('publish_timestamp', 0))).replace(tzinfo=timezone.utc),
            sharing_group_id = int(event.get('sharing_group_id', '0')),
            disable_correlation = event.get('disable_correlation', False),
            event_creator_email = event.get('event_creator_email'),
        )
        event_obj.save()
    except Exception as e:
        logger.error(e)
    return event_obj

def insertAttribute(attr):
    logger.info("Attribute ID: %s insert" % attr['id'])

    query = Attribute(
        id = int(attr['id']),
        type = attr['type'],
        category = attr['category'],
        to_ids = attr['to_ids'],
        uuid = attr['uuid'],
        event = Event(id=int(attr['event_id'])),
        distribution = int(attr['distribution']),
        timestamp = datetime.utcfromtimestamp(float(attr['timestamp'])).replace(tzinfo=timezone.utc),
        comment = attr.get('comment'),
        sharing_group_id = int(attr['sharing_group_id']),
        deleted = attr.get('deleted', False),
        disable_correlation = attr.get('disable_correlation', False),
        object_relation = attr.get('object_relation'),
        value = attr['value'],
    )
    if attr['object_id'] != '0':
        query.object_id = Object(id=int(attr['object_id']))

    if len(attr.get('Tag', '')) > 0:
        for tag in attr['Tag']:
            #tag_obj, tag_created = getOrCreateTag(tag)
            try:
                tag_obj = insertTag(tag)
                query.tags.add(tag_obj)
            except Exception as e:
                logger.error(e)
    return saveQuery(query)

def insertObjectReference(objref):
    logger.info("ObjectReference ID: %s insert" % objref['id'])
    query = ObjectReference(
        id = int(objref['id']),
        uuid = objref['uuid'],
        timestamp = datetime.utcfromtimestamp(float(objref['timestamp'])).replace(tzinfo=timezone.utc),
        object_id = Object(id=int(objref['object_id'])),
        event = Event(id=int(objref['event_id'])),
        referenced_id = int(objref.get('referenced_id', 0)),
        referenced_type = int(objref.get('referenced_type', 0)),
        relationship_type = objref.get('relationship_type'),
        comment = objref.get('comment'),
        deleted = objref.get('deleted', False),
        object_uuid = objref.get('object_uuid'),
        referenced_uuid = objref.get('referenced_uuid'),
    )
    return saveQuery(query)

def insertObject(obj):
    logger.info("Object ID: %s insert" % obj['id'])
    query = Object(
        id = int(obj['id']),
        name = obj['name'],
        meta_category = obj['meta-category'],
        description = obj['description'],
        template_uuid = obj['template_uuid'],
        template_version = int(obj['template_version']),
        event = Event(id=int(obj['event_id'])),
        uuid = obj['uuid'],
        timestamp = datetime.utcfromtimestamp(float(obj['timestamp'])).replace(tzinfo=timezone.utc),
        distribution = int(obj['distribution']),
        sharing_group_id = int(obj['sharing_group_id']),
        comment = obj.get('comment'),
        deleted = obj.get('deleted', False),
    )
    saveQuery(query)

    if len(obj['ObjectReference']) > 0:
        for objref in obj['ObjectReference']:
            try:
                objref_obj = insertObjectReference(objref)
                query.objectreferences.add(objref_obj)
            except Exception as e:
                logger.error(e)

    if len(obj['Attribute']) > 0:
        for attr in obj['Attribute']:
            try:
                attr_obj = insertAttribute(attr)
                query.attributes.add(attr_obj)
            except Exception as e:
                logger.error(e)

def insertEvent(event, tag_list, revent_list):
    logger.info("Event ID: %s insert" % event['id'])
    query = Event(
        id = int(event['id']),
        orgc = Org(id=int(event['orgc_id'])),
        org = Org(id=int(event['org_id'])),
        date = datetime.strptime(event['date'], '%Y-%m-%d').date(),
        threat_level_id = int(event['threat_level_id']),
        info = event['info'],
        published = event['published'],
        uuid = event['uuid'],
        attribute_count = int(event['attribute_count']),
        analysis = int(event['analysis']),
        timestamp = datetime.utcfromtimestamp(float(event['timestamp'])).replace(tzinfo=timezone.utc),
        distribution = int(event['distribution']),
        proposal_email_lock = event.get('proposal_email_lock', False),
        locked = event.get('locked', False),
        publish_timestamp = datetime.utcfromtimestamp(float(event.get('publish_timestamp', 0))).replace(tzinfo=timezone.utc),
        sharing_group_id = int(event.get('sharing_group_id', '0')),
        disable_correlation = event.get('disable_correlation', False),
        event_creator_email = event.get('event_creator_email'),
    )
    saveQuery(query)
    for tag in tag_list:
        try:
            #tag_obj, tag_created = getOrCreateTag(tag)
            tag_obj = insertTag(tag)
            query.tags.add(tag_obj)
        except Exception as e:
            logger.error(e)
    for revent in revent_list:
        try:
            revent_obj = getOrCreateEvent(revent['Event'])
            query.relatedevents.add(revent_obj)
        except Exception as e:
            logger.error(e)

def parseJson(json_dict):
    logger.info("parseJson")
    for content in json_dict['response']:
        event = content['Event']

        tag_list = []
        if len(event.get('Tag', '')) > 0:
            for tag in event['Tag']:
                tag_list.append(tag)

        revent_list = []
        if len(event.get('RelatedEvent', '')) > 0:
            for revent in event['RelatedEvent']:
                revent_list.append(revent)

        insertOrg(event['Org'])
        insertOrg(event['Orgc'])

        insertEvent(event, tag_list, revent_list)

        attribute_list = []
        if len(event.get('Attribute', '')) > 0:
            for attr in event['Attribute']:
                insertAttribute(attr)

        object_list = []
        if len(event.get('Object', '')) > 0:
            for obj in event['Object']:
                insertObject(obj)

if __name__ == '__main__':
    logger.info("start")
    #json_dict = importJsonFile(sys.argv[1])
    json_dict = fetchMispJson()
    parseJson(json_dict)
    logger.info("done")

