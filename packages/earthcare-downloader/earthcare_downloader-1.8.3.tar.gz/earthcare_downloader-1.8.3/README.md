# <img src="logo.png" width="35px"> earthcare-downloader

[![CI](https://github.com/actris-cloudnet/earthcare-downloader/actions/workflows/test.yml/badge.svg)](https://github.com/actris-cloudnet/earthcare-downloader/actions/workflows/test.yml)
[![PyPI version](https://badge.fury.io/py/earthcare-downloader.svg)](https://badge.fury.io/py/earthcare-downloader)

A Python tool for searching and downloading [EarthCARE](https://earth.esa.int/eogateway/missions/earthcare) satellite data from the European Space Agency’s (ESA) [Online Dissemination services](https://ec-pdgs-discovery.eo.esa.int/sxcat).

## Installation

```bash
python3 -m pip install earthcare-downloader
```

## :penguin: CLI usage

### Authentication

Store your [ESA EO Sign In](https://eoiam-idp.eo.esa.int/) credentials in the environment variables `ESA_EO_USERNAME` and `ESA_EO_PASSWORD`.
If these variables are not set, the program will prompt you to enter your credentials.

### Running the program

```
earthcare-downloader -p PRODUCT [options]
```

where the arguments are:

| Argument              | Description                                                                     |
| --------------------- | ------------------------------------------------------------------------------- |
| `-p`, `--product`     | Product type(s) to download (see full list below).                              |
| `--start`             | Start date (YYYY-MM-DD).                                                        |
| `--stop`              | Stop date (YYYY-MM-DD).                                                         |
| `-d`, `--date`        | Single date (YYYY-MM-DD). Overrides `--start` and `--stop`                      |
| `--orbit-min`         | Minimum orbit number.                                                           |
| `--orbit-max`         | Maximum orbit number.                                                           |
| `--orbit`             | Single orbit number. Overrides `--orbit-min` and `--orbit-max`                  |
| `--lat LAT`           | Latitude of the target location (-90..90 degrees).                              |
| `--lon LON`           | Longitude of the target location (-180..180 degrees).                           |
| `-r`, `--radius`      | Search radius around the location in km. Use with `--lat` and `--lon`.          |
| `-o`, `--output-path` | Directory to save downloaded files (default: current directory).                |
| `--by-product`        | Create subdirectories for each product type.                                    |
| `--max-workers`       | Maximum number of concurrent downloads (default: **5**).                        |
| `--show`              | Show filenames before downloading.                                              |
| `--unzip`             | Automatically unzip downloaded files.                                           |
| `--quiet`             | Hide progress bars during download.                                             |
| `--no-prompt`         | Skip confirmation prompt before downloading.                                    |
| `--all`               | Download all versions of the file. By default download only the newest version. |
| `-h`, `--help`        | Show help message and exit.                                                     |

Available products:

|                     **Level 1**                     | Product Code                                                                   | Description                                      |
| :-------------------------------------------------: | ------------------------------------------------------------------------------ | ------------------------------------------------ |
|                                                     | [ATL_NOM_1B](https://earthcarehandbook.earth.esa.int/catalogue/atl_nom_1b)     | ATLID Nominal Mode                               |
|                                                     | [AUX_JSG_1D](https://earthcarehandbook.earth.esa.int/catalogue/aux_jsg_1d)     | Auxiliary Joint Standard Grid                    |
|                                                     | [BBR_NOM_1B](https://earthcarehandbook.earth.esa.int/catalogue/bbr_nom_1b)     | Broadband Radiometer Nominal Mode                |
|                                                     | [BBR_SNG_1B](https://earthcarehandbook.earth.esa.int/catalogue/bbr_sng_1b)     | Broadband Radiometer Single View                 |
|                                                     | [CPR_NOM_1B](https://earthcarehandbook.earth.esa.int/catalogue/cpr_nom_1b)     | Cloud Profiling Radar Nominal Mode               |
|                                                     | [MSI_NOM_1B](https://earthcarehandbook.earth.esa.int/catalogue/msi_nom_1b)     | Multi-Spectral Imager Nominal Mode               |
|                                                     | [MSI_RGR_1C](https://earthcarehandbook.earth.esa.int/catalogue/msi_rgr_1c)     | Multi-Spectral Imager Re-Gridded                 |
|                    **Level 2A**                     |                                                                                |                                                  |
|                                                     | [ATL_AER_2A](https://earthcarehandbook.earth.esa.int/catalogue/atl_aer_2a)     | ATLID Aerosol Parameters                         |
|                                                     | [ATL_ALD_2A](https://earthcarehandbook.earth.esa.int/catalogue/atl_ald_2a)     | ATLID Aerosol Layer Descriptors                  |
|                                                     | [ATL_CTH_2A](https://earthcarehandbook.earth.esa.int/catalogue/am__cth_2b)     | ATLID Cloud Top Height                           |
|                                                     | [ATL_EBD_2A](https://earthcarehandbook.earth.esa.int/catalogue/atl_ebd_2a)     | ATLID Extinction, Backscatter and Depolarization |
|                                                     | [ATL_FM\_\_2A](https://earthcarehandbook.earth.esa.int/catalogue/atl_fm__2a)   | ATLID Feature Mask                               |
|                                                     | [ATL_ICE_2A](https://earthcarehandbook.earth.esa.int/catalogue/atl_ice_2a)     | ATLID Ice Parameters                             |
|                                                     | [ATL_TC\_\_2A](https://earthcarehandbook.earth.esa.int/catalogue/ac__tc__2b)   | ATLID Target Classification                      |
|                                                     | [CPR_CD\_\_2A](https://earthcarehandbook.earth.esa.int/catalogue/cpr_cd__2a)   | CPR Cloud Doppler parameters                     |
|                                                     | [CPR_CLD_2A](https://earthcarehandbook.earth.esa.int/catalogue/cpr_cld_2a)     | CPR Cloud Parameters                             |
|                                                     | [CPR_FMR_2A](https://earthcarehandbook.earth.esa.int/catalogue/cpr_fmr_2a)     | CPR Feature Mask and Radar Reflectivity          |
|                                                     | [CPR_TC\_\_2A](https://earthcarehandbook.earth.esa.int/catalogue/cpr_tc__2a)   | CPR Target Classification                        |
|                                                     | [MSI_AOT_2A](https://earthcarehandbook.earth.esa.int/catalogue/msi_aot_2a)     | MSI Aerosol Optical Thickness                    |
|                                                     | [MSI_CM\_\_2A](https://earthcarehandbook.earth.esa.int/catalogue/msi_cm__2a)   | MSI Cloud Mask                                   |
|                                                     | [MSI_COP_2A](https://earthcarehandbook.earth.esa.int/catalogue/msi_cop_2a)     | MSI Cloud Optical Properties                     |
| <span title="JAXA product">:japanese_castle:</span> | [ATL_CLA_2A](https://eolp.jaxa.jp/EarthCARE_ATLID_L2A_ATL_CLA.html)            | ATLID Cloud and Aerosol Classification           |
| <span title="JAXA product">:japanese_castle:</span> | [CPR_CLP_2A](https://eolp.jaxa.jp/EarthCARE_CPR_L2A_CPR_CLP.html)              | CPR Cloud Properties                             |
| <span title="JAXA product">:japanese_castle:</span> | [CPR_ECO_2A](https://eolp.jaxa.jp/EarthCARE_CPR_L2A_CPR_ECO.html)              | CPR Echo Characteristics                         |
| <span title="JAXA product">:japanese_castle:</span> | [MSI_CLP_2A](https://eolp.jaxa.jp/EarthCARE_MSI_L2A_MSI_CLP.html)              | MSI Cloud Properties                             |
|                    **Level 2B**                     |                                                                                |                                                  |
|                                                     | [AC\_\_TC\_\_2B](https://earthcarehandbook.earth.esa.int/catalogue/ac__tc__2b) | ATLID-CPR Target Classification                  |
|                                                     | [AM\_\_ACD_2B](https://earthcarehandbook.earth.esa.int/catalogue/am__acd_2b)   | ATLID-MSI Aerosol Column Descriptors             |
|                                                     | [AM\_\_CTH_2B](https://earthcarehandbook.earth.esa.int/catalogue/am__cth_2b)   | ATLID-MSI Cloud Top Height                       |
|                                                     | [BM\_\_RAD_2B](https://earthcarehandbook.earth.esa.int/catalogue/bm__rad_2b)   | BBR-MSI Radiative Fluxes and Heating Rates       |
| <span title="JAXA product">:japanese_castle:</span> | [AC\_\_CLP_2B](https://eolp.jaxa.jp/EarthCARE_L2B_AC__CLP.html)                | CPR-ATLID Synergy Cloud Properties               |
|                   **Orbit Data**                    |                                                                                |                                                  |
|                                                     | [AUX_ORBPRE](https://earthcarehandbook.earth.esa.int/catalogue/aux_orbpre)     | Orbit Predictions                                |
|                                                     | [MPL_ORBSCT](https://earthcarehandbook.earth.esa.int/catalogue/mpl_orbsct)     | Orbit Scenario                                   |

<span title="JAXA product">:japanese_castle:</span> = [JAXA](https://www.eorc.jaxa.jp/EARTHCARE/) product

### Examples

Download all `CPR_TC__2A` overpass data within 5 km of Hyytiälä, Finland:

```bash
earthcare-downloader -p CPR_TC__2A --lat 61.844 --lon 24.287 -r 5
```

Download all `ATL_ALD_2A` and `AUX_JSG_1D` data from two days:

```bash
earthcare-downloader -p ATL_ALD_2A,AUX_JSG_1D --start=2025-05-01 --stop=2025-05-02
```

## :snake: Python API

You can also use `earthcare-downloader` as a Python library:

```python
from earthcare_downloader import search, download

files = search(product="CPR_TC__2A", date="2025-01-01")
paths = download(files, unzip=True)
```

When working in notebooks, use the asynchronous versions of these functions:

```python
from earthcare_downloader.aio import search, download

files = await search(product="CPR_TC__2A", date="2025-01-01")
paths = await download(files, unzip=True)
```

## Disclaimer

This package provides tools to access data from the European Space Agency’s (ESA)
Online Dissemination services. The package does not host or redistribute ESA data.

All data are &copy; European Space Agency (ESA) and subject to the
[ESA Online Dissemination Terms and Conditions](https://earth.esa.int/eogateway/terms-and-conditions).
Please ensure your use complies with ESA’s non-commercial and attribution requirements.

## License

MIT
