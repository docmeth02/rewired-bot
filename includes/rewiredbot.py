from librewired import rewiredclient
from time import sleep
from signal import signal, SIGINT, SIGTERM
from sys import exit
import botfunctions
import simplestorage
from botdb import *
from logging import StreamHandler, getLogger, DEBUG, INFO, ERROR, CRITICAL


class rewiredbot():
    def __init__(self, daemonize=0, bundled=0, configfile=0, bundleCallback=0):
        self.configfile = configfile
        if not self.configfile:
            self.configfile = 'bot.conf'
        self.config = botfunctions.loadConfig(self.configfile)
        if not self.config:
            print "Failed to load config from file: %s!" % self.configfile
            raise SystemExit
        self.config['appversion'] = botfunctions.gitVersion('includes')
        self.config['appname'] = "re:wired Bot"
        if daemonize:
            botfunctions.daemonize()
        self.logger = getLogger('lib:re:wired')
        self.bundled = bundled
        if bundled:
            self.bundled = 1
            self.bundleCallback = bundleCallback
        else:
            ch = StreamHandler()
            self.logger.addHandler(ch)
            self.logger.setLevel(botfunctions.getLogLevel(self.config['loglevel']))
            self.sig1 = signal(SIGINT, self.botShutdown)
            self.sig2 = signal(SIGTERM, self.botShutdown)
        self.librewired = rewiredclient.client(self)
        self.librewired.start()
        botfunctions.initLogfile(self, botfunctions.getLogLevel(self.config['loglevel']))
        botfunctions.initPID(self.config)
        self.db = botDB(self)
        self.db.openDB()
        self.storage = simplestorage.simpleStorage()
        self.plugins = []
        self.pluginshutdowncallbacks = []
        self.initPlugins()
        self.nick = self.config['nick']
        self.librewired.appname = self.config['appname']
        self.librewired.version = self.config['appversion']

    def run(self):
        self.librewired.status = self.config['status']
        self.librewired.loadIcon(self.config['icon'])
        self.librewired.autoreconnect = int(self.config['autoreconnect'])
        if not self.librewired.connect(self.config['server'], self.config['port']):
            self.logger.error("Failed to connect to %s! Check your config settings", self.config['server'])
            if self.bundled:
                self.bundleCallback("CONNECT")
            self.librewired.keepalive = 0
            exit()
        if not self.librewired.login(self.nick, self.config['username'], self.config['password'], 1):
            self.logger.error("Login failed! Check your username/password!")
            if self.bundled:
                self.bundleCallback("LOGIN")
            self.librewired.keepalive = 0
            exit()
        self.librewired.subscribe(300, self.gotChat)
        self.librewired.subscribe(301, self.gotActionChat)
        self.librewired.notify("__ClientJoin", self.clientJoined)
        self.librewired.notify("__ClientLeave", self.clientLeft)
        self.librewired.notify("__ClientKicked", self.clientKicked)
        self.librewired.notify("__ClientBanned", self.clientBanned)
        self.librewired.notify("__ClientStatusChange", self.statusChange)
        self.librewired.notify("__PrivateChatInvite", self.chatInvite)
        self.librewired.notify("__ClientKicked", self.clientKicked)
        self.librewired.notify("__ClientBanned", self.clientBanned)
        sleep(0.5)

        while self.librewired.keepalive:
            #main loop
            sleep(1)
        self.botShutdown()

    def botShutdown(self, *args):
        for aplugin in self.pluginshutdowncallbacks:
            try:
                aplugin()
            except Exception as e:
                self.logger.error("Error in plugin shutdown handler: %s" % e)
        botfunctions.removePID(self.config)
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
        return 1

    def clientLeft(self, msg, client):
        return 1

    def clientKicked(self, msg):
        return 1

    def clientBanned(self, msg):
        return 1

    def gotActionChat(self, msg):
        return self.gotChat(msg)

    def gotChat(self, msg):
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
                    name = str(self.check_command(chat[2], 1))
                    result = "Sorry, " + str(self.librewired.getNickByID(chat[1]))\
                        + "... You are not allowed to use !%s" % name
                if result:
                        self.librewired.sendChat(int(chat[0]), result)
            else:
                pass
        return 1

        return 1

    def parse_command(self, line):
        if not line.count("!", 0, 5):
            return 0
        if line.count(" ") >= 1:
            command = line[line.find("!") + 1: line.find(" ")]
        else:
            command = line[line.find("!") + 1:]
        return command

    def check_command(self, line, parseOnly=0):
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
        if user.login in self.config['adminuser']:
            return 100
        if user.login in self.config['opuser']:
                return 50
        if user.login in self.config['guestuser']:
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

    def clientKicked(self, params, ban=False):
        killerid, victimid, text = params
        if int(victimid) == int(self.librewired.id):
            with self.librewired.lock:
                self.librewired.autoreconnect = 0
                self.librewired.keepalive = 0
        return

    def clientBanned(self, params):
        self.clientKicked(params, True)

    def updateConfig(self):
        """ updates the local configfile """
        print "moo"
        return botfunctions.saveConfig(self.config, self.configfile)

