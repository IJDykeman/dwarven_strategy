from libdwarf import *
from time import sleep
import os

def cls():
    os.system(['clear','cls'][os.name == 'nt'])


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
        Keys.kind: 'axe',
        Keys.loc: (10, 5),
    })
    add_obj_to_state({
        Keys.kind: 'tree',
        Keys.loc: (7, 8),
        Keys.inventory:  [{Keys.kind: 'wood'}]
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
    Keys.name: 'ori',
    Keys.kind: 'dwarf',
    Keys.loc: (2, 6),
})

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

actions = get_steps_to_condition('actor has wood', [], fili, None)
if actions is not None:
    print [action[1] for action in actions]

fili[Keys.goal] = 'actor has wood'


def plan_for_goal(creature):
    steps = get_steps_to_condition(creature[Keys.goal], [], creature, None)
    plan = []
    for step in steps:
        words = step[1].split(' ')
        verb = words[1]

        if verb == 'go_to':
            plan.append(step[1])
        elif verb == 'destroy':
            plan.append(step[1])
        elif verb == 'get':
            plan.append(step[1])
        else:
            assert 1 == 0  # verb not recongnized
    plan.append('actor has_completed_goal')

    return plan


def actor_failed(actor):
    actor[Keys.plan] = []


def execute(actor, step):
    words = step.split(' ')
    verb = words[1]
    if verb == 'go_to':
        potential_goals = select([(Keys.kind, words[2])])
        X = actor[Keys.loc]
        # prefer closer goals of the correct type
        sorted(potential_goals, key=lambda Y:
               abs(X[0]-Y[Keys.loc][0]) + abs(X[1]-Y[Keys.loc][1]))
        path_steps = []
        for item in potential_goals:
            path = get_path(actor[Keys.loc], item[Keys.loc])
            if path is not None:
                for step in path:
                    path_steps.append('actor step_to '+str(step))
        actor[Keys.plan] = path_steps + actor[Keys.plan]
    elif verb == 'step_to':
        target = step.split("(")[1]
        target = target.replace("(", "")
        target = target.replace(")", "")
        target = target.split(', ')
        target = tuple([int(target[0]), int(target[1])])
        if is_loc_passable(target):
            actor[Keys.loc] = target
        else:
            actor_failed(actor)

    elif verb == 'get':
        targets = select([(Keys.loc, actor[Keys.loc]), (Keys.kind, words[2])])
        if len(targets) > 0:
            put_obj_in_actors_inventory(targets[0], actor)
        else:
            actor_failed(actor)

    elif verb == 'destroy':
        targets = select([(Keys.loc, actor[Keys.loc]), (Keys.kind, words[2])])
        if len(targets) > 0:
            destroy(targets[0])
        else:
            actor_failed(actor)

    elif verb == 'has_completed_goal':
        actor[Keys.goal] = None
        actor[Keys.plan] = []

    else:
        print words
        raise ValueError('Verb '+verb+' not handled')


while True:
    for creature in select([(Keys.kind, 'creature')]):
        if creature[Keys.goal] is not None and len(creature[Keys.plan]) == 0:
            creature[Keys.plan] = plan_for_goal(creature)
        elif len(creature[Keys.plan]) > 0:
            execute(creature, creature[Keys.plan].pop(0))
    cls()
    draw_world()
    sleep(.2)
