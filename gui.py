import Tkinter as tk
from gui import app

from os import devnull
import sys
root = tk.Tk()
try:
    check = sys.frozen
    sys.stdout = open(devnull, 'w')
    sys.stderr = open(devnull, 'w')
except:
    pass
client = app.ThreadedApp(root)
root.mainloop()
