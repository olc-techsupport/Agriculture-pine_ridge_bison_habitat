# Pine Ridge Bison Habitat Suitability Analysis
**Author:** Lilly Jones, PhD, Daear Consulting, LLC
**Partner:** Oglala Lakota College (OLC)  
**Territory:** Pine Ridge Reservation, Oglala Lakota Nation  
**License:**  Apache 2.0

## Purpose
This repository supports the Oglala Lakota Nation's bison habitat restoration
program by providing a reproducible, spatially explicit assessment of land
suitability for bison across the full Pine Ridge Reservation.

Bison are not just a wildlife management objective. For the Oglala Lakota,
bison (Pte Oyate) are central to cultural identity, food sovereignty, and
land stewardship. Restoring bison habitat to Pine Ridge is an act of ecological
and cultural restoration simultaneously. This analysis is designed to
support that work by identifying which lands are most ready, which need
investment before they can carry herds, and how climate change will affect
habitat capacity over time.

## What This Repository Produces
**Bison Habitat Suitability Index (BHSI)** is a pixel-level composite
score (0–1) across the full Pine Ridge Reservation, synthesizing:
- Vegetation condition and type (NDVI and NLCD land cover)
- Soil grazing capacity (gSSURGO)
- Topographic suitability (slope, aspect)
- Water access (distance to streams, ponds, springs)
- Climate stress (heat days, precipitation trends)

**Priority restoration units** are viable bison habitat patches identified
by DBSCAN clustering of high-BHSI pixels, ranked by composite score and
accompanied by a summary table of area, water access, soils quality, and
current land cover. See `documents/methods_clustering.md` for the full
rationale for this approach.

## Notebooks
| Notebook | Topic | Outputs |
|---|---|---|
| 01 | Study area and data inventory | Pine Ridge boundary, data coverage map |
| 02 | Vegetation condition | NDVI trend, land cover classification |
| 03 | Soils and grazing capacity | gSSURGO grazing capacity surface |
| 04 | Topography | Slope, aspect, terrain suitability |
| 05 | Water access | Distance-to-water raster |
| 06 | Climate stress | Heat days, precip projections (MACAv2) |
| 07 | Bison Habitat Suitability Index | BHSI raster and priority restoration units |

## Data Sources
All data is downloaded at runtime and cached to `data/cache/`. Nothing
is committed to this repository.

| Source | What | Notebook |
|---|---|---|
| Census TIGER AIANNH | Pine Ridge boundary | 01 |
| MODIS MOD13Q1 via ORNL DAAC | NDVI time series | 02 |
| NLCD 2021 via MRLC | Land cover | 02 |
| USDA gSSURGO via SoilDataAccess | Grazing capacity | 03 |
| USGS 3DEP (1/3 arc-second) | Elevation model | 04 |
| USGS NHD | Streams, water bodies | 05 |
| MACAv2-METDATA via OPeNDAP | Climate projections | 06 |

## Quick Start
```bash
# Clone
git clone https://github.com/your-org/pine_ridge_bison_habitat
cd pine_ridge_bison_habitat

# Environment
conda env create -f environment.yml
conda activate pine-ridge-bison
python -m ipykernel install --user --name pine-ridge-bison \
    --display-name "Python (pine-ridge-bison)"

# Launch
jupyter lab notebooks/
```

Run notebooks in order 01 through 07. Each notebook exports intermediate
results to `outputs/` that the next notebook loads.

### Use the project Python environment

This project requires its Conda environment (`pine-ridge-bison`, Python 3.11).
Do not run its scripts with a system/global Python interpreter; it may not
have the required scientific packages.

Before running any terminal command, make sure you are in the **project root**:
the folder that contains `README.md`, `environment.yml`, `notebooks/`, and
`build_data_cube.py`. After cloning, change into the folder Git created (usually
named `pine_ridge_bison_habitat`). Do not copy a path from this README; your
own clone may be in a different location.

```powershell
Get-Location
Get-ChildItem README.md, environment.yml, build_data_cube.py
```

If that command lists all three files, you are in the correct folder. If it
reports one or more files are missing, find the project root automatically
from your current folder:

```powershell
$projectRoot = Get-ChildItem -Path . -Filter build_data_cube.py -File -Recurse |
    Select-Object -First 1 -ExpandProperty DirectoryName
Set-Location $projectRoot
Get-ChildItem README.md, environment.yml, build_data_cube.py
```

If `$projectRoot` is blank, you are not in the cloned project or one of its
parent folders. Navigate to the folder that contains your clone and run the
same command again.

From the inner repository folder, either activate the environment:

```powershell
conda activate pine-ridge-bison
python build_data_cube.py
```

or run a single command without activating it:

```powershell
conda run -n pine-ridge-bison python build_data_cube.py
```

In VS Code, select **Python (pine-ridge-bison)** as the notebook kernel and
Python interpreter before running notebooks or scripts.

Notebook 07 stops unless all five component rasters exist, contain valid
pixels, and match exactly on CRS, extent, transform, and shape. It also writes
`outputs/bhsi_provenance.json` with input hashes, parameters, weights, code
revision, and the required governance review status.

## Repository Structure
```
pine_ridge_bison_habitat/
├── notebooks/
│   ├── 01_study_area.ipynb
│   ├── 02_vegetation.ipynb
│   ├── 03_soils.ipynb
│   ├── 04_topography.ipynb
│   ├── 05_water_access.ipynb
│   ├── 06_climate_stress.ipynb
│   └── 07_habitat_suitability_index.ipynb
├── src/
│   ├── loaders.py           # Data download and cache functions
│   ├── raster_utils.py      # Raster alignment, resampling, normalization
│   ├── constants.py         # Bounding box, CRS, paths, weights
│   └── sovereignty.py       # Data governance acknowledgment
├── data/
│   └── cache/               # GITIGNORED: downloaded datasets
├── outputs/                 # GITIGNORED: intermediate and final products
│   └── figures/
├── documents/
│   ├── data_sovereignty.md
│   ├── methods_clustering.md
│   └── bhsi_weights.md
├── environment.yml
├── .gitignore
└── README.md
```

## Current analytical limits
The soils and climate notebooks currently create reservation-wide planning
scores when only tabular or point data are available. They must not be
interpreted as within-reservation variation or used alone to rank patches.
Before a management decision, replace them with gridded gSSURGO map-unit and
downscaled climate inputs, review thresholds and weights with the bison
program, then ground-truth candidate units.

## OLC learning and community tools

After notebooks 02–07 finish, build a compact NetCDF data cube containing the
aligned component layers and composite BHSI:

```bash
conda run -n pine-ridge-bison python build_data_cube.py
```

The resulting `outputs/pine_ridge_bhsi_cube.nc` is suitable for introductory
Python/R/GIS exploration. For a no-code local map explorer, install the
environment and run:

```bash
conda run -n pine-ridge-bison streamlit run dashboard/app.py
```

See `documents/olc_learning_lab.md` for course activities, research questions,
and further-study ideas. These tools follow the same governance and review
requirements as the analysis outputs.

## Data Sovereignty
This analysis describes Oglala Lakota land for Oglala Lakota land
restoration purposes. It is governed by:

- **OCAP®** : Ownership, Control, Access, Possession
- **CARE Principles** : Collective Benefit, Authority to Control,
  Responsibility, Ethics
- **FAIR Principles** : Findable, Accessible, Interoperable, Reusable
- **IEEE 2890-2025** : Recommended Practice for Provenance of
  Indigenous Peoples' Data

All analysis results should be shared with the Oglala Lakota College
Math and Science department and the relevant Oglala Lakota Nation land
management offices before any external distribution.

See `documents/data_sovereignty.md` for the full governance framework.

## Citation
Jones, L. (2025). Pine Ridge Bison Habitat Suitability Analysis.
Daear Consulting, LLC, in partnership with
Oglala Lakota College Cubedynamics Project.
