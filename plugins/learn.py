import json
from os.path import exists
from includes.botfunctions import regmatch, regexclude


class rewiredBotPlugin():
    def __init__(self, parent, *args):
        self.parent = parent
        self.defines = ["!learn", "!forget"]
        self.binds = "??"
        self.brain = {}
        if exists('brain.json'):
            with open('brain.json', 'r') as f:
                self.brain = json.loads(f.read())

    def run(self, params, *args):
        command = self.parent.parse_command(args[0][2])

        if str(command).upper() == "LEARN":
            if not params.count(" ", 0, 10):
                return 0
            name = params[0: params.find(" ")]
            item = params[(params.find(" ") + 1):]
            try:
                item = item.decode('UTF-8')
            except:
                pass
            if not name.upper() in self.brain:
                self.brain[name.upper()] = [item]
            else:
                self.brain[name.upper()].append(item)

            if self.save():
                return "Okay, I'll remember that"
            return 0

        if str(command).upper() == "FORGET":
            item = 0
            index = 0
            try:
                index = regmatch(params, self.parent.config['paramDelimiter'])
                item = regexclude(params, self.parent.config['paramDelimiter'])
                if index != '*':
                    index = int(index)
            except:
                return 0
            if not item.upper() in self.brain:
                return 0
            if type(index) is int:
                try:
                    check = self.brain[item.upper()][index]
                except:
                    return 0
            else:
                self.brain.pop(item.upper(), None)
                if self.save():
                    return "Okay, I forgot " + item
                return 0

            self.brain[item.upper()].pop(index)
            if self.save():
                return "Okay, I forgot " + " " + item + " " + self.parent.config['paramDelimiter'] + str(index) \
                + self.parent.config['paramDelimiter']
            return 0

    def save(self):
        try:
            with open('brain.json', 'w') as f:
                f.write(json.dumps(self.brain))
        except:
            return 0
        return 1

    def process(self, param):
        command = param[2][(param[2].find("??", 4) + 3):]
        command = command.lstrip()
        response = ""
        if command.upper() in self.brain:
            response = response + (command + ":\n")
            for n in range(len(self.brain[command.upper()])):
                #self.parent.librewired.sendChat(int(param[0]), "[" + str(n) + "] " + self.brain[command][n])
                response = response + (self.parent.config['paramDelimiter'] + " " + str(n) + " " \
                                       + self.parent.config['paramDelimiter'] + self.brain[command.upper()][n] + "\n")
        if response:
            try:
                response = response.encode('UTF-8')
            except:
                pass
            self.parent.librewired.sendChat(int(param[0]), response)
        return 1
