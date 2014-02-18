# -*- coding: UTF-8 -*-
import urllib2
from urllib import urlencode
from json import loads
from re import findall


class rewiredBotPlugin():
    def __init__(self, parent, *args):
        self.parent = parent
        self.defines = ["!img", '!imgadd', '!imgdel', '!imglist']
        self.privs = {'!img': 25, '!imgadd': 25, '!imgdel': 25, '!imglist': 1}

        self.parent.librewired.subscribe(300, self.monitorChat)
        self.parent.librewired.subscribe(301, self.monitorChat)

    def run(self, params, *args):
        command = self.parent.parse_command(args[0][2])
        chat = int(args[0][0])
        if command.lower() == 'img':
            try:
                if isinstance(params, list):
                    text = " ".join(params)
                else:
                    text = str(params)
            except:
                text = 0
            if len(findall(r'([\w]{12,14})', text)):
                image = getImage(gid=text)
                if not image:
                    # retry search using fulltext
                    image = getImage(text)
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
                self.parent.librewired.sendChatImage(chat, '', {'type': 'url', 'data': decode(image['url'])})
                if len(description):
                    self.parent.librewired.sendChat(chat, decode(description))
            else:
                return "No images for %s" % decode(text)
            return 0
        elif command.lower() == 'imgadd':
            result, url = (0, 0)
            if not len(params):
                return "!imgadd giphyid imagename"
            result = findall(r'([\w]{12,14}) ([\w ]+)', str(params))
            if not len(result):
                url = findall(r'(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+(?:.jpg|.jpeg|.gif|.png)) ([\w ]+)', str(params))
            if len(result) == 1:
                imgid, name = result[0]
            elif len(url):
                imgid, name = url[0]

            if imgid and name:
                if self.parent.storage.get('plugin.img', name.lower()):
                        return "::%s already exists." % name.lower()
                if self.parent.storage.store('plugin.img', {name.lower(): imgid}):
                        return "added ::%s" % name.lower()
                else:
                        return "::%s not added" % name

            return "!imgadd giphyid|url imagename"

        elif command.lower() == 'imgdel':
            if not len(params):
                return "!imgdel imagename"
            if not self.parent.storage.get('plugin.img', params.lower()):
                return "::%s no such image" % params.lower()
            if self.parent.storage.remove('plugin.img', params.lower()):
                return "removed ::%s" % params.lower()
        elif command.lower() == 'imglist':
            images = self.parent.storage.get('plugin.img', None)
            if len(images):
                msg = '::' + ', ::'.join(images.keys())
                self.parent.librewired.sendPrivateMsg(int(args[0][1]), '!img known images:\n%s' % msg)
        return 0

    def monitorChat(self, chat):
        msg = chat.msg
        if int(msg[1]) == (self.parent.librewired.id):
            return 0
        token = findall(r'\:\:\w+', msg[2])
        if len(token):
            name = token[0][2:].lower()
            if self.parent.storage.exists('plugin.img', name):
                gid = self.parent.storage.get('plugin.img', name)
                if len(findall(r'(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+(?:.jpg|.jpeg|.gif|.png))', gid)):
                    image = {}
                    image['url'] = gid
                else:
                    image = getImage(gid=gid)
                if isinstance(image, dict):
                    if not 'url' in image.keys():
                        return 0
                self.parent.librewired.sendChatImage(int(msg[0]), '', {'type': 'url', 'data': decode(image['url'])})
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
        if not len(image):
            return 0
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
