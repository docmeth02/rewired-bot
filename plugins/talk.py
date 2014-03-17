from chatterbotapi import ChatterBotFactory, ChatterBotType
from HTMLParser import HTMLParser
from re import sub, findall


class rewiredBotPlugin():
    """Pandorabots plugin. Talk directly to bot!"""
    def __init__(self, parent, *args):
        self.parent = parent
        self.defines = "!talk"
        self.privs = {'!talk': 100}
        self.parent.librewired.subscribe(300, self.monitorChat)
        self.parent.librewired.subscribe(301, self.monitorChat)
        if self.parent.storage.exists('plugin.talk', 'botid'):
            self.botid = self.parent.storage.get('plugin.talk', 'botid')
        else:
            self.botid = 'e6432308fe3401cc'
            self.parent.storage.store('plugin.talk', {'botid': self.botid})
        self.setupSession(self.botid)

    def run(self, params, *args):
        """!talk: Usage: !talk botid pandorabotid
        Setup the botid that will be used when users talk
        to bot by directly sending chat to botnick:
        !talk botid b0dafd24ee35a477
        _"""
        if not params:
            return 0
        command = self.parent.parse_command(args[0][2])
        chat = int(args[0][0])

        parts = str(params).split(" ")
        if len(parts) < 2:
            return "usage: !talk botid b0dafd24ee35a477"
        if parts[0].lower() == 'botid':
            result = findall(r'^([\d\w]{16})$', str(parts[1]))
            if not result:
                return "Invalid bot id: %s" % parts[1]
            self.botid = str(result[0])
            self.setupSession(self.botid)
            self.parent.storage.store('plugin.talk', {'botid': self.botid})
            return "New BotID: %s" % self.botid
        return 0

    def setupSession(self, botid):
        factory = ChatterBotFactory()
        self.chatterbot = factory.create(ChatterBotType.PANDORABOTS, botid)
        self.session = self.chatterbot.create_session()
        return 1

    def monitorChat(self, chat):
        msg = chat.msg
        if int(msg[1]) == self.parent.librewired.id:
            return 0
        if msg[2][:len(self.parent.librewired.nick)+1].lower() == "%s:" % self.parent.librewired.nick.lower():
            clean = msg[2][len(self.parent.librewired.nick)+1:].strip()
            try:
                text = self.session.think(clean)
            except Exception as e:
                print "Error 1: %s" % e
                return 0
            if text:
                self.parent.librewired.sendChat(int(msg[0]), decode(text))
            return 0


class _DeHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.__text = []

    def handle_data(self, data):
        text = data.strip()
        if len(text) > 0:
            text = sub('[ \t\r\n]+', ' ', text)
            self.__text.append(text + ' ')

    def handle_starttag(self, tag, attrs):
        if tag == 'p':
            self.__text.append('\n\n')
        elif tag == 'br':
            self.__text.append('\n')

    def handle_startendtag(self, tag, attrs):
        if tag == 'br':
            self.__text.append('\n\n')

    def text(self):
        return ''.join(self.__text).strip()


def decode(text):
    try:
        text = unicode(text, errors='ignore')
    except:
        pass
    text = text.encode("UTF-8")
    try:
        parser = _DeHTMLParser()
        parser.feed(text)
        parser.close()
        return parser.text()
    except:
        return text
