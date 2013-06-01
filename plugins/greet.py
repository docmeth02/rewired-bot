# -*- coding: UTF-8 -*-
from pygeoip import GeoIP  # pygeoip
from os.path import exists
from time import time
from time import sleep
from datetime import datetime
from random import choice
import json
import pytz  # python-tz


class rewiredBotPlugin():
    def __init__(self, parent, *args):
        self.parent = parent
        self.defines = ["!greet", "!moo"]
        self.privs = {'!greet': 50, "!moo": 1}
        self.parent.librewired.notify("__ClientLeave", self.clientleave)
        self.defaultbrain = {
            'locales': {
                'en':
                {'greetings':
                ['Welcome %NICK%. You are connecting from %LOCATION%',
                'Good %TIMEOFDAY% %NICK%. You are connecting from %LOCATION%',
                '%TIMEOFDAY% %NICK%',
                'Yo %NICK%'],
                'timeofday':
                    ['morning', 'day', 'afternoon']
                 },
                'se':
                {'greetings':
                    ['Hallå %NICK%',
                        'God %TIMEOFDAY% %NICK%',
                        'Välkommen %NICK%, du loggar in här ifrån %LOCATION%.'],
                    'timeofday':
                    ['morgon', 'dag', 'eftermiddag'],
                    'country': 'Sverige'
                 },
                'de':
                {'greetings':
                    ['Guten %TIMEOFDAY% %NICK%. Du kommst aus %LOCATION%',
                     'Hi %NICK%. Gruss nach %LOCATION%',
                     '%TIMEOFDAY% %NICK%'],
                'timeofday':
                    ['Morgen', 'Mittag', 'Abend'],
                'country': 'Deutschland'
                 },

                'it':
                {'greetings':
                    ['Ciao utente %NICK%. Sembra che tu ti stia collegando dall\'%LOCATION%.']
                 },
                'default':
                ['Hi %NICK%', 'Welcome %NICK%', 'Nice to see you %NICK%']
            }
        }

        if exists('greetings.json'):
            with open('greetings.json', 'r') as f:
                try:
                    self.brain = json.loads(f.read())
                except:
                    self.parent.logger.error("greet: Failed to load greetings from file. Check your syntax")
                    self.brain = self.defaultbrain
        else:
            with open('greetings.json', 'w') as f:
                self.parent.logger.info("greet: Saved default greetings to config file")
                f.write(json.dumps(self.defaultbrain))
                self.brain = self.defaultbrain
        self.greet = False  # False , "Guests", "All"
        self.parent.librewired.notify("__ClientJoin", self.clientJoined)

    def run(self, *args):
        command = self.parent.parse_command(args[1][2])
        if command.upper() == "MOO":
            try:
                userid = int(args[0].strip())
            except:
                userid = 0
            if userid:
                self.clientJoined([userid, int(args[1][0])])
            else:
                self.clientJoined([int(args[1][1]), int(args[1][0])])
            return 0

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
        if not self.greet or msg[1] != 1:  # set to not greet or not public chat
            return 0

        user = self.parent.librewired.getUserByID(int(msg[0]))
        if not user or (user.login != 'guest' and self.greet == "guest"):  # failed to find user or not greet guests
            return 0
        geodata = self.get_geolocation(user)
        greetings = self.brain['locales']['en']  # default to english
        try:
            if geodata['country_code'].lower() in self.brain['locales']:  # check for available locale greetings
                greetings = self.brain['locales'][geodata['country_code'].lower()]
            greeting = self.parseString(user, greetings, geodata)
        except:
            try:
                greeting = choice(self.brain['locales']['default'])
                greeting = greeting.replace('%NICK%', user.nick)
            except Exception as e:
                print e
                greeting = "HI " + str(user.nick)
        if greeting:
            sleep(0.25)
            try:
                greeting = greeting.encode("UTF-8")
            except:
                print "UTF-8 conversion failed"
                pass
            self.parent.librewired.sendChat(msg[1], greeting)
        return 0

    def parseString(self, user, greetings, geodata):
        greeting = greetings['greetings'][0]
        if len(greetings['greetings']) > 1:
            greeting = choice(greetings['greetings'])
        greeting = greeting.replace('%NICK%', user.nick)
        if 'country' in greetings:
            greeting = greeting.replace('%LOCATION%', greetings['country'])
        else:
            greeting = greeting.replace('%LOCATION%', geodata['country_name'])
        greeting = greeting.replace('%CITY%', geodata['city'])
        hour = int(datetime.fromtimestamp(time()).strftime('%H'))
        try:
            hour = int(datetime.now(pytz.timezone(geodata['time_zone'])).strftime('%H'))
        except:
            pass
        timeofday = greetings['timeofday'][self.getTimeOfDay(hour)]
        greeting = greeting.replace('%TIMEOFDAY%', timeofday)
        return greeting

    def get_geolocation(self, user):
        if not user.ip:
            self.parent.librewired.getUserInfo(user.id)
        if not user.ip:
            return 0
        from os.path import exists
        dbpath = "GeoLiteCity.dat"
        if not exists(dbpath):
            return 0
        location = 0
        gloc = GeoIP(dbpath)
        data = gloc.record_by_addr(user.ip)
        try:
            geodata = {
                'city': data['city'].encode("utf-8"),
                'country_code': data['country_code'].encode("utf-8"),
                'country_name': data['country_name'].encode("utf-8"),
                'time_zone': data['time_zone'].encode("utf-8"),
            }
        except:
            return 0
        return geodata

    def clientleave(self, *args):
        #([534, 1], {'nick': 'docmeth02', 'user': 'guest'})
        msg = "I never liked %s anyway" % args[1]['nick']
        #self.parent.librewired.sendChat(args[0][1], msg)
        return 0

    def getTimeOfDay(self, hour):
        # 0-12 = (0)morning, 12-17 = (1)noon, 17-0 = (2)evening
        #hour = int(datetime.fromtimestamp(localtime).strftime('%H'))
        if hour in range(0, 12):
            return 0
        if hour in range(12, 17):
            return 1
        return 2
