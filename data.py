from datetime import date
from typing import TypedDict


class AssetData(TypedDict):
    """Asset data type."""

    code: str
    name: str
    activation_cost: float
    availability: list[date]
    volume: int


ASSET_DATA: list[AssetData] = [
    {
        "code": "A-001",
        "name": "Asset 1",
        "activation_cost": 120.0,
        "availability": [date(2026, 4, 20), date(2026, 4, 21), date(2026, 4, 22)],
        "volume": 50,
    },
    {
        "code": "A-002",
        "name": "Asset 2",
        "activation_cost": 135.5,
        "availability": [date(2026, 4, 20), date(2026, 4, 23)],
        "volume": 60,
    },
    {
        "code": "A-003",
        "name": "Asset 3",
        "activation_cost": 80.0,
        "availability": [date(2026, 4, 21), date(2026, 4, 22), date(2026, 4, 24)],
        "volume": 35,
    },
    {
        "code": "A-004",
        "name": "Asset 4",
        "activation_cost": 82.5,
        "availability": [date(2026, 4, 20), date(2026, 4, 21), date(2026, 4, 25)],
        "volume": 40,
    },
    {
        "code": "A-005",
        "name": "Asset 5",
        "activation_cost": 98.0,
        "availability": [date(2026, 4, 22), date(2026, 4, 23), date(2026, 4, 24)],
        "volume": 45,
    },
    {
        "code": "A-006",
        "name": "Asset 6",
        "activation_cost": 101.25,
        "availability": [date(2026, 4, 20), date(2026, 4, 24), date(2026, 4, 26)],
        "volume": 55,
    },
    {
        "code": "A-007",
        "name": "Asset 7",
        "activation_cost": 210.0,
        "availability": [date(2026, 4, 20), date(2026, 4, 21), date(2026, 4, 22)],
        "volume": 120,
    },
    {
        "code": "A-008",
        "name": "Asset 8",
        "activation_cost": 225.75,
        "availability": [date(2026, 4, 23), date(2026, 4, 24), date(2026, 4, 25)],
        "volume": 140,
    },
    {
        "code": "A-009",
        "name": "Asset 9",
        "activation_cost": 75.0,
        "availability": [date(2026, 4, 20), date(2026, 4, 22), date(2026, 4, 26)],
        "volume": 30,
    },
    {
        "code": "A-010",
        "name": "Asset 10",
        "activation_cost": 78.5,
        "availability": [date(2026, 4, 21), date(2026, 4, 23), date(2026, 4, 25)],
        "volume": 32,
    },
]
