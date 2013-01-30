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

        if cmd == "AUTORECONNECT":
            status = {0: "Autoreconnect if off", 1: "Autoreconnect is on"}
            if not param:
                return status[int(self.parent.librewired.autoreconnect)]

            if "ON" in param.upper():
                self.parent.config['autoreconnect'] = True
                self.parent.librewired.autoreconnect = 1

            if "OFF" in param.upper():
                self.parent.config['autoreconnect'] = False
                self.parent.librewired.autoreconnect = 0

            return status[int(self.parent.librewired.autoreconnect)]

        if cmd == "ICON":
            if not param:
                return 0
