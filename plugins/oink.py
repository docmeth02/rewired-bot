class rewiredBotPlugin():
    """ Piggy bot plugin"""
    def __init__(self, *args):
        """!oink: Usage: !oink
        Responds with *squeal*
        _"""
        self.defines = "!oink"
        self.privs = {'!oink': 1}

    def run(*args):
        return "*squeal*"
