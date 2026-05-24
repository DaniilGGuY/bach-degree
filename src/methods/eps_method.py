from typing import List, Tuple, Optional
from datetime import date, datetime
from models.graph import Graph, Route


class EpsilonMethods:

    def __init__(self, routes: List[Route]):
        self.routes = routes

    def _get_criteria_bounds(self) -> Tuple[float, float, float, float]:
        durations = [r.duration_minutes for r in self.routes]
        deviations = [r.deviation_minutes for r in self.routes]

        f2_min = min(durations)
        f2_max = max(durations)
        f3_min = min(deviations)
        f3_max = max(deviations)

        f2_min = max(0, f2_min * 0.9)
        f2_max = f2_max * 1.1
        if f3_max - f3_min < 0.1:
            f3_min = 0
            f3_max = 1440
        f3_min = max(0, f3_min * 0.9)
        f3_max = f3_max * 1.1

        return f2_min, f2_max, f3_min, f3_max

    def _normalize_criteria(self, routes: List[Route]) -> Tuple[List[float], List[float], List[float]]:
        costs = [r.cost for r in routes]
        durations = [r.duration_minutes for r in routes]
        deviations = [r.deviation_minutes for r in routes]

        min_cost, max_cost = min(costs), max(costs)
        min_dur, max_dur = min(durations), max(durations)
        min_dev, max_dev = min(deviations), max(deviations)

        norm_costs = []
        norm_durations = []
        norm_deviations = []
        for i in range(len(routes)):
            if max_cost == min_cost:
                norm_costs.append(0.5)
            else:
                norm_costs.append((costs[i] - min_cost) / (max_cost - min_cost))
            if max_dur == min_dur:
                norm_durations.append(0.5)
            else:
                norm_durations.append((durations[i] - min_dur) / (max_dur - min_dur))
            if max_dev == min_dev:
                norm_deviations.append(0.5)
            else:
                norm_deviations.append((deviations[i] - min_dev) / (max_dev - min_dev))
        return norm_costs, norm_durations, norm_deviations

    def _find_optimal_for_epsilon(self, eps2: float, eps3: float, w1: float, w2: float, w3: float) -> Optional[Route]:
        valid_routes = []
        for route in self.routes:
            if route.duration_minutes <= eps2 and route.deviation_minutes <= eps3:
                valid_routes.append(route)
        if not valid_routes:
            return None
        norm_costs, norm_durations, norm_deviations = self._normalize_criteria(valid_routes)
        best_route = None
        best_score = float('inf')

        for i, route in enumerate(valid_routes):
            score = (w1 * norm_costs[i] + w2 * norm_durations[i] + w3 * norm_deviations[i])
            if score < best_score:
                best_score = score
                best_route = route
        return best_route

    def classic_epsilon(self, w1: float, w2: float, w3: float, grid_size: int = 8) -> List[Route]:
        f2_min, f2_max, f3_min, f3_max = self._get_criteria_bounds()
        solutions = []
        for i in range(grid_size):
            for j in range(grid_size):
                eps2 = f2_min + i * (f2_max - f2_min) / (grid_size - 1)
                eps3 = f3_min + j * (f3_max - f3_min) / (grid_size - 1)
                route = self._find_optimal_for_epsilon(eps2, eps3, w1, w2, w3)
                if route:
                    solutions.append(route)

        unique = {r.route_id: r for r in solutions}.values()
        return list(unique)

    def adaptive_epsilon(self, w1: float, w2: float, w3: float, max_levels: int = 3) -> List[Route]:
        f2_min, f2_max, f3_min, f3_max = self._get_criteria_bounds()
        all_solutions = []
        cells = [(0, 0, 2, 2)]
        for level in range(max_levels):
            new_cells = []
            for i, j, div_i, div_j in cells:
                eps2 = f2_min + (i + 1) * (f2_max - f2_min) / div_i
                eps3 = f3_min + (j + 1) * (f3_max - f3_min) / div_j
                route = self._find_optimal_for_epsilon(eps2, eps3, w1, w2, w3)
                if route:
                    all_solutions.append(route)
                    if level < max_levels - 1:
                        for di in [0, 1]:
                            for dj in [0, 1]:
                                new_i = i * 2 + di
                                new_j = j * 2 + dj
                                new_div_i = div_i * 2
                                new_div_j = div_j * 2
                                new_cells.append((new_i, new_j, new_div_i, new_div_j))
            cells = new_cells
        unique = {r.route_id: r for r in all_solutions}.values()
        return list(unique)
