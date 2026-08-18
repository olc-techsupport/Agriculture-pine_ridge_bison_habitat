# BHSI Component Weights: Rationale and Sensitivity

## Overview
The Bison Habitat Suitability Index (BHSI) combines five data layers
into a single score. Each layer contributes according to a weight that
reflects its relative importance for bison habitat quality on Pine Ridge.

**Release condition:** a component may distinguish priority patches only when
it is spatially resolved across the reservation. A reservation-wide fallback
score is planning context, not patch-scale evidence; see
`limitations_and_review.md` before presenting results externally.

Default weights (defined in `src/constants.py`):

| Component | Weight | Rationale |
|---|---|---|
| Vegetation | 30% | Dominant factor : forage availability determines carrying capacity |
| Water access | 25% | Hard constraint : bison must drink daily; distance to water limits ranging |
| Soils | 20% | Sustained productivity : grazing capacity determines long-term herd size |
| Topography | 15% | Terrain preference : bison avoid steep slopes for grazing and movement |
| Climate stress | 10% | Future planning : projects how heat and precipitation change will affect habitat |

## Component Rationale

### Vegetation (30%)
Forage availability is the primary determinant of bison habitat quality.
Bison on the Northern Great Plains evolved with mixed-grass prairie which is
a complex of grasses, forbs, and sedges that provides year-round nutrition
when managed appropriately.

NLCD land cover class determines the base vegetation suitability score:
- Native grassland (class 71) receives full weight (1.0)
- Pasture/hay (class 81) receives partial weight (0.60) is manageable
  but lacking the species diversity of native prairie
- Cropland (class 82) receives minimal weight (0.10) as this requires
  restoration before supporting bison

NDVI trend from MODIS adjusts the vegetation score:
- Sustained positive NDVI trend triggers a bonus (land is recovering)
- Declining NDVI trend triggers a penalty (land is degrading)

**Why 30%?** Forage is what bison need to survive. Without adequate
vegetation, water, soils, and terrain don't matter.

### Water Access (25%)
Bison are not drought-adapted in the way that some Great Plains ungulates
are. They drink daily, typically covering up to 5km from water.
Land beyond reliable water access cannot support a herd year-round,
regardless of forage quality.

Water access is scored as distance from each pixel to the nearest
perennial stream, pond, or spring (from NHD). The scoring is:
- Within 1km: full score (1.0)
- 1–3km: linear decline
- 3–5km: marginal (0.1–0.3)
- Beyond 5km: effectively excluded (0.0)

**Why 25%?** Water is a hard constraint on Pine Ridge where surface
water is limited and episodic. This is higher than a typical habitat
model for wetter regions would assign.

### Soils (20%)
Soil grazing capacity (from gSSURGO) reflects how many animal unit months
per acre the land can sustain under proper grazing management. High-capacity
soils support larger herds without degradation; low-capacity soils require
rotational management and lower stocking rates.

For bison restoration, soils quality determines:
- Initial herd size that the land can support
- Whether habitat investment (vegetation restoration) will be productive
- Long-term economic viability of the bison program

**Why 20%?** Soils affect carrying capacity but not immediate habitat
usability. A low-capacity soil can still support a small herd; it just
limits the program's scale.

### Topography (15%)
Bison strongly prefer terrain with slope < 15 degrees for grazing and
movement. They will cross steeper terrain but avoid it for extended use.
On Pine Ridge, the badlands areas and steep canyon terrain are effectively
excluded from sustained bison ranging regardless of other conditions.

Topographic aspect (north vs. south-facing slopes) also affects:
- Snow depth and persistence (north-facing slopes hold more snow so
  bison can access grass beneath shallow snow but avoid deep drifts)
- Vegetation composition and productivity
- Summer heat exposure

**Why 15%?** Most of Pine Ridge is relatively flat mixed-grass prairie.
Topography is locally important (especially near the White River breaks)
but not the dominant constraint across the reservation as a whole.

### Climate Stress (10%)
Heat stress is the primary climate threat to bison on Pine Ridge.
Bison are well-adapted to Northern Plains winters but show physiological
stress above 95°F. As mean temperatures increase under both RCP scenarios,
the number of heat stress days per year will increase, with implications
for:
- Water consumption (higher in heat = more pressure on water infrastructure)
- Forage productivity (higher ET = reduced grass growth in peak summer)
- Herd health and reproduction

This component uses projected (2040–2060) heat stress days from MACAv2
to give the analysis a 20–40 year planning horizon which is relevant for
infrastructure investment decisions being made today.

**Why only 10%?** The current climate is the dominant factor for
habitat assessment. Climate stress is important for long-term planning
but should not override the near-term physical conditions that determine
where bison can be placed today.

## Sensitivity Analysis
Notebook 07 includes a sensitivity analysis showing how the priority
ranking of restoration patches changes under different weight assumptions.
This is important for presenting results to OLC and Tribal decision-makers:

- If the ranking is stable across reasonable weight variations,
  the finding is robust
- If key patches move substantially with small weight changes,
  that instability points to where additional data collection would
  most change the analysis

**Alternative weight scenarios to explore:**
| Scenario | Vegetation | Water | Soils | Topography | Climate |
|---|---|---|---|---|---|
| Default | 30% | 25% | 20% | 15% | 10% |
| Water-critical | 25% | 35% | 20% | 15% | 5% |
| Restoration-focused | 35% | 20% | 25% | 15% | 5% |
| Climate-forward | 25% | 25% | 20% | 10% | 20% |
| Equal weights | 20% | 20% | 20% | 20% | 20% |

## Updating Weights
Weights are defined in `src/constants.py`:

```python
BHSI_WEIGHTS = {
    "vegetation":  0.30,
    "water":       0.25,
    "soils":       0.20,
    "topography":  0.15,
    "climate":     0.10,
}
```

Change these values in consultation with the OLC bison program and
the Oglala Lakota Nation land management office. The weights represent
a scientific starting point, but local ecological knowledge and management
priorities should inform any adjustments.

**Required:** weights must sum to 1.0.
