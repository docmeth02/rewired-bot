from time import time, ctime


class rewiredBotPlugin():
    def __init__(self, parent, *args):
        self.parent = parent
        self.config = self.parent.config
        self.defines = "!msg"
        self.parent.librewired
        self.mbox = []
        self.parent.librewired.notify("__ClientJoin", self.clientJoined)

    def run(self, *args):
        fullmsg = args[1]
        if not args[0]:
            nick = self.parent.librewired.getNickByID(fullmsg[1])
            pending = self.checkQueue(fullmsg[1])
            if not pending:
                return str(nick) + ": You have no pending messages."
            self.deliverMsg(fullmsg[1])
            return 0
            #return "!msg username/[usernick] msg"

        if args[0].count("[", 0, 2) and args[0].count("]"):
            name = args[0][args[0].find('[', 0, 2) + 1:args[0].find(']')]
            msg = args[0][args[0].find(']') + 1:]
            isnick = 1
            #userid = self.parent.librewired.getUserByNick(name)
        else:
            name = args[0][:args[0].find(" ")]
            msg = args[0][args[0].find(' ') + 1:]
            isnick = 0
            #userid = self.parent.librewired.getUserByName(name)

        msg = msg.strip()
        print fullmsg
        if not self.queueMsg(fullmsg[1], name, isnick, msg):
            return "Sorry, i can't store your message right now."
        return "Okay, I'll send your message to " + str(name) + " (Queue ID: " + str(len(self.mbox)) + ")"

    def queueMsg(self, userID, to, isnick, msg):
        try:
            user = self.parent.librewired.getUserNameByID(userID)
            nick = self.parent.librewired.getNickByID(userID)
            self.mbox.append({'fromuser': user, 'fromnick': nick, 'to': to, 'isnick': isnick, 'msg': msg, 'date': time()})
            print self.mbox
        except:
            return 0
        return 1

    def removeMsg(self, index):
        self.mbox.pop(index)
        return 1

    def deliverMsg(self, userID):
        userID = int(userID)
        msgs = self.getMsg(userID)
        for index, amsg in msgs.items():
            self.parent.librewired.sendPrivateMsg(userID, "Message from " + amsg['fromnick'] + "(" + amsg['fromuser'] +\
            ") sent on " + str(ctime(int(amsg['date']))) + ":\n" + str(amsg['msg']))
        msgs = sorted(msgs, reverse=True)
        print msgs
        for index in msgs:
            self.removeMsg(index)
            print index
        return 1

    def checkQueue(self, userID):
        return len(self.getMsg(userID))

    def getMsg(self, userID):
        userID = int(userID)
        msgs = {}
        username = self.parent.librewired.getUserNameByID(userID)
        nick = self.parent.librewired.getNickByID(userID)
        for index, item in enumerate(self.mbox):
            if item['isnick']:
                if nick.upper() == item['to'].upper():
                    msgs[index] = item
            else:
                if username.upper() == item['to'].upper():
                    msgs[index] = item
        return msgs

    def clientJoined(self, msg):
        userid = int(msg[0])
        chatid = int(msg[1])
        nick = self.parent.librewired.getNickByID(userid)
        username = self.parent.librewired.getUserNameByID(userid)
        count = self.checkQueue(userid)
        if count and chatid == 1:
            self.parent.librewired.sendChat(1, str(nick) + ": You have " + str(count) +\
            " unread messages. Type !msg to read them.")
        return 1
