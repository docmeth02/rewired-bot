# -*- coding: UTF-8 -*-
import urllib2
from urllib import urlencode
from json import loads
from re import findall


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
        if len(findall(r'([\w]{13})', text)):
            image = getImage(gid=text)
        else:
            image = getImage(text)
        if isinstance(image, dict):
            if not 'url' in image.keys():
                return 0
            description = '#:%s' % image['id']
            if 'tags' in image.keys():
                if len(image['tags']):
                    description += ' Tags: %s' % image['tags']
                else:
                    tags = ''
            self.parent.librewired.sendChat(chat, chr(128) + '[img]' + decode(image['url']) + '[/img]')
            if len(description):
                self.parent.librewired.sendChat(chat, decode(description))
        else:
            return "No images for %s" % decode(text)
        return 0


def getImage(search=0, gid=0):
    params = {'api_key': 'dc6zaTOxFJmzC'}
    if gid:
        url = 'http://api.giphy.com/v1/gifs/%s?%s' % (str(gid), urlencode(params))

    elif search:
        params['tag'] = search
        url = 'http://api.giphy.com/v1/gifs/random?%s' % urlencode(params)
    if not url:
        return 0
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
    if not gid:
        try:
            tags = 0
            if 'tags' in image.keys():
                tags = ', '.join(image['tags'])
        except:
            return 0
        return {'id':  image['id'], 'url': image['image_url'], 'tags': tags}

    elif gid:
        if 'images' in image.keys():
            result = image['images']
        else:
            return 0
        try:
            url = result['original']['url']
        except:
            return 0
        return {'id':  image['id'], 'url': url, 'tags': ''}


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
