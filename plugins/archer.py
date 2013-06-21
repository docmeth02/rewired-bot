import urllib2
from  HTMLParser import HTMLParser
import re
from random import choice
from time import time


class rewiredBotPlugin():
    def __init__(self, *args):
        self.defines = "!archer"
        self.quotes = []
        self.lastupdate = 0
        self.update()

    def run(self, *args):
        if (self.lastupdate + 86400) < time():  # refresh once per day
            self.update()
        if not len(self.quotes):
            return 0
        output = choice(self.quotes)
        return output.decode('string_escape')

    def update(self):
        parser = HTMLParser()
        try:
            quotes = urllib2.urlopen("http://www.sterlingsays.it/")
        except urllib2.URLError:
            return 0
        lines = quotes.readlines()

        for aline in lines:
            aline = aline.strip()
            if  aline.count('<p class="round">'):
                aline = aline[17:len(aline) - 4]
                try:
                    aline = parser.unescape(aline)
                    aline = aline.encode("UTF-8")
                    aline = re.sub('<br />', '\n', aline)
                    aline = re.sub('<[^<]+?>', '', aline)
                except:
                    pass
                if aline:
                    self.quotes.append(aline)
        return 0
