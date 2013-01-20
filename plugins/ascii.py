from includes.botfunctions import regmatch, regexclude
from pyfiglet import Figlet, FontNotFound


class rewiredBotPlugin():
    def __init__(self, parent, *args):
        self.defines = "!ascii"
        self.parent = parent

    def run(self, *args):
        font = 'slant'
        if args[0].upper() == "?FONTS":
            f = Figlet(font)
            return str(f.getFonts())

        param = regmatch(args[0], self.parent.config['paramDelimiter'])
        if param:
            font = param
            text = regexclude(args[0], self.parent.config['paramDelimiter'])
            if not text:
                return 0
        else:
            text = args[0]

        try:
            f = Figlet(font)
            text = f.renderText(text)
        except FontNotFound:
            return "Unknown font: " + str(font)
        return text
