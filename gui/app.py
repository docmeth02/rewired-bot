import Tkinter as tk
import ttk as ttk
import tkMessageBox
import sys
import Queue
import threading
import time
import subprocess
import logging
from os import sep
from platform import python_version, system
from includes import rewiredbot
from gui import guifunctions


class ThreadedApp:
    def __init__(self, master):
        self.lock = threading.Lock()
        self.master = master
        self.queue = Queue.Queue()
        self.gui = gui(self, master, self.queue)
        self.master.createcommand('exit', self.shutdownApp)  # osx
        self.master.protocol('exit', self.shutdownApp)  # osx too
        self.master.protocol('WM_DELETE_WINDOW', self.shutdownApp)
        self.monitor = threading.Timer(.2, self.monitorBot)
        self.monitor.start()
        self.running = 1
        self.botInstance = 0
        self.botthread = 0
        if self.gui.autoconnect.get():
            self.startBot()
        self.checkQueue()

    def checkQueue(self):
        self.gui.processIncoming()
        if not self.running:
            sys.exit(1)
        self.master.after(250, self.checkQueue)
        return 1

    def shutdownApp(self):
        self.monitor.cancel()
        if self.botInstance:
            self.botInstance.librewired.keepalive = 0
        self.running = 0

    def startBot(self):
        if self.botInstance:
            return 0
        self.gui.config['server'] = self.gui.server.get()
        self.gui.config['username'] = self.gui.username.get()
        self.gui.config['password'] = self.gui.passw.get()
        guifunctions.rewriteConfig(self.gui.config)
        self.botthread = threading.Thread(target=self.spawnBot)
        self.botthread.start()

    def spawnBot(self):
        self.botInstance = rewiredbot.rewiredbot(False, True, self.gui.configFile, self.errorCallback)
        self.botInstance.run()

    def stopBot(self):
        if self.botInstance:
            self.botInstance.librewired.keepalive = 0
            self.botthread.join(2)
        self.botthread = 0
        self.botInstance = 0
        return 1

    def monitorBot(self):
        self.monitor = threading.Timer(1, self.monitorBot)
        self.monitor.start()
        if not self.botInstance:
            self.displayStopped()
            return 0
        if not self.botInstance.librewired.keepalive:
            self.displayStopped()
            self.stopBot()
            return 0
        self.displayRunning()
        return 1

    def displayStopped(self):
        self.gui.icon.config(image=self.gui.icon.imageoff)
        self.gui.stopbutton.config(state=tk.DISABLED)
        self.gui.startbutton.config(state=tk.NORMAL)
        self.gui.statuslabel.config(text="re:wired bot is not connected")
        self.gui.indicator.config(text=str(self.gui.platform))
        return 1

    def displayRunning(self):
        self.gui.icon.config(image=self.gui.icon.imageon)
        self.gui.startbutton.config(state=tk.DISABLED)
        self.gui.stopbutton.config(state=tk.NORMAL)
        self.gui.statuslabel.config(text="re:wired bot is running and connected")
        self.gui.indicator.config(text="connected to: " + str(self.gui.config['server']))
        return 1

    def toggleAutoStart(self, *args):
        if self.gui.autoconnect.get():
            guifunctions.setAutoStart(True, self.gui.confDir)
            return 1
        guifunctions.setAutoStart(False, self.gui.confDir)
        return 0

    def errorCallback(self, errtype):
        if errtype == 'CONNECT':
            tkMessageBox.showinfo("Connection Error", "re:wired Bot failed to connect to %s\
                                  Check your server and port settings." % self.gui.config['server'])
            return 0
        if errtype == 'LOGIN':
            tkMessageBox.showinfo("Login failed", "Login for user %s failed.\
                                  Check your username and password." % self.gui.config['username'])
            return 0
        return 1


class gui:
    def __init__(self, parent, root, queue):
        self.parent = parent
        self.root = root
        self.queue = queue
        self.configFile = 0
        self.confDir = 0
        self.config = guifunctions.initConfig(self)
        self.platform = guifunctions.getPlatformString(self)
        self.root.geometry("%dx%d+%d+%d" % (480, 360, 0, 0))
        self.root.minsize(480, 360)
        self.root.maxsize(480, 360)
        self.root.title('re:wired Bot')
        self.root.createcommand('tkAboutDialog', self.showabout)  # replace about dialog on osx
        #self.root.createcommand('::tk::mac::ShowPreferences', prefs)
        self.autoconnect = tk.IntVar()
        self.autoconnect.set(guifunctions.getAutoStart(self.confDir))
        self.menubar = tk.Menu(self.root)
        self.apple = tk.Menu(self.menubar, tearoff=0)
        self.root.config(menu=self.apple)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.parentframe = ttk.Frame(width=480, height=360)
        self.parentframe.place(in_=self.root)
        self.frame = ttk.Frame(width=480, height=360)
        self.frame.place(in_=self.parentframe)
        self.frame.grid(column=0, row=0, sticky=(tk.E + tk.W) + (tk.N + tk.S), pady=15, padx=15)
        self.build()

        self.server.delete(0, tk.END)
        self.server.insert(0, self.config['server'])

        self.port.delete(0, tk.END)
        self.port.insert(0, self.config['port'])

        self.username.delete(0, tk.END)
        self.username.insert(0, self.config['username'])

        self.passw.delete(0, tk.END)
        self.passw.insert(0, self.config['password'])

    def build(self):
        self.frame.columnconfigure(0, weight=0)
        self.frame.columnconfigure(1, weight=1)
        self.frame.columnconfigure(2, weight=1)
        self.frame.columnconfigure(3, weight=0)
        iconimageon = tk.PhotoImage(file="gui/re-wired-bot_on.gif", width=64, height=64)
        iconimageoff = tk.PhotoImage(file="gui/re-wired-bot_off.gif", width=64, height=64)
        self.icon = ttk.Label(self.frame, image=iconimageoff)
        self.icon.imageon = iconimageon
        self.icon.imageoff = iconimageoff
        self.icon.grid(row=0, column=0, rowspan=2, sticky=tk.E, padx=5)
        self.statuslabel = ttk.Label(self.frame, text="re:wired Bot is not connected.",\
                                     font=("Lucida Grande Bold", 15))
        self.statuslabel.grid(row=0, column=1, columnspan=2, sticky=tk.W, padx=15)
        self.indicator = ttk.Label(self.frame, text=str(self.platform),\
                                     font=("Lucida Grande", 12))
        self.indicator.grid(row=1, column=1, columnspan=2, sticky=tk.W, padx=15)
        spacer = ttk.Separator(self.frame)
        spacer.grid(row=2, column=0, columnspan=3, sticky=tk.E + tk.W, pady=12)

        serverlabel = ttk.Label(self.frame, text="Server:")
        serverlabel.grid(row=3, column=0, sticky=tk.E, pady=12)
        self.server = tk.Entry(self.frame)
        self.server.insert(0, "re-wired.info")
        self.server.grid(row=3, column=1, columnspan=2, sticky=tk.W + tk.E)

        portlabel = ttk.Label(self.frame, text="Port:")
        portlabel.grid(row=4, column=0, sticky=tk.E, pady=12)
        self.port = tk.Entry(self.frame)
        self.port.insert(0, "2000")
        self.port.grid(row=4, column=1, columnspan=1, sticky=tk.W + tk.E)

        autoconnect = ttk.Checkbutton(self.frame, text="Connect on startup", variable=self.autoconnect,\
                                      command=self.parent.toggleAutoStart)
        autoconnect.grid(row=4, column=2, sticky=tk.E, pady=5, columnspan=1)

        namelabel = ttk.Label(self.frame, text="Username:")
        namelabel.grid(row=5, column=0, sticky=tk.E, pady=12)
        self.username = tk.Entry(self.frame)
        self.username.insert(0, "guest")
        self.username.grid(row=5, column=1, columnspan=2, sticky=tk.W + tk.E)

        passlabel = ttk.Label(self.frame, text="Password:")
        passlabel.grid(row=6, column=0, sticky=tk.E, pady=12)
        self.passw = tk.Entry(self.frame)
        self.passw.insert(0, "")
        self.passw.config(show="*")
        self.passw.grid(row=6, column=1, columnspan=2, sticky=tk.W + tk.E)

        spacer2 = ttk.Separator(self.frame)
        spacer2.grid(row=8, column=0, columnspan=3, sticky=tk.E + tk.W, pady=12)

        self.startbutton = ttk.Button(self.frame, text='Connect', command=self.parent.startBot)
        self.startbutton.place(x=140, y=300)

        self.stopbutton = ttk.Button(self.frame, text='Stop', command=self.parent.stopBot)
        self.stopbutton.place(x=230, y=300)
        return 1

    def showabout(self):
        self.root.tk.call('tk::mac::standardAboutPanel')
        return 1

    def processIncoming(self):
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)
                self.status.appendLog(msg)
            except Queue.Empty:
                pass
