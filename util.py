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
