from time import sleep

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
        Keys.kind: 'axe',
        Keys.loc: (10, 5),
    })
    add_obj_to_state({
        Keys.kind: 'tree',
        Keys.loc: (7, 8),
        Keys.inventory:  [{Keys.kind: 'wood'}]
    })


def plan_for_goal(creature):
    steps = get_steps_to_condition(creature[Keys.goal], [], creature, None)
    plan = []
    for step in steps:
        words = step[1]
        verb = words[1]

        plan.append(step[1])
    plan.append(('actor', 'has_completed_goal', ''))

    return plan


def actor_failed(actor):
    actor[Keys.plan] = []


def execute(actor, step):
    # TODO handle case of action being impossible
    printouts = []
    words = step
    verb = words[1]
    obj = words[2]
    if verb == 'go_to':
        # Get a list of objects that the agent could go to
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
                    path_steps.append(('actor', 'step_to', str(step)))
        actor[Keys.plan] = path_steps + actor[Keys.plan]
    elif verb == 'step_to':
        target = obj.split("(")[1]
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
        printouts.append(actor[Keys.name] + " picks up "
                         + targets[0][Keys.kind])

    elif verb == 'drop':
        targets = select([(Keys.kind, words[2])], obj_set=actor[Keys.inventory])
        obj = targets[0]
        actor[Keys.inventory].remove(obj)
        add_obj_to_state(obj)

    elif verb == 'destroy':
        targets = select([(Keys.loc, actor[Keys.loc]), (Keys.kind, words[2])])
        if len(targets) > 0:
            destroy(targets[0])
        else:
            actor_failed(actor)

    elif verb == 'has_completed_goal':
        actor[Keys.goal] = None
        actor[Keys.plan] = []

    elif verb == 'make':
        new_obj = {Keys.kind: words[2]}
        actor[Keys.inventory].append(new_obj)

    else:
        print words
        raise ValueError('Verb '+verb+' not handled')
    return printouts


def setup_world():
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

    add_obj_to_state(fili)
    create_simple_world()
    add_object_at_all('cliff', [(Keys.kind, 'stone_tile')])
    add_object_at_all('grass', [(Keys.kind, 'dirt_tile')])

    fili[Keys.goal] = ('actor', 'at', 'workbench')


def play():
    init_screen()
    while window_is_open():
        printout = []

        for creature in select([(Keys.kind, 'creature')]):
            if (creature[Keys.goal] is not None
                    and len(creature[Keys.plan]) == 0):
                creature[Keys.plan] = plan_for_goal(creature)
                print "plan is", creature[Keys.plan]
            elif len(creature[Keys.plan]) > 0:
                printout += execute(creature, creature[Keys.plan].pop(0))
        draw_world()
        # if printout:
        #     for item in printout:
        #         print item
        #     input = raw_input(">")
        # else:
        #     sleep(.2)
        sleep(.2)

setup_world()
play()
