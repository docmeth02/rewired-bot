from os.path import exists
from re import match, compile


def loadConfig(confFile):
    #will read config file or create one with the required defaults
    from configobj import ConfigObj
    from validate import Validator
    default = """server = string(default="re-wired.info")
    port = integer(default=2000)
    username = string("guest")
    password = string(default="")
    nick = string(default="re:Wired Bot")
    status = string(default="Another re:wired Bot")
    icon = string(default="icon.png")
    logFile = string(default="logfile")
    dbFile = string(default="rewiredBot.db")
    userLogging = boolean(default=True)
    legacyLogMode = boolean(default=True)
    legacyInterval = integer(default=30)
    eventLog = boolean(default=False)
    autoreconnect = boolean(default=False)
    PidFile = string(default="rewiredbot.pid")
    # loglevels: debug, info, warning, error, none
    adminUser = list(default=list('admin', 'docmeth02'))
    logLevel = string(default=debug)"""
    spec = default.split("\n")
    config = ConfigObj(confFile, list_values=False, stringify=True, configspec=spec)
    validator = Validator()
    config.validate(validator, copy=True)
    config.filename = confFile
    config.write()
    config['appVersion'] = "20121202A1"
    config['appName'] = "re:wired Bot"
    return config


def checkPlatform(name):
    if name.upper() == str(platform.system()).upper():
        return 1
    return 0


def regmatch(text, delimitStart, delimitEnd=False):
    if not delimitEnd:
        delimitEnd = delimitStart
    pattern = compile('\\' + str(delimitStart) + '(.*?)\\' + str(delimitEnd))
    match = pattern.search(text)
    if match:
        return text[match.start() + 1:match.end() - 1]
    else:
        return 0
