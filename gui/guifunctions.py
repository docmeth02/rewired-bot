import platform
from os.path import expanduser, join, exists
from os import mkdir, sep, unlink
from shutil import copyfile, copytree
from includes import botfunctions


def getPlatformString(parent):
    system = "Unknown OS"
    version = "Unknown Version"
    system = platform.system()

    if system == 'Darwin':
        system = "OS X"
        version = platform.mac_ver()[0]
    if system == 'Linux':
        try:
            distro = platform.linux_distribution()
            version = distro[0] + " " + distro[1]
        except:
            version = "None"
    if system == 'Windows':
        version = platform.win32_ver()[0]
    return system + " " + version + " - Python " + platform.python_version()


def checkPlatform(name):
    if name.upper() == str(platform.system()).upper():
        return 1
    return 0


def initConfig(parent):
    home = False
    config = 0
    home = expanduser("~")
    if not home:
        debugLog(parent, "Unable to find user home dir!")
        return 0
    debugLog(parent, "User Home is: " + home)
    configdir = join(home, ".rewired")
    configfile = join(configdir, "bot.conf")
    debugLog(parent, "Config Folder is: " + configdir)
    debugLog(parent, "Config File is: " + configfile)
    if not exists(configdir):
        debugLog(parent, "Creating the configdir")
        try:
            mkdir(configdir)
        except:
            debugLog(parent, "failed to create the configdir!")
            return 0
    else:
        debugLog(parent, "ConfigDir already exists")
    if not exists(join(configdir, 'icon.png')):
        if not saveCopy('gui/icon.png', join(configdir, 'icon.png')):
            debugLog(parent, "failed to install default Icon!")
    if not exists(join(configdir, 'bot.conf')):
        debugLog(parent, "creating new config file")
        config = botfunctions.loadConfig(configfile)
        config['icon'] = join(configdir, 'icon.png')
        config['logFile'] = join(configdir, 'bot.log')
        config['dbFile'] = join(configdir, 'rewiredBot.db')
        config['serverPidFile'] = join(configdir, "PidFile.pid")
        config['status'] = "Another re:wired GUI Bot"
        rewriteConfig(config)
    else:
        config = botfunctions.loadConfig(configfile)
    parent.configFile = configfile
    parent.confDir = configdir
    if not exists(config['dbFile']):
        file = open(config['dbFile'], 'w')
        file.close()
    debugLog(parent, "initConfig done")
    if not exists(config['logFile']):
        file = open(config['logFile'], "w")
        file.write("Blank Logfile\n")
        file.close()
    return config


def configListToString(alist):
    astring = ""
    for aitem in alist:
        astring += str(aitem) + ', '
    return astring[0:len(astring)-2]


def configStringToList(astring):
    alist = []
    parts = astring.split(',')
    for apart in parts:
        alist.append(apart.strip())
    return alist


def rewriteConfig(config):
    try:
        version = config['appVersion']
    except KeyError:
        pass
    config.write()
    config['appVersion'] = version
    return 1


def debugLog(parent, text):
    pass


def saveCopy(src, dst):
    try:
        copyfile(src, dst)
    except:
        return 0
    return 1


def getAutoStart(homedir):
    if exists(join(homedir, '.rewiredBotAutostart')):
        return 1
    return 0


def setAutoStart(state, homedir):
    path = join(homedir, '.rewiredBotAutostart')
    if int(state):
        if not exists(path):
            file = open(path, 'w')
            file.close()
        return 1
    if exists(path):
        try:
            unlink(path)
        except:
            return 0
    return 1
