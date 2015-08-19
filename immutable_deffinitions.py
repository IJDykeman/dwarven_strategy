from copy import deepcopy


class Keys:
    loc = 0
    name = 1
    kind = 3
    inventory = 4
    weight = 5
    goal = 6
    plan = 7
    layer = 8

ALL_KINDS = {
    'wood': {'weight': 'light', 'layer': 2},
    'axe': {'weight': 'light', 'layer': 6},
    'dwarf': {'weight': 'heavy', 'layer': 100},
    'cliff': {'weight': 'massive', 'layer': 2},
    'tree': {'weight': 'massive', 'layer': 4},
    'workbench': {'weight': 'heavy', 'layer': 5},
    'dirt_tile': {'weight': 'massive', 'layer': 0},
    'stone_tile': {'weight': 'massive', 'layer': 0},
    'grass': {'weight': 'light', 'layer': 1}

}

SUBTYPES = {
    'impassable': {'cliff'},
    'creature': {'dwarf'}
}

WIDTH = 15

GLYPH_MAP = {
    'dwarf': 'D',
    'dirt_tile': ',',
    'stone_tile': '.',
    'grass': '"',
    'cliff': '#',
    'axe': 'a',
    'tree': 'T',
    'wood': 'w'
}


def get_layer(kind):
    if 'layer' in ALL_KINDS[kind]:
        return ALL_KINDS[kind]['layer']
    return 0


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


#   actions


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
                    new_constraint.append(constraint[index].replace
                                          (oldstr, newstr))
                else:
                    new_constraint.append(word)
            return tuple(new_constraint)

        def str_replace_over_set_of_constraints(tuples, oldstr, newstr):
            result = []
            for constraint in tuples:
                result.append(str_replace_in_constraint(constraint,
                                                        oldstr, newstr))
            return set(result)

        action = list(deepcopy(action))
        action[0] = str_replace_over_set_of_constraints(action[0],
                                                        oldstr, newstr)
        action[1] = str_replace_in_constraint(action[1], oldstr, newstr)
        action[2] = str_replace_over_set_of_constraints(action[2],
                                                        oldstr, newstr)
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
