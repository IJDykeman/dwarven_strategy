###   Actions   ###

# Actions are 3-tuples of (precontitions, action, postconditions)
ACTIONS = [
    ({'at', 'weight light'}, 'get', {'has'}),
    ({'at', 'has axe'}, 'destroy', {'obj_inventory_available'})
]

###   Condition tests   ###

def condition_met(actor, condition, target, intermediary_state):
    words = condition.split(' ')
    predicate = words[0]
    if predicate == 'at':
        return actor[Keys.loc] == target[Keys.loc]

###   Immutable state   ###

class Keys:
    loc  = 0
    name = 1
    kind = 3
    inventory = 4
    weight = 5

WEIGHTS = {
    'wood' : 'light',
    'axe' : 'light',
    'dwarf' : 'heavy',
    'cliff' : 'massive',
    'tree' : 'massive'
}

GLYPH_MAP = {
    'dwarf':'D',#u'\u263A',
    'dirt_tile':',',
    'stone_tile':'.',
    'grass':'"',
    'cliff':'#',
    'axe':'a',
    'tree':'T',
    'wood':'w'
}

SUBTYPES = {
    'impassable': {'cliff'},
    'creature': {'dwarf'}
}

WIDTH = 15

###   Querying Immutable Properties ###

def is_of_kind(obj, kind):
    """
    True iff obj is of kind
    """
    if obj[Keys.kind] == kind:
        return True
    if kind in SUBTYPES and obj[Keys.kind] in SUBTYPES[kind]:
        return True
    return False

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


def is_tile(obj):
    return 'tile' in obj[Keys.kind].split('_')

def in_world(loc):
    return 0<=loc[0]<WIDTH and 0<=loc[1]<WIDTH

def is_not_tile(obj):
    return not is_tile(obj)

def get_adjacent_tiles(p):
    x = p[0]
    y = p[1]
    result = []
    for loc in [(x+1,y),(x,y+1),(x-1,y),(x,y-1)]:
        if in_world(loc):
            result.append(loc)
    return result

def get_weight(kind):
    if kind in WEIGHTS:
        return WEIGHTS[kind]
    elif is_tile(kind):
        return 'immobile'



'''
OPPOSITE_PROPERTIES = {}

def add_opposite(prop1, prop2):
    assert prop1 != prop2
    OPPOSITE_PROPERTIES[prop1] = prop2

add_opposite('impassable', 'passable')

def are_opposite(prop1, prop2):
    return (prop1 in OPPOSITE_PROPERTIES and OPPOSITE_PROPERTIES[prop1] == prop2
            or prop2 in OPPOSITE_PROPERTIES and OPPOSITE_PROPERTIES[prop2] == prop1)

def has_opposite(prop):
    return prop in OPPOSITE_PROPERTIES

def get_opposite(prop):
    return OPPOSITE_PROPERTIES[prop]
    '''
