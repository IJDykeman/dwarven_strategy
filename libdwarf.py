from copy import deepcopy

###   Immutable state   ###

class Keys:
    loc  = 0
    name = 1
    kind = 3
    inventory = 4
    weight = 5

ALL_KINDS = {
    'wood' : {'weight': 'light'},
    'axe' : {'weight': 'light'},
    'dwarf' : {'weight': 'heavy'},
    'cliff' : {'weight': 'massive'},
    'tree' : {'weight': 'massive'}
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

###   Actions   ###

# Actions are 3-tuples of (precontitions, action, postconditions)





def create_actions_from_template():
    action_templates = [
        ({'actor not_at any_type', 'actor has_path_to any_type', 'actor of_kind creature'}, 
                'actor go_to any_type', 
                {'actor at any_type'}),
        
        ({'actor at any_type', 'any_type is_of_weight light'}, 
                'actor get any_type', 
                {'actor has any_type'}),
        
        ({'actor at tree', 'actor has axe'}, 
            'actor destroy tree', 
            {'actor at wood'})
    ]
    def action_includes_str(action, item):
        for contstraint in action[0].union(action[2]):
            if item in contstraint:
                return True
        if item in action[1]:
            return True
        return False

    def get_action_with_str_replaced(action, oldstr, newstr):
        new_action = ({},"",{})
        for contstraint in new_action[0]:
            contstraint.replace(oldstr,newstr)
        contstraint[1].replace(oldstr,newstr)
        for contstraint in new_action[2]:
            contstraint.replace(oldstr,newstr)
        return new_action

    result = []
    for action in action_templates:
        if action_includes_str(action,'any_type'):
            for kind in ALL_KINDS:
                result.append(get_action_with_str_replaced(action,'any_type',kind))
    return result


ACTIONS = create_actions_from_template()

for item in ACTIONS:
    print item
###   Condition tests   ###

def condition_met(condition, intermediary_state, actor=None, target=None):
    words = condition.split(' ')
    verb = words[1]
    if verb == 'at':
        if condition == 'actor at target':
            return actor[Keys.loc] == target[Keys.loc]
        if 'actor at' in condition:
            return len(select({(Keys.loc,actor[Keys.loc]), (Keys.kind, words[2])}))>0

    if verb == 'not_at':
        if condition == 'actor not_at target':
            return actor[Keys.loc] != target[Keys.loc]

    if verb == 'has_path_to':
        if condition == 'actor has_path_to target':
            return get_path(actor[Keys.loc], target[Keys.loc]) != None

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

    if verb == 'has':
        if words[0] == 'actor':
            return contains(actor, ('kind', words[2]))

    assert 1==0


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
    if kind in ALL_KINDS:
        return ALL_KINDS[kind]['weight']
    elif is_tile(kind):
        return 'immobile'

###   Mutable World State ###

state = []

###   Querying Mutable World State   ###

def select(args, obj_set = state):
    """
    returns all items in obj_set (state by default) that meet the contstraints
    set by the set of tuples {(attribute_key, desired_value)}
    """
    result = []
    for item in obj_set:
        item_meets_criteria = True
        for key, val in args:
            if key == Keys.kind:
                item_meets_criteria &= is_of_kind(item,val)
            else:
                item_meets_criteria &= key in item and item[key] == val
            if not item_meets_criteria:
                break
        if item_meets_criteria:
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

def contains(subject, contstraints):
    """
    returns true if any item in subject's inventory matches contstraints
    """
    return len(select(contstraints, subject[Keys.inventory])) > 0

###   Algorithms   ###

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

def move_cost(a,b):
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
        
        for next in passable_from(current):
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
        path.insert(0,came_from[path[0]])
    return path[1:]