from tkinter import *
from PIL import ImageTk, Image, ImageDraw, ImageChops
from datetime import date
import util

STATUS_COLOR_MAX_VAL = 200
STATUS_COLOR_MIN_VAL = 50

DEFAULT_PIC_64 = None
DEFAULT_PIC_32 = None


def get_default_pic_64():
    global DEFAULT_PIC_64
    if DEFAULT_PIC_64 is None:
        DEFAULT_PIC_64 = ImageTk.PhotoImage(image_in_circle(Image.open("assets/default_pic.png")))
    return DEFAULT_PIC_64


def get_default_pic_32():
    global DEFAULT_PIC_32
    if DEFAULT_PIC_32 is None:
        DEFAULT_PIC_32 = ImageTk.PhotoImage(image_in_circle(Image.open("assets/default_pic.png"), size=32))
    return DEFAULT_PIC_32


def image_in_circle(im, size=64):
    im = im.resize((size, size)).convert("RGBA")
    bigsize = (im.size[0] * 3, im.size[1] * 3)
    border = Image.new('RGBA', bigsize, (0, 0, 0, 255))
    ImageDraw.Draw(border).ellipse((6, 6) + (bigsize[0]-6, bigsize[1]-6), fill=(0, 0, 0, 0))
    border = border.resize(im.size, Image.ANTIALIAS)
    im.paste(border, (0, 0), border)
    mask = Image.new('L', bigsize, 0)
    ImageDraw.Draw(mask).ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(im.size, Image.ANTIALIAS)
    mask = ImageChops.darker(mask, im.split()[-1])
    im.putalpha(mask)
    return im


def get_plant_pic(pid, pics_list, default_pic, size=64):
    pic = default_pic
    try:
        sq_image = Image.open("plants/" + str(pid) + "/pic.png")
        pic = ImageTk.PhotoImage(image_in_circle(sq_image, size))
        pics_list.append(pic)
    except FileNotFoundError:
        pass
    return pic


def get_color(water_rec_days, last_water_date):
    if water_rec_days == 0:
        return "#dbdbdb"
    if last_water_date is None:
        return '#%02x%02x%02x' % (STATUS_COLOR_MAX_VAL, STATUS_COLOR_MIN_VAL, STATUS_COLOR_MIN_VAL)
    days_since = (date.today() - last_water_date).days
    valrange = STATUS_COLOR_MAX_VAL - STATUS_COLOR_MIN_VAL
    rat = days_since/(water_rec_days * 1.5)
    n = rat * 2 * valrange
    red = util.clamp(STATUS_COLOR_MIN_VAL + n, STATUS_COLOR_MIN_VAL, STATUS_COLOR_MAX_VAL)
    green = util.clamp(STATUS_COLOR_MAX_VAL + valrange - n, STATUS_COLOR_MIN_VAL, STATUS_COLOR_MAX_VAL)
    return '#%02x%02x%02x' % (int(red), int(green), STATUS_COLOR_MIN_VAL)


def setup_scrollable_frame(window):
    def _bound_to_mousewheel(event):
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def _unbound_to_mousewheel(event):
        canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    outer_frame = Frame(window)
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

    return main_frame, canvas


class PopUpWindow(Toplevel):
    def __init__(self, master, **kwargs):
        Toplevel.__init__(self, master, **kwargs)
        self.focus_set()
        master.attributes('-disabled', True)
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.iconbitmap("assets/icon.ico")

    def close(self, event=None):
        self.master.attributes('-disabled', False)
        self.destroy()
