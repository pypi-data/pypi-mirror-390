import datetime
import math
from argparse import ArgumentTypeError
from typing import Final

from .products import VALID_PRODUCTS, Product, ProductsInput

MISSION_START: Final = datetime.date(2024, 5, 28)
MAX_ORBITS: Final = 1_000_000_000
EARTH_HALF_CIRCUMFERENCE: Final = 20040


def distance_to_lat_deg(distance: float) -> float:
    return round(distance / 111.32, 3)


def distance_to_lon_deg(lat: float, distance: float) -> float:
    return round(distance / (111.32 * math.cos(math.radians(lat))), 6)


def utctoday() -> datetime.date:
    return datetime.datetime.now(tz=datetime.UTC).date()


def str2date(date_str: str) -> datetime.date:
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()


def validate_lat(lat: float | None) -> None:
    if lat is not None and (lat < -90 or lat > 90):
        raise ValueError("Latitude must be between -90 and 90 degrees.")


def validate_lon(lon: float | None) -> None:
    if lon is not None and (lon < -180 or lon > 180):
        raise ValueError("Longitude must be between -180 and 180 degrees.")


def validate_products(products: ProductsInput) -> list[str]:
    if isinstance(products, str):
        raw_products = products.split(",")
    else:
        raw_products = [p.value if isinstance(p, Product) else p for p in products]

    input_products = set(raw_products)
    if invalid_products := (input_products - VALID_PRODUCTS):
        msg = f"Invalid product types: {', '.join(invalid_products)}."
        raise ArgumentTypeError(msg)
    return list(input_products)
