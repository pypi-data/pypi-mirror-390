def cast_str(value):
    try:
        return str(value) if value is not None else None
    except ValueError:
        return None


def cast_int(value):
    try:
        return int(value) if value is not None else None
    except ValueError:
        return None


def cast_float(value):
    try:
        return float(value) if value is not None else None
    except ValueError:
        return None
