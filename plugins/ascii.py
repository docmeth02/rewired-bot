from pyfiglet import Figlet, FontNotFound


class rewiredBotPlugin():
    def __init__(self, *args):
        self.defines = "!ascii"

    def run(*args):
        font = 'slant'
        if args[1].upper() == "?FONTS":
            f = Figlet(font)
            return str(f.getFonts())

        if args[1].count("[", 0, 2) and args[1].count("]"):
            font = args[1][args[1].find('[', 0, 2) + 1:args[1].find(']')]
            text = args[1][args[1].find(']') + 1:]
            text = text.strip()
        else:
            text = args[1]
        try:
            f = Figlet(font)
            text = f.renderText(text)
        except FontNotFound:
            return "Unknown font: " + str(font)
        return text
