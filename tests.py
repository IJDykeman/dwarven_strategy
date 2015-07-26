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

# TODO update these tests for the new condition API

#testing has_path_to

# assert not condition_met_by_world('actor has_path_to tree',
#                                   None, select([(Keys.name, 'fili')])[0])

# assert condition_met_by_world('actor has_path_to tree',
#                               None, select([(Keys.name, 'ori')])[0])

# assert condition_met_by_world('actor has_path_to axe',
#                               None, select([(Keys.name, 'ori')])[0])

# assert not condition_met_by_world('actor has_path_to target',
#                                   None, select([(Keys.name, 'ori')])[0],
#                                   target=select([(Keys.name, 'fili')])[0])

# assert not condition_met_by_world('actor has_path_to target',
#                                   None, select([(Keys.name, 'ori')])[0],
#                                   target=select([(Keys.name, 'fili')])[0])

# fili = select([(Keys.name, 'fili')])[0]
# ori = select([(Keys.name, 'ori')])[0]

# # testing of_kind

# assert condition_met_by_world('actor of_kind creature',
#                               None, ori)

# assert condition_met_by_world('actor of_kind dwarf',
#                               None, ori)

# assert not condition_met_by_world('actor of_kind axe',
#                                   None, fili)

# assert not condition_met_by_world('actor of_kind axe',
#                                   one, select([(Keys.kind, 'tree')])[0])

# assert not condition_met_by_world('actor of_kind axe',
#                                   None, select([(Keys.kind, 'tree')])[0])

# assert condition_met_by_world('actor of_kind tree',
#                               None, select([(Keys.kind, 'tree')])[0])

# axe = {Keys.kind: 'axe'}

# balin = {
#     Keys.name: 'balin',
#     Keys.kind: 'dwarf',
#     Keys.loc: (10, 5),
#     Keys.inventory:  [axe]
# }

# add_obj_to_state(balin)
# # testing at
# assert condition_met_by_world('actor at axe',
#                      None, balin)

# assert not condition_met_by_world('actor at tree',
#                          None, balin)

# assert not condition_met_by_world('actor at dwarf',
#                          None, balin)

# # testing not_at

# assert condition_met_by_world('actor not_at dwarf',
#                      None, balin)

# assert condition_met_by_world('actor not_at tree',
#                      None, balin)

# # testing has

# assert condition_met_by_world('actor has axe',
#                      None, balin)

# assert not condition_met_by_world('actor has tree',
#                          None, balin)

# # testing of_weight

# assert condition_met_by_world('actor is_of_weight heavy',
#                      None, balin)

# assert not condition_met_by_world('actor is_of_weight light',
#                          None, balin)

# assert condition_met_by_world('target is_of_weight light',
#                      None, balin, target=axe)

# assert condition_met_by_world('actor is_of_weight heavy',
#                      None, balin, target=axe)

# assert not condition_met_by_world('actor is_of_weight light',
#                          None, balin, target=axe)

balin = {
    Keys.name: 'balin',
    Keys.kind: 'dwarf',
    Keys.loc: (10, 5),
}

add_obj_to_state(balin)

print is_of_kind(balin, 'creature')
