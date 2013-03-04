from includes.botfunctions import regmatch, regexclude

class rewiredBotPlugin():
    def __init__(self, parent, *args):
        self.parent = parent
        self.config = self.parent.config
        self.defines = "!replay"
        self.privs = {'!replay': 50}
        self.default = 5

    def run(self, *args):
        lines = 0
        user = None
        nick = None
        if  not args[0]:
            lines = self.default
        else:
            params = args[0].split(" ", 1)
            try:
                lines = int(params[0])
            except:
                user = params[0]
                nick = regmatch(user, self.config['paramDelimiter'])
                if nick:
                    user = None
                try:
                    lines = int(params[1])
                except:
                    lines = self.default
        if user or nick:
            data = self.getFilteredChat(lines, user, nick)
        else:
            data = self.getChatLines(lines)
        if data:
            for aevent in data:
                unpacked = 0
                try:
                    unpacked = self.parent.eventlog.unpackEvent(aevent)
                except:
                    print "UNPACK FAILED"
                try:
                    chatid = int(args[1][0])
                except:
                    break
                if unpacked:
                    self.parent.librewired.sendChat(chatid, unpacked)
            return 0
        return "Sorry, i got nothing"

        return params[0]
        display = 10
        offset = 0
        print "len: %s" % len(self.parent.eventlog.buffer)
        if not self.config['eventLog']:
            return 0
        if len(self.parent.eventlog.buffer) > display:
            offset = len(self.parent.eventlog.buffer) - display
        for i in range(offset, len(self.parent.eventlog.buffer), 1):
            unpacked = 0
            try:
                unpacked = self.parent.eventlog.unpackEvent(self.parent.eventlog.buffer[i])
            except:
                print "FAIL"
            try:
                chatid = int(args[1][0])
            except:
                break
            if unpacked:
                self.parent.librewired.sendChat(chatid, unpacked)
        return 0

    def  getChatLines(self, lines):
        if len(self.parent.eventlog.buffer) < lines:
            # retrieve from db
            data = []
            data = self.parent.db.getEvents(lines)
            if self.parent.eventlog.buffer:
                data = self.parent.eventlog.buffer + data
            if data:
                del data[lines:]
                data.reverse()
                return data
        return 0

    def getFilteredChat(self, lines, user=None, nick=None):
        if user:
            myFilter = ['user', user]
        if nick:
            myFilter = ['nick', nick]

        data = self.filterEvents(lines, self.parent.eventlog.buffer, myFilter)
        return data

    def filterEvents(self, lines, events, myFilter):
        filtered = []
        # first filter buffer objects
        for aevent in self.parent.eventlog.buffer:
            if aevent[myFilter[0]] == myFilter[1]:
                filtered.append(aevent)
        if len(filtered) < events:
            data = self.parent.db.getEvents(lines - len(filtered), myFilter)
            if data:
                data.reverse()
                filtered = data + filtered
        return filtered