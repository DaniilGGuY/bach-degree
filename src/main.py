from models.graph import Graph
from methods.eps_method import EpsilonMethods
from methods.weighted_sum_method import WeightedSumMethod
from methods.pareto import get_pareto_front
from models.user_query import UserQuery

if __name__ == "__main__":
    graph = Graph("data/flights.csv")
    user_query = UserQuery.from_json("queries/moscow_ufa.json")

    origin = user_query.departure
    destination = user_query.arrival
    travel_date = user_query.datetime.date()
    desired_time = user_query.datetime
    w1, w2, w3 = user_query.w1, user_query.w2, user_query.w3

    all_routes = graph.get_all_routes(origin, destination, travel_date, desired_time, max_transfers=1)
    eps_method = EpsilonMethods(all_routes)
    weight_method = WeightedSumMethod(all_routes)

    print(f"\nВСЕГО НАЙДЕНО МАРШРУТОВ: {len(all_routes)}")

    pareto_front = get_pareto_front(all_routes)

    print(f"\nПАРЕТО-ФРОНТ: {len(pareto_front)} маршрутов")
    for r in pareto_front:
        print(f"   {r}")

    print("\nВЗВЕШЕННАЯ СУММА: ТОП-5 маршрутов")
    best_routes = weight_method.find_best_routes(w1, w2, w3)
    for r in best_routes:
        print(f"    {r}")

    print("\nКЛАССИЧЕСКИЙ ЭПСИЛОН МЕТОД:")
    best_routes_eps = eps_method.classic_epsilon(w1, w2, w3)
    for r in best_routes_eps:
        print(f"    {r}")

    print("\nАДАПТИВНЫЙ ЭПСИЛОН МЕТОД:")
    best_routes_ad = eps_method.adaptive_epsilon(w1, w2, w3)
    for r in best_routes_ad:
        print(f"    {r}")
