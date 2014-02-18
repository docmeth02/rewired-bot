from json import dumps, loads
from os.path import exists
from threading import Lock


class simpleStorage():
    def __init__(self, filename='pluginstorage.json'):
        self.data = {}
        self.filename = filename
        self.lock = Lock
        try:
            if exists(filename):
                with open(filename, 'r') as f:
                    jsondata = f.read()
                if jsondata:
                    self.data = loads(jsondata)
            else:
                with open(filename, 'w') as f:
                    pass
        except IOError as e:
            print "Failed to open simpleStorage file %s" % filename
        except Exception as e:
            print e

    def store(self, scope, data):
        #accepts a single dimensional dict that will get stored under scope
        #already existing keys will get updated
        with self.lock():
            if not scope in self.data.keys():
                self.data[scope] = {}
            for akey, avalue in data.items():
                self.data[scope][akey] = avalue
            self.save()
            return 1

    def get(self, scope, key):
        # returns value of key in scope
        # if key is Null all data of scope will be returned
        with self.lock():
            if not scope in self.data.keys():
                return 0
            if not key:
                return self.data[scope]
            try:
                value = self.data[scope][key]
            except Exception:
                return 0
            return value

    def remove(self, scope, key):
        #removes key from scope if it exists
        with self.lock():
            if not scope in self.data.keys():
                return 0
            try:
                del(self.data[scope][key])
            except:
                return 0
            self.save()
            return 1

    def save(self):
        with self.lock():
            try:
                with open(self.filename, 'w') as f:
                    f.write(dumps(self.data))
            except Exception:
                return 0
            return 1

    def exists(self, scope, key):
        with self.lock():
            if not scope in self.data.keys():
                return 0
            if key in self.data[scope].keys():
                return 1
            return 0
