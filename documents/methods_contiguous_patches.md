# Habitat patch identification: raster connected components

## Why this method

The series identifies contiguous groups of high-scoring raster cells using eight-neighbor connected-component labeling. This method runs efficiently on ordinary student laptops and uses the existing raster grid directly without constructing a large coordinate-neighbor graph.

Connected components answer a limited question: which selected high-score cells touch along an edge or corner and form an area at least as large as the configured minimum? They do not establish ecological connectivity, land access, herd viability, ownership, fencing feasibility, or restoration priority.

## Steps

1. Calculate the weighted BHSI only from complete, aligned, spatially varying component rasters.
2. Select cells above `BHSI_THRESHOLD_PCT`.
3. Label eight-neighbor connected regions with `scipy.ndimage.label`.
4. Remove regions smaller than `MIN_PATCH_ACRES`.
5. Re-label retained regions sequentially and summarize them for review.

The implementation is in `src/patches.py`. Zero represents background or a removed undersized region; positive integers identify retained connected regions.

## Parameters and interpretation

`BHSI_THRESHOLD_PCT = 70` and `MIN_PATCH_ACRES = 500` are transparent teaching defaults, not approved biological or management thresholds. Both must be reviewed locally. Diagonal connectivity can join cells that meet only at a corner; four-neighbor connectivity is an important sensitivity scenario.

Changing either parameter may substantially alter the count, shape, and area of candidate regions. Report parameter sensitivity and do not describe a stable result as true solely because it is stable.

## Limitations

The method does not account for seasonal movement, reliable water, land tenure, roads, fences, disease management, cultural priorities, or field conditions. Precise candidate locations remain sensitive screening outputs and must not be externally distributed before the required review and authorization.
