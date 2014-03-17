import re


class rewiredBotPlugin():
    """re:wired bot documentation plugin"""
    def __init__(self, parent, *args):
        self.parent = parent
        self.defines = "!help"
        self.privs = {'!help': 1}
        self.docs = None

    def run(self, *args):
        """!help: Usage: !help !command/plugin name
        Sends you the documentation for the command/plugin via pm.
        _"""
        if not self.docs:
            self.docs = self.build_doc()
        if not self.docs:
            return "Sorry im having problems building the docs :("
        userid = int(args[1][1])
        nick = self.parent.librewired.getNickByID(userid)
        if not args[0]:
            self.parent.librewired.sendPrivateMsg(userid, self.overview())
            return "%s: check your messages" % nick
        arg = args[0].strip().lower()
        if arg in self.pluginlist():
            helptext = self.pluginhelp(arg)
            if helptext:
                self.parent.librewired.sendPrivateMsg(userid, helptext)
                return 0
            else:
                return "%s: Sorry, no help available for %s" % (nick, arg)
        if arg in self.commandlist():
            helptext = self.commandhelp(arg)
            if helptext:
                self.parent.librewired.sendPrivateMsg(userid, helptext)
                return 0
            return "%s: Sorry, no help available for %s" % (nick, arg)
        return 0

    def overview(self):
        text = ''
        text += 're:wired Bot Help:\n'
        text += '  To interact with this bot simply type a command into the chat and it will respond to you.\n'
        text += '  Here is a list of all installed plugins and the commands they support:\n'
        for akey, aplugin in self.docs.items():
            try:
                text += "  %s: %s\n" % (akey, ', '.join(aplugin['commands']))
            except:
                pass
        text += '  to get more information on a plugin type: !help pluginname\n'
        text += '  for help on a plugin command type: !help !commandname'
        return text

    def pluginhelp(self, plugin):
        for akey, aplugin in self.docs.items():
            if plugin == akey:
                text = 'Plugin %s\n' % plugin
                text += "    %s\n" % aplugin['description']
                text += "Supported commands:\n"
                text += "    " + ", ".join(aplugin['commands'])
                return text
        return 0

    def commandlist(self):
        newlist = []
        for aname, aplugin in self.docs.items():
            try:
                newlist += aplugin['commands']
            except Exception as e:
                pass
        return newlist

    def commandhelp(self, command):
        for akey, aplugin in self.docs.items():
            commands = aplugin['commandhelp']
            try:
                if command.lower() in commands:
                    return commands[command.lower()].strip()
            except Exception as e:
                pass
        return 0

    def pluginlist(self):
        newlist = []
        for aplugin in self.docs.keys():
            newlist.append(aplugin)
        return newlist

    def build_doc(self):
        docs = {}
        for aplugin in self.parent.plugins:
            try:
                name = str(aplugin.__module__).replace('plugins.', '')
                docs[name] = {}
                docs[name]['commandhelp'] = {}
                docs[name]['description'] = aplugin.__doc__
                if hasattr(aplugin, 'run'):
                    if hasattr(aplugin.run, '__doc__'):
                        if len(aplugin.run.__doc__):
                            commandlist = aplugin.run.__doc__.split('___')
                            for acommand in commandlist:
                                thiscommand = re.findall(r'(!.*?):', acommand)
                                if thiscommand:
                                    acommand = acommand[len(thiscommand[0])+2:]  # strip command marker
                                    text = acommand.strip('___').split('\n')
                                    docs[name]['commandhelp'][thiscommand[0].lower()] =\
                                        "\n    ".join([x.strip() for x in text])
                docs[name]['commands'] = []
                if type(aplugin.defines) is list:
                    docs[name]['commands'] += aplugin.defines
                else:
                    docs[name]['commands'].append(aplugin.defines)
            except Exception as e:
                continue
        return docs
