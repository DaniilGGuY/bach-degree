from graph import Graph
from eps_method import EpsilonMethods
from weighted_sum import WeightedSumMethod
from user_query import UserQuery

if __name__ == "__main__":
    graph = Graph("data/flights.csv")
    query = UserQuery.from_json("queries/rq.json")

    print("=" * 70)
    print(f"Запрос пользователя:")
    print(f"   Маршрут: {query.departure} → {query.arrival}")
    print(f"   Дата/время: {query.datetime}")
    print(f"   Веса: w1={query.w1}, w2={query.w2}, w3={query.w3}")
    print("=" * 70)

    if not query.validate():
        exit(1)

    travel_date = query.datetime.date()
    desired_time = query.datetime

    # ===== 1. Метод взвешенной суммы (использует веса) =====
    weighted = WeightedSumMethod(graph)
    best = weighted.find_best_route(
        query.departure, query.arrival, travel_date, desired_time,
        query.w1, query.w2, query.w3, max_transfers=1
    )

    if best:
        print(f"\n⭐ ЛУЧШИЙ МАРШРУТ (по взвешенной сумме):")
        print(f"   {best}")
        print(f"   Оценка: {query.w1}×цена + {query.w2}×время + {query.w3}×отклонение")
    else:
        print("\n⚠️ Маршрутов не найдено")

    # ===== 2. Адаптивный ε-метод (Парето-фронт) =====
    methods = EpsilonMethods(graph, debug=False)
    pareto = methods.adaptive_epsilon(
        query.departure, query.arrival, travel_date, desired_time, max_levels=3
    )

    print(f"\n🏆 ПАРЕТО-ФРОНТ ({len(pareto)} маршрутов):")
    for r in pareto:
        print(f"   {r}")