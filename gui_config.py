from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import font
from PIL import ImageTk, Image, ImageDraw, ImageChops
import util
import gui_util
import dansplants


class EditWindow(gui_util.PopUpWindow):
    def __init__(self, master, plant, **kwargs):
        gui_util.PopUpWindow.__init__(self, master, **kwargs)
        self.is_new = plant.id == 0
        self.pid = dansplants.next_id() if self.is_new else plant.id
        if self.is_new:
            self.title("Add New Plant")
        else:
            self.title("Edit Plant " + str(self.pid))

        self.new_pic_filename = ""
        self.pics = []
        pic = gui_util.get_default_pic_64() if self.is_new else gui_util.get_plant_pic(self.pid, self.pics,
                                                                                       gui_util.get_default_pic_64(),
                                                                                       size=64)
        pic_label = Label(self, image=pic)
        choose_pic_btn = Button(self, text="Choose new image", command=self.choose_pic)
        name_label = Label(self, text="Name")
        descr1_label = Label(self, text="Short description (e.g. genus/species)")
        descr2_label = Label(self, text="Additional description")
        waterRecText_label = Label(self, text="Watering recommendations")
        waterRecNum_label = Label(self, text="Approximate days between waterings")
        fertRecText_label = Label(self, text="Fertilizing recommendations")
        fertRecNum_label = Label(self, text="Approximate days between fertilizing")
        self.name = Entry(self, width=60)
        self.descr1 = Entry(self, width=60)
        self.descr2 = Text(self, width=45, height=4)
        self.waterRecText = Text(self, width=45, height=4)
        self.waterRecNum = Entry(self, width=8)
        self.fertRecText = Text(self, width=45, height=4)
        self.fertRecNum = Entry(self, width=8)
        if not self.is_new:
            self.name.insert(0, plant.name)
            self.descr1.insert(0, plant.descr1)
            self.descr2.insert(1.0, plant.descr2)
            self.waterRecText.insert(1.0, plant.waterRecTxt)
            self.waterRecNum.insert(0, plant.waterRecDays)
            self.fertRecText.insert(1.0, plant.fertRecTxt)
            self.fertRecNum.insert(0, plant.fertRecDays)

        button_frame = Frame(self)
        cancel_btn = Button(button_frame, text="Cancel", command=self.close)
        submit_btn = Button(button_frame, text="Save", command=self.save_entry)

        pic_label.grid(row=0, column=0, rowspan=2, sticky=E, padx=10, pady=10)
        choose_pic_btn.grid(row=1, column=1, sticky=W, padx=10)
        self.name.grid(row=2, column=1, padx=10, sticky=W)
        name_label.grid(row=2, column=0, padx=10, sticky=E)
        self.descr1.grid(row=3, column=1, padx=10, sticky=W)
        descr1_label.grid(row=3, column=0, padx=10, sticky=E)
        self.descr2.grid(row=4, column=1, padx=10, sticky=W)
        descr2_label.grid(row=4, column=0, padx=10, sticky=E)
        self.waterRecText.grid(row=5, column=1, padx=10, sticky=W)
        waterRecText_label.grid(row=5, column=0, padx=10, sticky=E)
        self.waterRecNum.grid(row=6, column=1, padx=10, sticky=W)
        waterRecNum_label.grid(row=6, column=0, padx=10, sticky=E)
        self.fertRecText.grid(row=7, column=1, padx=10, sticky=W)
        fertRecText_label.grid(row=7, column=0, padx=10, sticky=E)
        self.fertRecNum.grid(row=8, column=1, padx=10, sticky=W)
        fertRecNum_label.grid(row=8, column=0, padx=10, sticky=E)
        button_frame.grid(row=9, column=0, columnspan=2, pady=10, padx=10)
        cancel_btn.grid(row=0, column=0, padx=10)
        submit_btn.grid(row=0, column=1, padx=10)

    def choose_pic(self):
        filename = filedialog.askopenfilename(parent=self, initialdir="/",
                                              title="Select an image file (preferably square)",
                                              filetypes=(("png files", ".png"),))
        if len(filename) > 0:
            sq_image = Image.open(filename)
            pic = ImageTk.PhotoImage(gui_util.image_in_circle(sq_image, 64))
            self.pics.append(pic)
            pic_label = Label(self, image=pic)
            pic_label.grid(row=0, column=0, rowspan=2, sticky=E, padx=10, pady=10)
            self.new_pic_filename = filename

    def save_entry(self):
        name_val = self.name.get().strip()
        descr1_val = self.descr1.get().strip()
        descr2_val = self.descr2.get(1.0, END).strip()
        waterRecText_val = self.waterRecText.get(1.0, END).strip()
        fertRecText_val = self.fertRecText.get(1.0, END).strip()
        waterRecNum_val = self.waterRecNum.get().strip()
        fertRecNum_val = self.fertRecNum.get().strip()

        if len(name_val) <= 0:
            messagebox.showwarning("", "Please enter a name for your plant", parent=self)
        elif len(waterRecNum_val) > 0 and not util.is_nonneg_num(waterRecNum_val):
            messagebox.showwarning("", "Approximate watering interval should be numeric or left blank", parent=self)
        elif len(fertRecNum_val) > 0 and not util.is_nonneg_num(fertRecNum_val):
            messagebox.showwarning("", "Approximate fertilizing interval should be numeric or left blank", parent=self)
        else:
            plant_dic = {"id": str(self.pid), "name": name_val, "descr_1": descr1_val,
                         "descr_2": descr2_val, "water_rec_txt": waterRecText_val, "fert_rec_txt": fertRecText_val,
                         "water_rec_days": waterRecNum_val, "fert_rec_days": fertRecNum_val, "is_active": "True"}
            if self.is_new:
                dansplants.add_plants([plant_dic])
                if len(self.new_pic_filename) > 0:
                    dansplants.set_plant_pic(self.pid, self.new_pic_filename)
                self.master.add_plant_frame(dansplants.Plant(plant_dic))
                self.master.scroll_to_bottom()
            else:
                dansplants.update_plant(plant_dic)
                if len(self.new_pic_filename) > 0:
                    dansplants.set_plant_pic(self.pid, self.new_pic_filename)
                self.master.update_plant_frame(dansplants.Plant(plant_dic))
            self.close()


class ConfigWindow(gui_util.PopUpWindow):
    def __init__(self, master, **kwargs):
        gui_util.PopUpWindow.__init__(self, master, **kwargs)
        self.title("Configure Plants")
        self.geometry("550x900")
        self.pics = []
        self.frames = {}
        self.id_labels = {}
        self.row_num = 0
        self.main_frame, self.canvas = gui_util.setup_scrollable_frame(self)
        for plant in dansplants.get_plant_list():
            if plant.isActive:
                self.add_plant_frame(plant)
        button_frame = Frame(self)
        button_frame.pack(pady=8)
        add_button = Button(button_frame, text="Add New Plant", command=self.add_clicked, bg="#a2ff96",
                            font=("", 8, "bold"), padx=4, pady=4)
        add_button.grid(row=0, column=0, padx=20)
        done_button = Button(button_frame, text="Done", command=self.close, font=("", 8), padx=4, pady=4)
        done_button.grid(row=0, column=1, padx=20)

    def fill_plant_frame(self, frame, plant):
        name = Label(frame, text=plant.name, font=("", 11, "bold"))
        descr_font = font.Font(font=("", 10, "italic"))
        descr = Label(frame, text=util.pad_to_length(descr_font, plant.descr1, 288), font=descr_font)
        edit_button = Button(frame, text="Edit", command=lambda plant=plant: self.edit_clicked(plant), bg="#ffcb96",
                             font=("", 8, "bold"), padx=4, pady=4)
        archive_button = Button(frame, text="Archive", command=lambda plant=plant: self.archive_clicked(plant),
                                bg="#ff96a2", font=("", 8, "bold"), padx=4, pady=4)
        pic = gui_util.get_plant_pic(plant.id, self.pics, gui_util.get_default_pic_32(), size=32)
        pic_label = Label(frame, image=pic)

        pic_label.grid(row=0, column=0, rowspan=2, padx=4)
        name.grid(row=0, column=1, sticky=W)
        descr.grid(row=1, column=1, sticky=N + W, padx=10)
        edit_button.grid(row=0, column=2, rowspan=2, padx=8)
        archive_button.grid(row=0, column=3, rowspan=2, padx=8)

    def update_plant_frame(self, plant):
        self.fill_plant_frame(self.frames[plant.id], plant)

    def add_plant_frame(self, plant):
        id_label = Label(self.main_frame, text=plant.id, font=("", 10, "bold"))
        id_label.grid(row=self.row_num, column=0, sticky=N)
        frame = LabelFrame(self.main_frame)
        frame.columnconfigure(1, weight=1)
        frame.grid(row=self.row_num, column=1, sticky=W + E)
        self.frames[plant.id] = frame
        self.id_labels[plant.id] = id_label
        self.fill_plant_frame(frame, plant)
        self.row_num += 1

    def scroll_to_bottom(self):
        self.canvas.yview_moveto('1.0')

    def edit_clicked(self, plant):
        EditWindow(self, plant).transient(self)

    def add_clicked(self):
        self.edit_clicked(dansplants.get_empty_plant())

    def archive_clicked(self, plant):
        response = messagebox.askyesno("Are you sure?", "Really archive " + plant.name + "?", parent=self)
        if response:
            dansplants.archive_plant(plant.id)
            self.frames[plant.id].destroy()
            self.id_labels[plant.id].destroy()
            self.frames.pop(plant.id)
            self.id_labels.pop(plant.id)

    def close(self, event=None):
        self.master.refresh()
        gui_util.PopUpWindow.close(self, event)
