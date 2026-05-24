import json
from datetime import datetime
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class UserQuery:
    departure: str
    arrival: str
    datetime: datetime
    w1: float
    w2: float
    w3: float

    @classmethod
    def from_json(cls, json_path: str) -> "UserQuery":
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        dt_str = data["datetime"]
        if dt_str.endswith('Z'):
            dt_str = dt_str.replace('Z', '+00:00')
        query_datetime = datetime.fromisoformat(dt_str)
        weights = data.get("weights", {})

        return cls(
            departure=data["departure"],
            arrival=data["arrival"],
            datetime=query_datetime,
            w1=weights.get("w1", 0.6),
            w2=weights.get("w2", 0.3),
            w3=weights.get("w3", 0.1)
        )

    def __repr__(self):
        return (f"UserQuery({self.departure} -> {self.arrival}, "
                f"datetime={self.datetime}, "
                f"weights=({self.w1}, {self.w2}, {self.w3}))")