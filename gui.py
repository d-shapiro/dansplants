from tkinter import *
from tkinter import ttk
from tkcalendar import *
import dansplants
from datetime import date
from PIL import ImageTk,Image,ImageOps,ImageDraw,ImageChops

# Attributions:
# <div>Default plant icon made by <a href="https://www.flaticon.com/authors/ddara" title="dDara">dDara</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div>
#

STATUS_COLOR_MAX_VAL = 200
STATUS_COLOR_MIN_VAL = 50


def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)


def waterClick(ref, entry_date=date.today(), notes=""):
    pid = ref.plant.id
    dansplants.water_plant(pid, entry_date, notes)

    status_color = get_color(ref.plant.waterRecDays, entry_date)
    colorBar = get_color_bar(ref.frame, status_color)
    lastWater = get_last_water_label(ref.frame, str(entry_date))
    wbstate = DISABLED if date.today() == entry_date else NORMAL
    wb = get_water_button(ref, wbstate)
    place_water_stuff(lastWater, wb, colorBar)


def fertClick(ref, entry_date, notes):
    pid = ref.plant.id
    dansplants.fert_plant(pid, entry_date, notes)

    lastFert = get_last_fert_label(ref.frame, str(entry_date))
    place_fert_stuff(lastFert)


def cancel_entry(win):
    win.destroy()


def submit_entry(ref, win, cal, notes, is_fert):
    entry_date = date.fromisoformat(cal.get_date())
    notes_text = notes.get(1.0, END).strip()
    if is_fert:
        fertClick(ref, entry_date, notes_text)
    else:
        waterClick(ref, entry_date, notes_text)
    win.destroy()


def dialog_click(ref, is_fert):
    verb = "Fertilize" if is_fert else "Water"
    noun = "Fertilization" if is_fert else "Watering"
    entry_win = Toplevel()
    entry_win.title(verb + " " + ref.plant.name)
    entry_win.iconbitmap("assets/icon.ico")
    entry_win.grab_set()

    date_picker_label = Label(entry_win, text=noun + " Date:", font=("", 10, "bold"))
    today = date.today()
    cal = Calendar(entry_win, selectmode="day", year=today.year, month=today.month, day=today.day, date_pattern='yyyy-mm-dd')
    notes_label = Label(entry_win, text="Notes:", font=("", 10, "bold"))
    notes_field = Text(entry_win, width=30, height=5)
    button_frame = Frame(entry_win)
    cancel_button = Button(button_frame, text="Cancel", command=lambda win=entry_win: cancel_entry(win))
    submit_button = Button(button_frame, text="Record " + noun, command=lambda ref=ref, win=entry_win, cal=cal, notes=notes_field, is_fert=is_fert: submit_entry(ref, win, cal, notes, is_fert))

    date_picker_label.grid(row=0, column=0, padx=10, pady=10, sticky=N+E)
    cal.grid(row=0, column=1, padx=10, pady=10)
    notes_label.grid(row=1, column=0, padx=10, pady=10, sticky=N+E)
    notes_field.grid(row=1, column=1, padx=10, pady=10)
    button_frame.grid(row=2, column=0, columnspan=2, pady=10, padx=10)
    cancel_button.grid(row=0, column=0, padx=10)
    submit_button.grid(row=0, column=1, padx=10)


def fert_dialog_click(ref):
    dialog_click(ref, True)


def water_dialog_click(ref):
    dialog_click(ref, False)


def image_in_circle(im):
    im = im.resize((64, 64)).convert("RGBA")
    bigsize = (im.size[0] * 3, im.size[1] * 3)
    border = Image.new('RGBA', bigsize, (0, 0, 0, 255))
    ImageDraw.Draw(border).ellipse((6, 6) + (bigsize[0]-6, bigsize[1]-6), fill=(0,0,0,0))
    border = border.resize(im.size, Image.ANTIALIAS)
    im.paste(border, (0, 0), border)
    mask = Image.new('L', bigsize, 0)
    ImageDraw.Draw(mask).ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(im.size, Image.ANTIALIAS)
    mask = ImageChops.darker(mask, im.split()[-1])
    im.putalpha(mask)
    return im


def get_color(water_rec_days, last_water_date):
    if water_rec_days == 0:
        return "#dbdbdb"
    if last_water_date is None:
        return '#%02x%02x%02x' % (STATUS_COLOR_MAX_VAL, STATUS_COLOR_MIN_VAL, STATUS_COLOR_MIN_VAL)
    days_since = (date.today() - last_water_date).days
    valrange = STATUS_COLOR_MAX_VAL - STATUS_COLOR_MIN_VAL
    rat = days_since/(water_rec_days * 1.5)
    n = rat * 2 * valrange
    red = clamp(STATUS_COLOR_MIN_VAL + n, STATUS_COLOR_MIN_VAL, STATUS_COLOR_MAX_VAL)
    green = clamp(STATUS_COLOR_MAX_VAL + valrange - n, STATUS_COLOR_MIN_VAL, STATUS_COLOR_MAX_VAL)
    return '#%02x%02x%02x' % (int(red), int(green), STATUS_COLOR_MIN_VAL)


def delete_water_records(ref, tree):
    to_delete = []
    for index in tree.selection():
        to_delete.append(int(index))
    dansplants.delete_water_entries(ref.plant.id, to_delete)
    for index in tree.get_children():
        tree.delete(index)
    entries = dansplants.get_last_water_entries(ref.plant.id)
    insert_entries_in_tree(tree, entries)

    last_water_text = entries[-1]['date'] if entries else "_________"
    last_water_date = dansplants.parse_date(last_water_text)
    status_color = get_color(ref.plant.waterRecDays, last_water_date)
    wbstate = DISABLED if date.today() == last_water_date else NORMAL
    color_bar = get_color_bar(ref.frame, status_color)
    last_water = get_last_water_label(ref.frame, last_water_text)
    wb = get_water_button(ref, wbstate)
    place_water_stuff(last_water, wb, color_bar)


def delete_fert_records(ref, tree):
    to_delete = []
    for index in tree.selection():
        to_delete.append(int(index))
    dansplants.delete_fert_entries(ref.plant.id, to_delete)
    for index in tree.get_children():
        tree.delete(index)
    entries = dansplants.get_last_fert_entries(ref.plant.id)
    insert_entries_in_tree(tree, entries)

    last_fert_text = entries[-1]['date'] if entries else "_________"
    last_fert = get_last_fert_label(ref.frame, last_fert_text)
    place_fert_stuff(last_fert)


def open_water_history(ref):
    if ref.plant.id in wh_windows:
        wh_windows[ref.plant.id].destroy()
    hwin = Toplevel()
    hwin.title(ref.plant.name + " Watering History")
    hwin.iconbitmap("assets/icon.ico")
    Label(hwin, text=ref.plant.name + " Watering History", font=("", 12, "bold")).pack()
    entries = dansplants.get_last_water_entries(ref.plant.id)
    wh_windows[ref.plant.id] = hwin
    tree = populate_history(hwin, entries)
    del_button = Button(hwin, text="Delete Selected Records", command=lambda ref=ref, tree=tree: delete_water_records(ref, tree))
    del_button.pack(padx=10, pady=10, anchor=W)


def open_fert_history(ref):
    if ref.plant.id in fh_windows:
        fh_windows[ref.plant.id].destroy()
    hwin = Toplevel()
    hwin.title(ref.plant.name + " Fertilizing History")
    hwin.iconbitmap("assets/icon.ico")
    Label(hwin, text=ref.plant.name + " Fertilizing History", font=("", 12, "bold")).pack()
    entries = dansplants.get_last_fert_entries(ref.plant.id)
    fh_windows[ref.plant.id] = hwin
    tree = populate_history(hwin, entries)
    del_button = Button(hwin, text="Delete Selected Records", command=lambda ref=ref, tree=tree: delete_fert_records(ref, tree))
    del_button.pack(padx=10, pady=10, anchor=W)


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


class Ref:
    def __init__(self, plant, frame):
        self.plant = plant
        self.frame = frame


def get_color_bar(frame, status_color):
    colorBar = Label(frame, bg=status_color, height=1, font=("", 2))
    return colorBar


def get_last_water_label(frame, date_text):
    return Label(frame, text="  Last Watering:  " + date_text + "  ", font=("", 9, "bold"), relief="groove")


def get_last_fert_label(frame, date_text):
    return Label(frame, text="  Last Fertilizing:  " + date_text + "  ", font=("", 9, "bold"), relief="groove")


def get_water_button(ref, state):
    return Button(ref.frame, text="Water", state=state, command=lambda ref=ref: waterClick(ref), bg="#96a2ff", font=("", 8, "bold"))


def get_fert_button(ref, state):
    return Button(ref.frame, text="Fertilize\n...", state=state, command=lambda ref=ref: fert_dialog_click(ref), bg="#cba1ff", font=("", 8, "bold"))


def place_water_stuff(water_label, water_button, color_bar):
    color_bar.grid(row=0, column=1, columnspan=6, sticky=W + E, padx=8)
    water_label.grid(row=1, column=2, columnspan=2, sticky=W+S)
    water_button.grid(row=1, column=4, padx=8, sticky=S)


def place_fert_stuff(fert_label):
    fert_label.grid(row=1, column=5, sticky=W+S)


def get_details_frame(ref, expand_button):
    det_frame = LabelFrame(ref.frame, padx=5)
    Label(det_frame, text="Description:", font=("", 9, "bold")).grid(row=0, column=0, sticky=W)
    Label(det_frame, text="Watering Recommendation:", font=("", 9, "bold")).grid(row=0, column=1, sticky=W)
    Label(det_frame, text="Fertilizing Recommendation:", font=("", 9, "bold")).grid(row=0, column=2, sticky=W)
    descr = Message(det_frame, text=ref.plant.descr2, justify=LEFT, relief="groove", anchor=W, width=270)
    descr.grid(row=1, column=0, padx=10, sticky=W+E+N+S)
    water_rec = Message(det_frame, text=ref.plant.waterRecTxt, justify=LEFT, relief="groove", anchor=W, width=130)
    water_rec.grid(row=1, column=1, padx=10, sticky=W+E+N+S)
    fert_rec = Message(det_frame, text=ref.plant.fertRecTxt, justify=LEFT, relief="groove", anchor=W, width=130)
    fert_rec.grid(row=1, column=2, padx=10, sticky=W+E+N+S)
    collapse_button = Button(det_frame, text="   /\   ", font=("", 7), command=lambda det_frame=det_frame, expand_button=expand_button: collapse(det_frame, expand_button))
    collapse_button.grid(row=2, column=0, columnspan=3)
    det_frame.columnconfigure(0, weight=2)
    det_frame.columnconfigure(1, weight=1)
    det_frame.columnconfigure(2, weight=1)

    return det_frame



def place_expand_button(expand_button):
    expand_button.grid(row=2, column=2, padx=16)


def expand(det_frame, expand_button):
    expand_button.grid_remove()
    det_frame.grid(row=3, column=0, columnspan=7, sticky=W+E)


def collapse(det_frame, expand_button):
    place_expand_button(expand_button)
    det_frame.grid_remove()


def _bound_to_mousewheel(event):
    canvas.bind_all("<MouseWheel>", _on_mousewheel)


def _unbound_to_mousewheel(event):
    canvas.unbind_all("<MouseWheel>")


def _on_mousewheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")


def open_config():
    pass


def open_about():
    pass

dansplants.init()

root = Tk()
root.title("Dansplants")
root.iconbitmap("assets/icon.ico")
root.geometry("900x900")
wh_windows = {}
fh_windows = {}
default_pic = ImageTk.PhotoImage(image_in_circle(Image.open("assets/default_pic.png")))
# necessary for very stupid reasons
pics_list = []

outer_frame = Frame(root)
outer_frame.pack(fill=BOTH, expand=1, padx=6, pady=6)
canvas = Canvas(outer_frame)
canvas.pack(side=LEFT, fill=BOTH, expand=1)
scrollbar = Scrollbar(outer_frame, orient=VERTICAL, command=canvas.yview)
scrollbar.pack(side=RIGHT, fill=Y)

canvas.configure(yscrollcommand=scrollbar.set)
canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

main_frame = Frame(canvas)
canvas.create_window((0, 0), window=main_frame, anchor="nw")

main_frame.bind('<Enter>', _bound_to_mousewheel)
main_frame.bind('<Leave>', _unbound_to_mousewheel)
main_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

i=0
for plant in dansplants.get_plant_list():
    if plant.isActive:
        waters = dansplants.get_last_water_entries(plant.id, 1)
        last_water_text = waters[0]['date'] if waters else "_________"
        ferts = dansplants.get_last_fert_entries(plant.id, 1)
        last_fert_text = ferts[0]['date'] if ferts else "_________"
        last_water_date = dansplants.parse_date(last_water_text)
        last_fert_date = dansplants.parse_date(last_fert_text)
        status_color = get_color(plant.waterRecDays, last_water_date)

        frame = LabelFrame(main_frame)
        frame.columnconfigure(1, weight=1)
        frame.grid(row=i, column=0, sticky=W+E)

        ref = Ref(plant, frame)

        colorBar = get_color_bar(frame, status_color)
        name = Label(frame, text=plant.name, font=("", 11, "bold"))
        descr = Label(frame, text=plant.descr1, font=("", 10, "italic"))
        lastWater = get_last_water_label(frame, last_water_text)
        lastFert = get_last_fert_label(frame, last_fert_text)
        expand_button = Button(frame, text="   \/   ", font=("", 7))
        details_frame = get_details_frame(ref, expand_button)
        expand_button.config(command=lambda det_frame=details_frame, expand_button=expand_button: expand(det_frame, expand_button))
        whbutton = Button(frame, text="History", font=("", 7), command=lambda ref=ref: open_water_history(ref))
        fhbutton = Button(frame, text="History", font=("", 7), command=lambda ref=ref: open_fert_history(ref))
        wbstate = DISABLED if date.today() == last_water_date else NORMAL
        fbstate = NORMAL
        waterButton = get_water_button(ref, wbstate)
        waterDialogButton = Button(ref.frame, text="...", command=lambda ref=ref: water_dialog_click(ref), bg="#96a2ff", font=("", 8, "bold"))
        fertButton = get_fert_button(ref, fbstate)

        pic = default_pic
        try:
            sq_image = Image.open("plants/" + str(plant.id) + "/pic.png")
            pic = ImageTk.PhotoImage(image_in_circle(sq_image))
            pics_list.append(pic)
        except FileNotFoundError:
            pass

        pic_label = Label(frame, image=pic)
        pic_label.grid(row=0, column=0, rowspan=3, padx=4)
        name.grid(row=1, column=1, sticky=W)
        place_water_stuff(lastWater, waterButton, colorBar)
        expand_button.grid(row=2, column=2, padx=16)
        waterDialogButton.grid(row=2, column=4, sticky=N+E+W, padx=8)
        place_fert_stuff(lastFert)
        fertButton.grid(row=1, column=6, rowspan=2, padx=8)
        whbutton.grid(row=2, column=3, padx=16, sticky=E)
        fhbutton.grid(row=2, column=5, padx=16, sticky=E)
        descr.grid(row=2, column=1, sticky=N+W, padx=10)
        i += 1

root.mainloop()