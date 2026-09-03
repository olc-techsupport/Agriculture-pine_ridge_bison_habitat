from __future__ import annotations

import ast
import json
from pathlib import Path

import numpy as np
import pytest

from src.constants import BHSI_WEIGHTS
from src.patches import label_habitat_patches
from src.provenance import write_bhsi_manifest
from src.validation import validate_bhsi_layers

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = sorted((ROOT / "notebooks").glob("[0-9][0-9]_*.ipynb"))
MARKERS = ("## Learning Objectives", "## Prerequisites and Timing", "## Governance Checkpoint", "## Learner Checkpoint", "## Interpretation Protocol", "## Contribution Activity")


def test_series_is_ordered_and_instructionally_scaffolded() -> None:
    assert [path.name[:2] for path in NOTEBOOKS] == [f"{number:02d}" for number in range(1, 8)]
    for path in NOTEBOOKS:
        notebook = json.loads(path.read_text(encoding="utf-8"))
        markdown = "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"] if cell["cell_type"] == "markdown")
        assert all(marker in markdown for marker in MARKERS)
        assert all(cell.get("id") for cell in notebook["cells"])


def test_notebooks_are_clean_and_code_parses() -> None:
    for path in NOTEBOOKS:
        notebook = json.loads(path.read_text(encoding="utf-8"))
        code = []
        for cell in notebook["cells"]:
            if cell["cell_type"] == "code":
                assert cell.get("execution_count") is None
                assert cell.get("outputs", []) == []
                code.extend(line for line in "".join(cell.get("source", [])).splitlines() if not line.lstrip().startswith(("%", "!")))
        ast.parse("\n".join(code), filename=path.name)


def test_removed_memory_intensive_method_is_not_part_of_the_series() -> None:
    removed_name = "DB" + "SCAN"
    relevant = [ROOT/"README.md", ROOT/"src"/"constants.py", ROOT/"src"/"patches.py", ROOT/"documents"/"methods_contiguous_patches.md"] + NOTEBOOKS
    assert all(removed_name not in path.read_text(encoding="utf-8") for path in relevant)


def test_weights_sum_to_one() -> None:
    assert sum(BHSI_WEIGHTS.values()) == pytest.approx(1.0)


def test_connected_components_respect_minimum_area() -> None:
    mask = np.zeros((8, 8), dtype=bool)
    mask[0:2, 0:2] = True
    mask[4:8, 4:8] = True
    labels, count = label_habitat_patches(mask, pixel_area_acres=1.0, minimum_acres=5.0)
    assert count == 1
    assert np.all(labels[0:2, 0:2] == 0)
    assert np.all(labels[4:8, 4:8] == 1)


def _write_raster(path: Path, values: np.ndarray) -> None:
    import rasterio
    from rasterio.transform import from_origin

    with rasterio.open(path, "w", driver="GTiff", height=values.shape[0], width=values.shape[1], count=1, dtype="float32", crs="EPSG:5070", transform=from_origin(0, 60, 30, 30), nodata=np.nan) as dst:
        dst.write(values.astype("float32"), 1)


def test_uniform_fallback_is_rejected(tmp_path: Path) -> None:
    path = tmp_path/"uniform.tif"
    _write_raster(path, np.full((2, 2), 0.5))
    with pytest.raises(ValueError, match="spatially uniform"):
        validate_bhsi_layers({"soils": path}, {"soils"})


def test_spatial_diagnostics_enter_provenance(tmp_path: Path) -> None:
    path = tmp_path / "varying.tif"
    _write_raster(path, np.array([[0.1, 0.2], [0.3, 0.4]]))
    diagnostics = validate_bhsi_layers({"vegetation": path}, {"vegetation"})
    output = write_bhsi_manifest(tmp_path / "manifest.json", {"vegetation": path}, {"patch_method": "eight-neighbor raster connected components"}, diagnostics)
    manifest = json.loads(output.read_text(encoding="utf-8"))
    assert manifest["inputs"]["vegetation"]["spatially_varying"] is True
    assert manifest["inputs"]["vegetation"]["fallback"] is False
    assert manifest["governance"]["external_distribution_authorized"] is False
