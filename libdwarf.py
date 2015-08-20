from immutable_deffinitions import *
from actions import *

#   Action planning with conditions   #
def condition_met_by_world(words, actor=None, target=None):
    condition = ''
    # convert to sentence representation
    for item in words:
        condition += str(item) + ' '
    condition = condition[:-1]  # slice off trailing space
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
    print "the calculated plan is", result
    return result


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


def contains(subject, constraints):
    """
    returns true if any item in subject's inventory matches constraints
    """
    return len(select([constraints], obj_set=subject[Keys.inventory])) > 0


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
    properties[Keys.layer] = get_layer(properties[Keys.kind])

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
    libtcod.console_set_custom_font('dejavu16x16_gs_tc.png',
                                    libtcod.FONT_TYPE_GRAYSCALE
                                    | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(WIDTH*3, WIDTH*3,
                              'The Smartest Dwarf in the Fortress', False)
    libtcod.console_set_default_foreground(0, libtcod.white)


FOREGROUND_COLOR_MAP = {
    'dwarf': libtcod.white,
    'grass': libtcod.dark_green,
    'cliff': libtcod.gray,
    'axe': libtcod.silver,
    'tree': libtcod.dark_green,
    'wood': libtcod.dark_sepia
}

BACKGROUND_COLOR_MAP = {
    'dirt_tile': libtcod.dark_sepia,
    'stone_tile': libtcod.dark_gray
}


def draw_world():
    for x in range(WIDTH):
        for y in range(WIDTH):
            at_loc = select([(Keys.loc, (x, y))])
            non_tiles = filter(is_not_tile, at_loc)
            item_to_display = ' '
            foreground_color = libtcod.white
            if non_tiles:
                non_tiles = sorted(non_tiles, key=lambda x: x[Keys.layer])
                item_to_display = non_tiles.pop()[Keys.kind]
                foreground_color = FOREGROUND_COLOR_MAP[item_to_display]
                libtcod.console_set_default_foreground(0, foreground_color)
            tile = [tile for tile in at_loc if '_tile' in tile[Keys.kind]][0]
            backround_color = BACKGROUND_COLOR_MAP[tile[Keys.kind]]
            libtcod.console_set_default_background(0, backround_color)
            libtcod.console_put_char(0, y, x,
                                     get_glyph(item_to_display),
                                     libtcod.BKGND_SET)

    libtcod.console_flush()


def window_is_open():
    return not libtcod.console_is_window_closed()
