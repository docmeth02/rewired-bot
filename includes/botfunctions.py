from pygeoip import GeoIP  # pygeoip
from os.path import exists


def get_geolocation(ip, includeCity=0):
    dbpath = "GeoLiteCity.dat"
    if not exists(dbpath):
        return 0
    location = 0
    gloc = GeoIP(dbpath)
    data = gloc.record_by_addr(ip)
    location = ""
    if includeCity:
        try:
            if 'city' in data:
                if data['city']:
                    location += data['city'] + "/"
        except TypeError:
            pass
    try:
        location += data['country_name']
    except TypeError:
        pass
    if location:
        return location.encode("utf-8")
    return 0


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
    greetUsers = boolean(default=True)
    # loglevels: debug, info, warning, error, none
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
