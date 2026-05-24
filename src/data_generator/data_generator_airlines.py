import csv
import math
import random
from datetime import datetime, timedelta
from models.flight import Flight

# Для Boeing 737-800
FUEL_PER_100KM_LITERS = 2800
PASSENGER_CAPACITY = 189
LOAD_FACTOR = 0.85
AVERAGE_SPEED_KMH = 800
FUEL_PRICE_USD_PER_LITER = 0.90
PROFIT_MARGIN = 0.20
ADDITIONAL_COSTS_PERCENT = 0.15
RUB_PER_USD = 74.3

# Авиакомпании с коэффициентами наценки
AIRLINES = [
    {"name": "Аэрофлот", "markup_coeff": 1.1},
    {"name": "Аэрофлот", "markup_coeff": 1.1},
    {"name": "S7 Airlines", "markup_coeff": 1.05},
    {"name": "S7 Airlines", "markup_coeff": 1.05},
    {"name": "Победа", "markup_coeff": 0.95},
    {"name": "Победа", "markup_coeff": 0.95},
    {"name": "Уральские авиалинии", "markup_coeff": 0.95},
    {"name": "Россия", "markup_coeff": 1.00},
    {"name": "Red Wings", "markup_coeff": 0.95},
]

# Времена вылета
DEPARTURE_TIMES = []
for hour in range(6, 24):
    for minute in range(0, 60, 10):
        DEPARTURE_TIMES.append(f"{hour:02d}:{minute:02d}:00")
for hour in range(6, 24):
    for minute in [5, 15, 25, 35, 45, 55]:
        DEPARTURE_TIMES.append(f"{hour:02d}:{minute:02d}:00")

DEPARTURE_TIMES = sorted(set(DEPARTURE_TIMES))


def get_hour_from_time(time_str):
    """Извлекает час из строки времени"""
    return int(time_str.split(':')[0])


# Коэффициент цены от часа вылета
HOUR_PRICE_COEFF = {
    6: 0.85, 7: 0.90, 8: 1.10, 9: 1.15,
    10: 1.20, 11: 1.15, 12: 1.10, 13: 1.05,
    14: 1.00, 15: 1.00, 16: 1.00, 17: 1.05,
    18: 1.15, 19: 1.20, 20: 1.10, 21: 0.95,
    22: 0.85, 23: 0.80
}

# Количество рейсов в день (мин, макс)
FLIGHTS_PER_DAY_CONFIG = {
    "ultra_popular": (10, 15),
    "popular": (6, 10),
    "medium": (4, 6),
    "low": (3, 4),
    "rare": (1, 3)
}


# Категории маршрутов на основе расстояния и популярности
def get_route_category(distance_km, is_ultra_popular, is_popular):
    if is_ultra_popular:
        return "ultra_popular"
    elif is_popular:
        return "popular"
    elif distance_km < 1000:
        return "medium"
    elif distance_km < 3000:
        return "low"
    else:
        return "rare"


# Ультра-популярные направления
ULTRA_POPULAR_ROUTES = [
    ("Москва", "Санкт-Петербург"),
    ("Москва", "Сочи"),
    ("Москва", "Краснодар"),
    ("Санкт-Петербург", "Москва"),
    ("Сочи", "Москва"),
]

# Популярные направления
POPULAR_ROUTES = [
    ("Москва", "Казань"),
    ("Москва", "Екатеринбург"),
    ("Москва", "Новосибирск"),
    ("Москва", "Калининград"),
    ("Санкт-Петербург", "Сочи"),
    ("Москва", "Ростов-на-Дону"),
    ("Москва", "Минеральные Воды"),
    ("Москва", "Уфа"),
    ("Москва", "Самара"),
]

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


def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def calculate_base_ticket_price(distance_km, time_str):
    """Рассчитывает базовую цену билета"""
    hour = get_hour_from_time(time_str)

    fuel_liters = (distance_km / 100) * FUEL_PER_100KM_LITERS
    fuel_cost_usd = fuel_liters * FUEL_PRICE_USD_PER_LITER
    total_cost_usd = fuel_cost_usd * (1 + ADDITIONAL_COSTS_PERCENT)
    actual_passengers = int(PASSENGER_CAPACITY * LOAD_FACTOR)
    cost_per_ticket_usd = total_cost_usd / actual_passengers
    base_price_usd = cost_per_ticket_usd * (1 + PROFIT_MARGIN)

    coeff = HOUR_PRICE_COEFF.get(hour, 1.0)
    price_usd = base_price_usd * coeff

    # Случайная вариация ±7%
    price_usd = price_usd * random.uniform(0.93, 1.07)

    price_rub = int(price_usd * RUB_PER_USD)
    return max(price_rub, 1500)


def calculate_ticket_price_with_airline(base_price, airline_markup):
    return int(base_price * airline_markup)


def calculate_duration_minutes(distance_km):
    hours = distance_km / AVERAGE_SPEED_KMH
    # Вариация ±5% из-за ветра, очередей и т.д.
    return int(hours * 60 * random.uniform(0.95, 1.05))


def generate_flights_for_date(target_date, cities, airlines):
    """Генерирует все рейсы на конкретную дату"""
    flights = []
    flight_id = 1

    ultra_popular_set = set(ULTRA_POPULAR_ROUTES)
    popular_set = set(POPULAR_ROUTES)
    total_cities = len(cities)

    for i in range(total_cities):
        for j in range(i + 1, total_cities):
            name1, code1, lat1, lon1 = cities[i]
            name2, code2, lat2, lon2 = cities[j]
            distance = haversine_distance(lat1, lon1, lat2, lon2)
            if distance < 600:
                continue

            route_forward = (name1, name2)
            route_backward = (name2, name1)

            is_ultra_popular = route_forward in ultra_popular_set or route_backward in ultra_popular_set
            is_popular = route_forward in popular_set or route_backward in popular_set

            category = get_route_category(distance, is_ultra_popular, is_popular)
            min_flights, max_flights = FLIGHTS_PER_DAY_CONFIG[category]
            num_flights = random.randint(min_flights, max_flights)

            selected_times = random.sample(DEPARTURE_TIMES, num_flights)
            selected_times.sort()

            for time_str in selected_times:
                airline = random.choice(airlines)

                base_price = calculate_base_ticket_price(distance, time_str)
                final_price = calculate_ticket_price_with_airline(base_price, airline["markup_coeff"])
                duration = calculate_duration_minutes(distance)
                flights.append({
                    "id": flight_id,
                    "departure": name1,
                    "arrival": name2,
                    "date": target_date.strftime("%Y-%m-%d"),
                    "time_departure": time_str,
                    "duration_minutes": duration,
                    "cost": final_price,
                    "distance_km": int(distance),
                    "airline": airline["name"]
                })
                flight_id += 1

                time_return = random.choice([t for t in DEPARTURE_TIMES if t != time_str])
                airline_return = random.choice(airlines)
                base_price_return = calculate_base_ticket_price(distance, time_return)
                final_price_return = calculate_ticket_price_with_airline(base_price_return, airline_return["markup_coeff"])
                flights.append({
                    "id": flight_id,
                    "departure": name2,
                    "arrival": name1,
                    "date": target_date.strftime("%Y-%m-%d"),
                    "time_departure": time_return,
                    "duration_minutes": duration,
                    "cost": final_price_return,
                    "distance_km": int(distance),
                    "airline": airline_return["name"]
                })
                flight_id += 1
    return flights


def generate_flights_for_period(start_date, days_count, cities, airlines):
    all_flights = []
    for day_offset in range(days_count):
        current_date = start_date + timedelta(days=day_offset)
        daily_flights = generate_flights_for_date(current_date, cities, airlines)
        all_flights.extend(daily_flights)
    return all_flights


def save_to_csv(flights, filename):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        fieldnames = ["id", "departure", "arrival", "date", "time_departure", "duration_minutes", "cost", "distance_km", "airline"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(flights)


if __name__ == "__main__":
    random.seed(42)
    start_date = datetime(2026, 7, 1).date()
    days_count = 31
    all_flights = generate_flights_for_period(start_date, days_count, CITIES, AIRLINES)
    filename = "../data/flights.csv"
    save_to_csv(all_flights, filename)