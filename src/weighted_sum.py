from typing import List, Optional
from datetime import date, datetime
from graph import Graph, Route


class WeightedSumMethod:
    """Метод взвешенной суммы для выбора одного лучшего маршрута"""

    def __init__(self, graph: Graph):
        self.graph = graph

    def _normalize(self, values: List[float]) -> List[float]:
        """Нормализует список значений в диапазон [0, 1]"""
        min_val = min(values)
        max_val = max(values)
        if max_val == min_val:
            return [0.5] * len(values)
        return [(v - min_val) / (max_val - min_val) for v in values]

    def find_best_route(self, origin: str, destination: str,
                        travel_date: date, desired_time: datetime,
                        w1: float, w2: float, w3: float,
                        max_transfers: int = 1) -> Optional[Route]:
        """
        Находит один лучший маршрут по взвешенной сумме нормализованных критериев.

        w1 - вес стоимости
        w2 - вес времени
        w3 - вес отклонения
        """
        # Получаем все маршруты
        routes = self.graph.get_all_routes(origin, destination, travel_date,
                                           desired_time, max_transfers)

        if not routes:
            return None

        # Собираем значения критериев
        costs = [r.cost for r in routes]
        durations = [r.duration_minutes for r in routes]
        deviations = [r.deviation_minutes for r in routes]

        # Нормализуем
        norm_costs = self._normalize(costs)
        norm_durations = self._normalize(durations)
        norm_deviations = self._normalize(deviations)

        # Вычисляем взвешенную сумму для каждого маршрута
        best_route = None
        best_score = float('inf')

        for i, route in enumerate(routes):
            score = (w1 * norm_costs[i] +
                     w2 * norm_durations[i] +
                     w3 * norm_deviations[i])

            if score < best_score:
                best_score = score
                best_route = route

        return best_route