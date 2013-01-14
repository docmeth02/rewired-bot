class rewiredBotPlugin():
    def __init__(self, parent, *args):
        self.parent = parent
        self.defines = "!debug"

    def run(self, parameters, *args):
        try:
            userid = int(parameters)
        except:
            return 0

        self.parent.librewired.sendPrivateMsg(userid, "Oink!")
        return 0

        chatid = self.parent.librewired.startPrivateChat()
        if not chatid:
            print "Error"
            return 0
        print "Created Private Chat %s" % chatid
        self.parent.librewired.invitePrivateChat(chatid, userid)
        return 0
