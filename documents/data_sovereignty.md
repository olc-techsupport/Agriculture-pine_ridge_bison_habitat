# Data Sovereignty
This analysis describes Oglala Lakota land for Oglala Lakota land
restoration purposes. All frameworks described below apply to every
dataset used in this repository.

## Pte Oyate and Oglala Lakota Sovereignty
Bison (Pte Oyate) are not wildlife in the Western management sense for
the Oglala Lakota. They are relatives, central to ceremony, food systems,
and the philosophical relationship between the Lakota people and the land.
The near-extermination of bison in the 19th century was inseparable from
the effort to dispossess Indigenous peoples of the Northern Great Plains.
Restoration is therefore an assertion of sovereignty.

This analysis exists to support that restoration. It provides information 
that combines spatial and environmental data from public federal sources
that can inform where and how restoration begins. It does not define
where bison belong. That knowledge resides with the Oglala Lakota people
and with the land itself.

## Governance Frameworks

### OCAP®
The Oglala Lakota Nation has Ownership, Control, Access, and Possession
of data describing their land, resources, and environment.

**In practice:**
- Analysis results should be shared with OLC Cubedynamics and the
  relevant Oglala Lakota Nation land management offices before any
  external distribution
- The priority restoration unit map (notebook 07 output) should be
  reviewed by the bison program before it informs any land management
  decisions
- If this analysis is published or presented externally, Oglala Lakota
  Nation consultation is required through the Research Review Board. 

Reference: https://fnigc.ca/ocap-training/

### CARE Principles
**Collective Benefit (C)**  
The bison habitat analysis is designed to benefit the Oglala Lakota
bison restoration program directly. Results are structured to support
Tribal land management decisions, not academic publication.

**Authority to Control (A)**  
The Oglala Lakota Nation has authority over land use decisions on
Pine Ridge. This analysis is advisory, not prescriptive. The bison
program, Research Review Board, and relevant governance bodies determine 
where and how restoration proceeds.

**Responsibility (R)**  
Every analytical step is documented and explainable. The BHSI weights,
the DBSCAN parameters, and the data sources are all transparent and
adjustable. If the analysis produces a result that doesn't match on-the-ground 
knowledge, the methodology can be examined and corrected.

**Ethics (E)**  
The analysis centers Oglala Lakota land stewardship values. Land that
has been degraded by agriculture or overgrazing is not written off,
the BHSI is designed to identify restoration opportunity as well as
current suitability.

Reference: https://www.gida-global.org/care

### FAIR Principles
All data is downloaded from public sources and analysis is fully
reproducible. Source citations are included for every dataset.
Outputs use standard formats (GeoTIFF, GeoPackage, CSV) accessible
with any GIS software.

Reference: https://www.go-fair.org/fair-principles/

### IEEE 2890-2025
Provenance of all data sources and transformations is documented in
the `src/sovereignty.py` data source registry and in notebook headers.
The analysis chain from raw data to final BHSI map is traceable and
auditable.

Reference: https://standards.ieee.org/ieee/2890/10318/

## Federal Data About Tribal Lands
All data used in this analysis comes from federal public sources
(USGS, USDA, NASA, Census Bureau, NOAA). This data covers Pine Ridge
but was not collected for the benefit of the Oglala Lakota Nation.

Specific governance notes:
**Census TIGER boundaries** is for statistical purposes only. The Census
boundary does not represent the full extent of Oglala Lakota territory
or treaty rights.

**USDA gSSURGO soil data** contains the grazing capacity estimates in gSSURGO
reflect federal resource management frameworks. Local NRCS offices and
Tribal range managers may have more accurate site-specific knowledge.

**NLCD land cover** is classified from satellite imagery at 30m resolution.
Classification errors are possible, particularly between grassland and
shrubland categories. Ground-truth validation with local knowledge is
important before using NLCD classes for management decisions.

**USGS 3DEP elevation data** is generally accurate for terrain analysis
at this scale. Badlands terrain in the White River breaks may have
higher error rates due to complex topography.

## Sharing Analysis Results
Before sharing analysis results outside the OLC/Oglala Lakota Nation
partnership:

1. Share the draft results with OLC Cubedynamics for review
2. Present to the relevant Oglala Lakota Nation land management or
   natural resources office
3. Incorporate feedback, particularly where results conflict with
   on-the-ground knowledge
4. Obtain explicit authorization before external publication,
   presentation, or distribution

Results that identify specific restoration priority areas are
particularly sensitive as they have implications for land management,
funding, and potentially for land use conflicts with adjacent
non-Tribal landowners.
