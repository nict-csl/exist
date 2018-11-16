#!/usr/bin/env python

import os
import configparser
import requests

version = '%(prog)s 20171117'

class SlackWrapper:

    def __init__(self):
        conffile = os.path.dirname(__file__) + "/slack.conf"
        conf = configparser.SafeConfigParser()
        conf.read(conffile)
        self.PROXIES = {
        #    "http": "http://example:port/",
        #    "https": "https://example:port/",
        }
        self.__token = conf.get('slack', 'token')
        self.__username = conf.get('slack', 'user')
        self.__postMessageURL = conf.get('slack', 'postMessageURL')
        self.__createChannelURL = conf.get('slack', 'createChannelURL')
        if conf.has_option('slack', 'icon'):
            self.__icon_url = conf.get('slack', 'icon')
        else:
            self.__icon_url = ''

    def post(self, channel, posttext):
        params = {
            'token': self.__token,
            'channel': channel,
            'text': posttext,
            'icon_url': self.__icon_url,
            'username': self.__username,
            'unfurl_links': 'false',
        }

        r = requests.post(self.__postMessageURL, params=params, proxies=self.PROXIES)
        return r

    def createChannel(self, channel):
        params = {
            'token': self.__token,
            'name': channel,
            'validate': 'false',
        }

        r = requests.post(self.__createChannelURL, params=params, proxies=self.PROXIES)
        return r

