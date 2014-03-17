# make sure you have python-pkg-resources installed for this to work
from includes.botfunctions import regmatch, regexclude
from pyfiglet import Figlet, FontNotFound


class rewiredBotPlugin():
    """Ascii Art plugin"""
    def __init__(self, parent, *args):
        self.defines = "!ascii"
        self.privs = {'!ascii': 1}
        self.parent = parent

    def run(self, *args):
        """!ascii: Usage: !ascii (_FontName_) Your Text / !ascii ?Fonts
        Posts custom ascii text art into chat.
        ?Fonts will send you a list of fonts via pm.
        Use custom fonts like this: !ascii _starwars_ Woooo Ascii Art!
        ___"""
        font = 'slant'
        try:
            chatid = int(args[1][0])
        except:
            print "FAILED"
            return 0
        try:
            if args[0].upper() == "?FONTS":
                f = Figlet(font)
                fontlist = "Available fonts:\n"
                fontlist += formatList(f.getFonts())
                self.parent.librewired.sendPrivateMsg(int(args[1][1]), fontlist)
                return 0
        except:
            return "Usage: !ascii (%FontName%) Text / !ascii ?Fonts"

        param = regmatch(args[0], '_')
        if param:
            font = param
            text = regexclude(args[0], '_')
            if not text:
                return 0
        else:
            text = args[0]

        if not len(text):
            return "Usage: !ascii (%FontName%) Text / !ascii ?Fonts"
        asciitext = 0
        try:
            f = Figlet(font)
            asciitext = f.renderText(text)
        except FontNotFound:
            return "Unknown font: " + str(font)
        if asciitext:
            lines = asciitext.split('\n')
            sswired = chr(31).join(lines)
            for aline in lines:
                if len(aline.strip()):
                    self.parent.librewired.sendChat(chatid, chr(14) + aline)
            self.parent.librewired.sendChat(chatid, chr(129) + sswired)
        return 0


def formatList(data):
    cols = 4
    rows = int(len(data)) / int(cols)
    out = ""
    for i in range(0, rows):
        chunk = data[(i * cols):(i * cols) + cols]
        out += "\t".join(chunk)
        out += "\n"
    return out
