from __future__ import annotations

"""Apply the common NIFA-aligned structure to the bison notebook series."""

import json
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ROOT / "notebooks"

MODULES = {
    "01": ("distinguish a Census statistical boundary from legal jurisdiction and community-defined lands; create and inspect a common raster grid; document source coverage", "Choose one boundary or grid assumption and state what it represents and one claim it cannot support.", "Improve one boundary caveat, source note, or grid explanation."),
    "02": ("interpret satellite land-cover classes and NDVI summaries; identify classification and scale limitations; compare mapped vegetation with evidence needed from the land", "Choose one vegetation class and record its source, date, resolution, assigned score, and evidence needed to evaluate forage condition.", "Improve one class rationale, citation, legend, or uncertainty statement."),
    "03": ("distinguish tabular context from spatial patch evidence; explain why a uniform score cannot rank locations; inspect soil attributes and missingness", "Demonstrate why a uniform layer has zero spatial variation and explain why notebook 07 rejects it.", "Improve one attribute definition, unit, crosswalk rationale, or fallback warning."),
    "04": ("derive slope from elevation; evaluate effects of resolution and resampling; distinguish a terrain score from observed bison movement", "Change one slope threshold hypothetically and identify what changes and what evidence would be needed to justify the change.", "Improve one resolution note, slope citation, threshold label, or limitation."),
    "05": ("construct a distance surface; distinguish mapped water from reliable and accessible water; identify seasonal and infrastructure evidence needed", "Inspect one mapped water feature and list what the dataset cannot tell you about reliability, quality, access, or seasonality.", "Improve one source caveat, distance assumption, legend, or validation question."),
    "06": ("distinguish a model scenario, projection, and forecast; evaluate spatial and threshold assumptions; communicate climate uncertainty", "Rewrite one result naming model, scenario, period, spatial representation, threshold source, and major uncertainty.", "Improve one uncertainty statement, period label, threshold citation, or multi-model recommendation."),
    "07": ("explain weighted overlay and raster connected components; test sensitivity to weights and patch parameters; identify review and release gates", "Trace one connected region back through its five inputs and list every assumption and missing decision constraint.", "Improve one sensitivity check, provenance field, release warning, or plain-language interpretation."),
}


def md(text: str) -> dict:
    lines = text.strip().splitlines()
    return {"cell_type": "markdown", "metadata": {}, "id": uuid.uuid4().hex[:8], "source": [line + "\n" for line in lines[:-1]] + [lines[-1]]}


def opening(outcomes: str) -> str:
    objectives = "\n".join(f"- {item.strip()}" for item in outcomes.split(";"))
    return f"""
## Learning Objectives

By the end of this notebook, learners will be able to:

{objectives}

## Prerequisites and Timing

Allow 75–100 minutes. Activate the project environment, read the draft governance statement, and complete the preceding notebook where applicable. Work in pairs and rotate analyst, data-steward, skeptic, and documentarian roles.

## Governance Checkpoint

This notebook uses public data describing Oglala Lakota lands and ecological context. Public availability does not authorize every interpretation or release. Do not add restricted data, precise sensitive locations, tenure information, or community knowledge. Outputs remain educational screening products pending the appropriate OLC/OST review.
"""


def closing(checkpoint: str, contribution: str, number: str) -> str:
    next_text = "Proceed to the next numbered notebook." if number != "07" else "Document one result, its evidence chain, assumptions, limitations, and required decision authority."
    return f"""
## Learner Checkpoint

{checkpoint}

## Interpretation Protocol

Separate **observation** (what the public data and computation show) from **interpretation** (a plausible explanation), **additional evidence** (literature, field observation, local expertise, or validation needed), and **decision authority** (who may approve release, parameters, priorities, or action). Do not convert a class, score, threshold, scenario, or connected region into a cultural, biological, management, or policy conclusion.

## Contribution Activity

{contribution} Review the change with a partner and record what became clearer or more defensible.

## Evidence Record and Next Step

Record one regenerated result, source and scale, transformation, assumption, limitation, and question requiring more evidence or local knowledge. {next_text}
"""


def main() -> None:
    for path in sorted(NOTEBOOKS.glob("[0-9][0-9]_*.ipynb")):
        number = path.name[:2]
        notebook = json.loads(path.read_text(encoding="utf-8"))
        cells = []
        for cell in notebook["cells"]:
            source = "".join(cell.get("source", []))
            if cell.get("cell_type") == "markdown" and any(marker in source for marker in ("## Learning Objectives", "## Learner Checkpoint")):
                continue
            source = source.replace("The uniform score is appropriate for a first-pass BHSI.", "A uniform score is demonstration-only and is rejected by notebook 07 because it cannot distinguish patches.")
            source = source.replace("Priority Restoration Units", "Candidate Connected Regions")
            source = source.replace("priority restoration units", "candidate connected regions")
            source = source.replace("TOP 15 PRIORITY RESTORATION UNITS", "TOP 15 CANDIDATE CONNECTED REGIONS (SCREENING ONLY)")
            source = source.replace("  HIGH: Substantial portion of Pine Ridge is suitable or restorable.", "  Mean score is at least 0.6 under the current unapproved assumptions.")
            source = source.replace("  MODERATE: Significant habitat exists with restoration investment needed.", "  Mean score is between 0.4 and 0.6 under the current unapproved assumptions.")
            source = source.replace("  LOW: Most land requires restoration: identify priority patches first.", "  Mean score is below 0.4 under the current unapproved assumptions.")
            source = source.replace("validate_bhsi_layers(available, set(LAYER_PATHS))", "layer_diagnostics = validate_bhsi_layers(available, set(LAYER_PATHS))")
            source = source.replace("validate_bhsi_layers(available, set(BHSI_WEIGHTS))", "layer_diagnostics = validate_bhsi_layers(available, set(BHSI_WEIGHTS))")
            while "layer_diagnostics = layer_diagnostics =" in source:
                source = source.replace("layer_diagnostics = layer_diagnostics =", "layer_diagnostics =")
            source = source.replace("{\"threshold_percentile\": BHSI_THRESHOLD_PCT,\n         \"minimum_patch_acres\": MIN_PATCH_ACRES}\n    )", "{\"threshold_percentile\": BHSI_THRESHOLD_PCT,\n         \"minimum_patch_acres\": MIN_PATCH_ACRES,\n         \"patch_method\": \"eight-neighbor raster connected components\"},\n        layer_diagnostics=layer_diagnostics,\n    )")
            if cell.get("source"):
                cell["source"] = source.splitlines(keepends=True)
            if cell.get("cell_type") == "code":
                cell["execution_count"] = None
                cell["outputs"] = []
            cell.setdefault("id", uuid.uuid4().hex[:8])
            cells.append(cell)
        outcomes, checkpoint, contribution = MODULES[number]
        cells.insert(1, md(opening(outcomes)))
        cells.append(md(closing(checkpoint, contribution, number)))
        notebook["cells"] = cells
        path.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
