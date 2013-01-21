from includes.botfunctions import saveConfig


class rewiredBotPlugin():
    def __init__(self, parent, *args):
        self.parent = parent
        self.defines = "!set"
        self.privs = {'!set': 99}

    def run(self, params, *args):
        if not params:
            return 0
        try:
            chatid = int(args[0][0])
        except:
            return 0

        params = params.split(" ", 1)
        try:
            cmd = str(params[0]).upper().strip()
            param = params[1].strip()
        except IndexError:
            param = 0

        if cmd == "SAVE":
            saveConfig(self.parent.config, 'bot.conf')
            return 0

        if cmd == "NICK":
            if not param:
                return 0
            self.parent.nick = param
            self.parent.librewired.sendChat(chatid, "changes nickname to %s" % param, 1)
            self.parent.config['nick'] = param
            self.parent.librewired.changeNick(param)
            return 0

        if cmd == "STATUS":
            if not param:
                param = ""
            self.parent.librewired.sendChat(chatid, "changes status to %s" % param, 1)
            self.parent.config['status'] = param
            self.parent.librewired.changeStatus(param)
            return 0
