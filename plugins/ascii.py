# make sure you have python-pkg-resources installed for this to work
from includes.botfunctions import regmatch, regexclude
from pyfiglet import Figlet, FontNotFound


class rewiredBotPlugin():
    def __init__(self, parent, *args):
        self.defines = "!ascii"
        self.privs = {'!ascii': 1}
        self.parent = parent

    def run(self, *args):
        font = 'slant'

        try:
            if args[0].upper() == "?FONTS":
                f = Figlet(font)
                fontlist = "Available fonts:\n"
                fontlist += formatList(f.getFonts())
                self.parent.librewired.sendPrivateMsg(int(args[1][1]), fontlist)
                return 0
        except:
            return "Usage: !ascii (%FontName%) Text / !ascii ?Fonts"

        param = regmatch(args[0], self.parent.config['paramDelimiter'])
        if param:
            font = param
            text = regexclude(args[0], self.parent.config['paramDelimiter'])
            if not text:
                return 0
        else:
            text = args[0]

        if not len(text):
            return "Usage: !ascii (%FontName%) Text / !ascii ?Fonts"

        try:
            f = Figlet(font)
            text = f.renderText(text)
        except FontNotFound:
            return "Unknown font: " + str(font)
        return text


def formatList(data):
    cols = 4
    rows = int(len(data)) / int(cols)
    out = ""
    for i in range(0, rows):
        chunk = data[(i * cols):(i * cols) + cols]
        out += "\t".join(chunk)
        out += "\n"
    return out
