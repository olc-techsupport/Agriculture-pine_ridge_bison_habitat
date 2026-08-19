"""Memory-safe raster patch identification for BHSI priority units."""
from __future__ import annotations

import numpy as np


def label_habitat_patches(
    high_suitability: np.ndarray,
    pixel_area_acres: float,
    minimum_acres: float,
) -> tuple[np.ndarray, int]:
    """Label contiguous high-suitability regions and remove undersized patches.

    Uses 8-neighbor raster connectivity, avoiding DBSCAN's large coordinate and
    neighbor-graph allocations.  Labels are sequential positive integers; zero
    represents background or a patch below ``minimum_acres``.
    """
    from scipy import ndimage

    labels, count = ndimage.label(high_suitability, structure=np.ones((3, 3), dtype=np.uint8))
    if count == 0:
        return labels.astype(np.int32), 0
    counts = np.bincount(labels.ravel())
    keep = counts * pixel_area_acres >= minimum_acres
    keep[0] = False
    labels[~keep[labels]] = 0
    labels, count = ndimage.label(labels > 0, structure=np.ones((3, 3), dtype=np.uint8))
    return labels.astype(np.int32), int(count)
