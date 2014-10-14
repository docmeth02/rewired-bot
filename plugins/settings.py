from includes.botfunctions import saveConfig
from os.path import exists


class rewiredBotPlugin():
    """re:wired bot settings plugin"""
    def __init__(self, parent, *args):
        self.parent = parent
        self.defines = "!set"
        self.privs = {'!set': 99}

    def run(self, params, *args):
        """!set: Usage: !set nick|status|autoreconnect|icon|save value
        Tune certain aspects of bots configuration:
        !set nick anotherbot - Change nickname to anotherbot
        !set status wooooo - Change bots status to wooooo
        !set autoreconnect off|on - Turn on or off bots reconnection setting
        !set icon /my/icon/path - Load new icon from path
        !set save - Save new settings permanently and overwrite config file.
        ___"""
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
            if self.parent.updateConfig():
                self.parent.librewired.sendChat(chatid, "updated its configuration file.", 1)
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
            if exists(param):
                if self.parent.librewired.loadIcon(param):
                    self.parent.config['icon'] = param
                    return 0
            return "Sorry, i can't find the file " + str(param)
