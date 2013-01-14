from os.path import basename, dirname, join
from time import sleep, time


class transferLogger():
    def __init__(self, parent):
        self.parent = parent
        self.logger = self.parent.logger
        self.lastrun = 0
        self.interval = int(self.parent.config['legacyInterval'])
        self.commitInterval = 60
        self.db = self.parent.db
        self.activeTransfers = {}
        self.nextRun = time() + self.interval
        self.nextCommit = time() + self.commitInterval

    def doLog(self):
        if time() >= self.nextRun:
            if self.parent.librewired.userlist:
                for key, auser in self.parent.librewired.userlist.items():
                    info = self.parent.librewired.getUserInfo(key)
                    if info:
                        self.processUserInfo(info)
                self.nextRun = time() + self.interval

        if time() >= self.nextCommit:
            self.commitRun()
            self.nextCommit = time() + self.commitInterval
        return 1

    def processUserInfo(self, info):
        types = {0: 'downloads', 1: 'uploads'}
        userid = info['user']
        for key, type in types.items():
            if info[type]:
                transfer = self.parseTransfer(info[type])
                for index, atransfer in transfer.items():
                    id = str(userid) + "/" + str(atransfer.filename)
                    if id in self.activeTransfers:
                        self.activeTransfers[id].update(atransfer)
                        if (time() + self.interval) > self.activeTransfers[id].eta:
                            # Transfer will finish within the next interval
                            self.activeTransfers[id].isdone = 1
                            self.activeTransfers[id].bytesdone = self.activeTransfers[id].bytestotal

                    else:
                        # New transfer item
                        atransfer.type = key
                        atransfer.id = userid
                        atransfer.nick = info['nick']
                        atransfer.account = info['login']
                        atransfer.dlcount = 0  # ???
                        self.activeTransfers[id] = atransfer

        return 1

    def parseTransfer(self, data):
        parsed = {}
        for key, atransfer in data.items():
            thistransfer = transfer()
            if len(atransfer) != 4:
                break
            thistransfer.type = type
            thistransfer.started = time()
            thistransfer.filename = basename(atransfer['path'])
            thistransfer.path = dirname(atransfer['path'])
            thistransfer.bytesdone = int(atransfer['transferred'])
            thistransfer.bytestotal = int(atransfer['size'])
            thistransfer.speed = int(atransfer['speed'])
            parsed[key] = thistransfer
        return parsed

    def commitRun(self):
        for key, transfer in self.activeTransfers.items():
            if transfer.committed:
                break  # no update since last run
            if (transfer.lastUpdated + 180) <= time():
                if transfer.percentDone > 99.0:
                    self.activeTransfers[key].bytesdone = self.activeTransfers[key].bytestotal
                    self.activeTransfers[key].committed = 0
                    self.activeTransfers[key].finished = time()
                    self.activeTransfers[key].isdone = 1
                    self.logger.info( "Flagging transfer " + str(key) + "as finished (" + transfer.percentDone + " % done)")

            if not self.db.addTransfer(transfer.type, transfer.pack()):
                # Failed to add this transfer - skip it for now
                break

            self.activeTransfers[key].committed = 1
            if transfer.isdone or (transfer.lastUpdated + 600) <= time():
                self.activeTransfers.pop(key)  # this one is done

        return 1


class transfer():
    def __init__(self):
        self.id = 0
        self.type = None  # 0 == Download, 1 == Upload
        self.nick = 0
        self.account = 0
        self.started = 0
        self.finished = 0
        self.filename = 0
        self.path = 0
        self.bytesdone = 0
        self.bytestotal = 0
        self.speed = 0
        self.eta = 0
        self.percentDone = 0
        # info for db management
        self.isdone = 0
        self.lastUpdated = time()
        self.committed = 0

    def update(self, data):
        if not self.filename == data.filename:
            return 0
        self.bytesdone = data.bytesdone
        self.speed = data.speed
        self.lastUpdated = time()
        self.eta = (time() + float((self.bytestotal - self.bytesdone) / self.speed))
        self.percentDone = (float(self.bytesdone) * 100) / float(self.bytestotal)
        self.committed = 0
        return 1

    def pack(self):
        return {
        'nick': self.nick,
        'account': self.account,
        'started': self.started,
        'finished': self.finished,
        'filename': self.filename,
        'path': self.path,
        'bytesdone': self.bytesdone,
        'bytestotal': self.bytestotal}
