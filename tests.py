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
    Keys.loc: (2, 3),
})
add_obj_to_state({
    Keys.kind: 'cliff',
    Keys.loc: (2, 1),
})
add_obj_to_state({
    Keys.kind: 'cliff',
    Keys.loc: (1, 2),
})
add_obj_to_state({
    Keys.kind: 'cliff',
    Keys.loc: (3, 2),
})
add_obj_to_state(fili)
create_simple_world()
add_object_at_all('cliff', [(Keys.kind, 'stone_tile')])

#testing has_path_to

assert not condition_met('actor has_path_to tree',
                         None, actor=select([(Keys.name, 'fili')])[0])

assert condition_met('actor has_path_to tree',
                     None, actor=select([(Keys.name, 'ori')])[0])

assert condition_met('actor has_path_to axe',
                     None, actor=select([(Keys.name, 'ori')])[0])

assert not condition_met('actor has_path_to target',
                         None, actor=select([(Keys.name, 'ori')])[0],
                         target=select([(Keys.name, 'fili')])[0])

assert not condition_met('actor has_path_to target',
                         None, actor=select([(Keys.name, 'ori')])[0],
                         target=select([(Keys.name, 'fili')])[0])

fili = select([(Keys.name, 'fili')])[0]
ori = select([(Keys.name, 'ori')])[0]

# testing of_kind

assert condition_met('actor of_kind creature',
                     None, actor=ori)

assert condition_met('actor of_kind dwarf',
                     None, actor=ori)

assert not condition_met('actor of_kind axe',
                         None, actor=fili)

assert not condition_met('actor of_kind axe',
                         None, actor=select([(Keys.kind, 'tree')])[0])

assert not condition_met('actor of_kind axe',
                         None, actor=select([(Keys.kind, 'tree')])[0])

assert condition_met('actor of_kind tree',
                     None, actor=select([(Keys.kind, 'tree')])[0])

axe = {Keys.kind: 'axe'}

balin = {
    Keys.name: 'balin',
    Keys.kind: 'dwarf',
    Keys.loc: (10, 5),
    Keys.inventory:  [axe]
}

add_obj_to_state(balin)
# testing at
assert condition_met('actor at axe',
                     None, actor=balin)

assert not condition_met('actor at tree',
                         None, actor=balin)

assert not condition_met('actor at dwarf',
                         None, actor=balin)

# testing not_at

assert condition_met('actor not_at dwarf',
                     None, actor=balin)

assert condition_met('actor not_at tree',
                     None, actor=balin)

# testing has

assert condition_met('actor has axe',
                     None, actor=balin)

assert not condition_met('actor has tree',
                         None, actor=balin)

# testing of_weight

assert condition_met('actor is_of_weight heavy',
                     None, actor=balin)

assert not condition_met('actor is_of_weight light',
                         None, actor=balin)

assert condition_met('target is_of_weight light',
                     None, actor=balin, target=axe)

assert condition_met('actor is_of_weight heavy',
                     None, actor=balin, target=axe)

assert not condition_met('actor is_of_weight light',
                         None, actor=balin, target=axe)
