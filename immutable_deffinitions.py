class Keys:
    loc = 0
    name = 1
    kind = 3
    inventory = 4
    weight = 5
    goal = 6
    plan = 7

ALL_KINDS = {
    'wood': {'weight': 'light'},
    'axe': {'weight': 'light'},
    'dwarf': {'weight': 'heavy'},
    'cliff': {'weight': 'massive'},
    'tree': {'weight': 'massive'},
    'workbench': {'weight': 'heavy'}
}


SUBTYPES = {
    'impassable': {'cliff'},
    'creature': {'dwarf'}
}

WIDTH = 15

GLYPH_MAP = {
    'dwarf': 'D',  # u'\u263A',
    'dirt_tile': ',',
    'stone_tile': '.',
    'grass': '"',
    'cliff': '#',
    'axe': 'a',
    'tree': 'T',
    'wood': 'w'
}


def get_glyph(kind):
    """
    Returns the glyph for this kind if one is specified, else returns the first
    letter of the kind.
    """
    if kind in GLYPH_MAP:
        return GLYPH_MAP[kind]
    return kind[0]


def get_glyph_kind(glyph):
    for key in GLYPH_MAP:
        if GLYPH_MAP[key] == glyph:
            return key