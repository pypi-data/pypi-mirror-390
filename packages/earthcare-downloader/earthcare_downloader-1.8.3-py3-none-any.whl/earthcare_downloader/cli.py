import argparse
import asyncio
import logging
from pathlib import Path

from earthcare_downloader import dl

from . import utils
from .params import SearchParams, TaskParams
from .products import VALID_PRODUCTS


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Download EarthCARE satellite data.")
    parser.add_argument(
        "-p",
        "--product",
        help=f"Product type to download. Choose from: {', '.join(VALID_PRODUCTS)}.",
        type=lambda product: utils.validate_products(product),
        required=True,
    )
    parser.add_argument(
        "--start",
        type=lambda s: utils.str2date(s),
        help="Start date (inclusive) for data search in YYYY-MM-DD format.",
        default=utils.MISSION_START,
    )
    parser.add_argument(
        "--stop",
        type=lambda s: utils.str2date(s),
        help="Stop date (inclusive) for data search in YYYY-MM-DD format.",
        default=utils.utctoday(),
    )
    parser.add_argument(
        "-d",
        "--date",
        type=lambda s: utils.str2date(s),
        help="Single date for data search in YYYY-MM-DD format. "
        "Can be used instead of --start and --stop.",
        default=None,
    )
    parser.add_argument(
        "--orbit-min",
        type=int,
        help="Minimum orbit number.",
        default=0,
    )
    parser.add_argument(
        "--orbit-max",
        type=int,
        help="Maximum orbit number.",
        default=None,
    )
    parser.add_argument(
        "--orbit",
        type=int,
        help="Single orbit number. Can be used instead of --orbit-min and --orbit-max.",
        default=None,
    )
    parser.add_argument(
        "--lat",
        type=float,
        help="Latitude of the location to download data for.",
    )
    parser.add_argument(
        "--lon",
        type=float,
        help="Longitude of the location to download data for.",
    )
    parser.add_argument(
        "-r",
        "--radius",
        type=float,
        help="Distance [km] from the location to search for data. "
        "Use with --lat and --lon.",
    )
    parser.add_argument(
        "-o",
        "--output-path",
        type=str,
        default=Path("."),
        help="Output directory for downloaded files (default: current directory).",
    )
    parser.add_argument(
        "--by-product",
        action="store_true",
        help="Create subdirectories for each product type.",
        default=False,
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=5,
        help="Maximum number of concurrent downloads (default: 5).",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Show files that would be downloaded.",
        default=False,
    )
    parser.add_argument(
        "--unzip",
        action="store_true",
        help="Unzip downloaded files after download.",
        default=False,
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Disable progress bars during download.",
        default=False,
    )
    parser.add_argument(
        "--no-prompt",
        action="store_true",
        help="Disable prompt for confirmation before downloading files.",
        default=False,
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Download all versions (different baselines and/or processing runs) "
        "of the product.",
        default=False,
    )

    args = parser.parse_args()

    utils.validate_lat(args.lat)
    utils.validate_lon(args.lon)

    if args.date is not None:
        args.start = args.date
        args.stop = args.date

    if args.orbit is not None:
        args.orbit_min = args.orbit
        args.orbit_max = args.orbit

    search_params = SearchParams(
        lat=args.lat,
        lon=args.lon,
        distance=args.radius or utils.EARTH_HALF_CIRCUMFERENCE,
        product=args.product,
        start=args.start,
        stop=args.stop,
        orbit_min=args.orbit_min,
        orbit_max=args.orbit_max or utils.MAX_ORBITS,
        all=args.all,
    )

    task_params = TaskParams(
        max_workers=args.max_workers,
        output_path=Path(args.output_path),
        by_product=args.by_product,
        unzip=args.unzip,
        show=args.show,
        quiet=args.quiet,
        no_prompt=args.no_prompt,
    )

    asyncio.run(
        dl.search_and_download(
            search_params,
            task_params,
        )
    )


if __name__ == "__main__":
    main()
