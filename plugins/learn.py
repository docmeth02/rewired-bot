import json
from os.path import exists
from includes.botfunctions import regmatch, regexclude


class rewiredBotPlugin():
    """Chat Facts Plugin. Adds ??facts tokens to chat."""
    def __init__(self, parent, *args):
        self.parent = parent
        self.defines = ["!learn", "!forget"]
        self.privs = {'!learn': 50, '!forget': 50}
        self.binds = "??"
        self.brain = {}
        if exists('brain.json'):
            with open('brain.json', 'r') as f:
                self.brain = json.loads(f.read())

    def run(self, params, *args):
        """!learn: Usage: !learn item fact
        Remember "fact" about "item".
        !learn bot is awesome
        will rember that "bot" "is awsome".
        Retrieve facts about "bot" by typing ??bot into chat
        ___
        !forget: Usage: !forget item _index_
        Forget a fact about "item". Index is the number that is
        displayed in front of the fact when doing ??item:
        !forget bot _0_
        forgets the first fact about bot. In case you want to
        delete all facts for a item use * as index:
        !forget bot _*_
        will forget all about item "bot".
        ___
        """
        command = self.parent.parse_command(args[0][2])

        if str(command).upper() == "LEARN":
            if not isinstance(params, str):
                return "Usage: !learn Topic Item"
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
                index = regmatch(params, '_')
                item = regexclude(params, '_')
                if index != '*':
                    index = int(index)
                print index
                print item
            except:
                print "NOPE"
                return 0
            if not item.upper() in self.brain:
                print "NOPE2"
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
            if not len(self.brain[item.upper()]):
                self.brain.pop(item.upper(), None)
            if self.save():
                return "Okay, I forgot" + " " + item + "  (" + str(index) + ")"
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
                response = response + "(" + str(n) + ") " + self.brain[command.upper()][n] + "\n"
        if response:
            try:
                response = response.encode('UTF-8')
            except:
                pass
            self.parent.librewired.sendChat(int(param[0]), response)
        return 1
