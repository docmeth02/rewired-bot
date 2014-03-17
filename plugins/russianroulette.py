from random import choice


class rewiredBotPlugin():
    "Play Russian Roulette"
    def __init__(self, parent, *args):
        self.parent = parent
        self.defines = "!russianroulette"
        self.privs = {'!russianroulette': 25}

    def run(self, *args):
        """!russianroulette: Usage: !russianroulette
        Bot randomly pretends to kick people off the server
        _"""
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
