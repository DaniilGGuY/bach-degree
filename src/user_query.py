import json
from datetime import datetime
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class UserQuery:
    """Пользовательский запрос из JSON (минималистичный)"""

    departure: str
    arrival: str
    datetime: datetime
    w1: float  # вес стоимости
    w2: float  # вес времени в пути
    w3: float  # вес отклонения

    @classmethod
    def from_json(cls, json_path: str) -> "UserQuery":
        """Загружает запрос из JSON файла"""
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Парсим datetime (ISO 8601)
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

    def validate(self) -> bool:
        """Проверяет, что веса дают сумму 1"""
        total = self.w1 + self.w2 + self.w3
        if abs(total - 1.0) > 0.01:
            print(f"⚠️ Веса должны давать 1, сейчас {total}")
            return False
        return True

    def __repr__(self):
        return (f"UserQuery({self.departure} → {self.arrival}, "
                f"datetime={self.datetime}, "
                f"weights=({self.w1}, {self.w2}, {self.w3}))")