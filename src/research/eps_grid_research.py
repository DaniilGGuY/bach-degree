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

    times, grids = [], []
    for g in range(3, 20):
        eps_method = EpsilonMethods(all_routes)

        start = time.time()
        for i in range(EXP_COL):
            result = eps_method.classic_epsilon(w1, w2, w3, grid_size=g)
        end = (time.time() - start) / EXP_COL * 1000

        times.append(end)
        grids.append(g)

    z = np.polyfit(grids, times, 2)
    p = np.poly1d(z)

    plt.figure(figsize=(10, 6))
    plt.plot(grids, p(grids))
    plt.xlabel('Размер сетки', fontsize=12)
    plt.ylabel('Время выполнения (мс)', fontsize=12)
    plt.title('Зависимость времени от размера сетки', fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.show()
