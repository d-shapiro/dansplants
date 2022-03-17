from tkinter import *
from tkinter import ttk
from tkinter import font
from tkcalendar import *
import webbrowser
import dansplants
import gui_archive
import util
import gui_util
import gui_about
import gui_config
from datetime import date

# Attributions:
# Default plant icon made by <a href="https://www.flaticon.com/authors/ddara" title="dDara">dDara</a>
# from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div>
#


def open_github():
    webbrowser.open_new("https://github.com/d-shapiro/dansplants")


class DetailsFrame(LabelFrame):
    def __init__(self, master, plant, expand_button, **kwargs):
        LabelFrame.__init__(self, master, **kwargs)
        self.expand_button = expand_button
        Label(self, text="Description:", font=("", 9, "bold")).grid(row=0, column=0, sticky=W)
        Label(self, text="Watering Recommendation:", font=("", 9, "bold")).grid(row=0, column=1, sticky=W)
        Label(self, text="Fertilizing Recommendation:", font=("", 9, "bold")).grid(row=0, column=2, sticky=W)
        descr = Message(self, text=plant.descr2, justify=LEFT, relief="groove", anchor=W, width=270)
        descr.grid(row=1, column=0, padx=10, sticky=W + E + N + S)
        water_rec = Message(self, text=plant.waterRecTxt, justify=LEFT, relief="groove", anchor=W, width=130)
        water_rec.grid(row=1, column=1, padx=10, sticky=W + E + N + S)
        fert_rec = Message(self, text=plant.fertRecTxt, justify=LEFT, relief="groove", anchor=W, width=130)
        fert_rec.grid(row=1, column=2, padx=10, sticky=W + E + N + S)
        collapse_button = Button(self, text="   /\   ", font=("", 7), command=self.collapse)
        collapse_button.grid(row=2, column=0, columnspan=3)
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

    def collapse(self):
        self.expand_button.grid(row=2, column=2, padx=16)
        self.grid_remove()

    def expand(self):
        self.expand_button.grid_remove()
        self.grid(row=3, column=0, columnspan=7, sticky=W + E)


def populate_history(hwin, entries):
    tree_frame = Frame(hwin)
    tree_frame.pack(padx=10, pady=10)
    tree_scroll = Scrollbar(tree_frame)
    tree_scroll.pack(side=RIGHT, fill=Y)
    tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set, height=20)
    tree['columns'] = ("Date", "Notes")
    tree.column("#0", width=0, stretch=NO)
    tree.column("Date", width=100)
    tree.column("Notes", width=400)
    tree.heading("Date", text="Date", anchor=W)
    tree.heading("Notes", text="Notes", anchor=W)

    insert_entries_in_tree(tree, entries)

    tree.pack()
    tree_scroll.config(command=tree.yview)
    return tree


def insert_entries_in_tree(tree, entries):
    i = 0
    for entry in entries:
        tree.insert(parent='', index='end', iid=i, values=(entry["date"], entry["notes"]))
        i += 1
    if i > 0:
        tree.see(i - 1)


class PlantFrame(LabelFrame):
    def __init__(self, master, mainwin, plant, **kwargs):
        LabelFrame.__init__(self, master, **kwargs)
        self.plant = plant
        self.mainwin = mainwin
        self.columnconfigure(1, weight=1)

    def open_water_history(self):
        hwin = self.mainwin.new_wh_window(self.plant.id)
        hwin.title(self.plant.name + " Watering History")
        hwin.iconbitmap("assets/icon.ico")
        Label(hwin, text=self.plant.name + " Watering History", font=("", 12, "bold")).pack()
        entries = dansplants.get_last_water_entries(self.plant.id)
        tree = populate_history(hwin, entries)
        del_button = Button(hwin, text="Delete Selected Records",
                            command=lambda tree=tree: self.delete_water_records(tree))
        del_button.pack(padx=10, pady=10, anchor=W)

    def open_fert_history(self):
        hwin = self.mainwin.new_fh_window(self.plant.id)
        hwin.title(self.plant.name + " Fertilizing History")
        hwin.iconbitmap("assets/icon.ico")
        Label(hwin, text=self.plant.name + " Fertilizing History", font=("", 12, "bold")).pack()
        entries = dansplants.get_last_fert_entries(self.plant.id)
        tree = populate_history(hwin, entries)
        del_button = Button(hwin, text="Delete Selected Records",
                            command=lambda tree=tree: self.delete_fert_records(tree))
        del_button.pack(padx=10, pady=10, anchor=W)

    def delete_water_records(self, tree):
        to_delete = []
        for index in tree.selection():
            to_delete.append(int(index))
        dansplants.delete_water_entries(self.plant.id, to_delete)
        for index in tree.get_children():
            tree.delete(index)
        entries = dansplants.get_last_water_entries(self.plant.id)
        insert_entries_in_tree(tree, entries)

        last_water_text = entries[-1]['date'] if entries else "_________"
        last_water_date = util.parse_date(last_water_text)
        status_color = gui_util.get_color(self.plant.waterRecDays, last_water_date)
        wbstate = DISABLED if date.today() == last_water_date else NORMAL
        color_bar = self.get_color_bar(status_color)
        last_water = self.get_last_water_label(last_water_text)
        wb = self.get_water_button(wbstate)
        place_water_stuff(last_water, wb, color_bar)

    def delete_fert_records(self, tree):
        to_delete = []
        for index in tree.selection():
            to_delete.append(int(index))
        dansplants.delete_fert_entries(self.plant.id, to_delete)
        for index in tree.get_children():
            tree.delete(index)
        entries = dansplants.get_last_fert_entries(self.plant.id)
        insert_entries_in_tree(tree, entries)

        last_fert_text = entries[-1]['date'] if entries else "_________"
        last_fert = self.get_last_fert_label(last_fert_text)
        place_fert_stuff(last_fert)

    def get_color_bar(self, status_color):
        colorBar = Label(self, bg=status_color, height=1, font=("", 2))
        return colorBar

    def get_last_water_label(self, date_text):
        return Label(self, text="  Last Watering:  " + date_text + "  ", font=("", 9, "bold"), relief="groove")

    def get_last_fert_label(self, date_text):
        return Label(self, text="  Last Fertilizing:  " + date_text + "  ", font=("", 9, "bold"), relief="groove")

    def get_water_button(self, state):
        return Button(self, text="Water", state=state, command=self.waterClick, bg="#96a2ff", font=("", 8, "bold"))

    def get_fert_button(self, state):
        return Button(self, text="Fertilize\n...", state=state, command=self.fert_dialog_click, bg="#cba1ff",
                      font=("", 8, "bold"))

    def waterClick(self, entry_date=date.today(), notes=""):
        pid = self.plant.id
        dansplants.water_plant(pid, entry_date, notes)

        status_color = gui_util.get_color(self.plant.waterRecDays, entry_date)
        colorBar = self.get_color_bar(status_color)
        lastWater = self.get_last_water_label(str(entry_date))
        wbstate = DISABLED if date.today() == entry_date else NORMAL
        wb = self.get_water_button(wbstate)
        place_water_stuff(lastWater, wb, colorBar)

    def fertClick(self, entry_date, notes):
        pid = self.plant.id
        dansplants.fert_plant(pid, entry_date, notes)

        lastFert = self.get_last_fert_label(str(entry_date))
        place_fert_stuff(lastFert)

    def dialog_click(self, is_fert):
        verb = "Fertilize" if is_fert else "Water"
        noun = "Fertilization" if is_fert else "Watering"
        entry_win = Toplevel()
        entry_win.title(verb + " " + self.plant.name)
        entry_win.iconbitmap("assets/icon.ico")
        entry_win.grab_set()

        date_picker_label = Label(entry_win, text=noun + " Date:", font=("", 10, "bold"))
        today = date.today()
        cal = Calendar(entry_win, selectmode="day", year=today.year, month=today.month, day=today.day,
                       date_pattern='yyyy-mm-dd')
        notes_label = Label(entry_win, text="Notes:", font=("", 10, "bold"))
        notes_field = Text(entry_win, width=30, height=5)
        button_frame = Frame(entry_win)
        cancel_button = Button(button_frame, text="Cancel", command=entry_win.destroy)
        submit_button = Button(button_frame, text="Record " + noun,
                               command=lambda win=entry_win, cal=cal, notes=notes_field,
                                              is_fert=is_fert: self.submit_entry(win, cal, notes, is_fert))
        date_picker_label.grid(row=0, column=0, padx=10, pady=10, sticky=N + E)
        cal.grid(row=0, column=1, padx=10, pady=10)
        notes_label.grid(row=1, column=0, padx=10, pady=10, sticky=N + E)
        notes_field.grid(row=1, column=1, padx=10, pady=10)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10, padx=10)
        cancel_button.grid(row=0, column=0, padx=10)
        submit_button.grid(row=0, column=1, padx=10)

    def fert_dialog_click(self):
        self.dialog_click(True)

    def water_dialog_click(self):
        self.dialog_click(False)

    def submit_entry(self, win, cal, notes, is_fert):
        entry_date = date.fromisoformat(cal.get_date())
        notes_text = notes.get(1.0, END).strip()
        if is_fert:
            self.fertClick(entry_date, notes_text)
        else:
            self.waterClick(entry_date, notes_text)
        win.destroy()

    def get_details_frame(self, expand_button):
        return DetailsFrame(self, self.plant, expand_button, padx=5)


def place_water_stuff(water_label, water_button, color_bar):
    color_bar.grid(row=0, column=1, columnspan=6, sticky=W + E, padx=8)
    water_label.grid(row=1, column=2, columnspan=2, sticky=W+S)
    water_button.grid(row=1, column=4, padx=8, sticky=S)


def place_fert_stuff(fert_label):
    fert_label.grid(row=1, column=5, sticky=W+S)


class MainWindow(Tk):
    def __init__(self, **kwargs):
        Tk.__init__(self, **kwargs)
        self.title("Dansplants")
        self.iconbitmap("assets/icon.ico")
        self.geometry("900x900")
        self.wh_windows = {}
        self.fh_windows = {}
        # necessary for very stupid reasons
        self.PICS_LIST = []

    def open_config(self):
        gui_config.ConfigWindow(self).transient(self)

    def open_archive(self):
        gui_archive.ArchiveWindow(self).transient(self)

    def open_about(self):
        gui_about.AboutWindow(self).transient(self)

    def new_wh_window(self, pid):
        if pid in self.wh_windows:
            self.wh_windows[pid].destroy()
        hwin = Toplevel()
        self.wh_windows[pid] = hwin
        return hwin

    def new_fh_window(self, pid):
        if pid in self.fh_windows:
            self.fh_windows[pid].destroy()
        hwin = Toplevel()
        self.fh_windows[pid] = hwin
        return hwin

    def refresh(self):
        self.PICS_LIST = []
        for widget in self.winfo_children():
            widget.destroy()
        self.init()

    def init_menubar(self):
        menubar = Menu(self)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Configure Plants", command=self.open_config)
        filemenu.add_command(label="View Archive", command=self.open_archive)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Github", command=open_github)
        helpmenu.add_command(label="About", command=self.open_about)
        menubar.add_cascade(label="Help", menu=helpmenu)

        self.config(menu=menubar)

    def init(self):
        self.init_menubar()

        main_frame, canvas = gui_util.setup_scrollable_frame(self)
        i = 0
        for plant in dansplants.get_plant_list():
            if plant.isActive:
                waters = dansplants.get_last_water_entries(plant.id, 1)
                last_water_text = waters[0]['date'] if waters else "_________"
                ferts = dansplants.get_last_fert_entries(plant.id, 1)
                last_fert_text = ferts[0]['date'] if ferts else "_________"
                last_water_date = util.parse_date(last_water_text)
                status_color = gui_util.get_color(plant.waterRecDays, last_water_date)

                frame = PlantFrame(main_frame, self, plant)
                frame.grid(row=i, column=0, sticky=W + E)

                colorBar = frame.get_color_bar(status_color)
                name = Label(frame, text=plant.name, font=("", 11, "bold"))
                descr_font = font.Font(font=("", 10, "italic"))
                descr = Label(frame, text=util.pad_to_length(descr_font, plant.descr1, 288), font=descr_font)
                lastWater = frame.get_last_water_label(last_water_text)
                lastFert = frame.get_last_fert_label(last_fert_text)
                expand_button = Button(frame, text="   \/   ", font=("", 7))
                details_frame = frame.get_details_frame(expand_button)
                expand_button.config(command=details_frame.expand)
                whbutton = Button(frame, text="History", font=("", 7), command=frame.open_water_history)
                fhbutton = Button(frame, text="History", font=("", 7), command=frame.open_fert_history)
                wbstate = DISABLED if date.today() == last_water_date else NORMAL
                fbstate = NORMAL
                waterButton = frame.get_water_button(wbstate)
                waterDialogButton = Button(frame, text="...", command=frame.water_dialog_click, bg="#96a2ff",
                                           font=("", 8, "bold"))
                fertButton = frame.get_fert_button(fbstate)

                pic = gui_util.get_plant_pic(plant.id, self.PICS_LIST, gui_util.get_default_pic_64())

                pic_label = Label(frame, image=pic)
                pic_label.grid(row=0, column=0, rowspan=3, padx=4)
                name.grid(row=1, column=1, sticky=W)
                place_water_stuff(lastWater, waterButton, colorBar)
                expand_button.grid(row=2, column=2, padx=16)
                waterDialogButton.grid(row=2, column=4, sticky=N + E + W, padx=8)
                place_fert_stuff(lastFert)
                fertButton.grid(row=1, column=6, rowspan=2, padx=8)
                whbutton.grid(row=2, column=3, padx=16, sticky=E)
                fhbutton.grid(row=2, column=5, padx=16, sticky=E)
                descr.grid(row=2, column=1, sticky=N + W, padx=10)
                i += 1
        self.lift()


dansplants.init()
root = MainWindow()
root.init()
root.mainloop()
