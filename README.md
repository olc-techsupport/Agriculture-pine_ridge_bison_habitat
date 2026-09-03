# Pine Ridge Bison Habitat Suitability Analysis
**Author:** Lilly Jones, PhD, Daear Consulting, LLC
**Developed for:** Oglala Lakota College (OLC)  
**Territory:** Pine Ridge Reservation, Oglala Lakota Nation  
**License:**  Apache 2.0 (code; review of other materials is pending)                                                                                    
**Funding**: This material was developed as part of a project funded by the USDA National Institute of Food and Agriculture (NIFA).                       
**Project role**: Daear Consulting LLC developed the geospatial code, workflows, and documentation under contract to Oglala Lakota College.                                                                                                                      

## Data Sovereignty and Governance (draft under review)
This repository contains workflows developed for use in support of Oglala Lakota College and Oglala Sioux Tribe–related research, education, and data activities. Public availability of code or documentation does not imply that Tribal data, knowledge, or derived information are open or unrestricted. Use of Tribal data and knowledge remains subject to applicable Tribal governance, permissions, protocols, and data sovereignty requirements.

## Purpose
This repository provides an educational, reproducible, spatially explicit
screening analysis of potential bison habitat conditions across the Pine Ridge
Census statistical boundary. It is intended to support learning and locally
authorized discussion; it does not represent an approved OST or OLC habitat
assessment or restoration plan.

Bison and Pte Oyate have cultural, ecological, food-system, and stewardship
significance that cannot be defined by this repository. Cultural framing,
terminology, and intended uses remain subject to review by the appropriate
OLC/OST authorities. The model asks how selected public environmental layers
behave under transparent assumptions; it does not determine where bison belong.

## What This Repository Produces
**Bison Habitat Suitability Index (BHSI)** is a pixel-level composite
score (0–1) across the full Pine Ridge Reservation, synthesizing:
- Vegetation condition and type (NDVI and NLCD land cover)
- Soil grazing capacity (gSSURGO)
- Topographic suitability (slope, aspect)
- Water access (distance to streams, ponds, springs)
- Climate stress (heat days, precipitation trends)

**Candidate connected regions** are contiguous groups of high-BHSI pixels
identified by memory-efficient eight-neighbor raster labeling, summarized by composite score and
accompanied by a summary table of area, water access, soils quality, and
current land cover. They are not approved priorities or viable management
units. See `documents/methods_contiguous_patches.md` for the full
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
| 07 | Bison Habitat Suitability Index | Screening raster and candidate connected regions |

## Data Sources
Source data and generated outputs are downloaded or created at runtime and are
ignored by Git. The notebooks themselves are committed without saved execution
outputs. See `outputs/artifact_manifest.csv` for the expected products and
their review status.

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

Run the automated quality checks before and after changing the workflow:

```powershell
python -m pytest
```

Continuous integration runs the same checks for pushes and pull requests.

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
pixels, vary spatially, and match exactly on CRS, extent, transform, and shape.
Uniform fallback layers are rejected because they cannot distinguish candidate
regions. Notebook 07 also writes
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
│   ├── methods_contiguous_patches.md
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

Biological, cultural, spatial, climate, and management assumptions are tracked
in `documents/assumptions_register.md`. Values in `src/constants.py` are
transparent teaching defaults unless that register identifies reviewed
evidence and an approved use.

## OLC learning and community tools

After notebooks 02–07 finish, build a compact NetCDF data cube containing the
aligned component layers and composite BHSI:

```bash
conda run -n pine-ridge-bison python build_data_cube.py
```

The resulting `outputs/pine_ridge_bhsi_cube.nc` is suitable for introductory
Python/R/GIS exploration. For a no-code local map explorer, install the
environment and, from this inner repository folder, run:

```powershell
conda run -n pine-ridge-bison python -m streamlit run dashboard/app.py --server.address=127.0.0.1 --server.port=8501 --browser.gatherUsageStats=false
```

This portable command works after cloning the GitHub repository and does not
contain a machine-specific installation path. It does not require
`conda activate`; Conda only needs to be installed and available in the
terminal. The final option suppresses Streamlit's optional first-run email
prompt. When it starts,
Streamlit prints a local address. Open `http://127.0.0.1:8501` in a browser;
this is the address configured by the command above. Keep the terminal window
open while using the dashboard; press `Ctrl+C` there to stop it.

GitHub stores and distributes the project but does not run Streamlit apps
directly. To give visitors a dashboard they can open without cloning the
repository, deploy `dashboard/app.py` to a Streamlit-compatible hosting service
and add the public dashboard URL here.

See `documents/olc_learning_lab.md` for course activities, research questions,
and further-study ideas. Instructors should also use
`documents/facilitator_guide.md` and `documents/learning_design.md`. These tools
follow the same governance and review requirements as the analysis outputs.

## Data Sovereignty
This analysis uses public data describing Oglala Lakota lands and ecological
context. The locally applicable governance approach remains under review.
Reference points under consideration include:

- **CARE Principles** : Collective Benefit, Authority to Control,
  Responsibility, Ethics
- **FAIR Principles** : Findable, Accessible, Interoperable, Reusable
- **IEEE 2890-2025** : Recommended Practice for Provenance of
  Indigenous Peoples' Data

Naming a framework does not imply that OST or OLC has adopted it. OCAP® may be
considered but originated in a Canadian First Nations context and must not be
treated as locally adopted without confirmation. Precise candidate-region
outputs must not be distributed externally until the appropriate OLC/OST
authority and review process are confirmed and approval is recorded.

See `documents/data_sovereignty.md` for the full governance framework.
