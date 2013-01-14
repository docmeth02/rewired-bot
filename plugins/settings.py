class rewiredBotPlugin():
    def __init__(self, parent, *args):
        self.parent = parent
        self.defines = "!set"

    def run(self, params, *args):
        if not params:
            return 0
        try:
            chatid = int(args[0][0])
        except:
            print "ERR"
            return 0
        params = params.split(" ", 1)
        if not len(params):
            print "No params in !set"
            return 0
        try:
            cmd = str(params[0]).upper()
            param = params[1]
        except IndexError:
            return 0

        if cmd == "NICK":
            self.parent.nick = params[1]
            self.parent.librewired.sendChat(chatid, "changes nickname to %s" % params[1], 1)
            self.parent.librewired.changeNick(params[1])
            return 0

        if cmd == "STATUS":
            self.parent.librewired.sendChat(chatid, "changes status to %s" % params[1], 1)
            self.parent.librewired.changeStatus(params[1])

        if cmd == "GREETING":
            if params[1].upper() == "OFF" or params[1].upper() == "FALSE":
                self.parent.config['greetUsers'] = 0
                return "User greeting is now off."
            if params[1].upper() == "ON" or params[1].upper() == "TRUE":
                self.parent.config['greetUsers'] = 1
                return "User greeting is now on."
        return 0
