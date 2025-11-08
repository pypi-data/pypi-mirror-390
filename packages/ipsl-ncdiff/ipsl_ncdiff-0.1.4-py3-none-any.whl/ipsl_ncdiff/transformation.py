from more_itertools import one

from ipsl_ncdiff.model.variable import Variable


def try_parse_int(text, base=10, default=None):
    try:
        return int(text, base)
    except ValueError:
        return default


def str2slice(text: str) -> None | slice:
    """
    Convert string formatted as a?:b?:c? to a slice object.
    Return None if not a correct slice.
    """
    items = text.split(":")
    if len(items) != 3:
        return None
    return slice(
        try_parse_int(items[0]),
        try_parse_int(items[1]),
        try_parse_int(items[2]),
    )


def align_variables(
    v1: Variable, v2: Variable, dim_name: str
) -> tuple[Variable, Variable] | None:
    try:
        match1 = one([d1 for d1 in v1.dimensions if d1.name == dim_name])
        match2 = one([d2 for d2 in v2.dimensions if d2.name == dim_name])
        inter = match1 & match2
        # No dimension intersection means no intersection at all!
        if not inter:
            return None
        return v1.intersection(inter), v2.intersection(inter)
    except ValueError:
        return None
