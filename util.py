from datetime import date


def parse_bool(b):
    return b.lower() != "false"


def str_to_int_or_zero(s):
    try:
        return int(s)
    except ValueError:
        return 0


def parse_date(s):
    try:
        return date.fromisoformat(s)
    except ValueError:
        return None


def is_nonneg_num(s):
    try:
        return int(s) >= 0
    except ValueError:
        return False


def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)


# Extremely hacky bullshit
def pad_to_length(font, text, length):
    text_len = font.measure(text)
    if text_len >= length:
        return text
    space_len = font.measure(" ")
    spaces_required = int((length - text_len) / space_len)
    spaces = n_spaces(spaces_required)
    return text + spaces


FIFTY_SPACES = "                                                  "


def n_spaces(n):
    spaces = ""
    while len(spaces) < n:
        spaces += FIFTY_SPACES
    spaces = spaces[:n]
    return spaces
