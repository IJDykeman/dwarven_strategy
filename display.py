import libtcodpy as libtcod
from immutable_deffinitions import *


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

def draw_world():
    print '\n' * 100
    for x in range(WIDTH):
        for y in range(WIDTH):
            at_loc = select([(Keys.loc, (x, y))])
            non_tiles = filter(is_not_tile, at_loc)
            if non_tiles:
                print get_glyph(non_tiles.pop()[Keys.kind]),
            else:
                print get_glyph(at_loc.pop()[Keys.kind]),
        print''
