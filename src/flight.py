from datetime import datetime, timedelta, date


class Flight:
    def __init__(self, data: dict):
        self.id = int(data['id'])
        self.departure = data['departure']
        self.arrival = data['arrival']
        self.time_departure = datetime.strptime(data['time_departure'], "%H:%M:%S").time()
        self.duration_minutes = int(data['duration_minutes'])
        self.recurrence_every_n_days = int(data['recurrence_every_n_days'])
        self.base_date = datetime.strptime(data['base_date'], "%Y-%m-%d").date()
        self.cost = int(data['cost'])
        self.distance_km = int(data['distance_km'])

    def is_available_on_date(self, target_date: date) -> bool:
        days_diff = (target_date - self.base_date).days
        return days_diff % self.recurrence_every_n_days == 0 and days_diff >= 0

    def get_departure_datetime(self, target_date: date) -> datetime:
        return datetime.combine(target_date, self.time_departure)

    def get_arrival_datetime(self, target_date: date) -> datetime:
        departure_dt = self.get_departure_datetime(target_date)
        return departure_dt + timedelta(minutes=self.duration_minutes)

    def __repr__(self):
        return f"{self.departure}→{self.arrival} | {self.time_departure} | {self.cost}₽ | каждые {self.recurrence_every_n_days} дн"
