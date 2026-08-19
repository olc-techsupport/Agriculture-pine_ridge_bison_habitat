"""Create a compact, documented BHSI data cube from aligned raster layers."""
from __future__ import annotations

from pathlib import Path
import numpy as np

from src.validation import validate_bhsi_layers


def create_bhsi_data_cube(layer_paths: dict[str, Path], output_path: Path) -> Path:
    """Write aligned BHSI layers as a compressed NetCDF data cube.

    The cube retains the analysis grid and layer names, giving students one
    portable file to inspect with Python, R, GIS software, or the dashboard.
    """
    import rasterio
    import xarray as xr

    validate_bhsi_layers(layer_paths, set(layer_paths))
    names = list(layer_paths)
    with rasterio.open(layer_paths[names[0]]) as first:
        transform, crs = first.transform, str(first.crs)
        height, width = first.height, first.width

    data = {}
    for name, path in layer_paths.items():
        with rasterio.open(path) as src:
            data[name] = (("y", "x"), src.read(1).astype(np.float32))

    x = transform.c + (np.arange(width) + 0.5) * transform.a
    y = transform.f + (np.arange(height) + 0.5) * transform.e
    dataset = xr.Dataset(
        data,
        coords={"x": x, "y": y},
        attrs={
            "title": "Pine Ridge Bison Habitat Suitability data cube",
            "crs": crs,
            "grid_resolution_m": abs(transform.a),
            "governance_note": "Review with OLC and appropriate Oglala Lakota Nation offices before external distribution.",
        },
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    encoding = {name: {"zlib": True, "complevel": 4, "dtype": "float32"} for name in data}
    dataset.to_netcdf(output_path, encoding=encoding)
    return output_path
