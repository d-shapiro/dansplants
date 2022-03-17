from tkinter import *
from tkinter import messagebox
import gui_config
import dansplants


class ArchiveWindow(gui_config.PlantListWindow):
    def __init__(self, master, **kwargs):
        gui_config.PlantListWindow.__init__(self, master, **kwargs)
        self.geometry("630x900")
        self.title("Archived Plants")

    def should_display(self, plant):
        return not plant.isActive

    def fill_plant_frame(self, frame, plant):
        gui_config.PlantListWindow.fill_plant_frame(self, frame, plant)
        delete_button = Button(frame, text="Delete Permanently", command=lambda plant=plant: self.delete_clicked(plant),
                               bg="#ff4a4a", font=("", 8, "bold"), padx=4, pady=4)
        restore_button = Button(frame, text="Restore", command=lambda plant=plant: self.restore_clicked(plant),
                                bg="#a2ff96", font=("", 8, "bold"), padx=4, pady=4)
        delete_button.grid(row=0, column=2, rowspan=2, padx=8)
        restore_button.grid(row=0, column=3, rowspan=2, padx=8)

    def delete_clicked(self, plant):
        response = messagebox.askyesno("Are you sure?", "Really delete " + plant.name + "? This cannot be undone.",
                                       parent=self)
        if response:
            dansplants.delete_plant(plant.id)
            self.frames[plant.id].destroy()
            self.id_labels[plant.id].destroy()
            self.frames.pop(plant.id)
            self.id_labels.pop(plant.id)

    def restore_clicked(self, plant):
        dansplants.restore_plant(plant.id)
        self.frames[plant.id].destroy()
        self.id_labels[plant.id].destroy()
        self.frames.pop(plant.id)
        self.id_labels.pop(plant.id)
