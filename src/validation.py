"""Validation helpers for BHSI inputs and patch outputs."""
from __future__ import annotations

from pathlib import Path
import numpy as np


def validate_bhsi_layers(layer_paths: dict[str, Path], expected_keys: set[str]) -> None:
    """Fail early unless every component is valid and on one common raster grid."""
    import rasterio

    missing = expected_keys - set(layer_paths)
    if missing:
        raise FileNotFoundError("Missing required BHSI layers: " + ", ".join(sorted(missing)))

    reference = None
    for name in sorted(expected_keys):
        path = Path(layer_paths[name])
        if not path.exists():
            raise FileNotFoundError(f"BHSI layer does not exist: {path}")
        with rasterio.open(path) as src:
            grid = (src.crs, src.transform, src.width, src.height)
            data = src.read(1, masked=True)
            if data.count() == 0:
                raise ValueError(f"BHSI layer contains no valid pixels: {name} ({path})")
        if reference is None:
            reference = grid
        elif grid != reference:
            raise ValueError(f"BHSI layer grid does not match the reference grid: {name}")


def retain_minimum_area_clusters(labels: np.ndarray, pixel_area_acres: float, minimum_acres: float) -> np.ndarray:
    """Mark DBSCAN clusters smaller than ``minimum_acres`` as noise (-1)."""
    filtered = labels.copy()
    for label in np.unique(labels):
        if label >= 0 and (labels == label).sum() * pixel_area_acres < minimum_acres:
            filtered[labels == label] = -1
    return filtered
