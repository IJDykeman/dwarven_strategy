import heapq
from rules import *
from algorithms import *

###   Mutable World State ###

state = []

###   Querying Mutable World State   ###

def select(args, obj_set = state):
    result = []
    for item in obj_set:
        if all([key in item and item[key] == val for key, val in args]):
            result.append(item)
    return result

def is_loc_passable(loc, obj_set=state):
    return all([not is_of_kind(obj, 'impassable') 
                for obj in select([(Keys.loc,loc)])])

def passable_from(p, obj_set=state):
    result = []
    for loc in get_adjacent_tiles(p):
        if is_loc_passable(loc, obj_set = obj_set):
            result.append(loc)
    return result

###   Mutating World State   ###

def add_obj_to_state(properties, obj_set=state):
    if not Keys.inventory in properties:
        properties[Keys.inventory] = []
    assert Keys.kind in properties
    properties[Keys.weight] = get_weight(properties[Keys.kind])
    kind = properties[Keys.kind]
    obj_set.append(properties)

def add_object_at_all(kind_to_add, criteria):
    places_to_add = select(criteria)
    for obj in places_to_add:
        loc = obj[Keys.loc]
        add_obj_to_state({
            Keys.kind: kind_to_add,
            Keys.loc: loc
            })

def create_simple_world():
    tiles = [
    ",,,,,,,,,,,,,,,",
    ",,,,,,,,,,,,,,,",
    ",,,,,,,,,,,,,,,",
    ",,,,,,,,,,,,,,,",
    ",,,,,,,,,,,,,,,",
    ",,,,,,,,,,,,,,,",
    ",,,,,,,,,,,,,,,",
    ",,,,,,,,,......",
    ",,,,,,,,,......",
    ",,,,,,,,,......",
    ",,,,,,,,,......",
    ",,,,,,,.,......",
    ",,,,,,,.,......",
    ",,,,,,.........",
    ",,,,,,........."
    ]
    for x in range(WIDTH):
        for y in range(WIDTH):
            add_obj_to_state(
                {
                    Keys.kind: get_glyph_kind(tiles[y][x]),
                    Keys.loc: (x,y)
                })

    add_obj_to_state({
        Keys.name:'fili',
        Keys.kind:'dwarf',
        Keys.loc: (2,2),
        Keys.inventory:  []
        })
    add_obj_to_state({
        Keys.name:'ori',
        Keys.kind:'dwarf',
        Keys.loc: (2,6),
        })
    add_obj_to_state({
        Keys.kind:'axe',
        Keys.loc: (10,5),
        })
    add_obj_to_state({
        Keys.kind:'tree',
        Keys.loc: (7,8),
        Keys.inventory:  ['wood']
        })

### Display   ###

def draw_world():
    for x in range(WIDTH):
        for y in range(WIDTH):
            at_loc = select([(Keys.loc,(x,y))])
            non_tiles = filter(is_not_tile, at_loc)
            if non_tiles:
                print get_glyph(non_tiles.pop()[Keys.kind]),
            else:
                print get_glyph(at_loc.pop()[Keys.kind]),
        print''

create_simple_world()
add_object_at_all('cliff',[(Keys.kind,'stone_tile')])

draw_world()