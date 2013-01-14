from sqlite3 import connect, Error
from time import sleep, time


class botDB():
    def __init__(self, parent):
        self.parent = parent
        self.config = self.parent.config
        self.dbIsOpen = 0
        self.conn = 0
        self.pointer = 0

    def openDB(self):
        self.conn = connect(self.config['dbFile'])
        self.pointer = self.conn.cursor()
        self.conn.text_factory = str
        self.dbIsOpen = 1
        # make sure our db's exist
        self.pointer.execute('CREATE TABLE IF NOT EXISTS downloads (transferkey TEXT UNIQUE PRIMARY KEY,\
                            nick TEXT, account TEXT, started REAL, finished REAL, filename TEXT, path TEXT,\
                            dlcount INTEGER, bytesdone TEXT, bytestotal TEXT)')
        self.pointer.execute('CREATE TABLE IF NOT EXISTS uploads (transferkey TEXT UNIQUE PRIMARY KEY, nick TEXT,\
                            account TEXT, started REAL, finished REAL, filename TEXT, path TEXT, ulcount INTEGER,\
                            bytesdone TEXT, bytestotal TEXT)')
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
            return 0
        try:
            self.pointer.execute("INSERT INTO chatlog VALUES (?, ?, ?, ?, ?);", [data['date'], data['type'],\
                                data['user'], data['nick'], data['data']])
        except Error, KeyError:
            print "Failed to add event to db"
            return 0
        return 1

    def addTransfer(self, type, data):
        if not self.dbIsOpen:
            return 0
        db = "downloads"
        if type:
            db = "uploads"
        if len(data) != 8:
            print "Invalid value count in addDB"
            return 0
        count = 0
        key = data['nick'] + chr(28) + data['account'] + chr(28) + data['path'] + chr(28) + data['filename']
        if int(data['bytestotal']) == int(data['bytesdone']):
            # this transfer is complete - lets check if it was transfered before
            data['finished'] = time()
            check = self.getTransferByKey(type, key)
            if check:
                try:
                    count = int(check[0][7])
                    count = count + 1
                except IndexError:
                    count = 1
            else:
                count = 1
        try:
            self.pointer.execute("INSERT OR REPLACE INTO " + db + " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",\
                                [key, data['nick'], data['account'], data['started'], data['finished'],\
                                data['filename'], data['path'], count, data['bytesdone'], data['bytestotal']])
            self.conn.commit()
        except Error:
            return 0
        return 1

    def getTransferByKey(self, type, key):
        if not self.dbIsOpen:
            return 0
        db = "downloads"
        if type:
            db = "uploads"
        try:
            self.pointer.execute("SELECT * FROM " + db + " WHERE transferkey = ?;", [key])
            existing = self.pointer.fetchall()
        except Error:
            print "Errot getByKey"
            return 0
        return existing
