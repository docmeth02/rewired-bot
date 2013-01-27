from sqlite3 import connect, Error
from os.path import basename, dirname, join
from time import sleep, time, strftime, localtime
from datetime import datetime


class eventLogger():
    def __init__(self, parent):
        self.parent = parent
        self.logger = parent.logger
        self.db = self.parent.db
        self.buffer = []
        self.bufferSize = 100  # keep 100 lines of chat in ram

        self.commitInterval = 60  # commit new data to db every minute
        self.nextCommit = (time() + self.commitInterval)

    def logEvent(self, kind, data):
        # Types: 1:chat, 2:actionchat, 3: lient join, 4:client leave, 5:kick, 6:ban
        if int(data[1]) == self.parent.librewired.id:  # add tunable here
            return 1
        if int(data[0]) != 1:  # we only log events in public chat
            return 0

        data = self.packEvent(kind, data)
        if not data:
            self.logger.error("Failed to pack data for type %s", kind)
            return 0
        data['type'] = kind
        self.buffer.append(data)
        return 1

    def commitData(self):
        if self.nextCommit > time():
            return 1

        for aevent in self.buffer:
            if not aevent['commited']:
                    self.db.openDB()
                    self.db.addEvent(aevent)
                    self.db.closeDB()
                    aevent['commited'] = 1

        while (len(self.buffer) > self.bufferSize):
            self.buffer.pop(0)

        self.nextCommit = (time() + self.commitInterval)
        return 1

    def packEvent(self, kind, data, *args):
        try:
            user = self.parent.librewired.getUserByID(data[1])
            packed = {}
            if kind == 1 or kind == 2:  # chat & actionchat
                packed['data'] = data[2]
            if kind == 3 or kind == 4:  # join & leave
                packed['data'] = None
            if kind == 5 or kind == 6:  # kick & ban
                packed['data'] = self.parent.librewired.getUserNameByID(data[2]) + chr(28) +\
                self.parent.librewired.getNickByID(data[2]) + chr(28) + data[3]  # name,nick,msg
            packed['nick'] = user.nick
            packed['user'] = user.login
            packed['date'] = time()
        except:
            return 0
        packed['commited'] = 0
        return packed

    def unpackEvent(self, data):
        unpacked = ""
        if int(data['type']) == 1:
            date = datetime.fromtimestamp(data['date'])
            unpacked += str(date.strftime("%H:%M")) + " "
            unpacked += str(data['nick']) + ": "
            unpacked += str(data['data'])
        if int(data['type']) == 2:
            date = datetime.fromtimestamp(data['date'])
            unpacked += str(date.strftime("%H:%M")) + " *** "
            unpacked += str(data['nick']) + " "
            unpacked += str(data['data'])
        if int(data['type']) == 3:
            date = datetime.fromtimestamp(data['date'])
            unpacked += str(date.strftime("%H:%M")) + " <<< "
            unpacked += str(data['nick']) + " has joined >>> "
        if int(data['type']) == 4:
            date = datetime.fromtimestamp(data['date'])
            unpacked += str(date.strftime("%H:%M")) + " <<< "
            unpacked += str(data['nick']) + " has left >>> "
        if int(data['type']) == 5:
            additional = data['data'].split(chr(28))
            date = datetime.fromtimestamp(data['date'])
            unpacked += str(date.strftime("%H:%M")) + " <<< "
            unpacked += str(data['nick']) + "(" + data['user'] + ") kicked "
            unpacked += additional[1] + "(" + additional[0] + ")"
            try:
                unpacked += '"' + additional[2] + '"'
            except:
                pass
            unpacked += " >>> "
        if int(data['type']) == 6:
            additional = data['data'].split(chr(28))
            date = datetime.fromtimestamp(data['date'])
            unpacked += str(date.strftime("%H:%M")) + " <<< "
            unpacked += str(data['nick']) + "(" + data['user'] + ") banned "
            unpacked += additional[1] + "(" + additional[0] + ")"
            try:
                unpacked += '"' + additional[2] + '"'
            except:
                pass
            unpacked += " >>> "
        return unpacked
