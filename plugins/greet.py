from pygeoip import GeoIP  # pygeoip


class rewiredBotPlugin():
    def __init__(self, parent, *args):
        self.parent = parent
        self.defines = "!greet"
        self.greet = False  # False , "Guests", "All"
        self.parent.librewired.notify("__ClientJoin", self.clientJoined)

    def run(*args):
        return 0

    def clientJoined(self, msg):
        if msg[1] == 1 and self.greet:  # this is public chat
            user = self.parent.librewired.getUserByID(int(msg[0]))
            if user:
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
            print "Nope"
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
