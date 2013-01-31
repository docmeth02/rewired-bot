import re
import urllib2
from urlparse import urlparse


class rewiredBotPlugin():
    def __init__(self, parent, *args):
        self.parent = parent
        self.config = self.parent.config
        self.defines = "!weblinks"
        self.privs = {'!weblinks': 50}
        self.state = 1
        self.parent.librewired.subscribe(300, self.checkChat)
        self.parent.librewired.subscribe(301, self.checkChat)

    def run(self, msg, *args):
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
        if int(msg[1]) == (self.parent.librewired.id) or not self.state:
            return 0
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str(msg[2]))
        if urls:
            debug = ""
            for aurl in urls:
                try:
                    response = urllib2.urlopen(aurl)
                except urllib2.URLError:
                    continue
                if response:
                    data = response.read()
                    if len(data):
                        host = urlparse(aurl)
                        if 'youtube.com' in host.netloc.lower() or 'youtu.be' in host.netloc.lower():
                            title = getSiteTitle(data)
                            if title:
                                title = title[0:title.find("- YouTube") - 1]
                                self.parent.librewired.sendChat(int(msg[0]), "Youtube video: " + title)
                            continue
                        if self.state == 2:
                            continue
                        title = getSiteTitle(data)
                        if title:
                            self.parent.librewired.sendChat(int(msg[0]), str(host.netloc) + " page title: " + title)
        return 0


def getSiteTitle(html):
    try:
        regex = re.compile('<title>(.*?)</title>', re.IGNORECASE | re.DOTALL)
        title = regex.search(html)
        title = title.group(0)
        lower = title.lower()
        begin = lower.find('<title>')
        end = lower.find('</title>')
        return title[begin + 7:end].strip()
    except:
        return 0
