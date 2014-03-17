# -*- coding: UTF-8 -*-
from xml.dom.minidom import parse, parseString
from urllib2 import urlopen
from time import time
from random import choice
from re import findall
import praw


class rewiredBotPlugin():
    """reddit/aww plugin"""
    def __init__(self, parent, *args):
        self.parent = parent
        self.defines = "!aww"
        self.privs = {'!aww': 1}
        self.reddit = reditClient()
        self.reddit.update()

    def run(self, params, *args):
        """!aww: Usage: !aww
        Posts random images from http://www.reddit.com/r/aww into chat.
        ___"""
        chatid = int(args[0][0])
        if not self.reddit.lastupdate or self.reddit.lastupdate <= (time() - 3600):
            self.reddit.update()
        aww = self.reddit.getRandom()
        if aww:
            #self.parent.librewired.sendChat(chatid, chr(128) + '[img]%s[/img]' % aww['image'])
            self.parent.librewired.sendChatImage(chatid, '', {'type': 'url', 'data': aww['image']})
            self.parent.librewired.sendChat(chatid, '/r/aww link: %s' % aww['link'])
        return 0


class reditClient(object):
    def __init__(self):
        self.cache = {}
        self.lastupdate = 0

    def update(self):
        print "Updating r/aww cache"
        try:
            r = praw.Reddit(user_agent='re:wired bot')
            aww = r.get_subreddit('aww')
        except Exception as e:
            print e
            return 0
        for submission in aww.get_hot(limit=100):
            if findall('(\.jpg|\.gif|\.png)', submission.url[-4:]):
                if submission.id in self.cache.keys():
                    continue
                self.cache[submission.id] = {'image': decode(submission.url),
                                             'link': decode(submission.short_link)}
        self.lastupdate = time()
        print "%s items in r/aww cache" % len(self.cache)
        return 1

    def getRandom(self):
        key = 0
        key = choice(self.cache.keys())
        if key:
            return self.cache[key]
        return 0


def decode(string):
    try:
        string = unicode(string, 'replace')
    except Exception as e:
        pass
    try:
        string = string.encode('UTF-8', 'xmlcharrefreplace')
    except Exception as e:
        pass
    return string
