import datetime
from pathlib import Path

from . import utils
from .dl import download_files
from .metadata import get_files
from .params import File, SearchParams, TaskParams
from .products import ProductsInput


async def search(
    product: ProductsInput,
    start: str | datetime.date | None = None,
    stop: str | datetime.date | None = None,
    date: str | datetime.date | None = None,
    orbit_min: int = 0,
    orbit_max: int | None = None,
    orbit: int | None = None,
    lat: float | None = None,
    lon: float | None = None,
    radius: float | None = None,
    all: bool = False,
) -> list[File]:
    if start is None:
        start = utils.MISSION_START
    elif isinstance(start, str):
        start = utils.str2date(start)

    if stop is None:
        stop = utils.utctoday()
    elif isinstance(stop, str):
        stop = utils.str2date(stop)

    if date is not None:
        if isinstance(date, str):
            date = utils.str2date(date)
        start = date
        stop = date

    if orbit is not None:
        orbit_min = orbit
        orbit_max = orbit

    utils.validate_lat(lat)
    utils.validate_lon(lon)

    search_params = SearchParams(
        lat=lat,
        lon=lon,
        distance=radius or utils.EARTH_HALF_CIRCUMFERENCE,
        product=utils.validate_products(product),
        start=start,
        stop=stop,
        orbit_min=orbit_min,
        orbit_max=orbit_max or utils.MAX_ORBITS,
        all=all,
    )
    return await get_files(search_params)


async def download(
    files: list[File],
    output_path: str | Path = Path("."),
    by_product: bool = False,
    unzip: bool = False,
    max_workers: int = 5,
    quiet: bool = True,
    credentials: tuple[str, str] | None = None,
) -> list[Path]:
    task_params = TaskParams(
        max_workers=max_workers,
        output_path=Path(output_path),
        unzip=unzip,
        quiet=quiet,
        no_prompt=False,
        show=False,
        by_product=by_product,
    )
    return await download_files(files, task_params, credentials)
