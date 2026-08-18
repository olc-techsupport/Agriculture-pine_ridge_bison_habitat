# Habitat Patch Identification: Why DBSCAN

## The Problem
The Bison Habitat Suitability Index (BHSI) produces a continuous raster where
every pixel has a score from 0 to 1. But a pixel-level score is not
actionable for a land management program. What OLC and the Oglala Lakota
Nation's bison program need is an answer to a different question:

> **Which contiguous areas of land are viable for bison management,
> and how should they be prioritized?**

This requires grouping high-scoring pixels into meaningful patches with
areas large enough to support a herd, contiguous enough to allow ranging,
and distinct enough from neighboring lower-quality land to be managed
as a unit.

## Algorithm Comparison
| Algorithm | Why it doesn't fit |
|---|---|
| **K-means** | Requires specifying number of clusters in advance, but we don't know how many viable habitat patches exist on Pine Ridge before running the analysis |
| **Hierarchical clustering** | Computationally expensive at raster pixel scale; the resulting dendrogram doesn't produce ecologically intuitive habitat patches |
| **Watershed segmentation** | Designed for image edge detection, not ecological suitability gradients |
| **Simple thresholding** | Produces binary in/out classification that cannot rank patches or exclude isolated pixels that don't form viable units |
| **DBSCAN** | Best fit: see rationale below |

## Why DBSCAN
**DBSCAN** (Density-Based Spatial Clustering of Applications with Noise)
identifies clusters based on spatial density rather than distance to
centroids or a predetermined count. For bison habitat, this means:

**1. No predetermined cluster count**  
DBSCAN finds however many contiguous high-suitability patches actually
exist on the landscape. We do not need to guess in advance.

**2. Noise handling**  
Isolated high-scoring pixels that don't form viable patches are labeled
as noise (class -1) rather than forced into a cluster. A single high-BHSI
pixel surrounded by cropland is not a restoration candidate, so DBSCAN
correctly excludes it from the ranked list.

**3. Shape agnostic**  
Bison habitat patches follow terrain, vegetation patterns, and water
availability, not circular or convex shapes. DBSCAN handles irregular,
elongated patches naturally because it defines clusters by density
continuity, not geometric shape.

**4. Two interpretable parameters**  
The two parameters that control DBSCAN can be explained directly to
land managers:

- **`eps`** is the maximum distance between high-suitability pixels
  for them to be considered part of the same patch. We set this to
  **1,000 meters** (~0.6 miles), roughly the distance a bison moves
  in a day during normal grazing. Two high-BHSI areas separated by
  more than 1km are treated as distinct management units.

- **`min_samples`** is the minimum number of contiguous pixels required
  to constitute a viable patch. We set this to correspond to
  **500 acres** (the default minimum viable bison management unit).
  At 30m resolution, 500 acres ≈ 220 pixels. Smaller patches are
  labeled noise and excluded from the priority ranking.

## Parameter Tuning
The `eps` and `min_samples` defaults are starting points, not fixed values.
They should be reviewed with the OLC bison program:

**`DBSCAN_EPS_M = 1000` (meters)**  
Increase if you want to connect nearby patches into a single unit
(ex. for a large contiguous management block).
Decrease if you want to distinguish smaller adjacent units.

**`DBSCAN_MIN_ACRES = 500`**  
This is a biological and management question:
- What is the minimum land area for a starter bison herd?
- What is the minimum area that can be economically fenced and managed?

If OST's program considers 250 acres viable for an initial herd,
set `DBSCAN_MIN_ACRES = 250`. The analysis recalculates automatically.

Both parameters are defined in `src/constants.py` and can be changed
without modifying any notebook code.

## Implementation
DBSCAN runs on the geographic coordinates of high-suitability pixels
(those in the top 30% of BHSI scores), not on the full raster. This
keeps the computation tractable without requiring downsampling.

```python
from sklearn.cluster import DBSCAN
import numpy as np

# Get coordinates of high-suitability pixels
threshold   = np.nanpercentile(bhsi_array, BHSI_THRESHOLD_PCT)
high_suit   = bhsi_array > threshold
rows, cols  = np.where(high_suit & ~np.isnan(bhsi_array))

# Convert pixel indices to projected coordinates (meters, EPSG:5070)
xs = transform.c + cols * transform.a    # easting
ys = transform.f + rows * transform.e    # northing
coords = np.column_stack([xs, ys])

# Compute min_samples from acres threshold
pixel_area_acres = (TARGET_RES_M ** 2) / 4046.86
min_samples      = max(10, int(DBSCAN_MIN_ACRES/pixel_area_acres))

db     = DBSCAN(eps=DBSCAN_EPS_M, min_samples=min_samples,
                algorithm="ball_tree", metric="euclidean").fit(coords)
labels = db.labels_
# label == -1 = noise (isolated pixels, not viable patches)
# label >= 0  = viable patch ID
```

## Patch Ranking
Each cluster identified by DBSCAN is ranked by a composite of:

1. **Mean BHSI score** (40%) the overall habitat quality
2. **Water access sub-score** (25%) the proximity to water (critical constraint)
3. **Soils grazing capacity** (20%) the land's sustained carrying capacity
4. **Area in acres** (15%) larger patches preferred for management flexibility

This ranking is produced as a summary table in notebook 07 and exported
as a GeoPackage file for use in GIS.

## Limitations
- DBSCAN identifies patches based on spatial contiguity and BHSI score.
  It does not account for land ownership, existing fencing infrastructure,
  road crossings, or other non-ecological constraints on management.
  These must be layered on top of the analysis results.

- The analysis uses a single BHSI threshold (top 30%) to define
  "high suitability." Lowering this threshold will identify more but
  lower-quality patches; raising it will produce fewer, higher-quality
  patches. Sensitivity to this choice should be explored.

- Bison ranging behavior is more complex than the simple `eps` parameter
  captures. Seasonal movements, water-seeking behavior, and social
  dynamics of the herd are not modeled. The patch analysis is a
  landscape-level starting point for a conversation with the bison
  program, not a final management prescription.

## References
- Ester, M., Kriegel, H.-P., Sander, J., & Xu, X. (1996). A density-based
  algorithm for discovering clusters in large spatial databases with noise.
  *KDD-96 Proceedings*, 226–231.

- Scikit-learn DBSCAN documentation:
  https://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html

- Steenweg, R., Hebblewhite, M., Gummer, D., Low, B., and Hunt, B. (2016).
  Assessing Potential Habitat and Carrying Capacity for Reintroduction of
  Plains Bison (*Bison bison bison*) in Banff National Park.
  *PLOS ONE*. doi:10.1371/journal.pone.0150065
  HSI model for plains bison reintroduction, carrying
  capacity estimation from forage and terrain data.

- Freese, C.H. et al. (2022). The Potential of Bison Restoration as an
  Ecological Approach to Future Tribal Food Sovereignty on the Northern
  Great Plains. *Frontiers in Ecology and Evolution*.
  doi:10.3389/fevo.2022.826282
  HSI analysis of bison habitat on Northern Great Plains
  Tribal reservations including Rosebud; estimates 1,828–4,354 km² of
  additional suitable habitat on reviewed Tribal lands. 
