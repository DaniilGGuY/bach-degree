from typing import List, Optional
from models.graph import Graph, Route


class WeightedSumMethod:
    def __init__(self, routes: List[Route]):
        self.routes = routes

    def _normalize(self, values: List[float]) -> List[float]:
        min_val = min(values)
        max_val = max(values)
        if max_val == min_val:
            return [0.5] * len(values)
        return [(v - min_val) / (max_val - min_val) for v in values]

    def find_best_routes(self, w1: float, w2: float, w3: float, top_m: int = 5) -> List[Route]:
        costs = [r.cost for r in self.routes]
        durations = [r.duration_minutes for r in self.routes]
        deviations = [r.deviation_minutes for r in self.routes]

        norm_costs = self._normalize(costs)
        norm_durations = self._normalize(durations)
        norm_deviations = self._normalize(deviations)

        scored_routes = []
        for i, route in enumerate(self.routes):
            score = (w1 * norm_costs[i] + w2 * norm_durations[i] + w3 * norm_deviations[i])
            scored_routes.append((score, route))
        scored_routes.sort(key=lambda x: x[0])
        return [route for _, route in scored_routes[:top_m]]
