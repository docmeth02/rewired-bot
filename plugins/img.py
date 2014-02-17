# -*- coding: UTF-8 -*-
import urllib2
from urllib import urlencode
from json import loads


class rewiredBotPlugin():
    def __init__(self, parent, *args):
        self.parent = parent
        self.defines = "!img"
        self.privs = {'!img': 25}

    def run(self, *args):
        chat = int(args[1][0])
        try:
            text = str(args[0])
        except:
            text = 0
        image = getImage(text)
        if isinstance(image, dict):
            if not 'url' in image.keys():
                return 0
            if 'tags' in image.keys():
                if len(image['tags']):
                    tags = 'Tags: %s' % image['tags']
                else:
                    tags = ''
            self.parent.librewired.sendChat(chat, chr(128) + '[img]' + decode(image['url']) + '[/img]')
            if len(tags):
                self.parent.librewired.sendChat(chat, decode(tags))
        else:
            return "No images for %s" % decode(text)
        return 0


def getImage(search=0):
    params = {'api_key': 'dc6zaTOxFJmzC'}
    if search:
        params['tag'] = search
    url = 'http://api.giphy.com/v1/gifs/random?%s' % urlencode(params)
    try:
        res = urllib2.urlopen(url)
    except:
        return 0
    if res:
        try:
            data = res.read()
            response = loads(data)
        except:
            return 0
    if 'data' in response.keys():
        image = response['data']

    else:
        return 0
    try:
        tags = 0
        if 'tags' in image.keys():
            tags = ', '.join(image['tags'])
    except:
        return 0
    return {'url': image['image_url'], 'tags': tags}


def decode(s):
    try:
        s = unicode(s, errors='ignore')
    except:
        pass
    s = s.encode("UTF-8")
    codes = [
        ["'", '&#39;'],
        ['&', '&amp;'],
        ['<', '&lt;'],
        ['>', '&gt;'],
        ['-', '&mdash;'],
        ['"', '&quot;']]
    for code in codes:
        s = s.replace(code[1], code[0])

    return s
