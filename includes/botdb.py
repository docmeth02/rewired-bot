from sqlite3 import connect, Error, Row
from time import sleep, time
from itertools import izip


class botDB():
    def __init__(self, parent):
        self.parent = parent
        self.config = self.parent.config
        self.dbIsOpen = 0
        self.conn = 0
        self.pointer = 0

    def openDB(self):
        self.conn = connect(self.config['dbFile'], check_same_thread=False)
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
            self.pointer.execute("INSERT INTO chatlog VALUES (?, ?, ?, ?, ?);", [data['date'], data['type'],\
                                data['user'], data['nick'], data['data']])
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
            self.pointer.execute("SELECT * FROM chatlog WHERE " + str(filtered[0]) + "=? ORDER BY date DESC LIMIT ?", [filtered[1], lines])
        result = []
        while True:
            row = self.pointer.fetchone()
            if row == None:
                break
            result.append(dict(izip(row.keys(), row)))
        if not len(result):
            return 0
        return result
