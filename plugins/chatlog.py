from sqlite3 import connect, Error, Row
from time import sleep, time
from itertools import izip
import datetime


class rewiredBotPlugin():
    """chatlogger for re:wired bot"""
    def __init__(self, parent, *args):
        self.parent = parent
        self.db = chatlogDB(self.parent)
        self.defines = "!chatlog"
        self.privs = {'!chatlog': 1}
        if self.parent.storage.exists('plugin.chatlog', 'enabled'):
            self.enabled = int(self.parent.storage.get('plugin.chatlog', 'enabled'))
        else:
            self.enabled = 0
            self.parent.storage.store('plugin.chatlog', {'enabled': self.enabled})
        self.logger = self.parent.logger

        self.buffer = []
        self.commitInterval = 10  # commit new data to db every minute
        self.nextCommit = (time() + self.commitInterval)

        self.parent.librewired.subscribe(300, self.logChat)
        self.parent.librewired.subscribe(301, self.logChat)
        self.parent.librewired.notify("__ClientJoin", self.logClientJoined)
        self.parent.librewired.notify("__ClientLeave", self.logClientLeft)
        self.parent.librewired.notify("__ClientKicked", self.logClientKicked)
        self.parent.librewired.notify("__ClientBanned", self.logClientBanned)
        self.parent.pluginshutdowncallbacks.append(self.shutdown)

    def run(self, params, *args):
        """!chatlog: Usage: !chatlog on|off|stats
        Control how bot logs activity in public chat.
        !chatlog on - enable chat log
        !chatlog off - disable all logging
        !chatlog stats - print statistics
        In future versions of the plugin there will be a command
        to dump the log into a file and get statistics on users.
        ___"""
        command = self.parent.parse_command(args[0][2])
        if not params:
            return "chatlog is %s" % ['disabled', 'enabled'][self.enabled]
        chat = int(args[0][0])
        parts = str(params).split(" ")
        if len(parts):
            if parts[0].lower() == 'off':
                self.enabled = 0
                self.parent.storage.store('plugin.chatlog', {'enabled': self.enabled})
                return "chatlog disabled"

            if parts[0].lower() == 'on':
                self.enabled = 1
                self.parent.storage.store('plugin.chatlog', {'enabled': self.enabled})
                return "chatlog enabled"

            if parts[0].lower() == 'stats':
                # build stats
                self.db.openDB()
                # lines of chat
                self.db.pointer.execute('SELECT COUNT(*) FROM chatlog WHERE TYPE BETWEEN 1 AND 2;')
                chatcount = self.db.pointer.fetchone()[0]

                self.db.pointer.execute('SELECT COUNT(*) FROM chatlog WHERE TYPE == 3')
                joins = self.db.pointer.fetchone()[0]

                self.db.pointer.execute('SELECT COUNT(*) FROM chatlog WHERE TYPE  == 4')
                leaves = self.db.pointer.fetchone()[0]

                self.db.pointer.execute('SELECT COUNT(*) FROM chatlog WHERE TYPE  == 5')
                kicks = self.db.pointer.fetchone()[0]

                self.db.pointer.execute('SELECT COUNT(*) FROM chatlog WHERE TYPE  == 6')
                bans = self.db.pointer.fetchone()[0]

                self.db.pointer.execute('SELECT date FROM chatlog ORDER BY date ASC LIMIT 1')
                first = self.db.pointer.fetchone()[0]
                first = datetime.datetime.fromtimestamp(int(first)).strftime('%Y-%m-%d %H:%M:%S')

                self.db.pointer.execute('SELECT date FROM chatlog ORDER BY date DESC LIMIT 1')
                last = self.db.pointer.fetchone()[0]
                last = datetime.datetime.fromtimestamp(int(last)).strftime('%Y-%m-%d %H:%M:%S')
                self.db.closeDB()

                stats = ''
                stats += 'Lines of chat logged: %s\n' % chatcount
                stats += 'Unique users: %s\n' % joins
                stats += 'Users left: %s\n' % leaves
                stats += 'Users kicked: %s\n' % kicks
                stats += 'Users banned: %s\n' % bans
                stats += 'Logging since %s\n' % first
                stats += 'Last logged event: %s' % last
                return stats

        return "chatlog Usage: !chatlog off|on|stats (user)"

    def shutdown(self):
        self.logger.info("Shutdown chatlog plugin")
        self.commitData(force=1)

    def logClientJoined(self, msg):
        if self.enabled:
            self.logEvent(3, [msg[1], msg[0]])
            self.commitData()

    def logClientLeft(self, msg, client):
        if self.enabled:
            self.logEvent(4, [msg[1], msg[0]])
            self.commitData()

    def logClientKicked(self, msg):
        if self.enabled:
            self.logEvent(5, [1, msg[0], msg[1], msg[2]])
            self.commitData()

    def logClientBanned(self, msg):
        if self.enabled:
            self.logEvent(6, [1, msg[0], msg[1], msg[2]])
            self.commitData()

    def logActionChat(self, msg):
        if self.enabled:
            self.logEvent(2, msg.msg)
            self.commitData()

    def logChat(self, event):
        if self.enabled:
            self.logEvent(1, event.msg)
            self.commitData()

    def commitData(self, force=0):
        if (time() <= self.nextCommit) and not force:
            return 0
        self.db.openDB()
        try:
            for aevent in self.buffer:
                if not aevent['commited']:
                        self.db.addEvent(aevent)
                        aevent['commited'] = 1
        except Exception as e:
            self.logger.error("chatlog: commitData %s" % e)

        for i in xrange(len(self.buffer) - 1, -1, -1):
            if self.buffer[i]['commited']:
                del self.buffer[i]

        self.db.closeDB()
        self.nextCommit = (time() + self.commitInterval)
        return 1

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


class chatlogDB():
    def __init__(self, parent):
        self.parent = parent
        self.dbIsOpen = 0
        self.conn = 0
        self.pointer = 0

    def openDB(self):
        self.conn = connect('chatlog.db', check_same_thread=True)
        self.conn.row_factory = Row
        self.pointer = self.conn.cursor()
        self.conn.text_factory = str
        self.dbIsOpen = 1
        # make sure our db exist
        self.pointer.execute('CREATE TABLE IF NOT EXISTS chatlog (date REAL PRIMARY KEY, type INTEGER,\
                            user TEXT, nick TEXT, data TEXT)')
        self.conn.commit()
        return 1

    def closeDB(self):
        if not self.dbIsOpen:
            return 0
        self.pointer.execute("VACUUM")
        self.conn.commit()
        self.conn.close()
        self.dbIsOpen = 0
        return 1

    def addEvent(self, data):
        if not self.dbIsOpen:
            self.openDB()
        try:
            self.pointer.execute("INSERT INTO chatlog VALUES (?, ?, ?, ?, ?);",
                                 [data['date'], data['type'], data['user'], data['nick'], data['data']])
            self.conn.commit()
        except Error, KeyError:
            print "Failed to add event to db"
            return 0
        return 1

    def getEvents(self, lines, filtered=None):
        if not self.dbIsOpen:
            self.openDB()
        if not filtered:
            self.pointer.execute("SELECT * FROM chatlog ORDER BY date DESC LIMIT ?", [lines])
        else:
            self.pointer.execute("SELECT * FROM chatlog WHERE " + str(filtered[0]) +
                                 "=? ORDER BY date DESC LIMIT ?", [filtered[1], lines])
        result = []
        while True:
            row = self.pointer.fetchone()
            if row is None:
                break
            result.append(dict(izip(row.keys(), row)))
        if not len(result):
            return 0
        return result
