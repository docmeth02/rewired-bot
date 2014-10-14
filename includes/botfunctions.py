from os.path import exists
try:
    from os import umask, setsid, dup2, path, fork, environ, pathsep, devnull, getcwd
except:
    pass  # process forking is na on windows - boohoo
from os import unlink, getpid
from sys import stdout, stderr, stdin
from re import match, compile
from logging import getLogger, Formatter, FileHandler
from subprocess import call
from ConfigParser import ConfigParser


def loadConfig(confFile):
    config = ConfigParser()
    if not exists(confFile):
        config.add_section("re:wired Bot")
        config.set("re:wired Bot", 'server', 're-wired.info')
        config.set("re:wired Bot", 'port', '2000')
        config.set("re:wired Bot", 'username', 'guest')
        config.set("re:wired Bot", 'password', '')
        config.set("re:wired Bot", 'nick', 're:wire Bot')
        config.set("re:wired Bot", 'status', 'Another re:wired Bot')
        config.set("re:wired Bot", 'icon', 'icon.png')
        config.set("re:wired Bot", 'logfile', 'logfile')
        config.set("re:wired Bot", 'loglevel', 'debug')
        config.set("re:wired Bot", 'dbfile', 'rewiredBot.db')
        config.set("re:wired Bot", 'pidfile', 'rewiredbot.pid')
        config.set("re:wired Bot", 'autoreconnect', 1)
        config.set("re:wired Bot", 'adminuser', 'admin, docmeth02')
        config.set("re:wired Bot", 'opuser', '')
        config.set("re:wired Bot", 'guestuser', 'guest')
        try:
            with open(confFile, 'w') as newfile:
                config.write(newfile)
        except Exception as e:
            print "Failed to write default config file: %s" % e
            return 0
    try:
        config.read(confFile)
    except Exception as e:
        print "Failed to read config file: %s" % e
        return 0
    # parse config object
    items = config.items('re:wired Bot')
    listitems = ['adminuser', 'opuser', 'guestuser']
    boolitems = ['autoreconnect']
    intitems = ['port']
    config = {}
    try:
        for aitem in items:
            if aitem[0] in boolitems:
                config[aitem[0]] = bool(aitem[1])
            elif aitem[0] in intitems:
                config[aitem[0]] = int(aitem[1])
            elif aitem[0] in listitems:
                config[aitem[0]] = []
                if not len(aitem[1]):
                    continue
                listelem = aitem[1].split(',')
                for aelem in listelem:
                    config[aitem[0]].append(aelem.strip())
            else:
                config[aitem[0]] = aitem[1]
    except Exception as e:
        print "Failed to parse config object: %s" % e
        return 0
    return config


def saveConfig(newconfig, confFile):
    config = ConfigParser()
    config.add_section("re:wired Bot")
    listitems = ['adminuser', 'opuser', 'guestuser']
    for akey, asetting in newconfig.items():
        if akey in ['appversion', 'appname']:
            continue
        if akey in listitems and type(asetting) == list:
            asetting = ', '.join(asetting)
        config.set("re:wired Bot", akey, asetting)
    try:
        with open(confFile, 'w') as newfile:
            config.write(newfile)
    except Exception as e:
        print "Failed to write default config file: %s" % e
        return 0
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
        return text[0:match.start()].strip() + text[match.end():].strip()
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
        f = open(config['pidfile'], 'w')
        f.write(pid)
        f.close()
    except:
        print "Failed to write pid file to " + config['pidfile']
        pass
    return pid


def removePID(config):
    try:
        unlink(config['pidfile'])
    except:
        print "failed to remove pid file"
    return 1


def getPID(config):
    try:
        f = open(config['pidfile'], 'r')
        pid = f.read()
        f.close()
    except:
        pid = 0
        pass
    return pid


def initLogfile(parent, level):
    if parent.config['logfile']:
        log = getLogger('lib:re:wired')
        formatter = Formatter('%(asctime)s: %(message)s', "%b %d %y - %H:%M:%S")
        filehandler = FileHandler(str(parent.config['logfile']), "a")
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


def gitVersion(basepath):
    # parse git branch and commitid to server version string
    hasgit = 0
    # test for git command
    for dir in environ['PATH'].split(pathsep):
        if path.exists(path.join(dir, 'git')):
            try:
                call([path.join(dir, 'git')], stdout=open(devnull, "w"), stderr=open(devnull, "w"))
            except OSError, e:
                break
            hasgit = 1
    if hasgit:
        if path.exists(path.join(getcwd(), basepath, "git-version.sh")):
            # both git and our version script exist
            call([path.join(getcwd(), basepath, "git-version.sh")],
                 stdout=open(devnull, "w"), stderr=open(devnull, "w"))
    # check for version token and load it
    if path.exists(path.join(getcwd(), basepath, ".gitversion")):
        version = 'git-unknown'
        try:
            with open(path.join(getcwd(), basepath, ".gitversion"), 'r') as f:
                version = f.readline()
        except (IOError, OSError):
            return 'git-unknown'
        return version.strip()
    return 'git-unknown'
