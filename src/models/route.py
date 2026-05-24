from typing import List, Tuple
from datetime import datetime, date
from models.flight import Flight


class Route:
    def __init__(self, route_id: int, flights: List[Flight], travel_date: date, desired_time: datetime = None, transfer_discount: float = 0):
        self.route_id = route_id
        self.flights = flights
        self.travel_date = travel_date
        self.desired_time = desired_time
        self.num_transfers = len(flights) - 1
        base_cost = sum(f.cost for f in flights)
        self.cost = int(base_cost * (1 - transfer_discount))
        self.base_cost = base_cost
        self.transfer_discount = transfer_discount
        self.duration_minutes = 0
        for i, f in enumerate(flights):
            self.duration_minutes += f.duration_minutes
            if i < len(flights) - 1:
                arrival = f.get_arrival_datetime()
                next_departure = flights[i + 1].get_departure_datetime()
                connection = (next_departure - arrival).total_seconds() / 60
                self.duration_minutes += connection

        if desired_time and flights:
            first_departure = flights[0].get_departure_datetime()
            self.deviation_minutes = abs((first_departure - desired_time).total_seconds() / 60)
        else:
            self.deviation_minutes = 0
        self.distance_km = sum(f.distance_km for f in flights)

    def get_criteria(self) -> Tuple[float, float, float]:
        return self.cost, self.duration_minutes, self.deviation_minutes

    def __repr__(self):
        transfers_str = f" | {self.num_transfers} пер"

        route_str = " → ".join([f.departure + f"({f.date}T{f.time_departure}) " for f in self.flights] + [self.flights[-1].arrival])
        return f"[{self.route_id}] {route_str} | {self.cost:,}₽{transfers_str} | {self.duration_minutes}мин | откл:{self.deviation_minutes:.1f}мин"