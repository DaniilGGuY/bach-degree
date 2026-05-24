from datetime import datetime, timedelta, date


class Flight:
    def __init__(self, data: dict):
        self.id = int(data['id'])
        self.departure = data['departure']
        self.arrival = data['arrival']
        self.date = datetime.strptime(data['date'], "%Y-%m-%d").date()
        self.time_departure = datetime.strptime(data['time_departure'], "%H:%M:%S").time()
        self.duration_minutes = int(data['duration_minutes'])
        self.cost = int(data['cost'])
        self.distance_km = int(data['distance_km'])
        self.airline = data['airline']

    def get_departure_datetime(self) -> datetime:
        return datetime.combine(self.date, self.time_departure)

    def get_arrival_datetime(self) -> datetime:
        return self.get_departure_datetime() + timedelta(minutes=self.duration_minutes)

    def __repr__(self):
        return f"{self.departure}->{self.arrival} | {self.date} {self.time_departure} | {self.cost}₽ | {self.airline}"
