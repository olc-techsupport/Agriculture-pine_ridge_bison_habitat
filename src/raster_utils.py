from __future__ import annotations

"""
raster_utils.py for raster alignment, resampling, and normalization utilities.

All BHSI component rasters must be aligned to the same grid before combination:
  - Same CRS (EPSG:5070 Albers Equal Area)
  - Same resolution (TARGET_RES_M meters)
  - Same extent (clipped to Pine Ridge boundary)
  - Values normalized to 0–1 (higher = better habitat)

Functions here handle that alignment pipeline.
"""

import warnings
import numpy as np
from pathlib import Path

from src.constants import TARGET_RES_M, CRS_PROJECTED, BHSI_WEIGHTS


def normalize_0_1(
    arr: np.ndarray,
    invert: bool = False,
    nodata: float = np.nan,
) -> np.ndarray:
    """
    Min-max normalize a 2D array to [0, 1].

    Parameters
    arr    : Input 2D numpy array (may contain NaN)
    invert : If True, invert so high raw values = low normalized values.
             Use for stress indicators (slope, heat days, distance to water).
    nodata : Value to treat as no-data (excluded from min/max calculation)

    Returns
    Normalized array in [0, 1] with NaN preserved
    """
    valid = arr[~np.isnan(arr)]
    if len(valid) == 0:
        return np.full_like(arr, np.nan, dtype=np.float32)

    mn, mx = valid.min(), valid.max()
    if mx == mn:
        return np.full_like(arr, 0.5, dtype=np.float32)

    normed = (arr - mn) / (mx - mn)
    if invert:
        normed = 1 - normed

    normed[np.isnan(arr)] = np.nan
    return normed.astype(np.float32)


def align_raster_to_template(
    src_path: Path,
    template_path: Path,
    output_path: Path,
    resampling_method: str = "bilinear",
) -> Path:
    """
    Reproject and resample a raster to match the template raster exactly:
    same CRS, same transform, same shape. Used to align all BHSI component 
    layers before combining.

    Parameters
    src_path        : Path to source raster
    template_path   : Path to template raster (target grid)
    output_path     : Path to write aligned raster
    resampling_method : 'bilinear' for continuous data, 'nearest' for categorical

    Returns
    Path to output aligned raster
    """
    import rasterio
    from rasterio.warp import reproject, Resampling

    RESAMPLING_MAP = {
        "bilinear": Resampling.bilinear,
        "nearest":  Resampling.nearest,
        "cubic":    Resampling.cubic,
        "average":  Resampling.average,
    }
    resample = RESAMPLING_MAP.get(resampling_method, Resampling.bilinear)

    with rasterio.open(template_path) as tmpl:
        dst_crs       = tmpl.crs
        dst_transform = tmpl.transform
        dst_width     = tmpl.width
        dst_height    = tmpl.height

    with rasterio.open(src_path) as src:
        dst_profile = src.profile.copy()
        dst_profile.update({
            "crs":       dst_crs,
            "transform": dst_transform,
            "width":     dst_width,
            "height":    dst_height,
            "dtype":     "float32",
            "nodata":    np.nan,
        })
        # Preserve uncovered areas as NoData rather than leaving arbitrary
        # memory values that can resemble valid terrain.
        dst_data = np.full(
            (src.count, dst_height, dst_width), np.nan, dtype=np.float32
        )
        reproject(
            source      = rasterio.band(src, list(range(1, src.count + 1))),
            destination = dst_data,
            src_crs     = src.crs,
            dst_crs     = dst_crs,
            src_transform   = src.transform,
            src_nodata      = src.nodata,
            dst_nodata      = np.nan,
            target_aligned_pixels = True,
            dst_transform   = dst_transform,
            resampling      = resample,
        )

    with rasterio.open(output_path, "w", **dst_profile) as dst:
        dst.write(dst_data)

    return output_path


def create_template_raster(
    boundary_gdf,
    output_path: Path,
    resolution_m: int = TARGET_RES_M,
    crs: str = CRS_PROJECTED,
) -> Path:
    """
    Create a template raster in the projected CRS covering the boundary extent.
    All BHSI component layers are aligned to this template.

    Parameters
    boundary_gdf : GeoDataFrame of the Pine Ridge boundary
    output_path  : Where to write the template raster
    resolution_m : Pixel size in meters (default TARGET_RES_M)

    Returns
    Path to template raster
    """
    import rasterio
    from rasterio.transform import from_bounds
    from rasterio.features import geometry_mask

    boundary_proj = boundary_gdf.to_crs(crs)
    bounds        = boundary_proj.total_bounds  

    # Snap bounds to resolution grid
    minx = np.floor(bounds[0] / resolution_m) * resolution_m
    miny = np.floor(bounds[1] / resolution_m) * resolution_m
    maxx = np.ceil(bounds[2]  / resolution_m) * resolution_m
    maxy = np.ceil(bounds[3]  / resolution_m) * resolution_m

    width     = int((maxx - minx) / resolution_m)
    height    = int((maxy - miny) / resolution_m)
    transform = from_bounds(minx, miny, maxx, maxy, width, height)

    # Burn boundary mask (1=inside, 0=outside)
    from rasterio.transform import from_bounds
    from shapely.geometry import mapping

    mask = geometry_mask(
        [mapping(geom) for geom in boundary_proj.geometry],
        transform=transform,
        invert=True,
        out_shape=(height, width),
    ).astype(np.float32)

    # Outside boundary to NaN
    data = np.where(mask, 1.0, np.nan).astype(np.float32)

    profile = {
        "driver":    "GTiff",
        "dtype":     "float32",
        "width":     width,
        "height":    height,
        "count":     1,
        "crs":       crs,
        "transform": transform,
        "nodata":    np.nan,
        "compress":  "lzw",
    }

    with rasterio.open(output_path, "w", **profile) as dst:
        dst.write(data, 1)

    print(f"Template raster: {width} × {height} px @ {resolution_m}m resolution")
    print(f"Extent: {minx:.0f}E, {miny:.0f}N to {maxx:.0f}E, {maxy:.0f}N (EPSG:5070)")
    return output_path


def compute_distance_raster(
    features_gdf,
    template_path: Path,
    output_path: Path,
    max_dist_m: float | None = None,
) -> Path:
    """
    Compute Euclidean distance from each raster cell to the nearest feature
    in features_gdf. Used for water access raster (distance to streams/ponds).

    Parameters
    features_gdf : GeoDataFrame of water features (must be in projected CRS)
    template_path: Path to template raster defining the grid
    max_dist_m   : If set, cap distances at this value and normalize to 0–1
                   (0 = at water, 1 = max_dist_m or beyond)
    """
    import rasterio
    from rasterio.features import rasterize
    from scipy.ndimage import distance_transform_edt

    with rasterio.open(template_path) as tmpl:
        profile   = tmpl.profile.copy()
        transform = tmpl.transform
        shape     = (tmpl.height, tmpl.width)
        mask      = tmpl.read(1)

    # Rasterize features: 1 where water exists, 0 elsewhere
    from shapely.geometry import mapping
    feat_proj = features_gdf.to_crs(CRS_PROJECTED)
    water_mask = rasterize(
        [(mapping(geom), 1) for geom in feat_proj.geometry],
        out_shape=shape,
        transform=transform,
        fill=0,
        dtype=np.uint8,
    )

    # Distance transform: distance in pixels = convert to meters
    pixel_size_m = abs(transform.a)
    dist_px      = distance_transform_edt(water_mask == 0)
    dist_m       = dist_px * pixel_size_m

    # Apply boundary mask
    dist_m[np.isnan(mask)] = np.nan

    if max_dist_m is not None:
        dist_m = np.minimum(dist_m, max_dist_m)

    profile.update(dtype="float32", count=1, nodata=np.nan)
    with rasterio.open(output_path, "w", **profile) as dst:
        dst.write(dist_m.astype(np.float32), 1)

    return output_path


def combine_bhsi_layers(
    layer_paths: dict[str, Path],
    weights: dict[str, float] | None = None,
    output_path: Path | None = None,
) -> np.ndarray:
    """
    Combine normalized BHSI component rasters into the final composite index.

    Parameters
    layer_paths : Dict of {component_name: path_to_normalized_raster}
                  All rasters must be aligned to the same grid.
    weights     : Dict of {component_name: weight}. Defaults to BHSI_WEIGHTS.
    output_path : If provided, write the composite raster to this path.

    Returns
    2D numpy array of BHSI values (0–1, NaN outside boundary)
    """
    import rasterio

    if weights is None:
        weights = BHSI_WEIGHTS

    arrays   = {}
    profile  = None

    for name, path in layer_paths.items():
        with rasterio.open(path) as src:
            arrays[name] = src.read(1).astype(np.float32)
            if profile is None:
                profile = src.profile.copy()

    # Compute weighted sum, distributing weight among available layers
    total_weight = sum(weights.get(k, 0) for k in arrays)
    if total_weight == 0:
        raise ValueError("No layers match weight keys.")

    composite = np.zeros_like(list(arrays.values())[0], dtype=np.float32)
    composite[:] = np.nan
    weight_sum   = np.zeros_like(composite)

    for name, arr in arrays.items():
        w    = weights.get(name, 0) / total_weight
        valid = ~np.isnan(arr)
        composite = np.where(valid, np.nan_to_num(composite) + arr * w, composite)
        weight_sum += np.where(valid, w, 0)

    # Normalize by actual weight received (handles missing pixels)
    with np.errstate(invalid="ignore", divide="ignore"):
        composite = np.where(weight_sum > 0, composite / weight_sum, np.nan)

    composite = np.clip(composite, 0, 1)

    if output_path and profile:
        profile.update(dtype="float32", count=1, nodata=np.nan)
        with rasterio.open(output_path, "w", **profile) as dst:
            dst.write(composite, 1)
        print(f"BHSI composite written: {output_path.name}")

    return composite
