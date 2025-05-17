import itertools

_id_counter = itertools.count(1)

def make_display_id() -> str:
    return f"REQ-{next(_id_counter):08d}"