import asyncio
import datetime
import logging
from pathlib import Path

import aiohttp

from earthcare_downloader import utils

from .params import File, SearchParams
from .products import ESAProd, JAXAProd, OrbitData


async def get_files(params: SearchParams) -> list[File]:
    base_url = "https://ec-pdgs-discovery.eo.esa.int/socat"
    common_params = _get_query_params(params)

    product_groups = {
        "esa-lv1": [p for p in params.product if p in ESAProd and "1" in p],
        "esa-lv2": [p for p in params.product if p in ESAProd and "2" in p],
        "jaxa-lv2": [p for p in params.product if p in JAXAProd],
        "orbit-scenarios": [p for p in params.product if p == OrbitData.MPL_ORBSCT],
        "orbit-predictions": [p for p in params.product if p == OrbitData.AUX_ORBPRE],
    }
    urls = {
        "esa-lv1": f"{base_url}/EarthCAREL1Validated/search",
        "esa-lv2": f"{base_url}/EarthCAREL2Validated/search",
        "jaxa-lv2": f"{base_url}/JAXAL2Validated/search",
        "orbit-scenarios": f"{base_url}/EarthCAREOrbitData/search",
        "orbit-predictions": f"{base_url}/EarthCAREOrbitData/search",
    }

    async with aiohttp.ClientSession() as session:
        tasks = []
        for type, prods in product_groups.items():
            if not prods:
                continue
            query_params = {**common_params, "query.productType": prods}
            if type in ("orbit-scenarios", "orbit-predictions"):
                msg = "Orbit number filtering not applicable for orbit data."
                logging.info(msg)
                query_params.update(
                    {"query.orbitNumber.min": "", "query.orbitNumber.max": ""}
                )
            if type == "orbit-scenarios":
                msg = "Acquisition date filtering not applicable for orbit scenarios."
                logging.info(msg)
                query_params.update(
                    {
                        "query.beginAcquisition.start": "",
                        "query.beginAcquisition.stop": "",
                        "query.endAcquisition.start": "",
                        "query.endAcquisition.stop": "",
                    }
                )
            tasks.append(_fetch_files(session, urls[type], query_params))
        results = await asyncio.gather(*tasks, return_exceptions=False)

    files = [
        _create_file(url, product)
        for result in results
        for url in result
        for product in params.product
        if product in url
    ]
    if params.all is False:
        files = _parse_newest_file_versions(files)

    return files


def _create_file(url: str, product: str) -> File:
    filename = Path(url).name
    parts = filename.split("_")
    return File(
        url=url,
        product=product,
        filename=filename,
        server=url.split("/data/")[0],
        baseline=parts[1][-2:],
        frame_start_time=datetime.datetime.strptime(parts[-3], "%Y%m%dT%H%M%SZ"),
        processing_time=datetime.datetime.strptime(parts[-2], "%Y%m%dT%H%M%SZ"),
        identifier="_".join(parts[2:-2]),
    )


def _parse_newest_file_versions(files: list[File]) -> list[File]:
    files_filtered: dict[str, File] = {}
    for f in files:
        key = f.identifier
        current = files_filtered.get(key)
        if current is None:
            files_filtered[key] = f
        else:
            if f.baseline > current.baseline or (
                f.baseline == current.baseline
                and f.processing_time > current.processing_time
            ):
                files_filtered[key] = f
    return list(files_filtered.values())


async def _fetch_files(
    session: aiohttp.ClientSession, url: str, query_params: dict
) -> list[str]:
    async with session.post(url, data=query_params) as response:
        response.raise_for_status()
        text = await response.text()
        return text.splitlines()


def _get_query_params(params: SearchParams) -> dict:
    query_params = {
        "service": "SimpleOnlineCatalogue",
        "version": "1.2",
        "request": "search",
        "format": "text/plain",
        "query.beginAcquisition.start": params.start,
        "query.beginAcquisition.stop": params.stop,
        "query.endAcquisition.start": params.start,
        "query.endAcquisition.stop": params.stop,
        "query.orbitNumber.min": params.orbit_min,
        "query.orbitNumber.max": params.orbit_max,
    }
    if (
        params.lat is not None
        and params.lon is not None
        and params.distance is not None
    ):
        lat_buffer = utils.distance_to_lat_deg(params.distance)
        lon_buffer = utils.distance_to_lon_deg(params.lat, params.distance)
        query_params.update(
            {
                "query.footprint.minlat": max(params.lat - lat_buffer, -90),
                "query.footprint.minlon": max(params.lon - lon_buffer, -180),
                "query.footprint.maxlat": min(params.lat + lat_buffer, 90),
                "query.footprint.maxlon": min(params.lon + lon_buffer, 180),
            }
        )

    return query_params
