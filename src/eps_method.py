from typing import List, Tuple, Optional
from datetime import date, datetime
from graph import Graph, Route
from pareto import get_pareto_front


class EpsilonMethods:

    def __init__(self, graph: Graph, debug: bool = False):
        self.graph = graph
        self.debug = debug

    def _get_criteria_bounds(self, origin: str, destination: str,
                             travel_date: date, desired_time: datetime) -> Tuple[float, float, float, float]:
        """Находит глобальные min и max для f2 (duration) и f3 (deviation)"""
        all_routes = self.graph.get_all_routes(origin, destination, travel_date, desired_time, max_transfers=1)

        if not all_routes:
            if self.debug:
                print(f"   [WARN] Нет маршрутов для {origin}→{destination}")
            return (0, 100, 0, 24)

        durations = [r.duration_minutes for r in all_routes]
        deviations = [r.deviation_minutes for r in all_routes]

        f2_min = min(durations)
        f2_max = max(durations)
        f3_min = min(deviations)
        f3_max = max(deviations)

        # Расширяем границы на 10%
        f2_min = max(0, f2_min * 0.9)
        f2_max = f2_max * 1.1

        # Если все отклонения одинаковые (например, 0), задаём разумный диапазон
        if f3_max - f3_min < 0.1:
            f3_min = 0
            f3_max = 24  # 24 часа максимальное отклонение

        f3_min = max(0, f3_min * 0.9)
        f3_max = f3_max * 1.1

        return f2_min, f2_max, f3_min, f3_max

    def _find_optimal_for_epsilon(self, origin: str, destination: str, travel_date: date,
                                  desired_time: datetime, epsilon2: float, epsilon3: float) -> Optional[Route]:
        """Находит маршрут с минимальной стоимостью при ограничениях f2 ≤ ε₂, f3 ≤ ε₃"""
        all_routes = self.graph.get_all_routes(origin, destination, travel_date, desired_time, max_transfers=1)

        best_route = None
        best_cost = float('inf')

        for route in all_routes:
            if route.duration_minutes <= epsilon2 and route.deviation_minutes <= epsilon3:
                if route.cost < best_cost:
                    best_cost = route.cost
                    best_route = route

        return best_route

    def classic_epsilon(self, origin: str, destination: str, travel_date: date,
                        desired_time: datetime, grid_size: int = 8) -> List[Route]:
        """Классический метод с равномерной сеткой"""

        f2_min, f2_max, f3_min, f3_max = self._get_criteria_bounds(origin, destination, travel_date, desired_time)

        if self.debug:
            print(f"   [Classic] Границы: f2=[{f2_min:.0f}, {f2_max:.0f}], f3=[{f3_min:.1f}, {f3_max:.1f}]")

        solutions = []
        evaluated = 0

        for i in range(grid_size):
            for j in range(grid_size):
                epsilon2 = f2_min + i * (f2_max - f2_min) / (grid_size - 1)
                epsilon3 = f3_min + j * (f3_max - f3_min) / (grid_size - 1)

                route = self._find_optimal_for_epsilon(origin, destination, travel_date,
                                                       desired_time, epsilon2, epsilon3)
                evaluated += 1
                if route:
                    solutions.append(route)

        if self.debug:
            print(f"   [Classic] Проверено клеток: {evaluated}, найдено решений: {len(solutions)}")

        unique = {r.route_id: r for r in solutions}.values()
        return get_pareto_front(list(unique))

    def adaptive_epsilon(self, origin: str, destination: str, travel_date: date,
                         desired_time: datetime, max_levels: int = 3) -> List[Route]:
        """Адаптивный метод с иерархической сеткой"""

        f2_min, f2_max, f3_min, f3_max = self._get_criteria_bounds(origin, destination, travel_date, desired_time)

        if self.debug:
            print(f"   [Adaptive] Границы: f2=[{f2_min:.0f}, {f2_max:.0f}], f3=[{f3_min:.1f}, {f3_max:.1f}]")

        all_solutions = []

        # Начальная сетка 2×2
        cells = [(0, 0, 2, 2)]

        for level in range(max_levels):
            new_cells = []

            for i, j, div_i, div_j in cells:
                epsilon2 = f2_min + (i + 1) * (f2_max - f2_min) / div_i
                epsilon3 = f3_min + (j + 1) * (f3_max - f3_min) / div_j

                route = self._find_optimal_for_epsilon(origin, destination, travel_date,
                                                       desired_time, epsilon2, epsilon3)

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

        if self.debug:
            print(f"   [Adaptive] Найдено решений (до фильтра): {len(all_solutions)}")

        unique = {r.route_id: r for r in all_solutions}.values()
        return get_pareto_front(list(unique))

    def compare_methods(self, origin: str, destination: str, travel_date: date,
                        desired_time: datetime, grid_size: int = 8, max_levels: int = 3) -> dict:
        import time

        # Классический
        start = time.time()
        classic_result = self.classic_epsilon(origin, destination, travel_date,
                                              desired_time, grid_size)
        classic_time = time.time() - start

        # Адаптивный
        start = time.time()
        adaptive_result = self.adaptive_epsilon(origin, destination, travel_date,
                                                desired_time, max_levels)
        adaptive_time = time.time() - start

        return {
            "classic": {
                "routes": classic_result,
                "count": len(classic_result),
                "time_ms": classic_time * 1000
            },
            "adaptive": {
                "routes": adaptive_result,
                "count": len(adaptive_result),
                "time_ms": adaptive_time * 1000
            },
            "improvement": {
                "time_ratio": classic_time / adaptive_time if adaptive_time > 0 else 0,
                "quality_ratio": len(adaptive_result) / len(classic_result) if classic_result else 0
            }
        }