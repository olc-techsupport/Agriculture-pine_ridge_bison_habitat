"""Build the BHSI data cube after notebooks 02–07 have produced their layers."""
from src.constants import OUTPUTS_DIR
from src.data_cube import create_bhsi_data_cube

layers = {
    "vegetation": OUTPUTS_DIR/"bhsi_vegetation.tif",
    "soils": OUTPUTS_DIR/"bhsi_soils.tif",
    "topography": OUTPUTS_DIR/"bhsi_topography.tif",
    "water": OUTPUTS_DIR/"bhsi_water.tif",
    "climate": OUTPUTS_DIR/"bhsi_climate.tif",
    "bhsi": OUTPUTS_DIR/"bhsi_composite.tif",
}
cube = create_bhsi_data_cube(layers, OUTPUTS_DIR/"pine_ridge_bhsi_cube.nc")
print(f"Data cube written: {cube}")