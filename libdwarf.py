from copy import deepcopy
from immutable_deffinitions import *
#   Immutable state   #





#   Actions   #


def get_all_actions():
    # Actions are 3-tuples of (precontitions, action, postconditions)
    action_templates = [
        # walk to an object of a certain kind
        ({('actor', 'of_kind', 'creature'),
          ('actor', 'has_path_to', 'any_kind')},
                ('actor', 'go_to', 'any_kind'),
         {('actor', 'at', 'any_kind')}),

        # cutting down a tree
        ({('actor', 'has', 'axe'),
          ('actor', 'at', 'tree')},
            ('actor', 'destroy', 'tree'),
          {('actor', 'at', 'wood')}),

        # pick up a light object
        ({('any_kind', 'is_of_weight', 'light'),
          ('actor', 'at', 'any_kind')},
            ('actor', 'get', 'any_kind'),
         {('actor', 'has', 'any_kind')}),

        # # make an axe from wood and stone using a workbench
        # ({'actor has wood', 'actor has stone', 'actor at workbench'},
        #  'actor make axe',
        #  {'actor has axe'}),

        # # make a wooden workbench
        # ({'actor has wood'},
        #  'actor make workbench',
        #  {'actor at workbench'})


    ]

    def action_includes_str(action, item):
        for constraint in action[0].union(action[2]):
            if item in constraint:
                return True
        if item in action[1]:
            return True
        return False

    def get_action_with_string_replaced(action, oldstr, newstr):
        """
        gets list of new actions where each action is the old action with
        oldstr replaced with each of the game's kinds
        """
        def str_replace_in_constraint(constraint, oldstr, newstr):
            new_constraint = []
            for index, word in enumerate(constraint):
                if type(word) is str:
                     new_constraint.append(
                        constraint[index].replace(oldstr, newstr))
                else:
                    new_constraint.append(word)
            return tuple(new_constraint)


        def str_replace_over_set_of_constraints(tuples, oldstr, newstr):
            result = []
            for constraint in tuples:
                result.append(str_replace_in_constraint(constraint, oldstr, newstr))
            return set(result)

        action = list(deepcopy(action))
        action[0] = str_replace_over_set_of_constraints(action[0], oldstr, newstr)
        action[1] = str_replace_in_constraint(action[1], oldstr, newstr)
        action[2] = str_replace_over_set_of_constraints(action[2], oldstr, newstr)
        return tuple(action)

    result = []
    for action in action_templates:
        if action_includes_str(action, 'any_kind'):
            for kind in ALL_KINDS:
                result.append(get_action_with_string_replaced(action,
                                                              'any_kind', kind))
        else:
            result.append(action)
    return result

ALL_ACTIONS = get_all_actions()


def action_has_result(action, constraint):
    return constraint in action[2]


def get_all_actions_with_result(constraint):
    return filter(lambda x: action_has_result(x, constraint), ALL_ACTIONS)


def condition_met_by_world(words, actor=None, target=None):
    condition = ''
    # convert to sentence representation
    for item in words:
        condition += str(item) + ' '
    condition = condition[:-1] # slice of trailing space
    verb = words[1]
    assert(len(words)) == 3

    if verb == 'at':
        if condition == 'actor at target':
            assert actor != target
            return actor[Keys.loc] == target[Keys.loc]
        if 'actor at' in condition:
            matching_targets = select({(Keys.loc, actor[Keys.loc]),
                                       (Keys.kind, words[2])})
            # Take only the targets that are not the actor.  Actor cannot be
            # 'at' itself
            matching_targets = filter(lambda x: x != actor, matching_targets)
            return len(matching_targets) > 0

    if verb == 'not_at':
        return not condition_met_by_world('actor at '+words[2],
                                          actor=actor, target=target)

    if verb == 'has_path_to':
        if condition == 'actor has_path_to target':
            return get_path(actor[Keys.loc], target[Keys.loc]) is not None
        else:  # concerned with a path to a kind
            for item in select([(Keys.kind, words[2])]):
                if get_path(item[Keys.loc], actor[Keys.loc]) is not None:
                    return True
            return False

    if verb == 'of_kind':
        if words[0] == 'actor':
            return is_of_kind(actor, words[2])
        if words[0] == 'target':
            return is_of_kind(target, words[2])

    if verb == 'is_of_weight':
        if words[0] == 'actor':
            return get_weight(actor[Keys.kind]) == words[2]
        if words[0] == 'target':
            return get_weight(target[Keys.kind]) == words[2]
        else:
            return get_weight(words[0]) == words[2]

    if verb == 'has':
        if words[0] == 'actor':
            return contains(actor, (Keys.kind, words[2]))

    print condition

    assert 1 == 0


def get_steps_to_condition(goal_condition, actions_so_far, actor, target):
    result = []

    def add_steps_to_result(goal_condition, actions_so_far, actor, target):
        if condition_met_by_world(goal_condition, actor=actor, target=target):
            return actions_so_far
        for next_action in get_all_actions_with_result(goal_condition):
            next_action_possible = True
            recursive_call = []
            for precondition in next_action[0]:
                recursive_call = \
                    add_steps_to_result(precondition, actions_so_far,
                                        actor, target)
                if recursive_call is None:
                    next_action_possible = False
                    break
            if next_action_possible:
                result.append(next_action)
                return actions_so_far

        # condition was not already met and no next actions exist
        return None

    add_steps_to_result(goal_condition, actions_so_far,
                        actor, target)
    return result


#   Querying Immutable Properties   #


def is_of_kind(obj, kind):
    """
    True iff obj is of kind.
    NB Checks also to see if obj's kind is a sub-kind of argument kind.
    """
    if obj[Keys.kind] == kind:
        return True
    if kind in SUBTYPES and obj[Keys.kind] in SUBTYPES[kind]:
        return True
    return False


def is_tile(obj):
    return 'tile' in obj[Keys.kind].split('_')


def is_not_tile(obj):
    return not is_tile(obj)


def in_world(loc):
    return 0 <= loc[0] < WIDTH and 0 <= loc[1] < WIDTH


def get_adjacent_tiles(p):
    x = p[0]
    y = p[1]
    result = []
    for loc in [(x + 1, y), (x, y + 1), (x - 1, y), (x, y - 1)]:
        if in_world(loc):
            result.append(loc)
    return result


def get_weight(kind):
    """
    Returns weight of kind
    """
    if kind in ALL_KINDS:
        return ALL_KINDS[kind]['weight']
    elif is_tile(kind):
        return 'immobile'

#   Declare Mutable World State #

state = []

#   Querying Mutable World State   #


def select(args, obj_set=state):
    """
    returns all items in obj_set (state by default) that meet the constraints
    set by the set of tuples {(attribute_key, desired_value)}
    """
    result = []
    for item in obj_set:
        item_meets_criteria = True
        for key, val in args:
            # This could perhaps be improved by making some kind of high-order
            # mapping between Keys and tests to see whether an object's
            # attribute at that key matches the query
            if key == Keys.kind:
                item_meets_criteria &= is_of_kind(item, val)
            else:
                item_meets_criteria &= key in item and item[key] == val
            if not item_meets_criteria:
                break
        if item_meets_criteria:
            result.append(item)
    return result


def is_loc_passable(loc, obj_set=state):
    """
    Returns true is a creature can walk at loc
    """
    return all([not is_of_kind(obj, 'impassable')
                for obj in select([(Keys.loc, loc)])])


def get_all_passable_from(loc, obj_set=state):
    """
    Returns a list of all tiles which can be stepped to from p.
    """
    result = []
    for loc in get_adjacent_tiles(loc):
        if is_loc_passable(loc, obj_set=obj_set):
            result.append(loc)
    return result


#   Mutating World State   #


def add_obj_to_state(properties, obj_set=state):
    """
    Adds given dict as object to state, setting absent required keys where
    necesarry.
    """
    if not Keys.inventory in properties:
        properties[Keys.inventory] = []
    assert Keys.kind in properties
    if is_of_kind(properties, 'creature'):
        if not Keys.goal in properties:
            properties[Keys.goal] = None
        if not Keys.plan in properties:
            properties[Keys.plan] = []
    properties[Keys.weight] = get_weight(properties[Keys.kind])
    obj_set.append(properties)


def put_obj_in_actors_inventory(obj, actor):
    assert obj in state
    state.remove(obj)
    actor[Keys.inventory].append(obj)


def destroy(obj):
    state.remove(obj)
    for drop in obj[Keys.inventory]:
        drop[Keys.loc] = obj[Keys.loc]
        add_obj_to_state(drop)


def add_object_at_all(kind_to_add, criteria):
    places_to_add = select(criteria)
    for obj in places_to_add:
        loc = obj[Keys.loc]
        add_obj_to_state({
            Keys.kind: kind_to_add,
            Keys.loc: loc
        })


def contains(subject, constraints):
    """
    returns true if any item in subject's inventory matches constraints
    """
    return len(select([constraints], obj_set=subject[Keys.inventory])) > 0


#   Path Finding   #


class PriorityQueue:

    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        self.elements.append((priority, item))

    def get(self):
        return self.elements.pop(0)[1]



def heuristic(a, b):
    """
    Manhattan distance from a to b.
    a and b are (x,y) pairs.
    """
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)


def move_cost(a, b):
    return 1


def get_path(start, goal):
    """
    Returns list of (x,y) which is the shortest path between start and goal.
    Goal and start are (x,y)
    """
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0
    while not frontier.empty():
        current = frontier.get()
        if current == goal:
            break
        for next in get_all_passable_from(current):
            new_cost = cost_so_far[current] + move_cost(current, next)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(goal, next)
                frontier.put(next, priority)
                came_from[next] = current
    if not goal in came_from:
        return None
    path = [goal]
    while path[0] in came_from:
        path.insert(0, came_from[path[0]])
    return path[1:]

#### Display ####


import libtcodpy as libtcod


def init_screen():
    libtcod.console_set_custom_font('courier12x12_aa_tc.png',
                                   libtcod.FONT_TYPE_GREYSCALE
                                   | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(WIDTH*3, WIDTH*3,
                              'The Smartest Dwarf in the Fortress', False)
    libtcod.console_set_default_foreground(0, libtcod.white)


FOREGROUND_COLOR_MAP = {
    'dwarf': libtcod.white,
    'grass': libtcod.green,
    'cliff': libtcod.dark_gray,
    'axe': libtcod.silver,
    'tree': libtcod.dark_green,
    'wood': libtcod.dark_sepia
}

BACKGROUND_COLOR_MAP = {
    'dirt_tile': libtcod.sepia,
    'stone_tile': libtcod.gray
}


def draw_world():
    for x in range(WIDTH):
        for y in range(WIDTH):
            at_loc = select([(Keys.loc, (x, y))])
            non_tiles = filter(is_not_tile, at_loc)
            item_to_display = ' '
            foreground_color = libtcod.white
            if non_tiles:
                item_to_display = non_tiles.pop()[Keys.kind]
                foreground_color = FOREGROUND_COLOR_MAP[item_to_display]
                libtcod.console_set_default_foreground(0, foreground_color)

            # if non_tiles:
            tile = [tile for tile in at_loc if '_tile' in tile[Keys.kind]][0]
            backround_color = BACKGROUND_COLOR_MAP[tile[Keys.kind]]
            libtcod.console_set_default_background(0, backround_color)
            libtcod.console_put_char(0, y, x,
                                     get_glyph(item_to_display),
                                         libtcod.BKGND_SET)
            # else:  # it's a tile
            #     backround_color = BACKGROUND_COLOR_MAP[at_loc.pop()[Keys.kind]]
            #     libtcod.console_set_default_background(0, backround_color)
            #     libtcod.console_put_char(0, y, x, ' ', libtcod.BKGND_SET)

    # libtcod.console_blit(panel, 0, 0, 300, 300, 0, 0, 0)
    libtcod.console_flush()


def window_is_open():
    return not libtcod.console_is_window_closed()
