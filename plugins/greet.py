from pygeoip import GeoIP  # pygeoip


class rewiredBotPlugin():
    def __init__(self, parent, *args):
        self.parent = parent
        self.defines = "!greet"
        self.greet = 0  # False , "Guests", "All"
        self.parent.librewired.notify("__ClientJoin", self.clientJoined)

    def run(self, *args):
        if not args[0]:
            if not self.greet:
                return "Set to greet no one"
            if self.greet == 'guest':
                return "Set to greet only guests"
            return "Set to greet everyone"
        if args[0].strip().upper() == "OFF":
            self.greet = 0
            return "Okay, i will greet no one from now on!"
        if args[0].strip().upper() == "GUEST":
            self.greet = "guest"
            return "Okay, i will only greet guests from now on!"
        if args[0].strip().upper() == "ALL":
            self.greet = "all"
            return "Okay, i will greet everyone from now on!"
        return "Usage: !greet off/guest/all"

    def clientJoined(self, msg):
        if not self.greet:
            return 0
        if msg[1] == 1 and self.greet:  # this is public chat
            user = self.parent.librewired.getUserByID(int(msg[0]))
            if user:
                if user.login != 'guest' and self.greet == "guest":
                    return 0
                greeting = "hi %s." % user.nick
                try:
                    if not user.ip:
                        self.parent.librewired.getUserInfo(user.id)
                    if user.ip:
                        location = 0
                        location = self.get_geolocation(user.ip)
                        if location:
                            greeting = greeting + (" You are connecting from %s" % location)
                except:
                    pass
                self.parent.librewired.sendChat(msg[1], greeting)
        return 1

    def get_geolocation(self, ip, includeCity=0):
        from os.path import exists
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
