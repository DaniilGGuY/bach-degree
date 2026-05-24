import csv
from datetime import datetime, date
from typing import List, Dict, Tuple
from models.flight import Flight
from models.route import Route


class Graph:
    MAX_OFFSET = 1
    TRANSFER_DISCOUNT_1 = 0.35
    TRANSFER_DISCOUNT_2 = 0.60

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

    def get_cities(self) -> List[str]:
        cities = set()
        for f in self.flights:
            cities.add(f.departure)
            cities.add(f.arrival)
        return sorted(list(cities))

    def get_direct_flights(self, origin: str, destination: str, travel_date: date, offset: int = 0) -> List[Flight]:
        key = (origin, destination)
        if key not in self.flights_by_pair:
            return []

        available = []
        for flight in self.flights_by_pair[key]:
            if abs((flight.date - travel_date).days) <= offset:
                available.append(flight)
        return available

    def get_all_routes(self, origin: str, destination: str, travel_date: date, desired_time: datetime = None, max_transfers: int = 1) -> List[Route]:
        routes = []
        route_id = 1

        direct_flights = self.get_direct_flights(origin, destination, travel_date, self.MAX_OFFSET)
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

                leg1_flights = self.get_direct_flights(origin, X, travel_date, self.MAX_OFFSET)
                leg2_flights = self.get_direct_flights(X, destination, travel_date, self.MAX_OFFSET)

                for flight1 in leg1_flights:
                    for flight2 in leg2_flights:
                        arrival1 = flight1.get_arrival_datetime()
                        departure2 = flight2.get_departure_datetime()
                        connection_minutes = (departure2 - arrival1).total_seconds() / 60
                        if connection_minutes >= 45:
                            routes.append(Route(
                                route_id=route_id,
                                flights=[flight1, flight2],
                                travel_date=travel_date,
                                desired_time=desired_time,
                                transfer_discount=self.TRANSFER_DISCOUNT_1
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

                    leg1_flights = self.get_direct_flights(origin, X, travel_date, self.MAX_OFFSET)
                    leg2_flights = self.get_direct_flights(X, Y, travel_date, self.MAX_OFFSET)
                    leg3_flights = self.get_direct_flights(Y, destination, travel_date, self.MAX_OFFSET)

                    for flight1 in leg1_flights:
                        for flight2 in leg2_flights:
                            for flight3 in leg3_flights:
                                arrival1 = flight1.get_arrival_datetime()
                                departure2 = flight2.get_departure_datetime()
                                connection1 = (departure2 - arrival1).total_seconds() / 60
                                if connection1 < 45:
                                    continue

                                arrival2 = flight2.get_arrival_datetime()
                                departure3 = flight3.get_departure_datetime()
                                connection2 = (departure3 - arrival2).total_seconds() / 60
                                if connection2 < 45:
                                    continue

                                routes.append(Route(
                                    route_id=route_id,
                                    flights=[flight1, flight2, flight3],
                                    travel_date=travel_date,
                                    desired_time=desired_time,
                                    transfer_discount=self.TRANSFER_DISCOUNT_2
                                ))
                                route_id += 1

        return routes
