from models.graph import Graph
from methods.eps_method import EpsilonMethods
from models.user_query import UserQuery
import time
import matplotlib.pyplot as plt
import numpy as np

if __name__ == '__main__':
    graph = Graph("../data/flights.csv")
    user_query = UserQuery.from_json("../queries/moscow_ufa.json")
    EXP_COL = 20

    origin = user_query.departure
    destination = user_query.arrival
    travel_date = user_query.datetime.date()
    desired_time = user_query.datetime
    w1, w2, w3 = user_query.w1, user_query.w2, user_query.w3

    all_routes = graph.get_all_routes(origin, destination, travel_date, desired_time, max_transfers=1)

    times, levels = [], []
    for l in range(1, 8):
        eps_method = EpsilonMethods(all_routes)

        start = time.time()
        for i in range(EXP_COL):
            result = eps_method.adaptive_epsilon(w1, w2, w3, max_levels=l)
        end = (time.time() - start) / EXP_COL * 1000

        times.append(end)
        levels.append(l)

    log_times = np.log(times)
    z_exp = np.polyfit(levels, log_times, 1)
    b, ln_a = z_exp[0], z_exp[1]
    a = np.exp(ln_a)

    levels_smooth = np.linspace(min(levels), max(levels), 100)
    times_smooth = a * np.exp(b * levels_smooth)

    plt.figure(figsize=(10, 6))
    plt.plot(levels_smooth, times_smooth)
    plt.xlabel('Максимальная глубина', fontsize=12)
    plt.ylabel('Время выполнения (мс)', fontsize=12)
    plt.title('Зависимость времени адаптивного метода от глубины', fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.show()
