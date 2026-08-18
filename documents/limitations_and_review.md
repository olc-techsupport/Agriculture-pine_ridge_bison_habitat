# Analytical Limits and Required Review

## Spatial evidence requirement
The BHSI is a decision-support screening product, not a management decision.
Only spatially resolved component layers may be used to distinguish candidate
patches. Reservation-wide scalar layers are planning context and must be
replaced by gridded data before priority units are presented as spatial
recommendations.

Current completion requirements are:

1. Rasterize gSSURGO MUPOLYGON attributes using the locally approved grazing
   capacity field and document any crosswalk to suitability scores.
2. Use gridded daily downscaled climate projections to calculate heat-stress
   days and seasonal precipitation metrics for each pixel; document scenario,
   model ensemble, baseline, and planning period.
3. Produce gridded vegetation-condition trends or remove the centroid NDVI
   adjustment from patch ranking.
4. Validate candidate units with field observations, water reliability,
   fencing, access, tenure, and locally held ecological knowledge.

## Review and release gate
`bhsi_provenance.json` intentionally records that external distribution is
not authorized. Before release, OLC Cubedynamics and the appropriate Oglala
Lakota Nation offices must review the data sources, weights, constraints,
candidate units, and intended audience, then authorize the specific release.

Do not publish precise priority-unit locations until that review is complete.
