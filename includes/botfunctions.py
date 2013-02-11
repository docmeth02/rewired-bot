from os.path import exists
try:
    from os import umask, setsid, dup2, fork
except:
    pass  # process forking is na on windows - boohoo
from os import unlink, getpid
from sys import stdout, stderr, stdin
from re import match, compile
from logging import getLogger, Formatter, FileHandler


def loadConfig(confFile):
    #will read config file or create one with the required defaults
    from configobj import ConfigObj
    from validate import Validator, VdtParamError
    default = """server = string(default="re-wired.info")
    port = integer(default=2000)
    username = string(default="guest")
    password = string(default="")
    nick = string(default="re:Wired Bot")
    status = string(default="Another re:wired Bot")
    icon = string(default="icon.png")
    logFile = string(default="logfile")
    dbFile = string(default="rewiredBot.db")
    eventLog = boolean(default=False)
    autoreconnect = boolean(default=False)
    paramDelimiter = string(default="_")
    PidFile = string(default="rewiredbot.pid")
    # loglevels: debug, info, warning, error, none
    logLevel = string(default=debug)
    adminUser = list(default=list('admin', 'docmeth02'))
    opUser = list(default=list())
    guestUser = list(default=list('guest'))"""
    spec = default.split("\n")
    try:
        config = ConfigObj(confFile, list_values=True, stringify=True, configspec=spec)
        validator = Validator()
        config.validate(validator, copy=True)
        config.filename = confFile
        config.write()
    except VdtParamError as e:
        print "Error in  config file!"

    config['appVersion'] = "20130102A1"
    config['appName'] = "re:wired Bot"
    return config


def saveConfig(newconfig, confFile):
    from configobj import ConfigObj
    config = ConfigObj(newconfig, list_values=True, stringify=True)
    config.pop('appVersion')
    config.pop('appName')
    config.filename = confFile
    config.write()
    return 1


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
        return text[match.start() + 1:match.end() - 1].strip()
    else:
        return 0


def regexclude(text, delimitStart, delimitEnd=False):
    if not delimitEnd:
        delimitEnd = delimitStart
    pattern = compile('\\' + str(delimitStart) + '(.*?)\\' + str(delimitEnd))
    match = pattern.search(text)
    if match:
        return text[match.end():].strip()
    else:
        return text


def daemonize():
    if fork():
        exit(0)
    umask(0)
    setsid()
    if fork():
        exit(0)
    stdout.flush()
    stderr.flush()
    si = file('/dev/null', 'r')
    so = file('/dev/null', 'a+')
    se = file('/dev/null', 'a+', 0)
    dup2(si.fileno(), stdin.fileno())
    dup2(so.fileno(), stdout.fileno())
    dup2(se.fileno(), stderr.fileno())
    return 1


def initPID(config):
    pid = str(getpid())
    try:
        f = open(config['PidFile'], 'w')
        f.write(pid)
        f.close()
    except:
        print "Failed to write pid file to " + config['PidFile']
        pass
    return pid


def removePID(config):
    try:
        unlink(config['PidFile'])
    except:
        print "failed to remove pid file"
    return 1


def getPID(config):
    try:
        f = open(config['PidFile'], 'r')
        pid = f.read()
        f.close()
    except:
        pid = 0
        pass
    return pid


def initLogfile(parent, level):
    if parent.config['logFile']:
        log = getLogger('lib:re:wired')
        formatter = Formatter('%(asctime)s: %(message)s', "%b %d %y - %H:%M:%S")
        filehandler = FileHandler(str(parent.config['logFile']), "a")
        filehandler.setLevel(level)
        filehandler.setFormatter(formatter)
        log.addHandler(filehandler)
        return 1
    return 0


def getLogLevel(level):
    from logging import DEBUG, INFO, WARN, ERROR
    level = level.upper()
    if level == "DEBUG":
        return DEBUG
    elif level == "INFO":
        return INFO
    elif level == "WARNING":
        return WARN
    elif level == "ERROR":
        return ERROR
    return WARN
