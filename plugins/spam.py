from os.path import exists
from os import sep


class rewiredBotPlugin():
    """Ascii art spam plugin"""
    def __init__(self, *args):
        #self.parent = parent
        self.defines = "!spam"
        self.privs = {'!spam': 25}
        self.data = {}
        self.loadDict()

    def run(self, command=0, *args):
        """!spam: Usage: !spam !reload/name
        Display ascii art stored in file spam.dict
        located in bots plugin directory. Changes
        made to the spam file can be reloaded by:
        !spam !reload
        !spam oink will display item oink defined in
        spam.dict
        _"""
        if not len(self.data):
            return 0
        if not command:
            return "No command given"
        if command.upper() == "!RELOAD":
            self.data = {}
            self.loadDict()
            return "done reloading"
        for key, data in self.data.items():
            if command.upper() == key.upper():
                return data
        return 0

    def loadDict(self):
        if not exists('plugins' + sep + 'spam.dict'):
            print "Can't find !spam dict"
            return 0
        try:
            file = open('plugins' + sep + 'spam.dict')
            data = file.read()
            file.close()
        except:
            print "Error while loading !spam dict"
            return 0
        if not len(data):
            print "Empty !spam dict"
            return 0
        splits = data.split('{%')
        for aitem in splits:
            data = 0
            name = 0
            pos = aitem.find('%}')
            if pos != -1:
                name = aitem[:pos]
                data = aitem[pos + 2:]
                data = data.lstrip('\r\n')
                data = data.rstrip('\r\n')
                self.data[name] = data
        return 0
