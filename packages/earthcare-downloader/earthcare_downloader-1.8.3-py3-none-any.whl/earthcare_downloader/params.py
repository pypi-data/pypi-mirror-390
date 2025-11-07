import datetime
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SearchParams:
    lat: float | None
    lon: float | None
    distance: float
    product: list[str]
    start: datetime.date
    stop: datetime.date
    orbit_min: int
    orbit_max: int
    all: bool


@dataclass
class TaskParams:
    max_workers: int
    output_path: Path
    by_product: bool
    unzip: bool
    show: bool
    quiet: bool
    no_prompt: bool


@dataclass
class File:
    url: str
    product: str
    filename: str
    server: str
    baseline: str
    frame_start_time: datetime.datetime
    processing_time: datetime.datetime
    identifier: str
