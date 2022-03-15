import gui_util
from tkinter import *
import dansplants


class AboutWindow(gui_util.PopUpWindow):
    def __init__(self, master, **kwargs):
        gui_util.PopUpWindow.__init__(self, master, **kwargs)
        self.title("About Dansplants")
        Label(self, text="Dansplants", font=("", 14)).grid(row=0, column=0, padx=10, pady=16)
        Label(self, text="Copyright © 2022 Daniel Shapiro").grid(row=1, column=0, padx=10)
        Label(self, text="Version " + dansplants.get_version()).grid(row=2, column=0, padx=10, pady=2)
