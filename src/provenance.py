"""Write a reproducible, reviewable manifest for BHSI outputs."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess

from src.constants import BHSI_WEIGHTS, CRS_PROJECTED, TARGET_RES_M


def write_bhsi_manifest(output_path: Path, layer_paths: dict[str, Path], parameters: dict) -> Path:
    """Write input paths, hashes, grid settings, and review status beside BHSI outputs."""
    import hashlib

    def digest(path: Path) -> str:
        h = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                h.update(block)
        return h.hexdigest()

    repo_root = Path(__file__).resolve().parents[1]
    try:
        revision = subprocess.check_output(["git", "-C", str(repo_root), "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        revision = "unavailable"
    manifest = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_revision": revision,
        "analysis_grid": {"crs": CRS_PROJECTED, "resolution_m": TARGET_RES_M},
        "weights": BHSI_WEIGHTS,
        "parameters": parameters,
        "inputs": {name: {"path": str(path), "sha256": digest(path)} for name, path in layer_paths.items()},
        "governance": {
            "external_distribution_authorized": False,
            "required_review": "OLC Cubedynamics and appropriate Oglala Lakota Nation offices",
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return output_path
