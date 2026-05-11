from typing import List, TypeVar

T = TypeVar('T')


# Доминирует ли route1 над route2
def is_dominated(route1, route2):
    c1_cost, c1_dur, c1_dev = route1.get_criteria()
    c2_cost, c2_dur, c2_dev = route2.get_criteria()

    not_worse = (c1_cost <= c2_cost and c1_dur <= c2_dur and c1_dev <= c2_dev)
    strictly_better = (c1_cost < c2_cost or c1_dur < c2_dur or c1_dev < c2_dev)

    return not_worse and strictly_better


def get_pareto_front(routes):
    pareto_front = []
    for i, route_i in enumerate(routes):
        is_dom = False
        for j, route_j in enumerate(routes):
            if i != j and is_dominated(route_j, route_i):
                is_dom = True
                break
        if not is_dom:
            pareto_front.append(route_i)
    return pareto_front
