
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

DISPLAY_INFO_MAP = {
    'dwarf': ('D', 'white'),
    'dirt_tile': (',', 'brown'),
    'stone_tile': ('.', 'gray'),
    'grass': ('"', 'green'),
    'cliff': ('#', 'gray'),
    'axe': ('a', 'red'),
    'tree': ('T', 'green'),
    'wood': ('w' 'brown')
}



def get_glyph(kind):
    """
    Returns the glyph for this kind if one is specified, else returns the first
    letter of the kind.
    """
    if kind in DISPLAY_INFO_MAP:
        return DISPLAY_INFO_MAP[kind][0]
    return kind[0]


def get_color_name(kind):
    if kind in DISPLAY_INFO_MAP:
        return DISPLAY_INFO_MAP[kind][1]
    return 'orange'


def get_glyph_kind(glyph):
    for key in DISPLAY_INFO_MAP:
        if DISPLAY_INFO_MAP[key][0] == glyph:
            return key
