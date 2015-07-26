from libdwarf import *


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
                    Keys.loc: (x, y)
                })

    add_obj_to_state({
        Keys.name: 'ori',
        Keys.kind: 'dwarf',
        Keys.loc: (2, 6),
    })
    add_obj_to_state({
        Keys.kind: 'axe',
        Keys.loc: (10, 5),
    })
    add_obj_to_state({
        Keys.kind: 'tree',
        Keys.loc: (7, 8),
        Keys.inventory:  ['wood']
    })

### Display   ###


def draw_world():
    for x in range(WIDTH):
        for y in range(WIDTH):
            at_loc = select([(Keys.loc, (x, y))])
            non_tiles = filter(is_not_tile, at_loc)
            if non_tiles:
                print get_glyph(non_tiles.pop()[Keys.kind]),
            else:
                print get_glyph(at_loc.pop()[Keys.kind]),
        print''


fili = {
    Keys.name: 'fili',
    Keys.kind: 'dwarf',
    Keys.loc: (2, 2),
    Keys.inventory:  []
}

add_obj_to_state({
    Keys.kind: 'cliff',
    Keys.loc: (10, 4),
})

add_obj_to_state({
    Keys.kind: 'cliff',
    Keys.loc: (10, 6),
})

add_obj_to_state({
    Keys.kind: 'cliff',
    Keys.loc: (9, 5),
})

# add_obj_to_state({
#     Keys.kind: 'cliff',
#     Keys.loc: (11, 5),
# })

add_obj_to_state(fili)
create_simple_world()
add_object_at_all('cliff', [(Keys.kind, 'stone_tile')])

draw_world()

actions = steps_to_condition('actor has wood', [], fili, None)
print "======"
if actions is not None:
    print "this action is possible by executing"
    print [action[1] for action in actions]
