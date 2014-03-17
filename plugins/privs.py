class rewiredBotPlugin():
    """Privilege control plugin"""
    def __init__(self, parent, *args):
        self.parent = parent
        self.defines = ["!+op", "!-op", "!privs"]
        self.privs = {'!+op': 99, '!-op': 99, '!privs': 99}

    def run(self, *args):
        """!privs: Usage: !privs username/nick
        Return current privilege score for user/nick
        User Privileges are setup in bots config file.
        Users can temporarily be opped by using !+op
        to use certain commands that require higher privileges.
        ___
        !+op: Usage: !+op username
        Elevate privilege score of this user to op level(50).
        Note that certain commands may require owner privileges(99).
        In case you want a user to be owner, edit the adminuser list
        in bots config file.
        ___
        !-op: Usage: !-op username
        Demote a previous opped user to default privilege level(5).
        The user will no longer be able to use commands that require
        op user privileges. In case the user is on the guestuser
        list in bots config file the score is lowered to 1.
        ___"""
        line = args[1][2]
        command = line[0:line.find(" ")]
        param = line[line.find(" "):].strip()

        if command.upper() == "!PRIVS":
            if param[0:1] == '!':
                privs = self.parent.getCommandPrivs(param)
                if privs > 0:
                    return param + ": privlevel >= " + str(privs)
                return param + ": no such command"
            user = self.getUser(param)
            if not user:
                return "Sorry, i can't find user " + str(param)
            privs = self.parent.getPrivs(user.userid)
            return "User: " + user.login + ": PrivLevel = " + str(privs) + " Nick: " + str(user.nick)

        if command.upper() == "!+OP":
            user = self.getUser(param)
            if not user:
                return "Sorry, i can't find user " + str(param)
            if user.login in self.parent.config['guestuser']:
                return "Sorry, can't promote a guest user"
            if user.login in self.parent.config['opuser']:
                return user.login + " is already a op user"
            if not isinstance(self.parent.config['opuser'], list):
                self.parent.config['opuser'] = []
            self. parent.config['opuser'].append(user.login)
            return user.login + " is now op"

        if command.upper() == "!-OP":
            user = self.getUser(param)
            if not user:
                return "Sorry, i can't find user " + str(param)
            if not isinstance(self.parent.config['opuser'], list):
                return str(param) + " is no op user"
            if not user.login in self.parent.config['opuser']:
                return str(param) + " is no op user"
            self.parent.config['opuser'].remove(user.login)
            return "Okay, demoted user " + str(user.login)

        return 0  # "Usage: !privs !command / !privs User/Nick"

    def getUser(self, param):
        user = self.parent.librewired.getUserByName(param)
        if not user:
            user = self.parent.librewired.getUserByNick(param)
            if not user:
                    return 0
            if not user in self.parent.librewired.userlist:
                return 0
        try:
            user = self.parent.librewired.userlist[user]
        except:
            return 0
        return user
