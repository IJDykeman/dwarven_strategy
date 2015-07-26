
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
