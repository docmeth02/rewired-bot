import Tkinter as tk
import ttk as ttk
import tkMessageBox
import sys
import Queue
import threading
import time
import subprocess
import logging
from tkFileDialog import askopenfilename
from os import sep, path
from PIL import Image, ImageTk
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
        try:
            args = self.queue.get_nowait()
            if args:
                tkMessageBox.showerror(args[0], args[1])
        except:
            pass
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
        self.gui.config['port'] = int(self.gui.port.get())
        self.gui.config['username'] = self.gui.username.get()
        self.gui.config['password'] = self.gui.passw.get()
        self.gui.config['nick'] = self.gui.nick.get()
        self.gui.config['status'] = self.gui.status.get()
        adminuser = guifunctions.configStringToList(self.gui.adminuser.get())
        if len(adminuser) < 1:
            adminuser = ['admin']
        self.gui.config['adminuser'] = adminuser
        self.toggleWidgetState(False)
        guifunctions.rewriteConfig(self.gui, self.gui.config)
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
        self.toggleWidgetState(True)
        return 1

    def toggleWidgetState(self, state):
        if state:
            state = tk.NORMAL
        else:
            state = tk.DISABLED
        self.gui.server.config(state=state)
        self.gui.port.config(state=state)
        self.gui.autoconnectbutton.config(state=state)
        self.gui.adminuser.config(state=state)
        self.gui.username.config(state=state)
        self.gui.passw.config(state=state)
        self.gui.status.config(state=state)
        self.gui.nick.config(state=state)
        self.gui.selecticon.config(state=state)
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
            self.queue.put(["Connection Error", "re:wired Bot failed to connect to %s\n\
                            Check your server and port settings." % self.gui.config['server']])
            return 0
        if errtype == 'LOGIN':
            self.queue.put(["Login failed", "Login for user %s failed.\n\
                            Check your username and password." % self.gui.config['username']])
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
        self.root.geometry("%dx%d+%d+%d" % (480, 380, 0, 0))
        self.root.minsize(480, 380)
        self.root.maxsize(480, 380)
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
        self.parentframe = ttk.Frame(width=480, height=380)
        self.parentframe.place(in_=self.root)
        self.main = ttk.Frame(width=480, height=380)
        self.main.place(in_=self.parentframe)
        self.main.grid(column=0, row=0, sticky=(tk.E + tk.W) + (tk.N + tk.S), pady=0, padx=0)
        self.connection = ttk.Frame(width=480, height=220)
        self.settings = ttk.Frame(width=480, height=220)

        self.build()
        self.notebook = ttk.Notebook(self.main)
        self.notebook.grid(column=0, columnspan=4, row=2,
                           sticky=(tk.E + tk.W) + (tk.N + tk.S), pady=0, padx=0)
        self.notebook.add(self.connection, text="Connection")
        self.notebook.add(self.settings, text="Settings")

        self.server.delete(0, tk.END)
        self.server.insert(0, self.config['server'])

        self.port.delete(0, tk.END)
        self.port.insert(0, self.config['port'])

        self.username.delete(0, tk.END)
        self.username.insert(0, self.config['username'])

        self.adminuser.delete(0, tk.END)
        self.adminuser.insert(0, guifunctions.configListToString(self.config['adminuser']))
        self.passw.delete(0, tk.END)
        self.passw.insert(0, self.config['password'])

        self.status.delete(0, tk.END)
        self.status.insert(0, self.config['status'])

        self.nick.delete(0, tk.END)
        self.nick.insert(0, self.config['nick'])

    def build(self):
        # setup main frame
        self.main.columnconfigure(0, weight=0)
        self.main.columnconfigure(1, weight=1)
        self.main.columnconfigure(2, weight=1)
        self.main.columnconfigure(3, weight=0)
        iconimageon = tk.PhotoImage(file="gui/re-wired-bot_on.gif", width=64, height=64)
        iconimageoff = tk.PhotoImage(file="gui/re-wired-bot_off.gif", width=64, height=64)
        self.icon = ttk.Label(self.main, image=iconimageoff)
        self.icon.imageon = iconimageon
        self.icon.imageoff = iconimageoff
        self.icon.grid(row=0, column=0, rowspan=2, sticky=tk.E, padx=15, pady=15)
        self.statuslabel = ttk.Label(self.main, text="re:wired Bot is not connected.",
                                     font=("Lucida Grande Bold", 15))
        self.statuslabel.grid(row=0, column=1, columnspan=2, sticky=tk.SW)
        self.indicator = ttk.Label(self.main, text=str(self.platform),
                                   font=("Lucida Grande", 12))
        self.indicator.grid(row=1, column=1, columnspan=2, sticky=tk.NW)

        self.startbutton = ttk.Button(self.main, text='Connect', command=self.parent.startBot)
        self.startbutton.place(x=140, y=335)

        self.stopbutton = ttk.Button(self.main, text='Stop', command=self.parent.stopBot)
        self.stopbutton.place(x=230, y=335)

        # connection tab
        self.connection.columnconfigure(0, weight=0)
        self.connection.columnconfigure(1, weight=1)
        self.connection.columnconfigure(2, weight=1)
        self.connection.columnconfigure(3, weight=0)
        serverlabel = ttk.Label(self.connection, text="Server:")
        serverlabel.grid(row=3, column=0, sticky=tk.E, pady=12)
        self.server = tk.Entry(self.connection)
        self.server.insert(0, "re-wired.info")
        self.server.grid(row=3, column=1, columnspan=2, sticky=tk.W + tk.E)

        portlabel = ttk.Label(self.connection, text="Port:")
        portlabel.grid(row=4, column=0, sticky=tk.E, pady=12)
        self.port = tk.Entry(self.connection)
        self.port.insert(0, "2000")
        self.port.grid(row=4, column=1, columnspan=1, sticky=tk.W + tk.E)

        self.autoconnectbutton = ttk.Checkbutton(self.connection, text="Connect on startup", variable=self.autoconnect,
                                                 command=self.parent.toggleAutoStart)
        self.autoconnectbutton.grid(row=4, column=2, sticky=tk.E, pady=5, columnspan=1)

        namelabel = ttk.Label(self.connection, text="Username:")
        namelabel.grid(row=5, column=0, sticky=tk.E, pady=12)

        self.username = tk.Entry(self.connection)
        self.username.insert(0, "guest")
        self.username.grid(row=5, column=1, columnspan=2, sticky=tk.W + tk.E)

        passlabel = ttk.Label(self.connection, text="Password:")
        passlabel.grid(row=6, column=0, sticky=tk.E, pady=12)
        self.passw = tk.Entry(self.connection)
        self.passw.insert(0, "")
        self.passw.config(show="*")
        self.passw.grid(row=6, column=1, columnspan=2, sticky=tk.W + tk.E)

        #settings tab
        self.settings.columnconfigure(0, weight=0)
        self.settings.columnconfigure(1, weight=1)
        self.settings.columnconfigure(2, weight=1)
        self.settings.columnconfigure(3, weight=0)
        nicklabel = ttk.Label(self.settings, text="Nick:")
        nicklabel.grid(row=0, column=0, sticky=tk.E, pady=12)
        self.nick = tk.Entry(self.settings)
        self.nick.insert(0, "re:wired Bot")
        self.nick.grid(row=0, column=1, columnspan=2, sticky=tk.W + tk.E)

        statuslabel = ttk.Label(self.settings, text="Status:")
        statuslabel.grid(row=1, column=0, sticky=tk.E, pady=12)
        self.status = tk.Entry(self.settings)
        self.status.insert(0, "Another re:wired Bot")
        self.status.grid(row=1, column=1, columnspan=2, sticky=tk.W + tk.E)

        adminulabel = ttk.Label(self.settings, text="Admin Users:")
        adminulabel.grid(row=2, column=0, sticky=tk.E, pady=12)

        self.adminuser = tk.Entry(self.settings)
        self.adminuser.grid(row=2, column=1, columnspan=2, sticky=tk.W + tk.E)

        boticonlabel = ttk.Label(self.settings, text="Icon:")
        boticonlabel.grid(row=3, column=0, sticky=tk.E)

        if not path.exists(self.config['icon']):
            self.config['icon'] = 'gui/icon.png'
        self.boticondata = ImageTk.PhotoImage(file=self.config['icon'], width=32, height=32)
        self.boticon = tk.Canvas(self.settings, bd=0, width=32, height=32, highlightthickness=0)
        self.boticon.create_image(16, 16, image=self.boticondata, anchor='c')
        self.boticon.grid(row=3, column=1, sticky=tk.W, padx=0)

        self.selecticon = ttk.Button(self.settings, text="Change", command=self.selecticon)
        self.selecticon.grid(row=3, column=1, sticky=tk.W, padx=40)
        return 1

    def selecticon(self):
        filename = askopenfilename(title='Select Image File', filetypes=[("Image Files",
                                                                          "*.png"), ("PNG", '*.png')])
        if not filename:
            ## aborted
            return 0
        try:
            self.boticondata = ImageTk.PhotoImage(file=filename, width=32, height=32)
        except Exception as e:
            print e
            return 0
        self.config['icon'] = filename
        self.boticon.create_image(16, 16, image=self.boticondata, anchor='c')
        guifunctions.rewriteConfig(self, self.config)
        return 0

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
