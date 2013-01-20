class rewiredBotPlugin():
    def __init__(self, parent, *args):
        self.parent = parent
        self.defines = "!debug"
        self.privs = {'!debug': 99}

    def run(self, parameters, *args):
        print self.parent.librewired.userlist
        return 0
        privs = self.parent.getPrivs(args[0][1])
        return "Priv Level: " + str(privs)
