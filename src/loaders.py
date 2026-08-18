from __future__ import annotations

"""
loaders.py data download and cache functions for pine_ridge_bison_habitat.

All loaders follow the same pattern:
  1. Check cache and return immediately if file exists
  2. Download from source API
  3. Cache to data/cache/
  4. Return clean GeoDataFrame, DataArray, or DataFrame

Data sources: Census TIGER, ORNL DAAC (MODIS), MRLC (NLCD),
              SoilDataAccess (gSSURGO), USGS TNM (3DEP), USGS NHD,
              Northwest Knowledge Network (MACAv2)
"""

import io
import gzip
import json
import logging
import os
import re
import warnings
import zipfile
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import geopandas as gpd
from tenacity import retry, stop_after_attempt, wait_exponential

from src.constants import (
    CACHE_DIR, CRS_GEOGRAPHIC, CRS_PROJECTED,
    CENSUS_TIGER_BASE, PINE_RIDGE_CENSUS_NAME,
    PINE_RIDGE_BBOX, PINE_RIDGE_LAT, PINE_RIDGE_LON,
    ORNL_BASE, MODIS_PRODUCT, MODIS_BAND,
    NDVI_SCALE, NDVI_FILL, MODIS_YEAR_CHUNKS,
    SOIL_DATA_ACCESS_URL,
    TNM_API_URL, DEM_DATASET, SRTM_SKADI_BASE,
    NHD_FLOWLINE_URL, NHD_WATERBODY_URL,
    MACA_BASE, MACA_MODEL,
)

log = logging.getLogger(__name__)

_retry = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
)


# Load Pine Ridge boundary

def load_pine_ridge_boundary(force_refresh: bool = False) -> gpd.GeoDataFrame:
    """
    Load Pine Ridge Reservation boundary from Census TIGER AIANNH.

    Returns
    GeoDataFrame with one feature: Pine Ridge boundary in EPSG:4326.
    area_km2 and area_acres columns added.
    """
    cache_path = CACHE_DIR/"pine_ridge_boundary.geojson"

    if not cache_path.exists() or force_refresh:
        log.info("Downloading Census TIGER AIANNH...")
        url = f"{CENSUS_TIGER_BASE}/TIGER2023/AIANNH/tl_2023_us_aiannh.zip"
        r   = requests.get(url, timeout=300)
        r.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            with tempfile.TemporaryDirectory() as tmp:
                z.extractall(tmp)
                shp = next(Path(tmp).glob("*.shp"))
                all_aiannh = gpd.read_file(shp).to_crs(CRS_GEOGRAPHIC)

        from shapely.validation import make_valid
        gdf = all_aiannh[all_aiannh["NAME"] == PINE_RIDGE_CENSUS_NAME].copy()
        gdf = gdf.dissolve(by="NAME", as_index=False)
        gdf["geometry"] = gdf.geometry.apply(make_valid)
        gdf.to_file(cache_path, driver="GeoJSON")
        log.info("Pine Ridge boundary cached.")
    else:
        gdf = gpd.read_file(cache_path)

    gdf_proj = gdf.to_crs(CRS_PROJECTED)
    gdf["area_km2"]   = gdf_proj.geometry.area / 1e6
    gdf["area_acres"] = gdf_proj.geometry.area / 4046.86

    return gdf.reset_index(drop=True)


# MODIS NDVI

@_retry
def fetch_ndvi_point(
    lat: float, lon: float,
    start_year: int, end_year: int,
    site_name: str = "site",
) -> pd.DataFrame:
    """
    Fetch MODIS MOD13Q1 NDVI time series for a single point via ORNL DAAC.
    Requests are chunked within each year to respect the 10-tile API limit.

    Returns
    DataFrame with columns: date, ndvi, pixel_count
    """
    cache_file = CACHE_DIR/ f"ndvi_{site_name}_{start_year}_{end_year}.csv"
    if cache_file.exists():
        return pd.read_csv(cache_file, parse_dates=["date"])

    print(f"Downloading MODIS NDVI for {site_name} ({start_year}–{end_year})...")
    parts = []
    for year in range(start_year, end_year + 1):
        for start_doy, end_doy in MODIS_YEAR_CHUNKS:
            url = f"{ORNL_BASE}/{MODIS_PRODUCT}/subset"
            params = {
                "latitude":     lat,
                "longitude":    lon,
                "startDate":    f"A{year}{start_doy}",
                "endDate":      f"A{year}{end_doy}",
                "kmAboveBelow": 2,
                "kmLeftRight":  2,
            }
            try:
                r = requests.get(url, params=params,
                                 headers={"Accept": "application/json"},
                                 timeout=120)
                r.raise_for_status()
                data = r.json()
                for subset in data.get("subset", []):
                    if subset.get("band") != MODIS_BAND:
                        continue
                    raw_vals = [v for v in subset.get("data", [])
                                if v is not None and v > NDVI_FILL]
                    if not raw_vals:
                        continue
                    try:
                        date = pd.to_datetime(subset.get("calendar_date", ""))
                    except Exception:
                        continue
                    parts.append({
                        "date":        date,
                        "ndvi":        round(float(np.mean(raw_vals)) * NDVI_SCALE, 4),
                        "pixel_count": len(raw_vals),
                    })
            except Exception as e:
                warnings.warn(
                    f"NDVI fetch failed for {year} chunk {start_doy}–{end_doy}: {e}",
                    UserWarning,
                )

    if not parts:
        warnings.warn(f"No NDVI data retrieved for {site_name}.", UserWarning)
        return pd.DataFrame(columns=["date", "ndvi", "pixel_count"])

    df = pd.DataFrame(parts).sort_values("date").reset_index(drop=True)
    df.to_csv(cache_file, index=False)
    return df


# NLCD Land Cover

def load_nlcd_bbox(
    bbox: tuple[float, float, float, float],
    force_refresh: bool = False,
) -> Path:
    """
    Download NLCD 2021 land cover GeoTIFF for a bounding box.

    Tries the MRLC WCS endpoint first. If unavailable, raises a clear
    error with manual download instructions.

    Returns
    Path to cached GeoTIFF file.
    """
    cache_file = CACHE_DIR/"nlcd_2021_pine_ridge.tif"
    if cache_file.exists() and not force_refresh:
        return cache_file

    min_lon, min_lat, max_lon, max_lat = bbox

    # MRLC WCS to try both workspace variants
    wcs_urls = [
        (
            "https://www.mrlc.gov/geoserver/mrlc_download/"
            "NLCD_2021_Land_Cover_L48/wcs"
            "?SERVICE=WCS&VERSION=2.0.1&REQUEST=GetCoverage"
            "&COVERAGEID=NLCD_2021_Land_Cover_L48"
            f"&SUBSET=Long({min_lon},{max_lon})"
            f"&SUBSET=Lat({min_lat},{max_lat})"
            "&FORMAT=image/geotiff"
        ),
        (
            "https://www.mrlc.gov/geoserver/NLCD_Land_Cover/"
            "NLCD_2021_Land_Cover_L48/wcs"
            "?SERVICE=WCS&VERSION=2.0.1&REQUEST=GetCoverage"
            "&COVERAGEID=NLCD_2021_Land_Cover_L48"
            f"&SUBSET=Long({min_lon},{max_lon})"
            f"&SUBSET=Lat({min_lat},{max_lat})"
            "&FORMAT=image/geotiff"
        ),
    ]

    for url in wcs_urls:
        try:
            print(f"Trying NLCD WCS endpoint...")
            r = requests.get(url, timeout=300, stream=True)
            if r.status_code == 200 and len(r.content) > 10000:
                with open(cache_file, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            f.write(chunk)
                print(f"NLCD cached: {cache_file.stat().st_size / 1e6:.1f} MB")
                return cache_file
        except Exception as e:
            log.debug(f"WCS attempt failed: {e}")
            continue

    # Both endpoints failed so provide manual download instructions
    raise RuntimeError(
        "NLCD 2021 WCS endpoint unavailable. Download manually:\n\n"
        "  1. Go to: https://www.mrlc.gov/viewer/\n"
        "  2. Use the rectangle tool to select the Pine Ridge area\n"
        "  3. Select 'NLCD 2021 Land Cover L48' layer\n"
        "  4. Download the GeoTIFF\n"
        f"  5. Save to: {cache_file}\n\n"
        "Alternatively, download the full CONUS file from:\n"
        "  https://www.mrlc.gov/data (NLCD 2021 Land Cover)\n"
        "  Then clip to Pine Ridge using the boundary in:\n"
        f"  outputs/pine_ridge_boundary.geojson"
    )


# gSSURGO Soils

@_retry
def load_ssurgo_grazing_capacity(
    bbox: tuple[float, float, float, float],
    force_refresh: bool = False,
) -> pd.DataFrame:
    """
    Query USDA SoilDataAccess for grazing capacity (Animal Unit Months per acre)
    within a bounding box.

    Returns
    DataFrame with columns: mukey, musym, muname, graze_class, nonirr_cap_cl,
    nonirr_cap_subcl, area_acres
    """
    cache_file = CACHE_DIR/"ssurgo_grazing.csv"
    if cache_file.exists() and not force_refresh:
        return pd.read_csv(cache_file)

    print("Querying gSSURGO grazing capacity via SoilDataAccess...")
    min_lon, min_lat, max_lon, max_lat = bbox

    # SQL query against the SSURGO tabular data web service
    query = f"""
    SELECT
        mu.mukey,
        mu.musym,
        mu.muname,
        scc.graze AS graze_class,
        scc.nonirrcapcl AS nonirr_cap_cl,
        scc.nonirrcapscl AS nonirr_cap_subcl
    FROM
        mapunit mu
        INNER JOIN muaggatt scc ON mu.mukey = scc.mukey
    WHERE
        mu.mukey IN (
            SELECT mukey FROM SDA_Get_Mukey_from_intersection_with_WktWgs84(
                'polygon(({min_lon} {min_lat}, {max_lon} {min_lat},
                          {max_lon} {max_lat}, {min_lon} {max_lat},
                          {min_lon} {min_lat}))'
            )
        )
    """

    try:
        r = requests.post(
            SOIL_DATA_ACCESS_URL,
            data={"format": "json+columnname", "query": query},
            timeout=120,
        )
        r.raise_for_status()
        data = r.json()

        rows  = data.get("Table", [])
        if not rows:
            warnings.warn(
                "gSSURGO returned no results. "
                "Check bounding box or try the Web Soil Survey at "
                "https://websoilsurvey.sc.egov.usda.gov/",
                UserWarning,
            )
            return pd.DataFrame()

        cols = rows[0]
        df   = pd.DataFrame(rows[1:], columns=cols)
        df.to_csv(cache_file, index=False)
        print(f"gSSURGO: {len(df):,} map units")
        return df

    except Exception as e:
        warnings.warn(f"gSSURGO query failed: {e}", UserWarning)
        return pd.DataFrame()


# Compact SRTM elevation

def load_srtm_dem(
    bbox: tuple[float, float, float, float], force_refresh: bool = False,
) -> Path:
    """Download and merge public AWS-hosted SRTM 1-arc-second HGT tiles."""
    import math
    import rasterio
    from rasterio.merge import merge
    from rasterio.transform import from_origin

    cache_file = CACHE_DIR / "dem_srtm_pine_ridge.tif"
    if cache_file.exists() and cache_file.stat().st_size > 0 and not force_refresh:
        return cache_file

    west, south, east, north = bbox
    paths: list[Path] = []
    for lat in range(math.floor(south), math.ceil(north)):
        for lon in range(math.floor(west), math.ceil(east)):
            ns = f"{'N' if lat >= 0 else 'S'}{abs(lat):02d}"
            ew = f"{'E' if lon >= 0 else 'W'}{abs(lon):03d}"
            stem = f"{ns}{ew}"
            hgt_path = CACHE_DIR / f"srtm_{stem}.hgt"
            tile_path = CACHE_DIR / f"srtm_{stem}.tif"
            if not tile_path.exists() or tile_path.stat().st_size == 0:
                if hgt_path.exists() and hgt_path.stat().st_size > 0:
                    raw = hgt_path.read_bytes()
                else:
                    response = requests.get(f"{SRTM_SKADI_BASE}/{ns}/{stem}.hgt.gz", timeout=120)
                    response.raise_for_status()
                    raw = gzip.decompress(response.content)
                side = 3601
                values = np.frombuffer(raw, dtype=">i2")
                if values.size != side * side:
                    raise RuntimeError(f"Unexpected SRTM tile size for {stem}: {values.size} samples")
                values = values.reshape((side, side))
                profile = {
                    "driver": "GTiff", "height": side, "width": side, "count": 1,
                    "dtype": "int16", "crs": "EPSG:4326", "nodata": -32768,
                    "transform": from_origin(lon, lat + 1, 1 / 3600, 1 / 3600),
                    "compress": "lzw",
                }
                with rasterio.open(tile_path, "w", **profile) as dst:
                    dst.write(values, 1)
                if hgt_path.exists():
                    hgt_path.unlink()
            paths.append(tile_path)

    datasets = [rasterio.open(path) for path in paths]
    try:
        mosaic, transform = merge(datasets, bounds=bbox, nodata=-32768)
        profile = datasets[0].profile.copy()
        profile.update(height=mosaic.shape[1], width=mosaic.shape[2], transform=transform,
                       compress="lzw", nodata=-32768)
        with rasterio.open(cache_file, "w", **profile) as dst:
            dst.write(mosaic)
    finally:
        for dataset in datasets:
            dataset.close()
    return cache_file


# USGS 3DEP Elevation

def load_3dep_dem(
    bbox: tuple[float, float, float, float],
    force_refresh: bool = False,
) -> Path | None:
    """
    Download USGS 3DEP 1/3 arc-second DEM tiles for a bounding box.

    Returns
    Path to cached DEM GeoTIFF, or None if no coverage found.
    """
    cache_file = CACHE_DIR/"dem_3dep_pine_ridge.tif"
    if cache_file.exists() and not force_refresh:
        return cache_file

    print("Querying USGS 3DEP tile inventory...")
    r = requests.get(
        TNM_API_URL,
        params={
            "datasets":     DEM_DATASET,
            "bbox":         f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}",
            "max":          50,
            "outputFormat": "JSON",
        },
        timeout=60,
    )
    r.raise_for_status()
    items = r.json().get("items", [])

    if not items:
        warnings.warn(
            "No 3DEP DEM tiles found for Pine Ridge bounding box. "
            "Check https://apps.nationalmap.gov/downloader/ for coverage.",
            UserWarning,
        )
        return None

    # The inventory contains repeated publication dates and both 1/3 and
    # 1/3 arc-second products.  Keep the most recent 1/3 arc-second product
    # per one-degree tile so the mosaic is complete without duplicate overlap.
    selected: dict[str, dict] = {}
    for item in items:
        title = item.get("title", "")
        match = re.search(r"n\d{2}w\d{3}", title.lower())
        if "1/3 Arc Second" not in title or not match:
            continue
        tile_id = match.group(0)
        if tile_id not in selected or title > selected[tile_id].get("title", ""):
            selected[tile_id] = item
    items = [selected[tile_id] for tile_id in sorted(selected)]
    if not items:
        warnings.warn("No 1/3 arc-second DEM tiles found for Pine Ridge.", UserWarning)
        return None

    # Download and merge tiles
    tile_paths = []
    # Use the complete API result set: limiting this list can omit part of
    # the requested study area when it spans more than ten DEM tiles.
    for i, item in enumerate(items):
        url  = item.get("downloadURL", "")
        if not url:
            continue
        tile_match = re.search(r"n\d{2}w\d{3}", item.get("title", "").lower())
        fname = CACHE_DIR / f"dem_tile_{tile_match.group(0)}.tif"
        if not fname.exists() or fname.stat().st_size == 0:
            print(f"  Downloading tile {i+1}/{len(items)}: "
                  f"{item.get('title', '')[:50]}")
            with requests.get(url, stream=True, timeout=300) as dr:
                dr.raise_for_status()
                with open(fname, "wb") as f:
                    for chunk in dr.iter_content(1024 * 1024):
                        if chunk:
                            f.write(chunk)
        tile_paths.append(str(fname))

    if not tile_paths:
        return None

    # Merge tiles with rasterio
    try:
        import rasterio
        from rasterio.merge import merge

        datasets = [rasterio.open(p) for p in tile_paths]
        mosaic, transform = merge(datasets)
        profile = datasets[0].profile.copy()
        profile.update(
            height=mosaic.shape[1],
            width=mosaic.shape[2],
            transform=transform,
        )
        with rasterio.open(cache_file, "w", **profile) as dst:
            dst.write(mosaic)
        for ds in datasets:
            ds.close()
        print(f"DEM mosaic written: {cache_file.stat().st_size / 1e6:.1f} MB")
    except Exception as e:
        warnings.warn(f"DEM merge failed: {e}", UserWarning)
        return None

    return cache_file


# NHD Streams and Water Bodies

@_retry
def load_nhd_water_features(
    bbox: tuple[float, float, float, float],
    force_refresh: bool = False,
) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """
    Load NHD stream flowlines and water body polygons for a bounding box.

    Returns
    (streams_gdf, waterbodies_gdf) with both in EPSG:4326
    """
    stream_cache = CACHE_DIR/"nhd_streams.geojson"
    water_cache  = CACHE_DIR/"nhd_waterbodies.geojson"

    def _query_nhd(url: str) -> gpd.GeoDataFrame:
        bbox_str = f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"
        r = requests.get(
            url,
            params={
                "where":          "1=1",
                "outFields":      "*",
                "f":              "geojson",
                "returnGeometry": "true",
                "outSR":          "4326",
                "geometry":       bbox_str,
                "geometryType":   "esriGeometryEnvelope",
                "spatialRel":     "esriSpatialRelIntersects",
                "inSR":           "4326",
            },
            timeout=120,
        )
        if r.status_code == 500:
            return gpd.GeoDataFrame()
        r.raise_for_status()
        try:
            payload = r.json()
        except Exception:
            return gpd.GeoDataFrame()
        if payload.get("error") or not payload.get("features"):
            return gpd.GeoDataFrame()
        gdf = gpd.read_file(io.BytesIO(r.content))
        return gdf.set_crs(CRS_GEOGRAPHIC, allow_override=True) if not gdf.empty else gdf

    if not stream_cache.exists() or force_refresh:
        print("Downloading NHD stream flowlines...")
        streams = _query_nhd(NHD_FLOWLINE_URL)
        if not streams.empty:
            streams.to_file(stream_cache, driver="GeoJSON")
            print(f"  Streams: {len(streams):,} features")
    else:
        streams = gpd.read_file(stream_cache)

    if not water_cache.exists() or force_refresh:
        print("Downloading NHD water bodies...")
        waterbodies = _query_nhd(NHD_WATERBODY_URL)
        if not waterbodies.empty:
            waterbodies.to_file(water_cache, driver="GeoJSON")
            print(f"  Water bodies: {len(waterbodies):,} features")
    else:
        waterbodies = gpd.read_file(water_cache)

    return streams, waterbodies


# MACAv2 Climate Projections

def fetch_maca_monthly(
    lat: float, lon: float,
    variable: str,
    scenario: str,
    model: str = MACA_MODEL,
    site_name: str = "pine_ridge",
) -> pd.DataFrame:
    """
    Fetch MACAv2 monthly climate projections for a single point via OPeNDAP.
    Uses aggregated files covering 2006–2099.
    Handles cftime NoLeap calendar.

    Parameters
    variable : MACAv2 variable name ex. 'tasmax', 'pr'
    scenario : 'rcp45' or 'rcp85'

    Returns
    DataFrame with columns: date, {variable}
    """
    import xarray as xr

    cache_file = CACHE_DIR/ f"maca_{site_name}_{variable}_{scenario}.csv"
    if cache_file.exists():
        return pd.read_csv(cache_file, parse_dates=["date"])

    url = (
        f"{MACA_BASE}{variable}_{model}_r1i1p1_{scenario}"
        f"_2006_2099_CONUS_monthly.nc"
    )
    print(f"Fetching MACAv2 {variable} {scenario}...")
    try:
        ds     = xr.open_dataset(url, engine="netcdf4",
                                 decode_times=True, use_cftime=True)
        lon360 = lon % 360
        ds_pt  = ds.sel(lon=lon360, lat=lat, method="nearest")
        var_name = [v for v in ds_pt.data_vars][0]
        da       = ds_pt[var_name]
        times    = da.time.values
        dates    = pd.to_datetime([
            f"{t.year}-{t.month:02d}-01" for t in times
        ])
        df = pd.DataFrame({"date": dates, variable: da.values})
        df = df.dropna(subset=[variable])
        df.to_csv(cache_file, index=False)
        ds.close()
        print(f"  {len(df):,} monthly records cached")
        return df
    except Exception as e:
        warnings.warn(f"MACAv2 {variable} {scenario} failed: {e}", UserWarning)
        return pd.DataFrame()
