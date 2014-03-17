from xml.dom.minidom import parse, parseString
from urllib2 import urlopen
from time import time
from random import choice


class rewiredBotPlugin():
    """Homer J. Simpson Quotes"""
    def __init__(self, parent, *args):
        self.parent = parent
        self.defines = "!doh"
        self.privs = {'!doh': 1}
        self.data = []
        self.lastupdate = 0
        self.update()

    def run(self, *args):
        """!doh: Usage: !doh
        Posts random Homer Simpson quotes to chat.
        ___"""
        if (self.lastupdate + 86400) < time():  # refresh once per day
            self.update()
        if not len(self.data):
            return 0
        output = choice(self.data)
        return "Homer says: " + output

    def update(self, *args):
        self.data = []
        self.parent.logger.info("Updating !doh dict.")
        quotes = parse(urlopen("http://www.happycow.org.uk/inspiration/quotes_simpson.xml"))
        for node in quotes.getElementsByTagName("quote"):
            aquote = node.firstChild.nodeValue
            aquote = aquote.strip('\r\n')
            self.data.append(aquote)
        self.lastupdate = time()
        return 1
