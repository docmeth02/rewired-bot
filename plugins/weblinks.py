# -*- coding: UTF-8 -*-
import re
import urllib2
from urlparse import urlparse
from HTMLParser import HTMLParser


class rewiredBotPlugin():
    """Weblink preview plugin for images, websites and youtube videos"""
    def __init__(self, parent, *args):
        self.parent = parent
        self.config = self.parent.config
        self.defines = "!weblinks"
        self.privs = {'!weblinks': 50}
        self.state = 1
        self.parent.librewired.subscribe(300, self.checkChat)
        self.parent.librewired.subscribe(301, self.checkChat)

    def run(self, msg, *args):
        """!weblinks: Usage: !weblinks on|off|youtube
        Alter the behaviour of link preview:
        !weblinks off - No preview at all.
        !weblinks youtube - Preview only youtube videos.
        !weblinks all - Preview images, web sites and videos.
        ____"""
        if not msg:
            display = {0: 'off', 1: 'on', 2: 'youtube only'}
            return "Current mode: " + display[self.state] + "\nUsage: !weblinks off/on/youtube"
        if 'off' in msg.lower():
            self.state = 0
            return "!weblinks is now off"
        if 'on' in msg.lower():
            self.state = 1
            return "!weblinks is now on"
        if 'youtube' in msg.lower():
            self.state = 2
            return "!weblinks: show youtube videos only"
        return 0

    def checkChat(self, chat):
        msg = chat.msg
        if int(msg[1]) == (self.parent.librewired.id) or not self.state or msg[2][:1] == '!':
            return 0
        hasimdb = 1
        if re.findall(r'(tt[0-9]+)', msg[2]):
            # imdb
            imdbids = re.findall(r'(tt[0-9]+)', str(msg[2]))
            try:
                    from plugins import imdb
            except Exception as e:
                hasimdb = 0
            if not '!IMDB' in msg[2].upper() and hasimdb:
                for aid in imdbids:
                    tvshow = imdb.getTVbyIMDB(aid)
                    if tvshow:
                        imdb.outputTVShow(tvshow, int(msg[0]), self.parent.librewired, link=False)
                        continue
                    else:
                        movie = imdb.lookupMovie(aid)
                    if movie:
                        imdb.outputMovie(movie, int(msg[0]), self.parent.librewired, link=False)
                return 0

        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str(msg[2]))
        if urls:
            debug = ""
            for aurl in urls:
                # is this a image?
                parser = urlparse(aurl)
                if parser.scheme in ['http', 'https']:
                    if parser.path[-4:] in ['jpeg', '.jpg', '.png', '.gif']:
                        self.parent.librewired.sendChatImage(int(msg[0]), '', {'type': 'url', 'data': aurl},
                                                             sendlegacy=0)
                        continue
                # is this a valid html document with a title tag we can use?
                try:
                    response = urllib2.urlopen(aurl)
                except:
                    continue
                if response:
                    data = unicode(response.read(1000000), errors='ignore')  # read 1m at the most
                    data = data.encode("UTF-8")
                    if len(data):
                        host = urlparse(aurl)
                        if host.netloc.lower() in ['youtube.com', 'youtu.be']:
                            title = getSiteTitle(data)
                            if title:
                                title = title[0:title.find("- YouTube") - 1]
                                self.parent.librewired.sendChat(int(msg[0]), "Youtube video: " + html_decode(title))
                            continue
                        if self.state == 2:
                            continue
                        title = getSiteTitle(data)
                        if title:
                            self.parent.librewired.sendChat(int(msg[0]), str(host.hostname) + " page title: "
                                                            + html_decode(title))
        return 0


def html_decode(s):
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
    try:
        parser = HTMLParser()
        result = parser.unescape(s)
    except:
        return s
    return html_decode(result)


def getSiteTitle(html):
    try:
        regex = re.compile('<title>(.*?)</title>', re.IGNORECASE | re.DOTALL)
        title = regex.search(html)
        title = title.group(0)
        lower = title.lower()
        begin = lower.find('<title>')
        end = lower.find('</title>')
        title = title[begin + 7:end].strip()
        title = title.replace("\n", " ")
        return title
    except:
        return 0
