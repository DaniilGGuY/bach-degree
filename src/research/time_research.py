from models.graph import Graph
from methods.eps_method import EpsilonMethods
from methods.weighted_sum_method import WeightedSumMethod
from models.user_query import UserQuery
import time
import matplotlib.pyplot as plt
import numpy as np

if __name__ == "__main__":
    graph = Graph("../data/test.csv")
    user_query = UserQuery.from_json("../queries/moscow_spb.json")
    EXP_COL = 20

    origin = user_query.departure
    destination = user_query.arrival
    travel_date = user_query.datetime.date()
    desired_time = user_query.datetime
    w1, w2, w3 = user_query.w1, user_query.w2, user_query.w3
    all_routes = graph.get_all_routes(origin, destination, travel_date, desired_time, max_transfers=1)

    ws_times, eps_times, adapt_times, samples = [], [], [], []
    for i in range(10, 100):
        test = all_routes * i
        samples.append(len(test))
        eps_method = EpsilonMethods(test)
        weight_method = WeightedSumMethod(test)
        print(len(test))
        start = time.time()
        for j in range(EXP_COL):
            best_routes = weight_method.find_best_routes(w1, w2, w3)
        ws_times.append((time.time() - start) / EXP_COL * 1000)

        start = time.time()
        for j in range(EXP_COL):
            best_routes_eps = eps_method.classic_epsilon(w1, w2, w3)
        eps_times.append((time.time() - start) / EXP_COL * 1000)

        start = time.time()
        for j in range(EXP_COL):
            best_routes_eps = eps_method.adaptive_epsilon(w1, w2, w3)
        adapt_times.append((time.time() - start) / EXP_COL * 1000)

    z1 = np.polyfit(samples, ws_times, 1)
    z2 = np.polyfit(samples, eps_times, 1)
    z3 = np.polyfit(samples, adapt_times, 1)

    p1 = np.poly1d(z1)
    p2 = np.poly1d(z2)
    p3 = np.poly1d(z3)

    plt.figure(figsize=(10, 6))
    plt.plot(samples, p1(samples), label="Метод взвешенной суммы")
    plt.plot(samples, p2(samples), label="Эпсилон метод")
    plt.plot(samples, p3(samples), label="Адаптивный эпсилон метод")
    plt.xlabel('Количество маршрутов в датасете', fontsize=12)
    plt.ylabel('Время поиска (мс)', fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()
