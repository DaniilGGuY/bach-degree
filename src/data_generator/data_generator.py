import csv
import math
import random
from datetime import datetime, timedelta

# Для Boeing 737-800
FUEL_PER_100KM_LITERS = 2800
PASSENGER_CAPACITY = 189
LOAD_FACTOR = 0.85
AVERAGE_SPEED_KMH = 800
FUEL_PRICE_USD_PER_LITER = 0.90
PROFIT_MARGIN = 0.20
ADDITIONAL_COSTS_PERCENT = 0.15
RUB_PER_USD = 74.3  # курс доллара

# Времена вылета
DEPARTURE_TIMES = [
    "06:00:00", "07:00:00", "08:00:00", "09:00:00", "10:00:00",
    "11:00:00", "12:00:00", "13:00:00", "14:00:00", "15:00:00",
    "16:00:00", "17:00:00", "18:00:00", "19:00:00", "20:00:00",
    "21:00:00", "22:00:00", "23:00:00"
]

# Коэффициент цены от времени вылета
TIME_PRICE_COEFF = {
    "06:00:00": 0.9, "07:00:00": 0.95, "08:00:00": 1.1, "09:00:00": 1.1,
    "10:00:00": 1.2, "11:00:00": 1.1, "12:00:00": 1.0, "13:00:00": 1.0,
    "14:00:00": 1.0, "15:00:00": 1.0, "16:00:00": 1.0, "17:00:00": 1.1,
    "18:00:00": 1.2, "19:00:00": 1.1, "20:00:00": 1.0, "21:00:00": 0.9,
    "22:00:00": 0.8, "23:00:00": 0.7
}

# Периодичность
RECURRENCE_WEIGHTS = {
    "short": [0.8, 0.2, 0.0],  # для расстояний < 1000 км
    "medium": [0.3, 0.4, 0.3],  # для расстояний 1000-3000 км
    "long": [0.1, 0.2, 0.7]  # для расстояний > 3000 км
}

# Количество перелетов в день
DAYLY_TRANSFERS_COL = {
    "short": [2, 3, 4],  # для расстояний < 1000 км
    "medium": [1, 2],  # для расстояний 1000-3000 км
    "long": [1]  # для расстояний > 3000 км
}

# СПИСОК ГОРОДОВ
CITIES = [
    ("Москва", "SVO", 55.7558, 37.6173),
    ("Санкт-Петербург", "LED", 59.9311, 30.3609),
    ("Нижний Новгород", "GOJ", 56.2300, 43.7841),
    ("Воронеж", "VOZ", 51.8142, 39.2297),
    ("Ярославль", "IAR", 57.5608, 40.1574),
    ("Казань", "KZN", 55.7887, 49.1221),
    ("Самара", "KUF", 53.1959, 50.1518),
    ("Уфа", "UFA", 54.5577, 55.8744),
    ("Волгоград", "VOG", 48.7849, 44.3468),
    ("Саратов", "RTW", 51.5654, 46.0465),
    ("Екатеринбург", "SVX", 56.8389, 60.5973),
    ("Челябинск", "CEK", 55.3057, 61.5033),
    ("Тюмень", "TJM", 57.1892, 65.3243),
    ("Омск", "OMS", 54.9670, 73.3105),
    ("Новосибирск", "OVB", 55.0122, 82.6507),
    ("Томск", "TOF", 56.3800, 85.2083),
    ("Кемерово", "KEJ", 55.2701, 86.1071),
    ("Барнаул", "BAX", 53.3638, 83.5385),
    ("Красноярск", "KJA", 56.0097, 92.8525),
    ("Иркутск", "IKT", 52.2681, 104.2899),
    ("Улан-Удэ", "UUD", 51.8078, 107.4376),
    ("Чита", "HTA", 52.0264, 113.3056),
    ("Якутск", "YKS", 62.0933, 129.7708),
    ("Хабаровск", "KHV", 48.5270, 135.1885),
    ("Владивосток", "VVO", 43.1151, 131.8854),
    ("Южно-Сахалинск", "UUS", 46.9571, 142.7168),
    ("Сочи", "AER", 43.4496, 39.9567),
    ("Краснодар", "KRR", 45.0348, 38.9693),
    ("Ростов-на-Дону", "ROV", 47.2585, 39.8181),
    ("Ставрополь", "STW", 45.1093, 42.1128),
    ("Минеральные Воды", "MRV", 44.2253, 43.0817),
    ("Махачкала", "MCX", 42.8168, 47.6523),
    ("Грозный", "GRV", 43.3881, 45.6986),
    ("Калининград", "KGD", 54.8901, 20.5927),
    ("Архангельск", "ARH", 64.6001, 40.7169),
    ("Мурманск", "MMK", 68.7817, 32.7509),
    ("Сыктывкар", "SCW", 61.6470, 50.8451),
]


# ФУНКЦИЯ РАСЧЁТА РАССТОЯНИЯ
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


# РАСЧЁТ СТОИМОСТИ БИЛЕТА
def calculate_ticket_price(distance_km, time_str):
    fuel_liters = (distance_km / 100) * FUEL_PER_100KM_LITERS
    fuel_cost_usd = fuel_liters * FUEL_PRICE_USD_PER_LITER
    additional_costs_usd = fuel_cost_usd * ADDITIONAL_COSTS_PERCENT
    total_cost_usd = fuel_cost_usd + additional_costs_usd
    actual_passengers = int(PASSENGER_CAPACITY * LOAD_FACTOR)
    cost_per_ticket_usd = total_cost_usd / actual_passengers
    base_price_usd = cost_per_ticket_usd * (1 + PROFIT_MARGIN)
    coeff = TIME_PRICE_COEFF.get(time_str, 1.0)
    price_usd = base_price_usd * coeff
    price_rub = int(price_usd * RUB_PER_USD)
    return max(price_rub, 1500)


def calculate_duration_minutes(distance_km):
    hours = distance_km / AVERAGE_SPEED_KMH
    return int(hours * 60)


# ГЕНЕРАЦИЯ ВСЕХ ВОЗМОЖНЫХ ПЕРЕЛЁТОВ
def generate_all_possible_flights():
    flights = []
    flight_id = 1
    base_date = datetime(2026, 1, 1).date()

    total_cities = len(CITIES)

    for i in range(total_cities):
        for j in range(i + 1, total_cities):
            name1, code1, lat1, lon1 = CITIES[i]
            name2, code2, lat2, lon2 = CITIES[j]

            distance = haversine_distance(lat1, lon1, lat2, lon2)
            if distance < 600:
                continue

            if distance < 1000:
                weights = RECURRENCE_WEIGHTS["short"]
                num_flights = random.choice(DAYLY_TRANSFERS_COL["short"])
            elif distance < 3000:
                weights = RECURRENCE_WEIGHTS["medium"]
                num_flights = random.choice(DAYLY_TRANSFERS_COL["medium"])
            else:
                weights = RECURRENCE_WEIGHTS["long"]
                num_flights = random.choice(DAYLY_TRANSFERS_COL["long"])

            selected_times = random.sample(DEPARTURE_TIMES, min(num_flights, len(DEPARTURE_TIMES)))

            for time_str in selected_times:
                duration = calculate_duration_minutes(distance)
                cost = calculate_ticket_price(distance, time_str)
                recurrence = random.choices([1, 2, 3], weights=weights)[0]
                flights.append({
                    "id": flight_id,
                    "departure": name1,
                    "arrival": name2,
                    "time_departure": time_str,
                    "duration_minutes": duration,
                    "recurrence_every_n_days": recurrence,
                    "base_date": base_date.strftime("%Y-%m-%d"),
                    "cost": cost,
                    "distance_km": int(distance)
                })
                flight_id += 1
                time_return = random.choice(DEPARTURE_TIMES)
                cost_return = calculate_ticket_price(distance, time_return)

                flights.append({
                    "id": flight_id,
                    "departure": name2,
                    "arrival": name1,
                    "time_departure": time_return,
                    "duration_minutes": duration,
                    "recurrence_every_n_days": recurrence,
                    "base_date": base_date.strftime("%Y-%m-%d"),
                    "cost": cost_return,
                    "distance_km": int(distance)
                })
                flight_id += 1

    return flights


# СОХРАНЕНИЕ В CSV
def save_to_csv(flights, filename="../data/flights_base.csv"):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        fieldnames = ["id", "departure", "arrival", "time_departure",
                      "duration_minutes", "recurrence_every_n_days", "base_date",
                      "cost", "distance_km"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(flights)


# СТАТИСТИКА
def print_statistics(flights):
    print(f"\nВсего городов: {len(CITIES)}")
    print(f"Всего рейсов: {len(flights)}")

    directions = {}
    for f in flights:
        key = (f["departure"], f["arrival"])
        if key not in directions:
            directions[key] = 0
        directions[key] += 1

    print(f"Уникальных направлений: {len(directions)}")
    if directions:
        avg_flights = len(flights) / len(directions)
        print(f"Рейсов на направление (среднее): {avg_flights:.1f}")

    costs = [f["cost"] for f in flights]
    print(f"\nЦена билета:")
    print(f"   - Минимум: {min(costs):,} руб")
    print(f"   - Максимум: {max(costs):,} руб")
    print(f"   - Среднее: {sum(costs) // len(costs):,} руб")

    durations = [f["duration_minutes"] for f in flights]
    print(f"\nДлительность полёта:")
    print(f"   - Минимум: {min(durations)} мин ({min(durations) // 60}ч {min(durations) % 60}м)")
    print(f"   - Максимум: {max(durations)} мин ({max(durations) // 60}ч {max(durations) % 60}м)")

    recurrences = [f["recurrence_every_n_days"] for f in flights]
    print(f"\nПериодичность:")
    for r in sorted(set(recurrences)):
        count = recurrences.count(r)
        print(f"   - Каждые {r} дн: {count} рейсов ({count / len(flights) * 100:.1f}%)")


if __name__ == "__main__":
    print("Генерация данных на основе физической модели Boeing 737-800")
    print("-" * 60)
    all_flights = generate_all_possible_flights()
    print(f"Создано {len(all_flights)} перелётов")
    save_to_csv(all_flights, "../data/flights_base.csv")
    print_statistics(all_flights)