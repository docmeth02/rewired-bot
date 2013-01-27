class rewiredBotPlugin():
    def __init__(self, parent, *args):
        self.parent = parent
        self.config = self.parent.config
        self.defines = "!chatreplay"
        self.privs = {'!chatreplay': 50}

    def run(self, *args):
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
