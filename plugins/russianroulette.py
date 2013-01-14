from random import choice


class rewiredBotPlugin():
    def __init__(self, parent, *args):
        self.parent = parent
        self.defines = "!russianroulette"

    def run(self, *args):
        print args
        players = []
        for key, user in self.parent.librewired.userlist.items():
            if int(key) != int(self.parent.librewired.id):
                players.append(key)
        victim = choice(players)
        msg = "kicks " + str(self.parent.librewired.userlist[victim].nick)
        try:
            chatid = int(args[1][0])
        except:
            return 0
        self.parent.librewired.sendChat(chatid, msg, 1)
        return 0
