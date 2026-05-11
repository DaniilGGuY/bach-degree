from graph import Graph
from pareto import get_pareto_front
from datetime import date, datetime

if __name__ == "__main__":
    graph = Graph("data/flights.csv")

    origin = "Москва"
    destination = "Уфа"
    travel_date = date(2026, 6, 16)
    desired_time = datetime(2026, 6, 15, 12, 0, 0)

    routes = graph.get_all_routes(origin, destination, travel_date, desired_time, max_transfers=1)

    print(f"\nНайдено маршрутов {origin} → {destination} на {travel_date}: {len(routes)}")

    print("\nВсе маршруты:")
    for r in routes:
        print(f"   {r}")

    pareto = get_pareto_front(routes)
    print(f"\nПарето-фронт (недоминируемые маршруты): {len(pareto)}")
    for r in pareto:
        print(f"   {r}")