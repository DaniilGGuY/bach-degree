import csv
from datetime import datetime, date
from typing import List, Dict, Tuple
from flight import Flight
from route import Route


class Graph:
    def __init__(self, csv_path: str):
        self.flights: List[Flight] = []
        self.flights_by_origin: Dict[str, List[Flight]] = {}
        self.flights_by_pair: Dict[Tuple[str, str], List[Flight]] = {}
        self._load_from_csv(csv_path)

    def _load_from_csv(self, csv_path: str):
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                flight = Flight(row)
                self.flights.append(flight)

                if flight.departure not in self.flights_by_origin:
                    self.flights_by_origin[flight.departure] = []
                self.flights_by_origin[flight.departure].append(flight)

                key = (flight.departure, flight.arrival)
                if key not in self.flights_by_pair:
                    self.flights_by_pair[key] = []
                self.flights_by_pair[key].append(flight)

        print(f"Загружено {len(self.flights)} рейсов")
        print(f"   Городов: {len(self.get_cities())}")
        print(f"   Направлений: {len(self.flights_by_pair)}")

    def get_cities(self) -> List[str]:
        cities = set()
        for f in self.flights:
            cities.add(f.departure)
            cities.add(f.arrival)
        return sorted(list(cities))

    def get_direct_flights(self, origin: str, destination: str, travel_date: date) -> List[Flight]:
        key = (origin, destination)
        if key not in self.flights_by_pair:
            return []

        available = []
        for flight in self.flights_by_pair[key]:
            if flight.is_available_on_date(travel_date):
                available.append(flight)

        return available

    # Все рейсы с количеством пересадок меньшим иле равным max_transfers
    def get_all_routes(self, origin: str, destination: str, travel_date: date,
                       desired_time: datetime = None, max_transfers: int = 0) -> List[Route]:
        routes = []
        route_id = 1

        direct_flights = self.get_direct_flights(origin, destination, travel_date)
        for flight in direct_flights:
            routes.append(Route(
                route_id=route_id,
                flights=[flight],
                travel_date=travel_date,
                desired_time=desired_time,
                transfer_discount=0
            ))
            route_id += 1

        if max_transfers >= 1:
            cities = self.get_cities()
            for X in cities:
                if X == origin or X == destination:
                    continue
                leg1_flights = self.get_direct_flights(origin, X, travel_date)
                leg2_flights = self.get_direct_flights(X, destination, travel_date)
                for flight1 in leg1_flights:
                    for flight2 in leg2_flights:
                        arrival1 = flight1.get_arrival_datetime(travel_date)
                        departure2 = flight2.get_departure_datetime(travel_date)
                        connection_minutes = (departure2 - arrival1).total_seconds() / 60
                        if 45 <= connection_minutes <= 360:
                            routes.append(Route(
                                route_id=route_id,
                                flights=[flight1, flight2],
                                travel_date=travel_date,
                                desired_time=desired_time,
                                transfer_discount=0.10
                            ))
                            route_id += 1

        if max_transfers >= 2:
            cities = self.get_cities()
            for X in cities:
                if X == origin or X == destination:
                    continue
                for Y in cities:
                    if Y == origin or Y == destination or Y == X:
                        continue
                    leg1_flights = self.get_direct_flights(origin, X, travel_date)
                    leg2_flights = self.get_direct_flights(X, Y, travel_date)
                    leg3_flights = self.get_direct_flights(Y, destination, travel_date)
                    for flight1 in leg1_flights:
                        for flight2 in leg2_flights:
                            for flight3 in leg3_flights:
                                arrival1 = flight1.get_arrival_datetime(travel_date)
                                departure2 = flight2.get_departure_datetime(travel_date)
                                connection1 = (departure2 - arrival1).total_seconds() / 60
                                if not (45 <= connection1 <= 360):
                                    continue

                                arrival2 = flight2.get_arrival_datetime(travel_date)
                                departure3 = flight3.get_departure_datetime(travel_date)
                                connection2 = (departure3 - arrival2).total_seconds() / 60
                                if not (45 <= connection2 <= 360):
                                    continue

                                routes.append(Route(
                                    route_id=route_id,
                                    flights=[flight1, flight2, flight3],
                                    travel_date=travel_date,
                                    desired_time=desired_time,
                                    transfer_discount=0.20
                                ))
                                route_id += 1

        return routes