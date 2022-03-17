import csv
import os
import os.path
import shutil
import util


def get_version():
    with open("version") as verfile:
        return verfile.read().strip()


class Plant:
    def __init__(self, dic):
        self.id = util.str_to_int_or_zero(dic["id"])
        self.name = dic["name"]
        self.descr1 = dic["descr_1"]
        self.descr2 = dic["descr_2"]
        self.waterRecTxt = dic["water_rec_txt"]
        self.fertRecTxt = dic["fert_rec_txt"]
        self.waterRecDays = util.str_to_int_or_zero(dic["water_rec_days"])
        self.fertRecDays = util.str_to_int_or_zero(dic["fert_rec_days"])
        self.isActive = util.parse_bool(dic["is_active"])

    def to_dict(self):
        return {"id": self.id, "name": self.name, "descr_1": self.descr1, "descr_2": self.descr2,
                "water_rec_txt": self.waterRecTxt, "fert_rec_txt": self.fertRecTxt,
                "water_rec_days": str(self.waterRecDays),
                "fert_rec_days": str(self.fertRecDays), "is_active": self.isActive}


def get_empty_plant():
    return Plant({"id": "0", "name": "", "descr_1": "", "descr_2": "", "water_rec_txt": "", "fert_rec_txt": "",
                  "water_rec_days": "0", "fert_rec_days": "0", "is_active": "True"})


def init():
    os.makedirs('plants/', exist_ok=True)
    os.makedirs('plants/archive/', exist_ok=True)
    if not os.path.isfile('plants/plants.csv'):
        with open('plants/plants.csv', 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile,
                                    fieldnames=["id", "name", "descr_1", "descr_2", "water_rec_txt", "water_rec_days",
                                                "fert_rec_txt", "fert_rec_days", "is_active"])
            writer.writeheader()


def next_id():
    highest = 0
    with open('plants/plants.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for plant in reader:
            pid = int(plant["id"])
            if pid > highest:
                highest = pid
    return highest + 1


def get_plant_list():
    plantlist = []
    with open('plants/plants.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for plant in reader:
            plantlist.append(Plant(plant))
    return plantlist


def get_last_water_entries(pid, count=0):
    return get_last_entries("water.csv", pid, count=count)


def get_last_fert_entries(pid, count=0):
    return get_last_entries("fert.csv", pid, count=count)


def get_last_entries(csvfilename, pid, count=0):
    root = 'plants/' + str(pid)
    last_entries = []
    with open(root + '/' + csvfilename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for entry in reader:
            last_entries.append(entry)
            if 0 < count < len(last_entries):
                last_entries.pop(0)
    return last_entries


def add_plants(plants):
    with open('plants/plants.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for header in reader:
            break

    with open('plants/plants.csv', 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        for plant in plants:
            init_logs(plant["id"])
            writer.writerow(plant)


def init_logs(pid):
    root = 'plants/' + str(pid)
    os.mkdir(root)

    with open(root + '/water.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["date", "notes", "id"])
        writer.writeheader()

    with open(root + '/fert.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["date", "notes", "id"])
        writer.writeheader()


def new_entry(csvfilename, pid, entry_date, notes):
    root = 'plants/' + str(pid)
    with open(root + '/' + csvfilename, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["date", "notes", "id"])
        writer.writerow({"date": entry_date, "notes": notes, "id": pid})


def delete_water_entries(pid, to_delete):
    delete_entries("water.csv", pid, to_delete)


def delete_fert_entries(pid, to_delete):
    delete_entries("fert.csv", pid, to_delete)


def delete_entries(csvfilename, pid, to_delete):
    root = 'plants/' + str(pid)
    with open(root + '/' + csvfilename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        with open(root + '/temp_' + csvfilename, 'w', newline='') as tempfile:
            writer = csv.DictWriter(tempfile, fieldnames=reader.fieldnames)
            writer.writeheader()
            i=0
            for entry in reader:
                if i not in to_delete:
                    writer.writerow(entry)
                else:
                    to_delete.remove(i)
                i += 1
    shutil.move(root + '/temp_' + csvfilename, root + '/' + csvfilename)


def water_plant(pid, entry_date, notes):
    new_entry("water.csv", pid, entry_date, notes)


def fert_plant(pid, entry_date, notes):
    new_entry("fert.csv", pid, entry_date, notes)


def archive_plant(pid):
    delete_archive_or_restore_in_list(pid, perma_delete=False, restore=False)
    shutil.move('plants/' + str(pid), 'plants/archive/' + str(pid))


def restore_plant(pid):
    delete_archive_or_restore_in_list(pid, perma_delete=False, restore=True)
    shutil.move('plants/archive/' + str(pid), 'plants/' + str(pid))


def delete_plant(pid):
    delete_archive_or_restore_in_list(pid, perma_delete=True, restore=False)
    shutil.rmtree('plants/' + str(pid), ignore_errors=True)
    shutil.rmtree('plants/archive/' + str(pid), ignore_errors=True)


def delete_archive_or_restore_in_list(pid, perma_delete, restore):
    with open('plants/plants.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        with open('plants/plants_temp.csv', 'w', newline='') as tempfile:
            writer = csv.DictWriter(tempfile, fieldnames=reader.fieldnames)
            writer.writeheader()
            for plant in reader:
                if int(plant["id"]) == pid:
                    if not perma_delete:
                        plant["is_active"] = restore
                        writer.writerow(plant)
                else:
                    writer.writerow(plant)
    shutil.move('plants/plants_temp.csv', 'plants/plants.csv')


def update_plant(new_plant_dic):
    with open('plants/plants.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        with open('plants/plants_temp.csv', 'w', newline='') as tempfile:
            writer = csv.DictWriter(tempfile, fieldnames=reader.fieldnames)
            writer.writeheader()
            for plant_dic in reader:
                if plant_dic["id"] == new_plant_dic["id"]:
                    writer.writerow(new_plant_dic)
                else:
                    writer.writerow(plant_dic)
    shutil.move('plants/plants_temp.csv', 'plants/plants.csv')


def set_plant_pic(pid, filepath):
    to_path = "plants/" + str(pid) + "/pic.png"
    shutil.copy(filepath, to_path)
