import csv
import os
from datetime import date
import shutil


class Plant:
    def __init__(self, dic):
        self.id = str_to_int_or_zero(dic["id"])
        self.name = dic["name"]
        self.descr1 = dic["descr_1"]
        self.descr2 = dic["descr_2"]
        self.waterRecTxt = dic["water_rec_txt"]
        self.fertRecTxt = dic["fert_rec_txt"]
        self.waterRecDays = str_to_int_or_zero(dic["water_rec_days"])
        self.fertRecDays = str_to_int_or_zero(dic["fert_rec_days"])
        self.isActive = parse_bool(dic["is_active"])


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


def list_plants(verbose=False):
    with open('plants/plants.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for plant in reader:
            if parse_bool(plant["is_active"]):
                print_plant(plant, verbose)


def print_plant(plant, verbose):
    print("{id})\t{name}\t[{descr_1}]".format(**plant))
    if verbose:
        print("\t" + plant["descr_2"])
        print("\tRecommended Watering: {water_rec_txt}\t({water_rec_days})".format(**plant))
        print("\tRecommended Fertilizing: {fert_rec_txt}\t({fert_rec_days})".format(**plant))


def next_id():
    highest = 0
    with open('plants/plants.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for plant in reader:
            pid = int(plant["id"])
            if pid > highest:
                highest = pid
    return highest + 1


def parse_bool(b):
    return b.lower() != "false"


def str_to_int_or_zero(str):
    try:
        return int(str)
    except ValueError:
        return 0


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


def add_plants_interactive():
    pid = next_id()
    to_add = []
    done = False
    while not done:
        plant = {"id": pid, "is_active": True}
        plant["name"] = prompt("Name?")
        plant["descr_1"] = prompt("Short description (e.g. genus/species)?")
        plant["descr_2"] = prompt("Additional description?")
        plant["water_rec_txt"] = prompt("Watering recommendations?")
        plant["water_rec_days"] = prompt("Approx watering frequency in days?")
        plant["fert_rec_txt"] = prompt("Fertilizing recommendations?")
        plant["fert_rec_days"] = prompt("Approx fertilizing frequency in days?")
        print("Going to add plant:")
        print_plant(plant, True)
        confirm = prompt("Looks good y/n?")
        if confirm.lower().startswith("y"):
            to_add.append(plant)
            pid += 1
        else:
            print("ok, cancelling that one")
        more = prompt("Add another y/n?")
        done = not more.lower().startswith("y")
    print("Adding {} plants".format(len(to_add)))
    add_plants(to_add)


def get_last_entry(csvfilename, pid):
    entries = get_last_entries(csvfilename, pid, count=1)
    if entries:
        return "{date}\t{notes}".format(**entries[0])
    else:
        return "N/A"


def get_last_water(pid):
    return get_last_entry("water.csv", pid)


def get_last_fert(pid):
    return get_last_entry("fert.csv", pid)


def view_plant(pid):
    with open('plants/plants.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for plant in reader:
            if pid == int(plant["id"]):
                print_plant(plant, True)
    print("Last watering: " + get_last_water(pid))
    print("Last fertilizing: " + get_last_fert(pid))
    print("For this plant, do you want to:")
    while True:
        choice = prompt("View watering history, view fertilizing history, water, fertilize, archive, delete, or return?").lower()
        if choice == "exit" or choice.startswith("return"):
            break
        elif "water" in choice and "history" in choice:
            print_water_history(pid)
        elif "fert" in choice and "history" in choice:
            print_fert_history(pid)
        elif choice.startswith("water"):
            water_plant_interactive(pid)
        elif choice.startswith("fert"):
            fert_plant_interactive(pid)
        elif choice == "archive":
            archive_plant(pid)
            break
        elif choice == "delete":
            delete_plant(pid)
            break


def print_water_history(pid):
    print("Watering history:")
    print_history("water.csv", pid)
    print()


def print_fert_history(pid):
    print("Fertilizing history:")
    print_history("fert.csv", pid)
    print()


def print_history(csvfilename, pid):
    root = 'plants/' + str(pid)
    with open(root + '/' + csvfilename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for entry in reader:
            print("{date}\t{notes}".format(**entry))


def water_plant_interactive(pid):
    new_entry_interactive("water.csv", pid)


def fert_plant_interactive(pid):
    new_entry_interactive("fert.csv", pid)


def new_entry_interactive(csvfilename, pid):
    entry_date = select_date()
    notes = prompt("Any notes?")
    new_entry(csvfilename, pid, entry_date, notes)


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
    confirm = prompt("Are you sure you want to archive plant number " + str(pid) + "?").lower()
    if confirm.startswith("y"):
        remove_plant_in_list(pid, False)
        shutil.move('plants/' + str(pid), 'plants/archive/' + str(pid))
        print("plant was archived - to unarchive, dig through the files manually lol")


def delete_plant(pid):
    confirm = prompt("Are you sure you want to permanently delete plant number " + str(pid) + "?").lower()
    if confirm.startswith("y"):
        remove_plant_in_list(pid, True)
        shutil.rmtree('plants/' + str(pid))
        print("plant was deleted - I can only assume you killed it. RIP.")


def remove_plant_in_list(pid, perma_delete):
    with open('plants/plants.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        with open('plants/plants_temp.csv', 'w', newline='') as tempfile:
            writer = csv.DictWriter(tempfile, fieldnames=reader.fieldnames)
            writer.writeheader()
            for plant in reader:
                if int(plant["id"]) == pid:
                    if not perma_delete:
                        plant["is_active"] = False
                        writer.writerow(plant)
                else:
                    writer.writerow(plant)
    shutil.move('plants/plants_temp.csv', 'plants/plants.csv')


def select_date():
    while True:
        datetxt = prompt("Choose date (YYYY-MM-DD)? (leave blank if today)")
        if not datetxt:
            return date.today().isoformat()
        try:
            return date.fromisoformat(datetxt).isoformat()
        except ValueError:
            print("Invalid date. Either enter a valid date in YYYY-MM-DD format or just hit enter to indicate today.")


def parse_date(str):
    try:
        return date.fromisoformat(str)
    except ValueError:
        return None


def prompt(text):
    print(text)
    return input("> ")


def id_from_choice(choice):
    return str_to_int_or_zero(choice.split()[-1])


def id_from_choice_or_prompt(choice):
    pid = id_from_choice(choice)
    if pid <= 0:
        pid = str_to_int_or_zero(prompt("Which plant (numeric id)?"))
    found = False
    with open('plants/plants.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for plant in reader:
            if pid == int(plant["id"]) and parse_bool(plant["is_active"]):
                found = True
    if found:
        return pid
    else:
        print("No plant found with that id")
        return 0


def interactive():
    print("Welcome to Daniel's Plants - the command-line interface")
    while True:
        choice = prompt("What to do? List plants, view plant, add plant(s), water a plant, fertilize a plant, exit?").lower()
        if choice == "exit":
            break
        elif choice.startswith("list"):
            verb = prompt("Verbose y/n?")
            if verb.lower().startswith("y"):
                list_plants(True)
            else:
                list_plants()
        elif choice.startswith("add"):
            add_plants_interactive()
        elif choice.startswith("view"):
            pid = id_from_choice_or_prompt(choice)
            if pid > 0:
                view_plant(pid)
        elif choice.startswith("water"):
            pid = id_from_choice_or_prompt(choice)
            if pid > 0:
                water_plant_interactive(pid)
        elif choice.startswith("fert"):
            pid = id_from_choice_or_prompt(choice)
            if pid > 0:
                fert_plant_interactive(pid)
        else:
            print("wat?")
