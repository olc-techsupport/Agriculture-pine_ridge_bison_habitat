"""
constants.py project-wide constants for pine_ridge_bison_habitat.
"""
from __future__ import annotations
from pathlib import Path

# Repository root 
REPO_ROOT = Path(__file__).resolve().parents[1]

# Coordinate reference systems
CRS_GEOGRAPHIC = "EPSG:4326"    # WGS84 for boundaries, API queries
CRS_PROJECTED  = "EPSG:5070"    # Albers Equal Area CONUS for area, distance calculations

# Target raster resolution 
# 30m matches Landsat/NLCD resolution to be consistent across all layers
TARGET_RES_M   = 30             # meters

# Data directories 
CACHE_DIR   = REPO_ROOT/"data"/"cache"
OUTPUTS_DIR = REPO_ROOT/"outputs"
FIGURES_DIR = OUTPUTS_DIR/"figures"

for _d in [CACHE_DIR, OUTPUTS_DIR, FIGURES_DIR]:
    _d.mkdir(parents=True, exist_ok=True)

# Pine Ridge bounding box (WGS84: min_lon, min_lat, max_lon, max_lat)
# Adds a 0.1° buffer beyond the reservation boundary for context
PINE_RIDGE_BBOX = (-103.5, 42.5, -101.5, 43.8)

# Centroid for point data queries
PINE_RIDGE_LAT =  43.35
PINE_RIDGE_LON = -102.55

# Census TIGER 
CENSUS_TIGER_BASE = "https://www2.census.gov/geo/tiger"
PINE_RIDGE_CENSUS_NAME = "Pine Ridge"       # NAME field in AIANNH shapefile

# MODIS NDVI (ORNL DAAC) 
ORNL_BASE        = "https://modis.ornl.gov/rst/api/v1"
MODIS_PRODUCT    = "MOD13Q1"
MODIS_BAND       = "250m_16_days_NDVI"
NDVI_SCALE       = 0.0001          # raw int to float
NDVI_FILL        = -3000           # fill value to exclude
MODIS_START_YEAR = 2000
MODIS_END_YEAR   = 2023
# Chunk requests to ≤ 8 composites per API call (10-tile limit)
MODIS_YEAR_CHUNKS = [("001", "113"), ("129", "241"), ("257", "353")]

# NLCD
# MRLC WCS endpoint for NLCD 2021
NLCD_WCS_URL = (
    "https://www.mrlc.gov/geoserver/mrlc_display/NLCD_2021_Land_Cover_L48/"
    "wcs?SERVICE=WCS&VERSION=2.0.1&REQUEST=GetCoverage"
    "&COVERAGEID=NLCD_2021_Land_Cover_L48"
)

# NLCD classes relevant to bison habitat
# Class : (label, base_suitability_score)
NLCD_BISON_SUITABILITY = {
    71: ("Grassland/Herbaceous",        1.00),   # ideal native mixed-grass prairie
    72: ("Sedge/Herbaceous",            0.90),   # good wet meadow grassland
    81: ("Pasture/Hay",                 0.60),   # moderate managed grassland
    82: ("Cultivated Crops",            0.10),   # poor needs restoration
    52: ("Shrub/Scrub",                 0.55),   # moderate browse component
    41: ("Deciduous Forest",            0.20),   # low too dense for open herds
    42: ("Evergreen Forest",            0.10),   # low
    43: ("Mixed Forest",                0.15),   # low
    11: ("Open Water",                  0.00),   # exclude
    21: ("Developed Open Space",        0.05),   # effectively exclude
    22: ("Developed Low Intensity",     0.00),
    23: ("Developed Medium Intensity",  0.00),
    24: ("Developed High Intensity",    0.00),
    31: ("Barren Land",                 0.15),   # low
    90: ("Woody Wetlands",              0.30),
    95: ("Emergent Herbaceous Wetland", 0.50),
}

# gSSURGO / SoilDataAccess 
SOIL_DATA_ACCESS_URL = "https://SDMDataAccess.sc.egov.usda.gov/Tabular/post.rest"

# USGS 3DEP 
TNM_API_URL    = "https://tnmaccess.nationalmap.gov/api/v1/products"
DEM_DATASET    = "National Elevation Dataset (NED) 1/3 arc-second"
# Slope thresholds for bison suitability (degrees)
SLOPE_THRESHOLDS = {
    "ideal":    5,    # < 5° = flat, bison strongly prefer
    "good":    15,    # 5–15° = usable terrain
    "marginal": 25,   # 15–25° = bison will traverse but avoid for grazing
    "exclude":  25,   # > 25° = too steep
}

# NHD flowlines 
NHD_FLOWLINE_URL = (
    "https://hydro.nationalmap.gov/arcgis/rest/services"
    "/NHDPlus_HR/MapServer/3/query"
)
NHD_WATERBODY_URL = (
    "https://hydro.nationalmap.gov/arcgis/rest/services"
    "/NHDPlus_HR/MapServer/7/query"
)
# Maximum distance to water for bison suitability (meters)
# Bison typically water daily; 5km is a practical limit for open range
WATER_DISTANCE_MAX_M = 5000

# MACAv2 
MACA_BASE  = (
    "http://thredds.northwestknowledge.net:8080/thredds/dodsC"
    "/agg_macav2metdata_"
)
MACA_MODEL    = "BNU-ESM"
MACA_SCENARIO = "rcp85"        # high emissions for conservative planning
MACA_PROJ_START = 2006
MACA_PROJ_END   = 2099
# Heat stress threshold relevant for bison (°F)
# Bison are well-adapted to cold; heat is the primary climate stress
HEAT_STRESS_F    = 95           # bison begin showing heat stress > 95°F
EXTREME_HEAT_F   = 105          # severe heat stress threshold

# BHSI component weights 
# Must sum to 1.0
# Rationale documented in documents/bhsi_weights.md
BHSI_WEIGHTS = {
    "vegetation":  0.30,    # dominant factor = what bison eat
    "soils":       0.20,    # grazing capacity = how much the land can support
    "water":       0.25,    # critical constraint = bison must drink daily
    "topography":  0.15,    # terrain preference = bison avoid steep slopes
    "climate":     0.10,    # future stress = planning horizon factor
}

# DBSCAN clustering parameters 
# Documented in documents/methods_clustering.md
DBSCAN_EPS_M         = 1000    # meters for max distance between pixels in same patch
DBSCAN_MIN_ACRES     = 500     # minimum viable bison management unit
BHSI_THRESHOLD_PCT   = 70      # top N% of BHSI scores considered high-suitability

# Growing season 
GROWING_MONTHS = [5, 6, 7, 8, 9]   

# Data sovereignty 
GOVERNANCE_REFS = {
    "ocap":       "https://fnigc.ca/ocap-training/",
    "care":       "https://www.gida-global.org/care",
    "fair":       "https://www.go-fair.org/fair-principles/",
    "ieee_2890":  "https://standards.ieee.org/ieee/2890/10318/",
}
