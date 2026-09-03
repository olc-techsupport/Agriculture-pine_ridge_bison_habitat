from __future__ import annotations

"""Validation helpers for BHSI inputs and patch outputs."""

from pathlib import Path
import numpy as np


def validate_bhsi_layers(
    layer_paths: dict[str, Path],
    expected_keys: set[str],
    *,
    require_spatial_variation: bool = True,
) -> dict[str, dict[str, float | int | bool]]:
    """Validate completeness, grid alignment, and spatial evidence.

    Uniform fallback layers are useful for demonstrating mechanics but cannot
    distinguish candidate patches. They are rejected by default.
    """
    import rasterio

    missing = expected_keys - set(layer_paths)
    if missing:
        raise FileNotFoundError("Missing required BHSI layers: " + ", ".join(sorted(missing)))

    reference = None
    diagnostics = {}
    for name in sorted(expected_keys):
        path = Path(layer_paths[name])
        if not path.exists():
            raise FileNotFoundError(f"BHSI layer does not exist: {path}")
        with rasterio.open(path) as src:
            grid = (src.crs, src.transform, src.width, src.height)
            data = src.read(1, masked=True)
            if data.count() == 0:
                raise ValueError(f"BHSI layer contains no valid pixels: {name} ({path})")
            values = data.compressed().astype(float)
            spatial_std = float(np.nanstd(values))
            unique_count = int(np.unique(values).size)
            has_spatial_variation = unique_count > 1 and spatial_std > 1e-12
            diagnostics[name] = {
                "valid_pixels": int(values.size),
                "unique_values": unique_count,
                "spatial_std": spatial_std,
                "spatially_varying": has_spatial_variation,
            }
            if require_spatial_variation and not has_spatial_variation:
                raise ValueError(
                    f"BHSI layer is spatially uniform and cannot rank patches: {name} ({path})"
                )
        if reference is None:
            reference = grid
        elif grid != reference:
            raise ValueError(f"BHSI layer grid does not match the reference grid: {name}")
    return diagnostics


def retain_minimum_area_clusters(labels: np.ndarray, pixel_area_acres: float, minimum_acres: float) -> np.ndarray:
    """Mark labeled regions smaller than ``minimum_acres`` as background (-1)."""
    filtered = labels.copy()
    for label in np.unique(labels):
        if label >= 0 and (labels == label).sum() * pixel_area_acres < minimum_acres:
            filtered[labels == label] = -1
    return filtered
