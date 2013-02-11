from urllib2 import urlopen
from random import choice
from time import time


class rewiredBotPlugin():
    def __init__(self, parent, *args):
        self.parent = parent
        self.defines = "!roundhouseme"
        self.privs = {'!roundhouseme': 1}
        self.data = []
        self.lastupdate = 0
        self.update()

    def run(self, *args):
        if (self.lastupdate + 86400) < time():  # refresh once per day
            self.update()
        if not len(self.data):
            return 0
        output = choice(self.data)
        return output.decode('string_escape')

    def update(self, *args):
        self.parent.logger.info("Updating !roundhouse dict.")
        rpc = urlopen('http://www.chucknorrisfactoids.com/ultrandom.js')
        data = rpc.readlines()
        rpc.close()
        self.data = []
        for aline in data:
            line = 0
            if (aline.count("quoteArray")) and (aline.count('\""')):
                chuck = aline[aline.find('="\"') + 1:aline.find('\""') - 2]
                chuck = aline[aline.find('="') + 3:len(chuck)] + '"'
                self.data.append(chuck)
        self.lastupdate = time()
        return 1
