from librewired import rewiredclient
from time import sleep
from signal import signal, SIGINT, SIGTERM
from sys import exit
import botfunctions
from botdb import *
from transferlogger import *
from eventlogging import *
from logging import StreamHandler, getLogger, DEBUG, INFO, ERROR


class rewiredbot():
    def __init__(self):
        self.logger = getLogger('lib:re:wired')
        ch = StreamHandler()
        self.logger.addHandler(ch)
        self.logger.setLevel(DEBUG)
        self.librewired = rewiredclient.client(self)
        self.librewired.start()
        self.sig1 = signal(SIGINT, self.serverShutdown)
        self.sig2 = signal(SIGTERM, self.serverShutdown)
        self.config = botfunctions.loadConfig('bot.conf')
        self.db = botDB(self)
        self.db.openDB()
        self.userLogger = transferLogger(self)
        self.eventlog = eventLogger(self)
        self.plugins = []
        self.initPlugins()
        self.nick = self.config['nick']
        self.librewired.appname = self.config['appName']
        self.librewired.version = self.config['appVersion']

    def run(self):
        self.librewired.status = self.config['status']
        self.librewired.loadIcon(self.config['icon'])
        #if not self.librewired.connect("storage.m2-entertainment.de", 2000):
        if not self.librewired.connect("shaosean.tk", 2000):
            self.logger.error("Failed to connect!")
            self.librewired.keepalive = 0
            exit()
        #if not self.librewired.login(self.nick, "guest", "", True):
        if not self.librewired.login(self.nick, "bot", "bot", True):
            self.logger.error("Failed to login!")
            self.librewired.keepalive = 0
            exit()
        self.librewired.subscribe(300, self.gotChat)
        self.librewired.subscribe(301, self.gotActionChat)
        self.librewired.notify("__ClientJoin", self.clientJoined)
        self.librewired.notify("__ClientLeave", self.clientLeft)
        self.librewired.notify("__ClientStatusChange", self.statusChange)
        self.librewired.notify("__PrivateChatInvite", self.chatInvite)

        sleep(0.5)
        while self.librewired.keepalive:
            #main loop
            if self.config['userLogging']:
                self.userLogger.doLog()
            if self.config['eventLog']:
                self.eventlog.commitData()
            sleep(1)
        self.serverShutdown()

    def serverShutdown(self, *args):
        self.librewired.keepalive = 0
        self.db.closeDB()
        raise SystemExit
        return 1

    def statusChange(self, msg):
        self.logger.debug("User %s changed status", msg)
        return 1

    def chatInvite(self, *args):
        self.librewired.joinPrivateChat(args[0])
        return 1

    def clientJoined(self, msg):
        if self.config['eventLog']:
            self.eventlog.logEvent(3, [msg[1], msg[0]])

        return 1

    def clientLeft(self, msg):
        if self.config['eventLog']:
            self.eventlog.logEvent(4, [msg[1], msg[0]])
        return 1

    def gotActionChat(self, msg):
        if self.config['eventLog']:
            self.eventlog.logEvent(2, msg.msg)
        return 1

    def gotChat(self, msg):
        if self.config['eventLog']:  # if eventlog is enabled, log this chatline
            self.eventlog.logEvent(1, msg.msg)
        chat = msg.msg

        if int(chat[1]) != int(self.librewired.id):  # we don't want to respond to ourself
            if self.plugins:  # check for plugins that bind to chat hints
                for aplugin in self.plugins:
                    if hasattr(aplugin, 'binds'):
                        try:
                            if chat[2][0:len(aplugin.binds)].upper() == aplugin.binds.upper():
                                aplugin.process(chat)
                        except:
                            pass

            command = self.check_command(chat[2])  # check for a command
            if command:
                reqprivs = self.getCommandPrivs("!" + self.check_command(chat[2], 1))
                userprivs = self.getPrivs(chat[1])
                if userprivs >= reqprivs:
                    result = command['command'].run(command['parameter'], chat)
                else:
                    result = "Sorry, " + str(self.librewired.getNickByID(chat[1])) + "... You are not allowed to use !"\
                    + self.check_command(chat[2], 1)
                if result:
                        self.librewired.sendChat(int(chat[0]), result)
            else:
                pass
        return 1

        return 1

    def check_chat(self, line, returncleaned=0):
        # no longer in use
        mynames = {self.nick + ":", "@" + self.nick}
        for aname in mynames:
            if line[:len(aname)].upper() == aname.upper():
                if returncleaned == 1:
                    return line[(len(aname)):].strip()
                return 1
        return 0

    def parse_command(self, line):
        #parse command
        if not line.count("!", 0, 5):
            return 0
        if line.count(" ") >= 1:
            command = line[line.find("!") + 1: line.find(" ")]
        else:
            command = line[line.find("!") + 1:]
        return command

    def check_command(self, line, parseOnly=0):
        #parse command
        if not line.count("!", 0, 5):
            return 0
        if line.count(" ") >= 1:
            command = line[line.find("!") + 1: line.find(" ")]
        else:
            command = line[line.find("!") + 1:]
        if parseOnly:
            return command
        # now check for a valid command
        acommand = 0
        if self.plugins:
            for aplugin in self.plugins:

                if type(aplugin.defines) is list:  # this plugin defines multiple commands
                    for adefine in aplugin.defines:
                        if command.upper() == adefine[1:].upper():
                            acommand = aplugin
                else:  # single command plugin
                    if command.upper() == aplugin.defines[1:].upper():
                        acommand = aplugin
        if not acommand:
            return 0
        parameter = 0
        if line.count(" ") >= 1:
            # parse parameters as well
            parameter = line[line.find(" ") + 1:(len(line))]
        return {"command": acommand, "parameter": parameter}

    def split_param(self, param, count=1):
        space = param.find(' ')
        newline = param.find("\n")
        if (newline != -1) and (newline < space):
            return param.split("\n", count)
        return param.split(" ", count)

    def initPlugins(self):
        try:
            import plugins
        except:
            self.logger.error("Error while loading plugin directory")
            return 0
        allplugs = dir(plugins)
        for key in range(len(allplugs)):
            plugin = 0
            name = allplugs[key]
            try:
                obj = eval("plugins." + name)
                plugin = getattr(obj, "rewiredBotPlugin")
            except:
                pass
            if plugin:
                try:
                    self.plugins.append(plugin(self))
                except:
                    pass
        return 1

    def getPrivs(self, userID):
        user = self.librewired.getUserByID(int(userID))
        if not user:
            return 0
        if user.login in self.config['adminUser']:
            return 100
        if isinstance(self.config['opUser'], list):
            if user.login in self.config['opUser']:
                return 50
        if user.login in self.config['guestUser']:
            return 1
        return 25

    def getCommandPrivs(self, command):
        for aplugin in self.plugins:
            if isinstance(aplugin.defines, list):
                if command in aplugin.defines:
                    plugin = aplugin
                    break
            else:
                if aplugin.defines == command:
                    plugin = aplugin
                    break
        try:
            plugin.privs
        except:
            return -1
        if command in plugin.privs:
            return plugin.privs[command]
        return -1
