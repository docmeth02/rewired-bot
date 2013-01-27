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
            return 0
        try:
            self.pointer.execute("INSERT INTO chatlog VALUES (?, ?, ?, ?, ?);", [data['date'], data['type'],\
                                data['user'], data['nick'], data['data']])
        except Error, KeyError:
            print "Failed to add event to db"
            return 0
        return 1
