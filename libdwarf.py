
###   Immutable state   ###


class Keys:
    loc = 0
    name = 1
    kind = 3
    inventory = 4
    weight = 5
    goal = 6
    plan = 7

ALL_KINDS = {
    'wood': {'weight': 'light'},
    'axe': {'weight': 'light'},
    'dwarf': {'weight': 'heavy'},
    'cliff': {'weight': 'massive'},
    'tree': {'weight': 'massive'}
}

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

SUBTYPES = {
    'impassable': {'cliff'},
    'creature': {'dwarf'}
}

WIDTH = 15


###   Actions   ###


def get_all_actions():
    # Actions are 3-tuples of (precontitions, action, postconditions)
    action_templates = [
        ({'actor of_kind creature', 'actor has_path_to any_kind'},
            'actor go_to any_kind',
         {'actor at any_kind'}),

        ({'actor has axe', 'actor at tree'},
            'actor destroy tree',
            {'actor at wood'}),

        ({'any_kind is_of_weight light', 'actor at any_kind'},
         'actor get any_kind',
         {'actor has any_kind'})
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
        new_action = [set([]), "", set([])]
        for constraint in action[0]:
            new_action[0].add(constraint.replace(oldstr, newstr))
        new_action[1] = action[1].replace(oldstr, newstr)
        for constraint in action[2]:
            new_action[2].add(constraint.replace(oldstr, newstr))
        return tuple(new_action)

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


def condition_met_by_world(condition, actor=None, target=None):
    words = condition.split(' ')
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

    def do_the_yeah(goal_condition, actions_so_far, actor, target):

        if condition_met_by_world(goal_condition, actor=actor, target=target):
            return actions_so_far
        for next_action in get_all_actions_with_result(goal_condition):
            next_action_possible = True
            recursive_call = []
            for precondition in next_action[0]:
                recursive_call = \
                    do_the_yeah(precondition, actions_so_far, actor, target)
                if recursive_call is None:
                    next_action_possible = False
                    break
            if next_action_possible:
                result.append(next_action)
                return actions_so_far

        # condition was not already met and no next actions exist
        return None

    do_the_yeah(goal_condition, actions_so_far,
                actor, target)
    return result


###   Querying Immutable Properties ###


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

###   Declare Mutable World State ###

state = []

###   Querying Mutable World State   ###


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


###   Mutating World State   ###


def add_obj_to_state(properties, obj_set=state):
    """
    Adds given dict as object to state, setting absent required keys where
    necesarry.
    """
    if not Keys.inventory in properties:
        properties[Keys.inventory] = []
    assert Keys.kind in properties
    if is_of_kind('creature', properties[Keys.kind]):
        if not Keys.goal in properties:
            properties[Keys.plan] = None
        if not Keys.plan in properties:
            properties[Keys.plan] = []
    properties[Keys.weight] = get_weight(properties[Keys.kind])
    obj_set.append(properties)


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


###   Path Finding   ###


import heapq


class PriorityQueue:

    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]


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
