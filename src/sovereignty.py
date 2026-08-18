from __future__ import annotations

"""
sovereignty.py data governance acknowledgment for pine_ridge_bison_habitat.

This analysis describes Oglala Lakota land for Oglala Lakota land
restoration purposes. All frameworks below apply.
"""
from src.constants import GOVERNANCE_REFS

_PREAMBLE = """
PINE RIDGE BISON HABITAT ANALYSIS DATA GOVERNANCE ACKNOWLEDGMENT
This analysis describes land within the Pine Ridge Reservation, home of
the Oglala Lakota Nation. Bison (Pte Oyate) hold deep cultural, spiritual,
and ecological significance for the Oglala Lakota people. This analysis
exists to support Tribal land stewardship, not to define it.

Results should be understood as one input into a land management
conversation, not as a determination of where bison belong.
That determination rests with the Oglala Lakota Nation.

GOVERNANCE FRAMEWORKS:

OCAP®  : The Oglala Lakota Nation has Ownership, Control, Access, and
  Possession of data describing their land and resources. Analysis results
  derived from public federal data about Pine Ridge still carry this
  obligation. Share results with OLC Cubedynamics and the relevant
  Oglala Lakota Nation land management offices before external distribution.
  Reference: https://fnigc.ca/ocap-training/

CARE   : Analysis must deliver Collective Benefit to the Oglala Lakota
  community, respect their Authority to Control land use decisions,
  uphold Responsibility to the community throughout the research process,
  and center Ethics across the full data lifecycle.
  Reference: https://www.gida-global.org/care

FAIR   : Data is Findable, Accessible, Interoperable, and Reusable.
  FAIR governs technical practices; CARE and OCAP® govern ethical
  obligations to the Oglala Lakota Nation.
  Reference: https://www.go-fair.org/fair-principles/

IEEE 2890-2025 : Recommended Practice for Provenance of Indigenous
  Peoples' Data. All analysis steps are documented so results can be
  traced back to specific data sources and methodological choices.
  Reference: https://standards.ieee.org/ieee/2890/10318/
"""

_DATA_SOURCES = {
    "census_aiannh": {
        "name":    "US Census Bureau TIGER/Line AIANNH Boundaries",
        "url":     "https://www.census.gov/cgi-bin/geo/shapefiles/index.php",
        "steward": "US Census Bureau",
        "license": "Public domain",
        "note":    (
            "Census boundaries are for statistical purposes. They do not "
            "represent legal jurisdiction or Tribal self-definition of territory."
        ),
    },
    "modis_ndvi": {
        "name":    "MODIS MOD13Q1 V061 NDVI via ORNL DAAC",
        "url":     "https://modis.ornl.gov/rst/api/v1/",
        "steward": "NASA / ORNL DAAC",
        "license": "NASA open data policy: non-commercial research",
        "citation": (
            "Didan, K. (2021). MODIS/Terra Vegetation Indices 16-Day L3 Global "
            "250m SIN Grid V061. NASA EOSDIS Land Processes DAAC. "
            "doi:10.5067/MODIS/MOD13Q1.061"
        ),
    },
    "nlcd": {
        "name":    "NLCD 2021 Land Cover for the Conterminous US",
        "url":     "https://www.mrlc.gov/data",
        "steward": "USGS / Multi-Resolution Land Characteristics Consortium",
        "license": "Public domain (USGS)",
        "citation": (
            "Dewitz, J. (2023). National Land Cover Database (NLCD) 2021 Products. "
            "US Geological Survey. doi:10.5066/P9OGBGM6"
        ),
    },
    "gssurgo": {
        "name":    "USDA gSSURGO Gridded Soil Survey Geographic Database",
        "url":     "https://www.nrcs.usda.gov/resources/data-and-reports/gridded-soil-survey-geographic-gssurgo-database",
        "steward": "USDA Natural Resources Conservation Service",
        "license": "Public domain (USDA)",
        "note":    (
            "Grazing capacity estimates from gSSURGO reflect average conditions "
            "under proper grazing management. Drought years reduce actual capacity. "
            "Local NRCS offices can provide site-specific guidance."
        ),
    },
    "dem_3dep": {
        "name":    "USGS 3DEP 1/3 Arc-Second DEM",
        "url":     "https://www.usgs.gov/3d-elevation-program",
        "steward": "US Geological Survey",
        "license": "Public domain (USGS)",
    },
    "nhd": {
        "name":    "USGS National Hydrography Dataset (NHD) Plus HR",
        "url":     "https://www.usgs.gov/national-hydrography/nhdplus-high-resolution",
        "steward": "US Geological Survey",
        "license": "Public domain (USGS)",
    },
    "maca_climate": {
        "name":    "MACAv2-METDATA Downscaled Climate Projections",
        "url":     "https://www.climatologylab.org/maca.html",
        "steward": "Northwest Knowledge Network, University of Idaho",
        "license": "Creative Commons CC0",
        "citation": (
            "Abatzoglou, J.T. and Brown, T.J. (2012). A comparison of statistical "
            "downscaling methods suited for wildfire applications. "
            "Int. J. Climatology. doi:10.1002/joc.2312"
        ),
    },
}


def print_data_acknowledgment(source_keys: list[str] | None = None) -> None:
    """Print governance preamble and data source acknowledgments."""
    print(_PREAMBLE)
    if not source_keys:
        return
    print("DATA SOURCES FOR THIS NOTEBOOK")
    for key in source_keys:
        src = _DATA_SOURCES.get(key)
        if not src:
            print(f"  [Unknown source key: {key}]")
            continue
        print(f"\n  {src['name']}")
        if src.get("url"):
            print(f"  URL     : {src['url']}")
        print(f"  Steward : {src['steward']}")
        print(f"  License : {src['license']}")
        if src.get("citation"):
            print(f"  Cite as : {src['citation']}")
        if src.get("note"):
            print(f"  Note    : {src['note']}")


def generate_citations(source_keys: list[str]) -> str:
    """Generate a plain-text citation block for notebook outputs."""
    lines = ["DATA CITATIONS", "=" * 55]
    for key in source_keys:
        src = _DATA_SOURCES.get(key)
        if not src:
            continue
        lines.append(f"\n{src['name']}")
        if src.get("citation"):
            lines.append(f"  {src['citation']}")
        if src.get("url"):
            lines.append(f"  {src['url']}")
        lines.append(f"  Steward: {src['steward']} | License: {src['license']}")
    lines.append("\nGovernance: OCAP® | CARE | FAIR | IEEE 2890-2025")
    for name, url in GOVERNANCE_REFS.items():
        lines.append(f"  {name.upper()}: {url}")
    return "\n".join(lines)
